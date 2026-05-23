import { useMemo, useState } from "react";
import { DollarSign, Search, CheckCircle2, Pencil } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import { useAuth } from "@/hooks/useAuth";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchAllUsers, fetchInstitutions, fetchSalaryPayments, paySalary, updateEducatorSalary } from "@/services/api";

interface SalaryRecord {
  id: string;
  name: string;
  institution: string;
  salary: number | null;
  salaryType: string;
  monthlyStatus: "Paid" | "Unpaid";
  type: string;
}

const currentMonthKey = () => new Date().toISOString().slice(0, 7); // YYYY-MM

const SalaryManagement = () => {
  const role = useRole();
  const { user } = useAuth();
  const isAdmin = role === "admin";
  const isInstitutionAdmin = role === "institution_admin";

  const { showToast } = useVToast();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const usersQuery = useQuery({
    queryKey: ["adminUsers"],
    queryFn: () => fetchAllUsers({ max: 500 }),
    enabled: isAdmin || isInstitutionAdmin,
  });

  const institutionsQuery = useQuery({
    queryKey: ["institutions"],
    queryFn: fetchInstitutions,
    enabled: isAdmin || isInstitutionAdmin,
  });

  const month = currentMonthKey();

  const salaryPaymentsQuery = useQuery({
    queryKey: ["salaryPayments", month],
    queryFn: () => fetchSalaryPayments({ month, limit: 500 }),
    enabled: isAdmin,
  });

  const institutionLookup = useMemo(() => {
    const items = institutionsQuery.data ?? [];
    return Object.fromEntries(items.map((i) => [i.id, i.name])) as Record<string, string>;
  }, [institutionsQuery.data]);

  const paidLookup = useMemo(() => {
    const items = salaryPaymentsQuery.data?.items ?? [];
    return Object.fromEntries(items.map((p) => [p.educator_id, p])) as Record<string, { amount: number }>;
  }, [salaryPaymentsQuery.data?.items]);

  const records: SalaryRecord[] = useMemo(() => {
    const users = usersQuery.data ?? [];
    const educators = users.filter((u) => u.role === "educator");
    const scoped = isInstitutionAdmin ? educators.filter((u) => u.institution_id === user?.institution_id) : educators;

    return scoped.map((u) => {
      const paidRecord = paidLookup[u.id];
      const paid = !!paidRecord;
      const salary = paidRecord?.amount ?? (u.salary_amount ?? 0);
      return {
        id: u.id,
        name: u.name || u.email,
        institution: u.institution_id ? institutionLookup[u.institution_id] ?? u.institution_id : "",
        salary: salary > 0 ? salary : null,
        salaryType: u.salary_type || "monthly",
        monthlyStatus: paid ? "Paid" : "Unpaid",
        type: u.salary_type || "monthly",
      };
    });
  }, [institutionLookup, isInstitutionAdmin, paidLookup, user?.institution_id, usersQuery.data]);

  const filtered = records.filter((r) => {
    const matchSearch = r.name.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "All" || r.monthlyStatus === statusFilter;
    return matchSearch && matchStatus;
  });

  const totalSalary = records.reduce((s, r) => s + (r.salary ?? 0), 0);
  const paidCount = records.filter((r) => r.monthlyStatus === "Paid").length;
  const unpaidCount = records.filter((r) => r.monthlyStatus === "Unpaid").length;
  const payableUnpaidCount = records.filter((r) => r.monthlyStatus === "Unpaid" && r.salary !== null).length;

  const payMutation = useMutation({
    mutationFn: async (payload: { educatorId: string; amount: number }) => {
      return paySalary({ educatorId: payload.educatorId, month, amount: payload.amount });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["salaryPayments", month] });
      showToast("success", "Salary Paid", "Payment processed successfully.");
    },
    onError: (err: unknown) => {
      showToast("destructive", "Payment Failed", err instanceof Error ? err.message : "Unable to process payment.");
    },
  });

  const payAllMutation = useMutation({
    mutationFn: async () => {
      const unpaidWithKnownAmount = records.filter((r) => r.monthlyStatus === "Unpaid" && r.salary !== null);
      for (const r of unpaidWithKnownAmount) {
        await paySalary({ educatorId: r.id, month, amount: r.salary as number });
      }
      return unpaidWithKnownAmount.length;
    },
    onSuccess: (count) => {
      queryClient.invalidateQueries({ queryKey: ["salaryPayments", month] });
      showToast("success", "All Salaries Paid", `${count} payments processed.`);
    },
    onError: (err: unknown) => {
      showToast("destructive", "Bulk Payment Failed", err instanceof Error ? err.message : "Unable to process bulk payment.");
    },
  });

  const [editingSalary, setEditingSalary] = useState<SalaryRecord | null>(null);
  const [salaryAmount, setSalaryAmount] = useState("");
  const [salaryType, setSalaryType] = useState("monthly");

  const updateSalaryMutation = useMutation({
    mutationFn: async (payload: { educatorId: string; salaryAmount: number; salaryType: string }) => {
      return updateEducatorSalary(payload.educatorId, { salary_amount: payload.salaryAmount, salary_type: payload.salaryType });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] });
      showToast("success", "Salary Updated", "Educator salary has been updated.");
      setEditingSalary(null);
    },
    onError: (err: unknown) => {
      showToast("destructive", "Update Failed", err instanceof Error ? err.message : "Unable to update salary.");
    },
  });

  const handleEditSalary = (record: SalaryRecord) => {
    setEditingSalary(record);
    setSalaryAmount(record.salary?.toString() || "0");
    setSalaryType(record.salaryType || "monthly");
  };

  const handleSaveSalary = () => {
    if (!editingSalary) return;
    updateSalaryMutation.mutate({
      educatorId: editingSalary.id,
      salaryAmount: parseInt(salaryAmount) || 0,
      salaryType,
    });
  };

  const columns = [
    { key: "name", header: "Educator" },
    { key: "institution", header: "Institution" },
    { key: "type", header: "Type", render: (r: SalaryRecord) => <VBadge variant="outline">{r.type}</VBadge> },
    { key: "salary", header: "Salary", render: (r: SalaryRecord) => r.salary === null ? <span className="text-muted-foreground">Not set</span> : <span className="font-bold text-foreground">INR {r.salary.toLocaleString()}</span> },
    { key: "monthlyStatus", header: "Status", render: (r: SalaryRecord) => <VBadge variant={r.monthlyStatus === "Paid" ? "success" : "warning"}>{r.monthlyStatus}</VBadge> },
    { key: "actions", header: "Actions", render: (r: SalaryRecord) => (
      <div className="flex gap-1">
        <VButton variant="ghost" size="sm" onClick={() => handleEditSalary(r)} disabled={!isAdmin} title="Edit Salary">
          <Pencil className="h-3.5 w-3.5" />
        </VButton>
        {r.monthlyStatus === "Unpaid" && r.salary !== null && (
          <VButton size="sm" onClick={() => payMutation.mutate({ educatorId: r.id, amount: r.salary as number })} disabled={!isAdmin} isLoading={payMutation.isPending}>
            <DollarSign className="h-3.5 w-3.5" /> Pay
          </VButton>
        )}
        {r.monthlyStatus === "Paid" && (
          <span className="text-xs text-success flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5" /></span>
        )}
      </div>
    )},
  ];

  const emptyText =
    usersQuery.isLoading || institutionsQuery.isLoading || (isAdmin && salaryPaymentsQuery.isLoading)
      ? "Loading salary records..."
      : (usersQuery.isError || institutionsQuery.isError || salaryPaymentsQuery.isError)
        ? "Unable to load salary records."
        : "No salary records found.";

  return (
    <DashboardLayout title="Salary Management">
      {!isAdmin && (
        <div className="mb-4 text-sm text-muted-foreground">
          This page is read-only for non-admin roles.
        </div>
      )}

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-4 mb-6">
        <VCard hover className="p-5"><p className="text-sm text-muted-foreground">Total Payroll</p><p className="text-2xl font-bold text-foreground">INR {totalSalary.toLocaleString()}</p></VCard>
        <VCard hover className="p-5"><p className="text-sm text-muted-foreground">Educators</p><p className="text-2xl font-bold text-foreground">{records.length}</p></VCard>
        <VCard hover className="p-5"><p className="text-sm text-muted-foreground">Paid</p><p className="text-2xl font-bold text-success">{paidCount}</p></VCard>
        <VCard hover className="p-5"><p className="text-sm text-muted-foreground">Unpaid</p><p className="text-2xl font-bold text-warning">{unpaidCount}</p></VCard>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input type="text" placeholder="Search..." value={search} onChange={e => setSearch(e.target.value)} className="vidya-input pl-10" />
        </div>
        <div className="flex gap-2">
          {["All", "Paid", "Unpaid"].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)} className={`px-3 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${statusFilter === s ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-accent"}`}>
              {s}
            </button>
          ))}
          {payableUnpaidCount > 0 && (
            <VButton size="sm" onClick={() => payAllMutation.mutate()} disabled={!isAdmin} isLoading={payAllMutation.isPending}>
              Pay All Unpaid
            </VButton>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <VTable columns={columns} data={filtered} emptyText={emptyText} />
      </div>

      {editingSalary && (
        <VModal isOpen={true} onClose={() => setEditingSalary(null)} title="Edit Educator Salary">
          <div className="space-y-4">
            <div className="p-4 bg-muted/30 rounded-lg">
              <p className="font-medium">{editingSalary.name}</p>
              <p className="text-sm text-muted-foreground">{editingSalary.institution}</p>
            </div>
            <VInput
              label="Salary Amount (INR)"
              type="number"
              value={salaryAmount}
              onChange={(e) => setSalaryAmount(e.target.value)}
              placeholder="Enter salary amount"
            />
            <VSelect
              label="Salary Type"
              value={salaryType}
              onChange={(e) => setSalaryType(e.target.value)}
              options={[
                { value: "monthly", label: "Monthly" },
                { value: "per_session", label: "Per Session" },
                { value: "per_hour", label: "Per Hour" },
              ]}
            />
            <div className="flex justify-end gap-3 pt-2">
              <VButton variant="ghost" onClick={() => setEditingSalary(null)}>
                Cancel
              </VButton>
              <VButton onClick={handleSaveSalary} isLoading={updateSalaryMutation.isPending}>
                Save Changes
              </VButton>
            </div>
          </div>
        </VModal>
      )}
    </DashboardLayout>
  );
};

export default SalaryManagement;
