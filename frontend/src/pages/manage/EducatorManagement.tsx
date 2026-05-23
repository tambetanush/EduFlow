import { useMemo, useState } from "react";
import { Eye, Search, DollarSign, Send } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import { useAuth } from "@/hooks/useAuth";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  approveApprovalRequest,
  createApprovalRequest,
  fetchAllUsers,
  fetchInstitutions,
  fetchSalaryPayments,
  paySalary,
} from "@/services/api";

interface EducatorRow {
  id: string;
  name: string;
  email: string;
  institution: string;
  department: string;
  salary: number;
  monthlyStatus: "Paid" | "Unpaid";
  type: "Internal" | "Visiting" | "Unknown";
}

const currentMonthKey = () => new Date().toISOString().slice(0, 7); // YYYY-MM

const normalizeEducatorType = (rawType?: string | null): EducatorRow["type"] => {
  const value = (rawType || "").trim().toLowerCase();
  if (value === "internal") return "Internal";
  if (value === "visiting") return "Visiting";
  return "Unknown";
};

const EducatorManagement = () => {
  const role = useRole();
  const { user } = useAuth();
  const { showToast } = useVToast();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All");
  const [selected, setSelected] = useState<EducatorRow | null>(null);
  const [viewModal, setViewModal] = useState(false);
  const [removalTarget, setRemovalTarget] = useState<EducatorRow | null>(null);
  const [removalConfirm, setRemovalConfirm] = useState(false);

  const isAdmin = role === "admin";
  const isInstitutionAdmin = role === "institution_admin";

  const usersQuery = useQuery({
    queryKey: ["adminUsers"],
    queryFn: () => fetchAllUsers({ max: 500 }),
  });

  const institutionsQuery = useQuery({
    queryKey: ["institutions"],
    queryFn: fetchInstitutions,
  });

  const month = currentMonthKey();

  const salaryPaymentsQuery = useQuery({
    queryKey: ["salaryPayments", month],
    queryFn: () => fetchSalaryPayments({ month, limit: 500 }),
    enabled: isAdmin || isInstitutionAdmin,
  });

  const institutionLookup = useMemo(() => {
    const items = institutionsQuery.data ?? [];
    return Object.fromEntries(items.map((i) => [i.id, i.name])) as Record<string, string>;
  }, [institutionsQuery.data]);

  const paidLookup = useMemo(() => {
    const payments = salaryPaymentsQuery.data?.items ?? [];
    return Object.fromEntries(payments.map((p) => [p.educator_id, p])) as Record<string, { amount: number }>;
  }, [salaryPaymentsQuery.data?.items]);

  const educators: EducatorRow[] = useMemo(() => {
    const users = usersQuery.data ?? [];
    const list = users.filter((u) => u.role === "educator");
    const scoped = isInstitutionAdmin ? list.filter((u) => u.institution_id === user?.institution_id) : list;

    return scoped.map((u) => {
      const institutionName = u.institution_id ? institutionLookup[u.institution_id] ?? u.institution_id : "";
      const type = normalizeEducatorType(u.educator_type);
      const paid = !!paidLookup[u.id];
      // Use the educator's base salary_amount, not the payment amount
      const salary = u.salary_amount ?? 0;
      return {
        id: u.id,
        name: u.name || u.email,
        email: u.email,
        institution: institutionName,
        department: u.department?.trim() || "—",
        salary,
        monthlyStatus: paid ? "Paid" : "Unpaid",
        type,
      };
    });
  }, [institutionLookup, isInstitutionAdmin, paidLookup, user?.institution_id, usersQuery.data]);

  const visibleEducators = educators;

  const filtered = visibleEducators.filter((e) => {
    const matchSearch = e.name.toLowerCase().includes(search.toLowerCase()) || e.email.toLowerCase().includes(search.toLowerCase());
    const matchType = typeFilter === "All" || e.type === typeFilter;
    return matchSearch && matchType;
  });

  const removeMutation = useMutation({
    mutationFn: async (target: EducatorRow) => {
      // All deletes go through approvals to match backend workflow.
      const created = await createApprovalRequest({
        request_type: "delete_educator",
        payload: { user_id: target.id, name: target.name, email: target.email, institution: target.institution },
      });
      if (isAdmin) {
        await approveApprovalRequest(created.id);
      }
      return created;
    },
    onSuccess: (_, target) => {
      showToast(
        isAdmin ? "success" : "info",
        isAdmin ? "Educator Removed" : "Request Sent",
        isAdmin
          ? `"${target.name}" has been removed.`
          : `Removal request for "${target.name}" sent to Platform Admin.`
      );
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] });
      queryClient.invalidateQueries({ queryKey: ["approvalRequests"] });
    },
    onError: (err: unknown) => {
      showToast("error", "Action Failed", err instanceof Error ? err.message : "Unable to process request.");
    },
  });

  const markPaidMutation = useMutation({
    mutationFn: async (payload: { educatorId: string; amount: number }) => {
      return paySalary({ educatorId: payload.educatorId, month, amount: payload.amount });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["salaryPayments", month] });
      showToast("success", "Payment Processed", "Salary marked as paid.");
    },
    onError: (err: unknown) => {
      showToast("error", "Payment Failed", err instanceof Error ? err.message : "Unable to process payment.");
    },
  });

  const handleRemoveAction = (e: EducatorRow) => {
    setRemovalTarget(e);
    setRemovalConfirm(true);
  };

  const columns = [
    { key: "name", header: "Name" },
    { key: "email", header: "Email" },
    ...(!isInstitutionAdmin ? [{ key: "institution", header: "Institution" }] : []),
    { key: "department", header: "Department" },
    { key: "type", header: "Type", render: (r: EducatorRow) => <VBadge variant={r.type === "Internal" ? "default" : "outline"}>{r.type}</VBadge> },
    { key: "salary", header: "Salary", render: (r: EducatorRow) => <span className="font-medium text-foreground">INR {r.salary.toLocaleString()}</span> },
    { key: "monthlyStatus", header: "Status", render: (r: EducatorRow) => (
      <VBadge variant={r.monthlyStatus === "Paid" ? "success" : "warning"}>{r.monthlyStatus}</VBadge>
    )},
    { key: "actions", header: "Actions", render: (r: EducatorRow) => (
      <div className="flex gap-1">
        <button onClick={() => { setSelected(r); setViewModal(true); }} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors">
          <Eye className="h-4 w-4" />
        </button>
        {(isAdmin || isInstitutionAdmin) && (
          <button onClick={() => handleRemoveAction(r)} className={`rounded-lg p-1.5 text-muted-foreground transition-colors ${isInstitutionAdmin ? "hover:bg-warning/10 hover:text-warning" : "hover:bg-destructive/10 hover:text-destructive"}`} title={isInstitutionAdmin ? "Send Removal Request" : "Remove"}>
            <Send className="h-4 w-4" />
          </button>
        )}
      </div>
    )},
  ];

  const emptyText =
    usersQuery.isLoading || institutionsQuery.isLoading || (isAdmin && salaryPaymentsQuery.isLoading)
      ? "Loading educators..."
      : usersQuery.isError
        ? "Unable to load educators."
        : "No educators found.";

  return (
    <DashboardLayout title="Educator Management">
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search educators..." value={search} onChange={e => setSearch(e.target.value)} className="vidya-input pl-10" />
        </div>
        <div className="flex gap-2">
          {["All", "Internal", "Visiting", "Unknown"].map((t) => (
            <button key={t} onClick={() => setTypeFilter(t)} className={`px-3 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${typeFilter === t ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-accent"}`}>
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-3 mb-6">
        <VCard hover className="p-5">
          <p className="text-sm text-muted-foreground">Educators</p>
          <p className="text-2xl font-bold text-foreground">{visibleEducators.length}</p>
        </VCard>
        <VCard hover className="p-5 cursor-pointer" onClick={() => showToast("info", "Paid", `${visibleEducators.filter(e => e.monthlyStatus === "Paid").length} paid`)}>
          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-success" />
            <p className="text-sm text-muted-foreground">Paid This Month</p>
          </div>
          <p className="text-2xl font-bold text-success">{visibleEducators.filter(e => e.monthlyStatus === "Paid").length}</p>
        </VCard>
        <VCard hover className="p-5 cursor-pointer" onClick={() => showToast("warning", "Unpaid", `${visibleEducators.filter(e => e.monthlyStatus === "Unpaid").length} unpaid`)}>
          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-warning" />
            <p className="text-sm text-muted-foreground">Unpaid This Month</p>
          </div>
          <p className="text-2xl font-bold text-warning">{visibleEducators.filter(e => e.monthlyStatus === "Unpaid").length}</p>
        </VCard>
      </div>

      <div className="overflow-x-auto">
        <VTable columns={columns} data={filtered} emptyText={emptyText} />
      </div>

      {/* View Modal */}
      <VModal isOpen={viewModal} onClose={() => setViewModal(false)} title="Educator Details">
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground font-bold text-lg">
                {selected.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground">{selected.name}</h3>
                <p className="text-sm text-muted-foreground">{selected.email}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Institution</p><p className="text-sm font-medium text-foreground">{selected.institution}</p></div>
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Department</p><p className="text-sm font-medium text-foreground">{selected.department}</p></div>
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Type</p><VBadge variant={selected.type === "Internal" ? "default" : "outline"}>{selected.type}</VBadge></div>
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Salary</p><p className="text-sm font-bold text-foreground">INR {selected.salary.toLocaleString()}</p></div>
              <div className="rounded-xl bg-muted p-3 col-span-2"><p className="text-xs text-muted-foreground">Monthly Status</p><VBadge variant={selected.monthlyStatus === "Paid" ? "success" : "warning"}>{selected.monthlyStatus}</VBadge></div>
            </div>
            {selected.monthlyStatus === "Unpaid" && (
              <VButton
                className="w-full"
                isLoading={markPaidMutation.isPending}
                onClick={() => markPaidMutation.mutate({ educatorId: selected.id, amount: selected.salary })}
              >
                <DollarSign className="h-4 w-4" /> Mark as Paid
              </VButton>
            )}
          </div>
        )}
      </VModal>

      {/* Removal Request Modal */}
      <VModal isOpen={removalConfirm} onClose={() => setRemovalConfirm(false)} title={isAdmin ? "Remove Educator" : "Send Removal Request"}>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            {isAdmin
              ? `This will remove "${removalTarget?.name}" from the platform.`
              : `This will send a removal request to the Platform Admin for "${removalTarget?.name}". The educator will NOT be removed immediately.`}
          </p>
          {!isAdmin && (
            <div className="rounded-xl bg-warning/10 p-3">
              <p className="text-xs text-warning font-medium">The Platform Admin must approve this request before the educator is removed.</p>
            </div>
          )}
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setRemovalConfirm(false)}>Cancel</VButton>
            <VButton
              onClick={() => {
                const target = removalTarget;
                setRemovalConfirm(false);
                if (!target) return;
                removeMutation.mutate(target);
              }}
              isLoading={removeMutation.isPending}
              variant="primary"
            >
              <Send className="h-4 w-4" /> {isAdmin ? "Remove" : "Send Request"}
            </VButton>
          </div>
        </div>
      </VModal>
    </DashboardLayout>
  );
};

export default EducatorManagement;
