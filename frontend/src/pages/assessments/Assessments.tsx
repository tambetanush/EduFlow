import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Play, Eye, ClipboardList, Trophy, BarChart3 } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { useAuth } from "@/hooks/useAuth";
import { useRole } from "@/hooks/useRole";
import {
  createAssessment,
  createAssessmentQuestion,
  createWorkshopModule,
  deleteAssessment,
  fetchAssessmentLeaderboard,
  fetchAssessmentLeaderboardDrilldown,
  fetchAssessmentQuestions,
  fetchAssessments,
  fetchWorkshopModules,
  fetchWorkshops,
  updateAssessmentQuestion,
  updateAssessment,
} from "@/services/api";
type AssessmentRow = Awaited<ReturnType<typeof fetchAssessments>>[number];

type QuestionType = "MCQ" | "MSQ" | "Integer";

interface QuestionItem {
  text: string;
  type: QuestionType;
  options: string[];
  correct: number[];
  marks: number;
}

const AssessmentsPage = () => {
  const navigate = useNavigate();
  const role = useRole();
  const { user } = useAuth();
  const canManage = role !== "student";
  const isStudent = role === "student";
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const { data: all = [] } = useQuery({
    queryKey: ["assessments", role, user?.id],
    queryFn: () =>
      role === "student"
        ? fetchAssessments({ studentId: user?.id })
        : fetchAssessments(),
    enabled: role !== "student" || Boolean(user?.id),
  });
  const { data: workshops = [] } = useQuery({
    queryKey: ["workshops", "assessment-edit"],
    queryFn: fetchWorkshops,
    enabled: canManage,
  });
  const [createModal, setCreateModal] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [selected, setSelected] = useState<AssessmentRow | null>(null);
  const [formTitle, setFormTitle] = useState("");
  const [formWorkshop, setFormWorkshop] = useState("");
  const [formWorkshopId, setFormWorkshopId] = useState("");
  const [formModuleId, setFormModuleId] = useState("");
  const [newModuleTitle, setNewModuleTitle] = useState("");
  const [formTotal, setFormTotal] = useState("100");
  const [formPassing, setFormPassing] = useState("40");

  // Question builder state
  const [questionModal, setQuestionModal] = useState(false);
  const [qText, setQText] = useState("");
  const [qType, setQType] = useState<QuestionType>("MCQ");
  const [qOptions, setQOptions] = useState(["", "", "", ""]);
  const [qCorrect, setQCorrect] = useState<number[]>([0]);
  const [qMarks, setQMarks] = useState("10");
  const [editQuestionModal, setEditQuestionModal] = useState(false);
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [editingQuestionText, setEditingQuestionText] = useState("");
  const [editingQuestionType, setEditingQuestionType] = useState<QuestionType>("MCQ");
  const [editingQuestionOptions, setEditingQuestionOptions] = useState(["", "", "", ""]);
  const [editingQuestionCorrect, setEditingQuestionCorrect] = useState<number[]>([0]);
  const [editingQuestionMarks, setEditingQuestionMarks] = useState("10");

  // Leaderboard & Student Performance
  const [leaderboardModal, setLeaderboardModal] = useState(false);
  const [studentPerfModal, setStudentPerfModal] = useState(false);
  const [selectedStudentIndex, setSelectedStudentIndex] = useState<number | null>(null);
  const [perfTab, setPerfTab] = useState<"basic" | "detailed">("basic");

  const leaderboardQuery = useQuery({
    queryKey: ["assessmentLeaderboard", selected?.id],
    queryFn: () => fetchAssessmentLeaderboard(selected?.id ?? ""),
    enabled: Boolean(selected?.id && leaderboardModal),
  });
  const leaderboardEntries = leaderboardQuery.data?.entries ?? [];
  const selectedStudent = selectedStudentIndex !== null ? leaderboardEntries[selectedStudentIndex] : null;
  const selectedStudentId = selectedStudent?.student_id ?? "";
  const studentDrilldownQuery = useQuery({
    queryKey: ["assessmentLeaderboardDrilldown", selected?.id, selectedStudentId],
    queryFn: () => fetchAssessmentLeaderboardDrilldown(selected?.id ?? "", selectedStudentId),
    enabled: Boolean(studentPerfModal && perfTab === "detailed" && selected?.id && selectedStudentId),
  });

  const questionsQuery = useQuery({
    queryKey: ["assessmentQuestions", selected?.id],
    queryFn: () => fetchAssessmentQuestions(selected?.id ?? ""),
    enabled: Boolean(selected?.id && questionModal),
  });

  const { data: workshopModules = [] } = useQuery({
    queryKey: ["workshopModules", formWorkshopId],
    queryFn: () => fetchWorkshopModules(formWorkshopId),
    enabled: canManage && Boolean(formWorkshopId),
  });

  useEffect(() => {
    if (!formWorkshopId) {
      setFormModuleId("");
      return;
    }
    if (!workshopModules.some((item) => item.id === formModuleId)) {
      setFormModuleId(workshopModules[0]?.id ?? "");
    }
  }, [formWorkshopId, formModuleId, workshopModules]);

  const workshopOptions = useMemo(
    () => [{ value: "", label: "Select a workshop" }].concat(workshops.map((w) => ({ value: w.id, label: w.name }))),
    [workshops],
  );

  const moduleOptions = useMemo(
    () => [{ value: "", label: "Select a module" }].concat(
      workshopModules.map((m) => ({ value: m.id, label: m.title ?? "Module" })),
    ),
    [workshopModules],
  );

  const createAssessmentMutation = useMutation({
    mutationFn: createAssessment,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["assessments"] });
      setCreateModal(false);
      showToast("success", "Assessment Created");
    },
    onError: (err: unknown) => {
      showToast("error", "Create Failed", err instanceof Error ? err.message : "Unable to create assessment.");
    },
  });

  const createModuleMutation = useMutation({
    mutationFn: (payload: { workshopId: string; title: string }) =>
      createWorkshopModule(payload),
    onSuccess: async (module) => {
      await queryClient.invalidateQueries({ queryKey: ["workshopModules", formWorkshopId] });
      setFormModuleId(module.id);
      setNewModuleTitle("");
      showToast("success", "Module Created", "New module selected automatically.");
    },
    onError: (err: unknown) => {
      showToast("error", "Module Create Failed", err instanceof Error ? err.message : "Unable to create module.");
    },
  });

  const updateAssessmentMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { title?: string; totalMarks?: number; passingMarks?: number; moduleId?: string | null } }) =>
      updateAssessment(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["assessments"] });
      setEditModal(false);
      showToast("success", "Assessment Updated");
    },
    onError: (err: unknown) => {
      showToast("error", "Update Failed", err instanceof Error ? err.message : "Unable to update assessment.");
    },
  });

  const deleteAssessmentMutation = useMutation({
    mutationFn: deleteAssessment,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["assessments"] });
      setDeleteDialog(false);
      showToast("success", "Assessment Deleted");
    },
    onError: (err: unknown) => {
      showToast("error", "Delete Failed", err instanceof Error ? err.message : "Unable to delete assessment.");
    },
  });

  const addQuestionMutation = useMutation({
    mutationFn: (payload: { assessmentId: string; question: QuestionItem }) =>
      createAssessmentQuestion(payload.assessmentId, {
        text: payload.question.text,
        type: payload.question.type,
        marks: payload.question.marks,
        options:
          payload.question.type === "Integer"
            ? []
            : payload.question.options.map((opt, idx) => ({
                id: `opt-${idx + 1}`,
                text: opt,
                is_correct: payload.question.correct.includes(idx),
              })),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["assessmentQuestions", selected?.id] });
      showToast("success", "Question Added");
    },
    onError: (err: unknown) => {
      showToast("error", "Add Question Failed", err instanceof Error ? err.message : "Unable to add question.");
    },
  });

  const updateQuestionMutation = useMutation({
    mutationFn: (payload: { questionId: string; question: QuestionItem }) =>
      updateAssessmentQuestion(payload.questionId, {
        text: payload.question.text,
        type: payload.question.type,
        marks: payload.question.marks,
        options:
          payload.question.type === "Integer"
            ? []
            : payload.question.options.map((opt, idx) => ({
                id: `opt-${idx + 1}`,
                text: opt,
                is_correct: payload.question.correct.includes(idx),
              })),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["assessmentQuestions", selected?.id] });
      setEditQuestionModal(false);
      setEditingQuestionId(null);
      showToast("success", "Question Updated");
    },
    onError: (err: unknown) => {
      showToast("error", "Update Question Failed", err instanceof Error ? err.message : "Unable to update question.");
    },
  });

  const openStudentPerf = (index: number) => {
    setSelectedStudentIndex(index);
    setPerfTab("basic");
    setStudentPerfModal(true);
  };

  const displayQuestions: QuestionItem[] =
    questionsQuery.data?.map((question) => ({
      text: question.text ?? "",
      type: (question.type?.toUpperCase() as QuestionType) || "MCQ",
      options: (question.options ?? []).map((option) => option.text),
      correct: (question.options ?? [])
        .map((option, index) => (option.is_correct ? index : -1))
        .filter((index) => index >= 0),
      marks: question.marks ?? 1,
    })) ?? [];

  const openQuestionEditor = (questionIndex: number) => {
    const question = questionsQuery.data?.[questionIndex];
    if (!question) return;
    const options = (question.options ?? []).map((option) => option.text);
    while (options.length < 4) options.push("");
    const correct = (question.options ?? [])
      .map((option, index) => (option.is_correct ? index : -1))
      .filter((index) => index >= 0);
    setEditingQuestionId(question.id);
    setEditingQuestionText(question.text ?? "");
    setEditingQuestionType((question.type?.toUpperCase() as QuestionType) || "MCQ");
    setEditingQuestionOptions(options.slice(0, 4));
    setEditingQuestionCorrect(correct.length > 0 ? correct : [0]);
    setEditingQuestionMarks(String(question.marks ?? 1));
    setEditQuestionModal(true);
  };

  return (
    <DashboardLayout title="Assessments">
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-muted-foreground">{all.length} assessments</p>
        <div className="flex gap-2">
          {canManage && (
            <>
              <VButton
                variant="secondary"
                onClick={() => {
                  if (!selected && all.length > 0) {
                    setSelected(all[0]);
                  }
                  setLeaderboardModal(true);
                }}
              >
                <Trophy className="h-4 w-4" /> Leaderboard
              </VButton>
              <VButton onClick={() => {
                setFormTitle("");
                setFormWorkshop("");
                setFormWorkshopId("");
                setFormModuleId("");
                setNewModuleTitle("");
                setFormTotal("100");
                setFormPassing("40");
                setCreateModal(true);
              }}>
                <Plus className="h-4 w-4" /> Create Assessment
              </VButton>
            </>
          )}
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {all.map((a) => (
          <VCard key={a.id} hover className="p-5 flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <VBadge variant="success">Available</VBadge>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{a.totalMarks} marks</span>
              </div>
            </div>
            <div className="flex items-center gap-3 mb-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary shrink-0">
                <ClipboardList className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">{a.title}</h3>
                <p className="text-xs text-muted-foreground">{a.workshop}</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground mb-4 flex-1">Passing: {a.passingMarks}/{a.totalMarks} marks</p>
            <div className="flex gap-2">
              {isStudent ? (
                <VButton className="flex-1" onClick={() => navigate(`/assessments/attempt/${a.id}`)}>
                  <Play className="h-4 w-4" /> Take Test
                </VButton>
              ) : canManage ? (
                <>
                  <VButton variant="secondary" size="sm" onClick={() => { setSelected(a); setQuestionModal(true); }}>
                    <Eye className="h-3.5 w-3.5" /> Questions
                  </VButton>
                  <VButton variant="secondary" size="sm" onClick={() => {
                    const workshopId = workshops.find((workshop) => workshop.name === a.workshop)?.id ?? "";
                    setSelected(a);
                    setFormTitle(a.title);
                    setFormWorkshop(a.workshop);
                    setFormWorkshopId(workshopId);
                    setFormModuleId("");
                    setNewModuleTitle("");
                    setFormTotal(String(a.totalMarks));
                    setFormPassing(String(a.passingMarks));
                    setEditModal(true);
                  }}>
                    <Pencil className="h-3.5 w-3.5" /> Edit
                  </VButton>
                  <VButton variant="secondary" size="sm" onClick={() => { setSelected(a); setLeaderboardModal(true); }}>
                    <BarChart3 className="h-3.5 w-3.5" /> Stats
                  </VButton>
                  <VButton variant="destructive" size="sm" onClick={() => { setSelected(a); setDeleteDialog(true); }}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </VButton>
                </>
              ) : (
                <VButton variant="secondary" className="flex-1" onClick={() => showToast("info", "Assessment Details", a.title)}>
                  <Eye className="h-4 w-4" /> View
                </VButton>
              )}
            </div>
          </VCard>
        ))}
      </div>

      {/* Create Modal */}
      <VModal isOpen={createModal} onClose={() => setCreateModal(false)} title="Create Assessment">
        <div className="space-y-4">
          <VInput label="Title" placeholder="Assessment title" value={formTitle} onChange={e => setFormTitle(e.target.value)} />
          <VSelect label="Workshop" value={formWorkshopId} onChange={e => {
            const workshopId = e.target.value;
            const workshopName = workshops.find((workshop) => workshop.id === workshopId)?.name ?? "";
            setFormWorkshopId(workshopId);
            setFormWorkshop(workshopName);
          }} options={workshopOptions} />
          <VSelect label="Module" value={formModuleId} onChange={e => setFormModuleId(e.target.value)} options={moduleOptions} />
          {formWorkshopId && workshopModules.length === 0 && (
            <div className="rounded-lg border border-warning/40 bg-warning/5 p-3 space-y-2">
              <p className="text-sm text-foreground">No modules yet — create one first.</p>
              <div className="flex gap-2">
                <VInput
                  placeholder="New module title"
                  value={newModuleTitle}
                  onChange={e => setNewModuleTitle(e.target.value)}
                />
                <VButton
                  variant="secondary"
                  onClick={() => {
                    if (!newModuleTitle.trim()) {
                      showToast("warning", "Module Title Required", "Enter a module title.");
                      return;
                    }
                    createModuleMutation.mutate({
                      workshopId: formWorkshopId,
                      title: newModuleTitle.trim(),
                    });
                  }}
                  isLoading={createModuleMutation.isPending}
                >
                  Create Module
                </VButton>
              </div>
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <VInput label="Total Marks" type="number" value={formTotal} onChange={e => setFormTotal(e.target.value)} />
            <VInput label="Passing Marks" type="number" value={formPassing} onChange={e => setFormPassing(e.target.value)} />
          </div>
          <div className="flex justify-end gap-3"><VButton variant="ghost" onClick={() => setCreateModal(false)}>Cancel</VButton><VButton onClick={() => {
            if (!formWorkshopId) {
              showToast("warning", "Workshop Required", "Select a workshop name that exists.");
              return;
            }
            if (!formModuleId) {
              showToast("warning", "Module Required", "Select or create a module first.");
              return;
            }
            createAssessmentMutation.mutate({
              workshopId: formWorkshopId,
              moduleId: formModuleId,
              title: formTitle,
              totalMarks: Number(formTotal),
              passingMarks: Number(formPassing),
            });
          }} disabled={!formTitle || !formWorkshopId || !formModuleId || createAssessmentMutation.isPending}>Create</VButton></div>
        </div>
      </VModal>

      {/* Edit Modal */}
      <VModal isOpen={editModal} onClose={() => setEditModal(false)} title="Edit Assessment">
        <div className="space-y-4">
          <VInput label="Title" value={formTitle} onChange={e => setFormTitle(e.target.value)} />
          <VSelect label="Workshop" value={formWorkshopId} onChange={e => {
            const workshopId = e.target.value;
            const workshopName = workshops.find((workshop) => workshop.id === workshopId)?.name ?? "";
            setFormWorkshopId(workshopId);
            setFormWorkshop(workshopName);
          }} options={workshopOptions} />
          <VSelect label="Module" value={formModuleId} onChange={e => setFormModuleId(e.target.value)} options={moduleOptions} />
          {formWorkshopId && workshopModules.length === 0 && (
            <div className="rounded-lg border border-warning/40 bg-warning/5 p-3 space-y-2">
              <p className="text-sm text-foreground">No modules yet — create one first.</p>
              <div className="flex gap-2">
                <VInput
                  placeholder="New module title"
                  value={newModuleTitle}
                  onChange={e => setNewModuleTitle(e.target.value)}
                />
                <VButton
                  variant="secondary"
                  onClick={() => {
                    if (!newModuleTitle.trim()) {
                      showToast("warning", "Module Title Required", "Enter a module title.");
                      return;
                    }
                    createModuleMutation.mutate({
                      workshopId: formWorkshopId,
                      title: newModuleTitle.trim(),
                    });
                  }}
                  isLoading={createModuleMutation.isPending}
                >
                  Create Module
                </VButton>
              </div>
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <VInput label="Total Marks" type="number" value={formTotal} onChange={e => setFormTotal(e.target.value)} />
            <VInput label="Passing Marks" type="number" value={formPassing} onChange={e => setFormPassing(e.target.value)} />
          </div>
          <div className="flex justify-end gap-3"><VButton variant="ghost" onClick={() => setEditModal(false)}>Cancel</VButton><VButton onClick={() => {
            if (!selected) return;
            updateAssessmentMutation.mutate({
              id: selected.id,
              payload: { title: formTitle, totalMarks: Number(formTotal), passingMarks: Number(formPassing), moduleId: formModuleId || null },
            });
          }} disabled={updateAssessmentMutation.isPending}>Save</VButton></div>
        </div>
      </VModal>

      {/* Question Builder Modal */}
      <VModal isOpen={questionModal} onClose={() => setQuestionModal(false)} title={`Questions |  ${selected?.title || ""}`} className="max-w-2xl">
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {displayQuestions.map((q, i) => (
            <VCard key={i} className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-foreground">{i + 1}. {q.text}</p>
                  <VBadge variant="outline">{q.type}</VBadge>
                  <span className="text-xs text-muted-foreground">{q.marks} marks</span>
                </div>
                <VButton variant="secondary" size="sm" onClick={() => openQuestionEditor(i)}>
                  <Pencil className="h-3.5 w-3.5" /> Edit
                </VButton>
              </div>
              {q.type !== "Integer" && (
                <div className="grid grid-cols-2 gap-2">
                  {q.options.map((opt, oi) => (
                    <span key={oi} className={`text-xs px-3 py-1.5 rounded-lg ${q.correct.includes(oi) ? "bg-success/10 text-success font-medium" : "bg-muted text-muted-foreground"}`}>
                      {String.fromCharCode(65 + oi)}. {opt}
                    </span>
                  ))}
                </div>
              )}
              {q.type === "Integer" && <p className="text-xs text-muted-foreground">Answer: Numerical input</p>}
            </VCard>
          ))}
        </div>
        <div className="border-t border-border pt-4 mt-4">
          <p className="text-sm font-semibold text-foreground mb-3">Add Question</p>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <VSelect label="Question Type" value={qType} onChange={e => {
              const nextType = e.target.value as QuestionType;
              setQType(nextType);
              setQCorrect(nextType === "MCQ" ? [0] : []);
            }} options={[
              { value: "MCQ", label: "MCQ (Single Choice)" },
              { value: "MSQ", label: "MSQ (Multiple Select)" },
              { value: "Integer", label: "Integer Input" },
            ]} />
            <VInput label="Marks" type="number" value={qMarks} onChange={e => setQMarks(e.target.value)} />
          </div>
          <VInput label="Question" value={qText} onChange={e => setQText(e.target.value)} placeholder="Enter question text" className="mb-3" />
          {qType !== "Integer" && (
            <div className="grid grid-cols-2 gap-2 mb-3">
              {qOptions.map((opt, i) => (
                <VInput key={i} placeholder={`Option ${String.fromCharCode(65 + i)}`} value={opt} onChange={e => { const n = [...qOptions]; n[i] = e.target.value; setQOptions(n); }} />
              ))}
            </div>
          )}
          {qType !== "Integer" && (
            qType === "MCQ" ? (
              <VSelect label="Correct Answer" value={String(qCorrect[0] ?? 0)} onChange={e => setQCorrect([Number(e.target.value)])} options={qOptions.map((_, i) => ({ value: String(i), label: `Option ${String.fromCharCode(65 + i)}` }))} />
            ) : (
              <div className="space-y-2">
                <p className="text-sm font-medium text-foreground">Correct Answers</p>
                <div className="grid grid-cols-2 gap-2">
                  {qOptions.map((_, i) => {
                    const isSelected = qCorrect.includes(i);
                    return (
                      <button
                        key={i}
                        type="button"
                        onClick={() => {
                          setQCorrect((prev) =>
                            prev.includes(i)
                              ? prev.filter((idx) => idx !== i)
                              : [...prev, i].sort((a, b) => a - b)
                          );
                        }}
                        className={`rounded-lg border px-3 py-2 text-sm text-left ${isSelected ? "border-primary bg-primary/5 text-primary" : "border-border text-foreground hover:bg-accent"}`}
                      >
                        Option {String.fromCharCode(65 + i)}
                      </button>
                    );
                  })}
                </div>
              </div>
            )
          )}
          <VButton className="w-full mt-3" variant="secondary" onClick={() => {
            if (!qText) { showToast("warning", "Enter question text"); return; }
            if (qType === "Integer") { showToast("warning", "Unsupported", "Backend currently supports MCQ/MSQ question types only."); return; }
            if (qOptions.some(o => !o)) { showToast("warning", "Fill all options"); return; }
            if (qType === "MCQ" && qCorrect.length !== 1) { showToast("warning", "Select one correct option for MCQ."); return; }
            if (qType === "MSQ" && qCorrect.length === 0) { showToast("warning", "Select at least one correct option for MSQ."); return; }
            if (!selected?.id) return;
            addQuestionMutation.mutate({
              assessmentId: selected.id,
              question: { text: qText, type: qType, options: [...qOptions], correct: qCorrect, marks: Number(qMarks) || 10 },
            });
            setQText(""); setQOptions(["", "", "", ""]); setQCorrect(qType === "MCQ" ? [0] : []); setQMarks("10");
          }} disabled={addQuestionMutation.isPending}>
            <Plus className="h-4 w-4" /> Add Question
          </VButton>
        </div>
      </VModal>

      <VModal isOpen={editQuestionModal} onClose={() => setEditQuestionModal(false)} title="Edit Question" className="max-w-2xl">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <VSelect
              label="Question Type"
              value={editingQuestionType}
              onChange={e => {
                const nextType = e.target.value as QuestionType;
                setEditingQuestionType(nextType);
                setEditingQuestionCorrect(nextType === "MCQ" ? [0] : []);
              }}
              options={[
                { value: "MCQ", label: "MCQ (Single Choice)" },
                { value: "MSQ", label: "MSQ (Multiple Select)" },
              ]}
            />
            <VInput label="Marks" type="number" value={editingQuestionMarks} onChange={e => setEditingQuestionMarks(e.target.value)} />
          </div>
          <VInput label="Question" value={editingQuestionText} onChange={e => setEditingQuestionText(e.target.value)} />
          <div className="grid grid-cols-2 gap-2">
            {editingQuestionOptions.map((opt, i) => (
              <VInput
                key={i}
                placeholder={`Option ${String.fromCharCode(65 + i)}`}
                value={opt}
                onChange={e => {
                  const next = [...editingQuestionOptions];
                  next[i] = e.target.value;
                  setEditingQuestionOptions(next);
                }}
              />
            ))}
          </div>
          {editingQuestionType === "MCQ" ? (
            <VSelect
              label="Correct Answer"
              value={String(editingQuestionCorrect[0] ?? 0)}
              onChange={e => setEditingQuestionCorrect([Number(e.target.value)])}
              options={editingQuestionOptions.map((_, i) => ({ value: String(i), label: `Option ${String.fromCharCode(65 + i)}` }))}
            />
          ) : (
            <div className="space-y-2">
              <p className="text-sm font-medium text-foreground">Correct Answers</p>
              <div className="grid grid-cols-2 gap-2">
                {editingQuestionOptions.map((_, i) => {
                  const isSelected = editingQuestionCorrect.includes(i);
                  return (
                    <button
                      key={i}
                      type="button"
                      onClick={() => {
                        setEditingQuestionCorrect((prev) =>
                          prev.includes(i)
                            ? prev.filter((idx) => idx !== i)
                            : [...prev, i].sort((a, b) => a - b)
                        );
                      }}
                      className={`rounded-lg border px-3 py-2 text-sm text-left ${isSelected ? "border-primary bg-primary/5 text-primary" : "border-border text-foreground hover:bg-accent"}`}
                    >
                      Option {String.fromCharCode(65 + i)}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setEditQuestionModal(false)}>Cancel</VButton>
            <VButton
              onClick={() => {
                if (!editingQuestionId) return;
                if (!editingQuestionText) {
                  showToast("warning", "Enter question text");
                  return;
                }
                if (editingQuestionType !== "Integer" && editingQuestionOptions.some((option) => !option)) {
                  showToast("warning", "Fill all options");
                  return;
                }
                updateQuestionMutation.mutate({
                  questionId: editingQuestionId,
                  question: {
                    text: editingQuestionText,
                    type: editingQuestionType,
                    options: editingQuestionOptions,
                    correct: editingQuestionCorrect,
                    marks: Number(editingQuestionMarks) || 1,
                  },
                });
              }}
              isLoading={updateQuestionMutation.isPending}
            >
              Save
            </VButton>
          </div>
        </div>
      </VModal>

      {/* Leaderboard Modal */}
      <VModal isOpen={leaderboardModal} onClose={() => setLeaderboardModal(false)} title="Assessment Leaderboard" className="max-w-lg">
        <div className="space-y-2">
          {!selected?.id && <p className="text-xs text-muted-foreground px-1">Choose an assessment to load leaderboard data.</p>}
          {leaderboardEntries.map((entry, index) => (
            <div key={entry.rank} className="flex items-center gap-4 rounded-xl px-4 py-3 hover:bg-accent transition-all cursor-pointer" onClick={() => {
              setLeaderboardModal(false);
              openStudentPerf(index);
            }}>
              <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${entry.rank <= 3 ? "bg-warning/10 text-warning" : "bg-muted text-muted-foreground"}`}>
                {entry.rank <= 3 ? <Trophy className="h-4 w-4" /> : entry.rank}
              </span>
              <div className="flex-1"><p className="text-sm font-medium text-foreground">{entry.student_name}</p></div>
              <span className="text-sm font-bold text-foreground">{Math.round(entry.average_percentage)}%</span>
              <span className="text-xs text-muted-foreground">{entry.attempts} attempts</span>
            </div>
          ))}
          {leaderboardEntries.length === 0 && (
            <p className="text-sm text-muted-foreground px-1">{leaderboardQuery.isLoading ? "Loading leaderboard..." : "No leaderboard entries yet."}</p>
          )}
        </div>
      </VModal>

      {/* Student Performance Modal */}
      <VModal isOpen={studentPerfModal} onClose={() => { setStudentPerfModal(false); setSelectedStudentIndex(null); }} title="Student Performance" className="max-w-2xl">
        {selectedStudent ? (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground font-bold">
                {selectedStudent.student_name.split(" ").map(n => n[0]).join("").slice(0, 2)}
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground">{selectedStudent.student_name}</h3>
                <p className="text-sm text-muted-foreground">Rank #{selectedStudent.rank}</p>
              </div>
            </div>

            {/* Basic / Detailed tabs */}
            <div className="flex gap-1 border-b border-border">
              {(["basic", "detailed"] as const).map(t => (
                <button key={t} onClick={() => setPerfTab(t)} className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors capitalize ${perfTab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
                  {t} Stats
                </button>
              ))}
            </div>

            {perfTab === "basic" && (
              <div className="grid grid-cols-2 gap-3">
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Score</p><p className="text-2xl font-bold text-foreground">{Math.round(selectedStudent.average_percentage)}%</p></VCard>
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Rank</p><p className="text-2xl font-bold text-foreground">#{selectedStudent.rank}</p></VCard>
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Attempts</p><p className="text-2xl font-bold text-success">{selectedStudent.attempts}</p></VCard>
                <VCard className="p-4 text-center"><p className="text-xs text-muted-foreground">Passed</p><p className="text-2xl font-bold text-destructive">{selectedStudent.passed}</p></VCard>
                <VCard className="p-4 text-center col-span-2"><p className="text-xs text-muted-foreground">Accuracy</p><p className="text-2xl font-bold text-foreground">{Math.round(selectedStudent.average_percentage)}%</p></VCard>
              </div>
            )}

            {perfTab === "detailed" && (
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {studentDrilldownQuery.isLoading && <p className="text-sm text-muted-foreground">Loading detailed review...</p>}
                {!studentDrilldownQuery.isLoading && studentDrilldownQuery.data?.attempts?.length === 0 && (
                  <p className="text-sm text-muted-foreground">No graded attempts available for this student.</p>
                )}
                {studentDrilldownQuery.data?.attempts?.map((attempt) => (
                  <VCard key={attempt.submission_id} className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-semibold text-foreground">{Math.round(attempt.percentage)}% ({attempt.score})</p>
                      <VBadge variant={attempt.pass_fail ? "success" : "destructive"}>{attempt.pass_fail ? "Pass" : "Fail"}</VBadge>
                    </div>
                    <div className="space-y-2">
                      {attempt.questions.map((question, idx) => (
                        <div key={question.question_id} className={`rounded-lg px-3 py-2 ${question.is_correct ? "bg-success/5" : "bg-destructive/5"}`}>
                          <p className="text-sm text-foreground">{idx + 1}. {question.question_text}</p>
                          <p className="text-xs text-muted-foreground">Selected: {question.selected_option_texts.join(", ") || "Not answered"}</p>
                          <p className="text-xs text-muted-foreground">Correct: {question.correct_option_texts.join(", ") || "—"}</p>
                          <p className={`text-xs ${question.is_correct ? "text-success" : "text-destructive"}`}>Marks: {question.earned_marks}/{question.max_marks}</p>
                        </div>
                      ))}
                    </div>
                  </VCard>
                ))}
              </div>
            )}

            <VButton variant="secondary" className="w-full" onClick={() => { setSelectedStudentIndex(null); setStudentPerfModal(false); setLeaderboardModal(true); }}>
              ← Back to Leaderboard
            </VButton>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground mb-3">Select a student to view detailed performance:</p>
            {leaderboardEntries.map((s, index) => (
              <button key={s.rank} onClick={() => openStudentPerf(index)} className="flex w-full items-center gap-3 rounded-xl px-4 py-3 hover:bg-accent transition-all text-left">
                <div className="h-9 w-9 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground text-xs font-bold">{s.student_name.split(" ").map(n => n[0]).join("").slice(0, 2)}</div>
                <div className="flex-1"><p className="text-sm font-medium text-foreground">{s.student_name}</p></div>
                <span className="text-sm font-bold text-foreground">{Math.round(s.average_percentage)}%</span>
              </button>
            ))}
          </div>
        )}
      </VModal>

      <VConfirmDialog isOpen={deleteDialog} onClose={() => setDeleteDialog(false)} onConfirm={() => {
        if (!selected) return;
        deleteAssessmentMutation.mutate(selected.id);
      }} title="Delete Assessment" message={`Delete "${selected?.title}"?`} />
    </DashboardLayout>
  );
};

export default AssessmentsPage;


