import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Search, Eye, Pencil, Trash2, Plus, Trophy, Send } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import VCard from "@/components/ui-custom/VCard";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VDrawer from "@/components/ui-custom/VDrawer";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import { createApprovalRequest, createWorkshop, deleteWorkshop, fetchInstitutions, fetchWorkshopLeaderboard, fetchWorkshops, updateWorkshop } from "@/services/api";
import type { Workshop } from "@/mock/mockData";
import type { BackendInstitution } from "@/api/types";

const WorkshopsList = () => {
  const navigate = useNavigate();
  const role = useRole();
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const {
    data: workshops = [],
    isLoading,
    isError,
    error,
  } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selected, setSelected] = useState<Workshop | null>(null);
  const [createModal, setCreateModal] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [leaderboardModal, setLeaderboardModal] = useState(false);
  const [formName, setFormName] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [formInst, setFormInst] = useState("");
  const [formStatus, setFormStatus] = useState<Workshop["status"]>("Upcoming");
  const {
    data: institutions = [] as BackendInstitution[],
  } = useQuery({ queryKey: ["institutions"], queryFn: fetchInstitutions });

  const leaderboardQuery = useQuery({
    queryKey: ["workshopLeaderboard", selected?.id],
    queryFn: () => fetchWorkshopLeaderboard(selected?.id ?? ""),
    enabled: Boolean(selected?.id && leaderboardModal),
  });
  const workshopLeaderboard = leaderboardQuery.data?.entries ?? [];

  const isInstitution = role === "institution_admin";

  const all = workshops;

  const tableEmptyText = isLoading
    ? "Loading workshops..."
    : isError
    ? error instanceof Error
      ? error.message
      : "Failed to load workshops."
    : "No workshops found.";
  const filtered = all.filter(w => {
    const matchSearch = w.name.toLowerCase().includes(search.toLowerCase()) || w.institution.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "All" || w.status === statusFilter;
    return matchSearch && matchStatus;
  });
  const canEdit = role === "admin" || role === "institution_admin" || role === "educator";

  const createMutation = useMutation({
    mutationFn: (payload: { title: string; description?: string | null; institution_id?: string | null; start_date?: string | null; end_date?: string | null }) =>
      createWorkshop(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workshops"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: { workshopId: string; title: string; description: string; institution_id?: string | null; start_date?: string | null; end_date?: string | null }) =>
      updateWorkshop(payload.workshopId, {
        title: payload.title,
        description: payload.description,
        institution_id: payload.institution_id,
        start_date: payload.start_date,
        end_date: payload.end_date,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workshops"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (workshopId: string) => deleteWorkshop(workshopId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workshops"] });
    },
  });

  const resolveStatusDates = (status: Workshop["status"]) => {
    const now = new Date();
    if (status === "Completed") {
      const end = new Date(now);
      end.setDate(now.getDate() - 1);
      const start = new Date(end);
      start.setDate(end.getDate() - 14);
      return { start, end };
    }
    if (status === "Upcoming") {
      const start = new Date(now);
      start.setDate(now.getDate() + 7);
      const end = new Date(start);
      end.setDate(start.getDate() + 14);
      return { start, end };
    }
    const start = new Date(now);
    start.setDate(now.getDate() - 7);
    const end = new Date(now);
    end.setDate(now.getDate() + 14);
    return { start, end };
  };

  const handleDelete = async (w: Workshop) => {
    if (isInstitution) {
      try {
        await createApprovalRequest({
          request_type: "delete_workshop",
          payload: { workshop_id: w.id, workshop_title: w.name, institution: w.institution },
        });
        setDeleteDialog(false);
        showToast(
          "info",
          "Removal Request Sent",
          `Request to delete "${w.name}" has been sent to Platform Admin for approval.`
        );
      } catch (err: unknown) {
        showToast(
          "error",
          "Request Failed",
          err instanceof Error ? err.message : "Unable to send request."
        );
      }
      return;
    }

    try {
      await deleteMutation.mutateAsync(w.id);
      setDeleteDialog(false);
      showToast("success", "Workshop Deleted");
    } catch (err: unknown) {
      setDeleteDialog(false);
      showToast(
        "error",
        "Delete Failed",
        err instanceof Error ? err.message : "Unable to delete workshop."
      );
    }
  };
  const columns = [
    { key: "name", header: "Workshop Name" },
    { key: "institution", header: "Institution" },
    { key: "startDate", header: "Start Date" },
    { key: "studentsEnrolled", header: "Students" },
    { key: "status", header: "Status", render: (r: Workshop) => (
      <VBadge variant={r.status === "Active" ? "success" : r.status === "Upcoming" ? "warning" : "outline"}>
        {r.status}
      </VBadge>
    )},
    { key: "actions", header: "Actions", render: (r: Workshop) => (
      <div className="flex gap-1">
        <button onClick={() => { setSelected(r); setDrawerOpen(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors">
          <Eye className="h-4 w-4" />
        </button>
        {canEdit && (
          <>
            <button onClick={() => { setSelected(r); setLeaderboardModal(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-warning transition-colors" title="Leaderboard">
              <Trophy className="h-4 w-4" />
            </button>
            <button onClick={() => { setSelected(r); setFormName(r.name); setFormDesc(r.description); setFormInst(r.institution); setFormStatus(r.status); setEditModal(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-info transition-colors">
              <Pencil className="h-4 w-4" />
            </button>
            <button onClick={() => { setSelected(r); setDeleteDialog(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors">
              {isInstitution ? <Send className="h-4 w-4" /> : <Trash2 className="h-4 w-4" />}
            </button>
          </>
        )}
      </div>
    )},
  ];

  return (
    <DashboardLayout title="Workshops">
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search workshops..." value={search} onChange={(e) => setSearch(e.target.value)} className="vidya-input pl-10" />
        </div>
        <div className="flex gap-2">
          {["All", "Active", "Upcoming", "Completed"].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)} className={`px-3 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${statusFilter === s ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-accent"}`}>
              {s}
            </button>
          ))}
        </div>
        {canEdit && (
          <VButton onClick={() => { setFormName(""); setFormDesc(""); setFormInst(""); setFormStatus("Upcoming"); setCreateModal(true); }}>
            <Plus className="h-4 w-4" /> Create
          </VButton>
        )}
      </div>
      <VTable columns={columns} data={filtered} emptyText={tableEmptyText} />

      <VDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} title={selected?.name || ""}>
        {selected && (
          <div className="space-y-6">
            <div><p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Description</p><p className="text-sm text-foreground">{selected.description}</p></div>
            <div className="grid grid-cols-2 gap-4">
              <div><p className="text-xs text-muted-foreground mb-1">Institution</p><p className="text-sm font-medium text-foreground">{selected.institution}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Status</p><VBadge variant={selected.status === "Active" ? "success" : "outline"}>{selected.status}</VBadge></div>
              <div><p className="text-xs text-muted-foreground mb-1">Duration</p><p className="text-sm text-foreground">{selected.startDate} — {selected.endDate}</p></div>
              <div><p className="text-xs text-muted-foreground mb-1">Enrolled</p><p className="text-2xl font-bold text-foreground">{selected.studentsEnrolled}</p></div>
            </div>
            <VButton className="w-full" onClick={() => { setDrawerOpen(false); navigate(`/workshops/${selected.id}`); }}>View Full Details</VButton>
          </div>
        )}
      </VDrawer>

      {/* Create Modal — textarea for description */}
      <VModal isOpen={createModal} onClose={() => setCreateModal(false)} title="Create Workshop">
        <div className="space-y-4">
          <VInput label="Name" value={formName} onChange={e => setFormName(e.target.value)} placeholder="Workshop name" />
          {role === "admin" || role === "institution_admin" ? (
            <VSelect 
              label="Institution" 
              value={formInst} 
              onChange={e => setFormInst(e.target.value)} 
              options={[{ value: "", label: "Select Institution" }, ...institutions.map(i => ({ value: i.name, label: i.name }))]}
            />
          ) : (
            <VInput label="Institution" value={formInst} onChange={e => setFormInst(e.target.value)} placeholder="Institution" />
          )}
          <div className="space-y-1.5">
            <label className="vidya-label">Description</label>
            <textarea value={formDesc} onChange={e => setFormDesc(e.target.value)} placeholder="Detailed workshop description..." rows={5} className="vidya-input resize-none" />
          </div>
          <div className="flex justify-end gap-3"><VButton variant="ghost" onClick={() => setCreateModal(false)}>Cancel</VButton><VButton onClick={async () => {
            try {
              // Resolve institution name → ID for admin role
              let resolvedInstitutionId: string | null = null;
              if (role === "admin" && formInst.trim()) {
                const trimmed = formInst.trim().toLowerCase();
                const match = institutions.find((i) => i.name.toLowerCase() === trimmed);
                if (!match) {
                  showToast("error", "Invalid Institution", `No institution found matching "${formInst}". Please check the name.`);
                  return;
                }
                resolvedInstitutionId = match.id;
              }
              const dateRange = resolveStatusDates(formStatus);
              await createMutation.mutateAsync({
                title: formName,
                description: formDesc,
                institution_id: resolvedInstitutionId,
                start_date: dateRange.start.toISOString(),
                end_date: dateRange.end.toISOString(),
              });
              setCreateModal(false);
              showToast("success", "Workshop Created");
            } catch (err: unknown) {
              showToast(
                "error",
                "Create Failed",
                err instanceof Error ? err.message : "Unable to create workshop."
              );
            }
          }} disabled={!formName || createMutation.isPending}>Create</VButton></div>
        </div>
      </VModal>

      {/* Edit Modal — textarea for description */}
      <VModal isOpen={editModal} onClose={() => setEditModal(false)} title="Edit Workshop">
        <div className="space-y-4">
          <VInput label="Name" value={formName} onChange={e => setFormName(e.target.value)} />
          {(role === "admin" || role === "institution_admin") && (
            <VSelect 
              label="Institution" 
              value={formInst} 
              onChange={e => setFormInst(e.target.value)} 
              options={[{ value: "", label: "Select Institution" }, ...institutions.map(i => ({ value: i.name, label: i.name }))]}
            />
          )}
          <div className="space-y-1.5">
            <label className="vidya-label">Description</label>
            <textarea value={formDesc} onChange={e => setFormDesc(e.target.value)} rows={5} className="vidya-input resize-none" />
          </div>
          <VSelect
            label="Status"
            value={formStatus}
            onChange={e => setFormStatus(e.target.value as Workshop["status"])}
            options={[
              { value: "Upcoming", label: "Upcoming" },
              { value: "Active", label: "Active" },
              { value: "Completed", label: "Completed" },
            ]}
          />
          <div className="flex justify-end gap-3"><VButton variant="ghost" onClick={() => setEditModal(false)}>Cancel</VButton><VButton onClick={async () => {
            if (!selected) return;
            try {
              const dateRange = resolveStatusDates(formStatus);
              let resolvedInstitutionId: string | null | undefined = undefined;
              if (role === "admin" && formInst.trim()) {
                const trimmed = formInst.trim().toLowerCase();
                const match = institutions.find((i) => i.name.toLowerCase() === trimmed);
                if (!match) {
                  showToast("error", "Invalid Institution", `No institution found matching "${formInst}". Please check the name.`);
                  return;
                }
                resolvedInstitutionId = match.id;
              }
              await updateMutation.mutateAsync({
                workshopId: selected.id,
                title: formName,
                description: formDesc,
                institution_id: role === "admin" ? resolvedInstitutionId : undefined,
                start_date: dateRange.start.toISOString(),
                end_date: dateRange.end.toISOString(),
              });
              setEditModal(false);
              showToast("success", "Workshop Updated");
            } catch (err: unknown) {
              showToast(
                "error",
                "Update Failed",
                err instanceof Error ? err.message : "Unable to update workshop."
              );
            }
          }} disabled={!selected || updateMutation.isPending}>Save</VButton></div>
        </div>
      </VModal>

      {/* Workshop Leaderboard */}
      <VModal isOpen={leaderboardModal} onClose={() => setLeaderboardModal(false)} title={`Leaderboard — ${selected?.name || "Workshop"}`} className="max-w-lg">
        <div className="space-y-2">
          {!selected?.id && <p className="text-xs text-muted-foreground px-1">Choose a workshop to load leaderboard entries.</p>}
          {workshopLeaderboard.map(entry => (
            <div key={entry.rank} className="flex items-center gap-4 rounded-xl px-4 py-3 hover:bg-accent transition-all">
              <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${entry.rank <= 3 ? "bg-warning/10 text-warning" : "bg-muted text-muted-foreground"}`}>
                {entry.rank <= 3 ? <Trophy className="h-4 w-4" /> : entry.rank}
              </span>
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground">{entry.student_name}</p>
                <p className="text-xs text-muted-foreground">{entry.attempts} attempts</p>
              </div>
              <span className="text-sm font-bold text-foreground">{Math.round(entry.average_percentage)}%</span>
            </div>
          ))}
          {!workshopLeaderboard.length && (
            <p className="text-sm text-muted-foreground px-1">
              {leaderboardQuery.isLoading ? "Loading leaderboard..." : "No leaderboard entries yet."}
            </p>
          )}
        </div>
      </VModal>

      <VConfirmDialog isOpen={deleteDialog} onClose={() => setDeleteDialog(false)} onConfirm={() => selected && handleDelete(selected)}
        title={isInstitution ? "Request Deletion" : "Delete Workshop"}
        message={isInstitution ? `This will send a deletion request to the Platform Admin for "${selected?.name}". Continue?` : `Delete "${selected?.name}"? This cannot be undone.`}
        confirmText={isInstitution ? "Send Request" : "Delete"}
      />
    </DashboardLayout>
  );
};

export default WorkshopsList;
