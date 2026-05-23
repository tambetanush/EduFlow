import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, CheckCircle2, Search, XCircle } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import VCard from "@/components/ui-custom/VCard";
import { useVToast } from "@/components/ui-custom/VToast";
import { fetchSubmissionReview, fetchSubmissions, gradeSubmission } from "@/services/api";
import type { Submission } from "@/mock/mockData";

const SubmissionsPage = () => {
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const { data: submissions = [], isLoading, isError, error, refetch } = useQuery({ queryKey: ["submissions"], queryFn: fetchSubmissions });

  const tableEmptyText = isLoading
    ? "Loading submissions..."
    : isError
    ? (error instanceof Error ? error.message : "Failed to load submissions.")
    : "No submissions found.";
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [selected, setSelected] = useState<Submission | null>(null);
  const [viewModal, setViewModal] = useState(false);
  const submissionReviewQuery = useQuery({
    queryKey: ["submissionReview", selected?.id],
    queryFn: () => fetchSubmissionReview(selected?.id ?? ""),
    enabled: Boolean(selected?.id && viewModal && selected?.status === "Graded"),
  });
  const gradeMutation = useMutation({
    mutationFn: gradeSubmission,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["submissions"] });
      showToast("success", "Graded", "Submission has been graded.");
      setViewModal(false);
    },
    onError: (err: unknown) => {
      showToast("destructive", "Grade Failed", err instanceof Error ? err.message : "Unable to grade submission.");
    },
  });

  const filtered = submissions.filter(s => {
    const matchSearch = s.studentName.toLowerCase().includes(search.toLowerCase()) || s.assessment.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "All" || s.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const columns = [
    { key: "studentName", header: "Student" },
    { key: "assessment", header: "Assessment" },
    { key: "score", header: "Score", render: (r: Submission) => <span className="font-medium text-foreground">{r.status === "Pending" ? "—" : r.score}</span> },
    { key: "status", header: "Status", render: (r: Submission) => (
      <VBadge variant={r.status === "Graded" ? "success" : r.status === "Pending" ? "warning" : "destructive"}>
        {r.status}
      </VBadge>
    )},
    { key: "submittedAt", header: "Submitted" },
    { key: "actions", header: "Actions", render: (r: Submission) => (
      <div className="flex gap-1">
        <button onClick={() => { setSelected(r); setViewModal(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors">
          <Eye className="h-4 w-4" />
        </button>
        {r.status === "Pending" && (
          <button onClick={() => gradeMutation.mutate(r.id)} className="rounded-lg p-1.5 text-muted-foreground hover:bg-success/10 hover:text-success transition-colors">
            <CheckCircle2 className="h-4 w-4" />
          </button>
        )}
      </div>
    )},
  ];

  return (
    <DashboardLayout title="Submissions">
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search submissions..." value={search} onChange={(e) => setSearch(e.target.value)} className="vidya-input pl-10" />
        </div>
        <div className="flex gap-2">
          {["All", "Graded", "Pending", "Late"].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)} className={`px-3 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${statusFilter === s ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-accent"}`}>
              {s}
            </button>
          ))}
        </div>
      </div>
      {isError && (
        <div className="mb-4">
          <VButton variant="secondary" onClick={() => refetch()}>Retry</VButton>
        </div>
      )}
      <VTable columns={columns} data={filtered} emptyText={tableEmptyText} />

      <VModal isOpen={viewModal} onClose={() => setViewModal(false)} title="Submission Details" className="max-w-2xl">
        {selected && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div><p className="text-xs text-muted-foreground mb-1">Student</p><p className="text-sm font-medium text-foreground">{selected.studentName}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Assessment</p><p className="text-sm font-medium text-foreground">{selected.assessment}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Score</p><p className="text-2xl font-bold text-foreground">{selected.status === "Pending" ? "—" : selected.score}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Status</p><VBadge variant={selected.status === "Graded" ? "success" : "warning"}>{selected.status}</VBadge></div>
              <div className="col-span-2"><p className="text-xs text-muted-foreground mb-1">Submitted At</p><p className="text-sm text-foreground">{selected.submittedAt}</p></div>
            </div>

            {/* Full question-level breakdown for graded submissions */}
            {selected.status === "Graded" && (
              <div className="border-t border-border pt-4">
                <h4 className="text-sm font-semibold text-foreground mb-3">Question-Level Breakdown</h4>
                <div className="rounded-xl bg-muted p-4">
                  {submissionReviewQuery.isLoading && <p className="text-sm text-muted-foreground">Loading review...</p>}
                  {!submissionReviewQuery.isLoading && submissionReviewQuery.data && (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {submissionReviewQuery.data.questions.map((question, index) => (
                        <VCard key={question.question_id} className={`p-3 ${question.is_correct ? "border-success/40" : "border-destructive/40"}`}>
                          <p className="text-sm font-medium text-foreground">{index + 1}. {question.question_text}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Selected: {question.selected_option_texts.join(", ") || "Not answered"}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Correct: {question.correct_option_texts.join(", ") || "—"}
                          </p>
                          <p className={`text-xs mt-1 ${question.is_correct ? "text-success" : "text-destructive"}`}>
                            Marks: {question.earned_marks}/{question.max_marks}
                          </p>
                        </VCard>
                      ))}
                    </div>
                  )}
                  {!submissionReviewQuery.isLoading && !submissionReviewQuery.data && (
                    <p className="text-sm text-muted-foreground">Detailed review unavailable for this submission.</p>
                  )}
                </div>
              </div>
            )}

            {selected.status === "Pending" && (
              <VButton className="w-full" onClick={() => gradeMutation.mutate(selected.id)} isLoading={gradeMutation.isPending}>
                <CheckCircle2 className="h-4 w-4" /> Grade Submission
              </VButton>
            )}
          </div>
        )}
      </VModal>
    </DashboardLayout>
  );
};

export default SubmissionsPage;
