import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Eye, Search, Building2, Plus } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { fetchInstitutions, fetchUsers, fetchWorkshops, createInstitution, updateInstitutionStatus } from "@/services/api";
import type { BackendInstitution, BackendUser } from "@/api/types";

interface InstituteRow {
  id: string;
  name: string;
  code: string;
  location: string;
  workshops: number;
  educators: number;
  students: number;
  status: "Active" | "Inactive";
}

const InstituteManagement = () => {
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<InstituteRow | null>(null);
  const [selectedInstitution, setSelectedInstitution] = useState<BackendInstitution | null>(null);
  const [viewModal, setViewModal] = useState(false);
  const [addModal, setAddModal] = useState(false);
  const [toggleConfirm, setToggleConfirm] = useState(false);
  const [addForm, setAddForm] = useState({ name: "", code: "", address: "", contact_email: "", contact_phone: "" });

  const {
    data: institutions = [],
    isLoading: instLoading,
    isError: instError,
    error: instErr,
    refetch: refetchInst,
  } = useQuery({ queryKey: ["institutions"], queryFn: fetchInstitutions });

  const {
    data: usersPage,
    isLoading: usersLoading,
    isError: usersError,
    error: usersErr,
    refetch: refetchUsers,
  } = useQuery({ queryKey: ["users", "admin"], queryFn: () => fetchUsers({ limit: 500 }) });

  const {
    data: workshops = [],
    isLoading: workshopsLoading,
    isError: workshopsError,
    error: workshopsErr,
    refetch: refetchWorkshops,
  } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });

  const rows = useMemo<InstituteRow[]>(() => {
    const users = (usersPage?.items ?? []) as BackendUser[];

    const educatorCountByInst: Record<string, number> = {};
    const studentCountByInst: Record<string, number> = {};
    for (const u of users) {
      const instId = u.institution_id ?? "";
      if (!instId) continue;
      if (u.role === "educator") educatorCountByInst[instId] = (educatorCountByInst[instId] ?? 0) + 1;
      if (u.role === "student") studentCountByInst[instId] = (studentCountByInst[instId] ?? 0) + 1;
    }

    // Workshops are already adapted to show institution name. Build counts by institution name.
    const workshopsByInstName: Record<string, number> = {};
    for (const w of workshops) {
      const name = w.institution ?? "";
      if (!name) continue;
      workshopsByInstName[name] = (workshopsByInstName[name] ?? 0) + 1;
    }

    return (institutions as BackendInstitution[]).map((i) => ({
      id: i.id,
      name: i.name,
      code: `INST-${i.id.slice(0, 8).toUpperCase()}`,
      location: i.address ?? "—",
      workshops: workshopsByInstName[i.name] ?? 0,
      educators: educatorCountByInst[i.id] ?? 0,
      students: studentCountByInst[i.id] ?? 0,
      status: i.is_active === false ? "Inactive" : "Active",
    }));
  }, [institutions, usersPage, workshops]);

  const updateStatusMutation = useMutation({
    mutationFn: (payload: { institutionId: string; isActive: boolean }) =>
      updateInstitutionStatus(payload.institutionId, payload.isActive),
    onSuccess: async (updatedInstitution) => {
      setSelectedInstitution(updatedInstitution);
      await queryClient.invalidateQueries({ queryKey: ["institutions"] });
      await queryClient.refetchQueries({ queryKey: ["institutions"], type: "active" });
      setToggleConfirm(false);
      showToast(
        "success",
        "Status Updated",
        updatedInstitution.is_active === false
          ? "Institution deactivated successfully."
          : "Institution activated successfully."
      );
    },
    onError: (error: unknown) => {
      showToast(
        "destructive",
        "Update Failed",
        error instanceof Error ? error.message : "Unable to update institution status."
      );
    },
  });

  const filtered = rows.filter((i) =>
    i.name.toLowerCase().includes(search.toLowerCase()) || i.code.toLowerCase().includes(search.toLowerCase())
  );

  const loading = instLoading || usersLoading || workshopsLoading;
  const errorMsg =
    (instError && (instErr instanceof Error ? instErr.message : "Failed to load institutions.")) ||
    (usersError && (usersErr instanceof Error ? usersErr.message : "Failed to load users.")) ||
    (workshopsError && (workshopsErr instanceof Error ? workshopsErr.message : "Failed to load workshops.")) ||
    null;

  const emptyText = loading
    ? "Loading institutes..."
    : errorMsg
    ? errorMsg
    : "No institutes found.";

  const columns = [
    {
      key: "name",
      header: "Institute",
      render: (r: InstituteRow) => (
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Building2 className="h-4 w-4 text-primary" />
          </div>
          <span className="font-medium text-foreground">{r.name}</span>
        </div>
      ),
    },
    { key: "code", header: "Code" },
    { key: "location", header: "Location" },
    { key: "workshops", header: "Workshops" },
    { key: "educators", header: "Educators" },
    { key: "students", header: "Students" },
    {
      key: "status",
      header: "Status",
      render: (r: InstituteRow) => (
        <VBadge variant={r.status === "Active" ? "success" : "destructive"}>{r.status}</VBadge>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (r: InstituteRow) => (
        <button
          onClick={() => {
            setSelected(r);
            const institution = institutions.find((i) => i.id === r.id);
            setSelectedInstitution(institution ?? null);
            setViewModal(true);
          }}
          className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors"
        >
          <Eye className="h-4 w-4" />
        </button>
      ),
    },
  ];

  const totalWorkshops = rows.reduce((s, i) => s + i.workshops, 0);
  const totalStudents = rows.reduce((s, i) => s + i.students, 0);

  return (
    <DashboardLayout title="Institute Management">
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search institutes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="vidya-input pl-10"
          />
        </div>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-3 mb-6">
        <VCard hover className="p-5">
          <p className="text-sm text-muted-foreground">Total Institutes</p>
          <p className="text-2xl font-bold text-foreground">{rows.length}</p>
        </VCard>
        <VCard hover className="p-5">
          <p className="text-sm text-muted-foreground">Total Workshops</p>
          <p className="text-2xl font-bold text-foreground">{totalWorkshops}</p>
        </VCard>
        <VCard hover className="p-5">
          <p className="text-sm text-muted-foreground">Total Students</p>
          <p className="text-2xl font-bold text-foreground">{totalStudents.toLocaleString()}</p>
        </VCard>
      </div>

      {errorMsg && (
        <div className="mb-4">
          <button
            className="text-sm text-primary underline"
            onClick={() => {
              refetchInst();
              refetchUsers();
              refetchWorkshops();
            }}
          >
            Retry
          </button>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <input type="text" placeholder="Search institutions..." value={search} onChange={(e) => setSearch(e.target.value)} className="vidya-input w-64" />
        <VButton onClick={() => setAddModal(true)}><Plus className="h-4 w-4 mr-1" /> Add Institution</VButton>
      </div>

      <div className="overflow-x-auto">
        <VTable columns={columns} data={filtered} emptyText={emptyText} />
      </div>

      <VModal isOpen={viewModal} onClose={() => { setViewModal(false); setSelectedInstitution(null); }} title="Institute Details">
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-primary/10 flex items-center justify-center">
                <Building2 className="h-7 w-7 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-foreground">{selected.name}</h3>
                <p className="text-sm text-muted-foreground">{selected.code}</p>
              </div>
              <div>
                <VBadge variant={selectedInstitution?.is_active !== false ? "success" : "destructive"}>
                  {selectedInstitution?.is_active !== false ? "Active" : "Inactive"}
                </VBadge>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Location</p>
                <p className="text-sm font-medium text-foreground">{selected.location}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Workshops</p>
                <p className="text-lg font-bold text-foreground">{selected.workshops}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Educators</p>
                <p className="text-lg font-bold text-foreground">{selected.educators}</p>
              </div>
              <div className="rounded-xl bg-muted p-3 col-span-2">
                <p className="text-xs text-muted-foreground">Students</p>
                <p className="text-lg font-bold text-foreground">{selected.students}</p>
              </div>
            </div>
            <div className="border-t border-border pt-4 flex justify-end gap-2">
              <VButton
                variant={selectedInstitution?.is_active !== false ? "destructive" : "default"}
                onClick={() => setToggleConfirm(true)}
                isLoading={updateStatusMutation.isPending}
              >
                {selectedInstitution?.is_active !== false ? "Deactivate" : "Activate"}
              </VButton>
            </div>
          </div>
        )}
      </VModal>

      {/* Add Institution Modal */}
      <VModal isOpen={addModal} onClose={() => setAddModal(false)} title="Add Institution">
        <div className="space-y-4">
          <VInput label="Institution Name" value={addForm.name} onChange={e => setAddForm({ ...addForm, name: e.target.value })} placeholder="e.g. IIT Delhi" />
          <VInput label="Code" value={addForm.code} onChange={e => setAddForm({ ...addForm, code: e.target.value })} placeholder="e.g. IITD" />
          <VInput label="Address" value={addForm.address} onChange={e => setAddForm({ ...addForm, address: e.target.value })} placeholder="City, State" />
          <VInput label="Contact Email" value={addForm.contact_email} onChange={e => setAddForm({ ...addForm, contact_email: e.target.value })} placeholder="contact@institution.edu" />
          <VInput label="Contact Phone" value={addForm.contact_phone} onChange={e => setAddForm({ ...addForm, contact_phone: e.target.value })} placeholder="+91 1234567890" />
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setAddModal(false)}>Cancel</VButton>
            <VButton onClick={async () => {
              if (!addForm.name.trim()) {
                showToast("error", "Error", "Institution name is required.");
                return;
              }
              try {
                await createInstitution(addForm);
                queryClient.invalidateQueries({ queryKey: ["institutions"] });
                setAddModal(false);
                setAddForm({ name: "", code: "", address: "", contact_email: "", contact_phone: "" });
                showToast("success", "Success", "Institution created successfully.");
              } catch (err: unknown) {
                showToast("error", "Error", err instanceof Error ? err.message : "Failed to create institution.");
              }
            }}>Create</VButton>
          </div>
        </div>
      </VModal>

      {/* Status Toggle Confirmation */}
      <VConfirmDialog
        isOpen={toggleConfirm}
        title={selectedInstitution?.is_active !== false ? "Deactivate Institution?" : "Activate Institution?"}
        description={
          selectedInstitution?.is_active !== false
            ? "This will deactivate the institution and may affect active workshops and enrollments."
            : "This will activate the institution."
        }
        onConfirm={() => {
          if (selectedInstitution) {
            updateStatusMutation.mutate({
              institutionId: selectedInstitution.id,
              isActive: selectedInstitution.is_active === false,
            });
          }
        }}
        onCancel={() => setToggleConfirm(false)}
      />
    </DashboardLayout>
  );
};

export default InstituteManagement;