import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { BookOpen, Users, ClipboardList, Award, TrendingUp, TrendingDown, Plus, AlertCircle, Eye, Calendar, CheckSquare, Pencil } from "lucide-react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { useAuth } from "@/hooks/useAuth";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import { useVToast } from "@/components/ui-custom/VToast";
import {
  applyInstitutionStudentBulkAction,
  createWorkshop,
  exportInstitutionAttendanceReport,
  exportInstitutionDashboardReport,
  exportInstitutionStudents,
  fetchInstitutionAttendanceReport,
  fetchInstitutionDashboardAggregate,
  fetchInstitutionStudentRoster,
  fetchWorkshops,
  fetchAllUsers,
  updateEducatorSalary,
  paySalary,
} from "@/services/api";

type WorkshopRow = {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  studentsEnrolled: number;
  status: "Active" | "Upcoming" | "Completed";
};

const iconColors = [
  "bg-primary/10 text-primary",
  "bg-info/10 text-info",
  "bg-warning/10 text-warning",
  "bg-success/10 text-success",
];

const InstitutionDashboard = () => {
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { data: workshops = [] } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });
  const institutionAggregateQuery = useQuery({
    queryKey: ["institutionDashboardAggregate"],
    queryFn: fetchInstitutionDashboardAggregate,
  });
  const [activeTab, setActiveTab] = useState<"overview" | "students" | "attendance" | "reports" | "salaries">("overview");
  const [createModal, setCreateModal] = useState(false);
  const [selectedStudents, setSelectedStudents] = useState<Set<string>>(new Set());
  const [createName, setCreateName] = useState("");
  const [createDescription, setCreateDescription] = useState("");
  const [createStatus, setCreateStatus] = useState("Upcoming");
  const [editingSalary, setEditingSalary] = useState<{ id: string; name: string; salary: number; salaryType: string } | null>(null);
  const [salaryAmount, setSalaryAmount] = useState("");
  const [salaryType, setSalaryType] = useState("monthly");

  const studentRosterQuery = useQuery({
    queryKey: ["institutionStudentRoster"],
    queryFn: fetchInstitutionStudentRoster,
    enabled: activeTab === "students",
  });
  const attendanceReportQuery = useQuery({
    queryKey: ["institutionAttendanceReport"],
    queryFn: fetchInstitutionAttendanceReport,
    enabled: activeTab === "attendance",
  });
  const createWorkshopMutation = useMutation({
    mutationFn: createWorkshop,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["workshops"] }),
        queryClient.invalidateQueries({ queryKey: ["institutionDashboardAggregate"] }),
      ]);
      setCreateName("");
      setCreateDescription("");
      setCreateStatus("Upcoming");
      setCreateModal(false);
      showToast("success", "Workshop Created", "New workshop added successfully");
    },
    onError: (error: unknown) => {
      showToast("error", "Create Failed", error instanceof Error ? error.message : "Unable to create workshop.");
    },
  });
  const bulkStudentActionMutation = useMutation({
    mutationFn: (studentIds: string[]) => applyInstitutionStudentBulkAction({ studentIds, action: "set_inactive" }),
    onSuccess: async (result) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["institutionStudentRoster"] }),
        queryClient.invalidateQueries({ queryKey: ["institutionDashboardAggregate"] }),
      ]);
      setSelectedStudents(new Set());
      showToast("success", "Bulk Action Applied", `${result.updated_enrollments} enrollments updated.`);
    },
    onError: (error: unknown) => {
      showToast("error", "Bulk Action Failed", error instanceof Error ? error.message : "Unable to apply bulk action.");
    },
  });
  const exportStudentsMutation = useMutation({
    mutationFn: (studentIds: string[]) => exportInstitutionStudents(studentIds),
    onSuccess: (result) => {
      window.open(result.download_url, "_blank", "noopener,noreferrer");
      showToast("success", "Export Ready", "Student CSV export started.");
    },
    onError: (error: unknown) => {
      showToast("error", "Export Failed", error instanceof Error ? error.message : "Unable to export students.");
    },
  });
  const exportAttendanceMutation = useMutation({
    mutationFn: exportInstitutionAttendanceReport,
    onSuccess: (result) => {
      window.open(result.download_url, "_blank", "noopener,noreferrer");
      showToast("success", "Attendance Export Ready", "Attendance CSV export started.");
    },
    onError: (error: unknown) => {
      showToast("error", "Export Failed", error instanceof Error ? error.message : "Unable to export attendance report.");
    },
  });
  const exportDashboardReportMutation = useMutation({
    mutationFn: exportInstitutionDashboardReport,
    onSuccess: (result) => {
      window.open(result.download_url, "_blank", "noopener,noreferrer");
      showToast("success", "Report Export Ready", "Dashboard CSV export started.");
    },
    onError: (error: unknown) => {
      showToast("error", "Export Failed", error instanceof Error ? error.message : "Unable to export report.");
    },
  });

  const aggregate = institutionAggregateQuery.data;
  const studentData = studentRosterQuery.data?.items ?? [];
  const attendanceData = attendanceReportQuery.data?.rows ?? [];

  // Educators for salary management
  const usersQuery = useQuery({
    queryKey: ["adminUsers"],
    queryFn: () => fetchAllUsers({ max: 500 }),
    enabled: activeTab === "salaries",
  });
  const educators = useMemo(() => {
    const users = usersQuery.data ?? [];
    const allEducators = users.filter((u) => u.role === "educator");
    // Filter by institution for institution admins
    if (user?.institution_id) {
      return allEducators.filter((u) => u.institution_id === user.institution_id);
    }
    return allEducators;
  }, [usersQuery.data, user?.institution_id]);

  const currentMonth = new Date().toISOString().slice(0, 7);

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
      showToast("error", "Update Failed", err instanceof Error ? err.message : "Unable to update salary.");
    },
  });

  const paySalaryMutation = useMutation({
    mutationFn: async (payload: { educatorId: string; amount: number }) => {
      return paySalary({ educatorId: payload.educatorId, month: currentMonth, amount: payload.amount });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] });
      showToast("success", "Salary Paid", "Payment processed successfully.");
    },
    onError: (err: unknown) => {
      showToast("error", "Payment Failed", err instanceof Error ? err.message : "Unable to process payment.");
    },
  });

  const statsData = [
    { label: "Institution Workshops", value: String(aggregate?.kpis.workshops ?? 0), icon: BookOpen, trend: String(aggregate?.kpis.workshops ?? 0), up: true },
    { label: "Educators", value: String(aggregate?.kpis.educators ?? 0), icon: Users, trend: String(aggregate?.kpis.educators ?? 0), up: true },
    { label: "Active Assessments", value: String(aggregate?.kpis.active_assessments ?? 0), icon: ClipboardList, trend: String(aggregate?.kpis.active_assessments ?? 0), up: true },
    { label: "Students", value: String(aggregate?.kpis.students ?? 0), icon: Award, trend: String(aggregate?.kpis.students ?? 0), up: true },
  ];
  const alerts = (aggregate?.alerts ?? []).map((item) => ({
    id: item.id,
    text: item.text,
    type: ((item.level === "warning" || item.level === "success") ? item.level : "info") as "warning" | "success" | "info",
  }));
  const recentActivity = (aggregate?.activity_feed ?? []).map((item) => ({
    id: item.id,
    text: item.text,
    time: item.time,
  }));
  const enrollmentData = (aggregate?.enrollment_trend ?? []).map((item) => ({
    month: item.label,
    students: Math.round(item.value),
  }));
  const reportCards = aggregate?.report_cards ?? {
    average_score: 0,
    completion_rate: 0,
    top_workshop: "—",
    pass_rate: 0,
  };

  const toggleStudent = (id: string) => {
    setSelectedStudents((previous) => {
      const next = new Set(previous);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    if (selectedStudents.size === studentData.length) setSelectedStudents(new Set());
    else setSelectedStudents(new Set(studentData.map((student) => student.id)));
  };

  const columns = [
    { key: "name", header: "Workshop" },
    { key: "startDate", header: "Start" },
    { key: "endDate", header: "End" },
    { key: "studentsEnrolled", header: "Students" },
    {
      key: "status",
      header: "Status",
      render: (row: WorkshopRow) => (
        <VBadge variant={row.status === "Active" ? "success" : row.status === "Upcoming" ? "warning" : "outline"}>
          {row.status}
        </VBadge>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (row: WorkshopRow) => (
        <VButton variant="secondary" size="sm" onClick={() => { navigate(`/workshops/${row.id}`); }}>
          <Eye className="h-3.5 w-3.5" /> View
        </VButton>
      ),
    },
  ];

  const tabs = [
    { key: "overview", label: "Overview" },
    { key: "students", label: "Students" },
    { key: "attendance", label: "Attendance" },
    { key: "reports", label: "Reports" },
    { key: "salaries", label: "Salaries" },
  ];

  return (
    <DashboardLayout title="Institution Dashboard">
      <div className="flex gap-1 mb-6 border-b border-border overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as "overview" | "students" | "attendance" | "reports" | "salaries")}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
              activeTab === tab.key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && (
        <>
          {institutionAggregateQuery.isLoading && (
            <p className="text-xs text-muted-foreground mb-3">Loading institution aggregate metrics...</p>
          )}
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 mb-8">
            {statsData.map(({ label, value, icon: Icon, trend, up }, index) => (
              <VCard key={label} hover className="p-5 cursor-pointer" onClick={() => showToast("info", label, `Showing ${label.toLowerCase()} details`)}>
                <div className="flex items-center justify-between mb-4">
                  <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconColors[index]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${up ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"}`}>
                    {up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {trend}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{label}</p>
                <p className="text-3xl font-bold text-foreground mt-1">{value}</p>
              </VCard>
            ))}
          </div>

          <div className="grid gap-5 lg:grid-cols-2 mb-8">
            <VCard className="p-5">
              <h3 className="text-base font-semibold text-foreground mb-4">Alerts & Reminders</h3>
              <div className="space-y-2">
                {alerts.map((alert) => (
                  <button
                    key={alert.id}
                    onClick={() => showToast(alert.type as "warning" | "success" | "info", alert.text)}
                    className="flex w-full items-start gap-3 rounded-xl px-3 py-3 text-left hover:bg-accent transition-colors"
                  >
                    <AlertCircle className={`h-5 w-5 mt-0.5 shrink-0 ${
                      alert.type === "warning" ? "text-warning" : alert.type === "success" ? "text-success" : "text-info"
                    }`} />
                    <p className="text-sm text-foreground">{alert.text}</p>
                  </button>
                ))}
              </div>
            </VCard>

            <VCard className="p-5">
              <h3 className="text-base font-semibold text-foreground mb-4">Recent Activity</h3>
              <div className="space-y-1">
                {recentActivity.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => showToast("info", item.text)}
                    className="flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left hover:bg-accent transition-colors"
                  >
                    <div className="mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0" />
                    <div>
                      <p className="text-sm text-foreground">{item.text}</p>
                      <p className="text-xs text-muted-foreground">{item.time}</p>
                    </div>
                  </button>
                ))}
              </div>
            </VCard>
          </div>

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">Institution Workshops</h2>
            <VButton onClick={() => setCreateModal(true)}>
              <Plus className="h-4 w-4" /> Create Workshop
            </VButton>
          </div>
          <div className="overflow-x-auto">
            <VTable columns={columns} data={workshops} />
          </div>
        </>
      )}

      {activeTab === "students" && (
        <>
          {studentRosterQuery.isLoading && (
            <p className="text-xs text-muted-foreground mb-3">Loading students...</p>
          )}
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted-foreground">{selectedStudents.size} selected</p>
            <div className="flex gap-2">
              {selectedStudents.size > 0 && (
                <>
                  <VButton
                    variant="secondary"
                    size="sm"
                    onClick={() => exportStudentsMutation.mutate(Array.from(selectedStudents))}
                    isLoading={exportStudentsMutation.isPending}
                  >
                    Export Selected
                  </VButton>
                  <VButton
                    variant="secondary"
                    size="sm"
                    onClick={() => bulkStudentActionMutation.mutate(Array.from(selectedStudents))}
                    isLoading={bulkStudentActionMutation.isPending}
                  >
                    Bulk Action
                  </VButton>
                </>
              )}
            </div>
          </div>
          <VCard className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-4 py-3 text-left">
                    <input type="checkbox" checked={studentData.length > 0 && selectedStudents.size === studentData.length} onChange={toggleAll} className="rounded border-border" />
                  </th>
                  <th className="vidya-table-header px-4 py-3 text-left">Name</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Email</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Workshop</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Status</th>
                  <th className="vidya-table-header px-4 py-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {studentData.map((student) => (
                  <tr key={student.id} className={`border-b border-border last:border-0 transition-colors ${selectedStudents.has(student.id) ? "bg-primary/5" : "hover:bg-accent/50"}`}>
                    <td className="px-4 py-4">
                      <input type="checkbox" checked={selectedStudents.has(student.id)} onChange={() => toggleStudent(student.id)} className="rounded border-border" />
                    </td>
                    <td className="px-4 py-4 font-medium text-foreground">{student.name}</td>
                    <td className="px-4 py-4 text-muted-foreground">{student.email}</td>
                    <td className="px-4 py-4 text-foreground">{student.workshop}</td>
                    <td className="px-4 py-4">
                      <VBadge variant={student.status === "Active" ? "success" : student.status === "Completed" ? "default" : "warning"}>
                        {student.status}
                      </VBadge>
                    </td>
                    <td className="px-4 py-4">
                      <VButton variant="secondary" size="sm" onClick={() => showToast("info", `Viewing ${student.name}'s profile`)}>
                        <Eye className="h-3.5 w-3.5" /> View
                      </VButton>
                    </td>
                  </tr>
                ))}
                {studentData.length === 0 && !studentRosterQuery.isLoading && (
                  <tr>
                    <td colSpan={6} className="px-4 py-6 text-center text-sm text-muted-foreground">
                      No students found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </VCard>
        </>
      )}

      {activeTab === "attendance" && (
        <VCard className="overflow-hidden">
          {attendanceReportQuery.isLoading && (
            <p className="text-xs text-muted-foreground px-5 pt-4">Loading attendance report...</p>
          )}
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h3 className="text-base font-semibold text-foreground">Weekly Attendance — React Fundamentals</h3>
            <VButton
              variant="secondary"
              size="sm"
              onClick={() => exportAttendanceMutation.mutate()}
              isLoading={exportAttendanceMutation.isPending}
            >
              <Calendar className="h-3.5 w-3.5" /> Export
            </VButton>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="vidya-table-header px-4 py-3 text-left">Student</th>
                {["Mon", "Tue", "Wed", "Thu", "Fri"].map((day) => (
                  <th key={day} className="vidya-table-header px-4 py-3 text-center">{day}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {attendanceData.map((row) => (
                <tr key={row.student} className="border-b border-border last:border-0 hover:bg-accent/50 transition-colors">
                  <td className="px-4 py-4 font-medium text-foreground">{row.student}</td>
                  {["mon", "tue", "wed", "thu", "fri"].map((day) => (
                    <td key={day} className="px-4 py-4 text-center">
                      <span className={`inline-flex h-7 w-7 items-center justify-center rounded-lg text-xs font-bold ${
                        (row as unknown as Record<string, boolean | string>)[day] ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"
                      }`}>
                        {(row as unknown as Record<string, boolean | string>)[day] ? <CheckSquare className="h-4 w-4" /> : "×"}
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
              {attendanceData.length === 0 && !attendanceReportQuery.isLoading && (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-sm text-muted-foreground">
                    No attendance rows available for this week.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </VCard>
      )}

      {activeTab === "reports" && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Enrollment Trends</h3>
            <VButton
              variant="secondary"
              size="sm"
              onClick={() => exportDashboardReportMutation.mutate()}
              isLoading={exportDashboardReportMutation.isPending}
            >
              Export Report
            </VButton>
          </div>
          <VCard className="p-0 mb-8">
            <div className="h-64 px-2 py-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={enrollmentData}>
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                  <Bar dataKey="students" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </VCard>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Average Score", value: `${Math.round(Number(reportCards.average_score ?? 0))}%`, desc: "Across all assessments" },
              { label: "Completion Rate", value: `${Math.round(Number(reportCards.completion_rate ?? 0))}%`, desc: "Workshop completion" },
              { label: "Top Workshop", value: String(reportCards.top_workshop ?? "—"), desc: "Highest enrollment" },
              { label: "Pass Rate", value: `${Math.round(Number(reportCards.pass_rate ?? 0))}%`, desc: "Assessment pass rate" },
            ].map((item) => (
              <VCard key={item.label} hover className="p-5 cursor-pointer" onClick={() => showToast("info", item.label, item.desc)}>
                <p className="text-sm text-muted-foreground">{item.label}</p>
                <p className="text-2xl font-bold text-foreground mt-1">{item.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
              </VCard>
            ))}
          </div>
        </>
      )}

      {activeTab === "salaries" && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Educator Salaries</h3>
          </div>
          
          {usersQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading educators...</p>
          ) : educators.length === 0 ? (
            <p className="text-sm text-muted-foreground">No educators found for this institution.</p>
          ) : (
            <div className="overflow-x-auto">
              <VTable
                columns={[
                  { key: "name", header: "Educator" },
                  { key: "email", header: "Email" },
                  { 
                    key: "salary", 
                    header: "Salary", 
                    render: (row: { id: string; name: string; email: string; salary_amount: number; salary_type: string }) => (
                      <span className="font-medium">₹{row.salary_amount?.toLocaleString() || 0} / {row.salary_type || 'monthly'}</span>
                    )
                  },
                  {
                    key: "actions",
                    header: "Actions",
                    render: (row: { id: string; name: string; email: string; salary_amount: number; salary_type: string }) => (
                      <div className="flex gap-2">
                        <VButton 
                          variant="secondary" 
                          size="sm"
                          onClick={() => {
                            setEditingSalary({ 
                              id: row.id, 
                              name: row.name || row.email, 
                              salary: row.salary_amount || 0, 
                              salaryType: row.salary_type || 'monthly' 
                            });
                            setSalaryAmount(String(row.salary_amount || 0));
                            setSalaryType(row.salary_type || 'monthly');
                          }}
                        >
                          <Pencil className="h-3.5 w-3.5" /> Edit
                        </VButton>
                        <VButton 
                          variant="primary" 
                          size="sm"
                          onClick={() => {
                            paySalaryMutation.mutate({ educatorId: row.id, amount: row.salary_amount || 0 });
                          }}
                          disabled={!row.salary_amount}
                        >
                          Pay Now
                        </VButton>
                      </div>
                    ),
                  },
                ]}
                data={educators.map(e => ({
                  id: e.id,
                  name: e.name || e.email,
                  email: e.email,
                  salary_amount: e.salary_amount || 0,
                  salary_type: e.salary_type || 'monthly',
                }))}
              />
            </div>
          )}
        </>
      )}

      <VModal isOpen={createModal} onClose={() => setCreateModal(false)} title="Create Workshop">
        <div className="space-y-4">
          <VInput id="inst-w-name" label="Workshop Name" placeholder="e.g. React Fundamentals" value={createName} onChange={(event) => setCreateName(event.target.value)} />
          <div className="space-y-1.5"><label className="vidya-label">Description</label><textarea value={createDescription} onChange={(event) => setCreateDescription(event.target.value)} placeholder="Workshop description..." rows={3} className="vidya-input resize-none" /></div>
          <VSelect id="inst-w-status" label="Status" value={createStatus} onChange={(event) => setCreateStatus(event.target.value)} options={[
            { value: "Upcoming", label: "Upcoming" },
            { value: "Active", label: "Active" },
          ]} />
          <div className="flex justify-end gap-3 pt-2">
            <VButton variant="ghost" onClick={() => setCreateModal(false)}>Cancel</VButton>
            <VButton
              onClick={() => {
                if (!createName.trim()) {
                  showToast("warning", "Workshop Name Required", "Enter a workshop name before creating.");
                  return;
                }
                const now = new Date();
                const startDate = createStatus === "Active" ? now : new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
                const endDate = new Date(startDate.getTime() + 30 * 24 * 60 * 60 * 1000);
                createWorkshopMutation.mutate({
                  title: createName.trim(),
                  description: createDescription.trim() || undefined,
                  start_date: startDate.toISOString(),
                  end_date: endDate.toISOString(),
                });
              }}
              disabled={createWorkshopMutation.isPending}
            >
              Create Workshop
            </VButton>
          </div>
        </div>
      </VModal>

      {/* Edit Salary Modal */}
      <VModal isOpen={!!editingSalary} onClose={() => setEditingSalary(null)} title="Edit Educator Salary">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Update salary for <span className="font-semibold text-foreground">{editingSalary?.name}</span>
          </p>
          <VInput
            label="Salary Amount"
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
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setEditingSalary(null)}>
              Cancel
            </VButton>
            <VButton
              onClick={() => {
                if (!editingSalary || !salaryAmount) return;
                updateSalaryMutation.mutate({
                  educatorId: editingSalary.id,
                  salaryAmount: parseInt(salaryAmount, 10),
                  salaryType,
                });
              }}
              isLoading={updateSalaryMutation.isPending}
              disabled={!salaryAmount || updateSalaryMutation.isPending}
            >
              Save Changes
            </VButton>
          </div>
        </div>
      </VModal>
    </DashboardLayout>
  );
};

export default InstitutionDashboard;
