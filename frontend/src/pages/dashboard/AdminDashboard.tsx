import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, BookOpen, Users, GraduationCap, TrendingUp, Plus, Eye, Pencil, Trash2, Zap, ArrowRight } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Bar, BarChart } from "recharts";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VDrawer from "@/components/ui-custom/VDrawer";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { createWorkshop, deleteWorkshop, fetchAdminDashboardInsights, fetchAdminStats, fetchInstitutions, fetchWorkshops, updateWorkshop } from "@/services/api";
import type { Workshop } from "@/mock/mockData";

const iconColors = [
  "bg-primary/10 text-primary",
  "bg-info/10 text-info",
  "bg-warning/10 text-warning",
  "bg-success/10 text-success",
];

const statCards = [
  { key: "totalInstitutions", label: "Institutions", icon: Building2 },
  { key: "totalWorkshops", label: "Total Workshops", icon: BookOpen },
  { key: "totalEducators", label: "Educators", icon: Users },
  { key: "totalStudents", label: "Students", icon: GraduationCap },
] as const;

const AdminDashboard = () => {
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { data: stats } = useQuery({ queryKey: ["adminStats"], queryFn: fetchAdminStats });
  const insightsQuery = useQuery({ queryKey: ["adminDashboardInsights"], queryFn: fetchAdminDashboardInsights });
  const { data: workshops = [] } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });
  const { data: institutions = [] } = useQuery({ queryKey: ["institutions"], queryFn: fetchInstitutions });
  const insights = insightsQuery.data;
  const weeklyActivity = (insights?.weekly_activity ?? []).map((point) => ({ day: point.label, value: point.value }));
  const demographicData = insights?.demographics ?? [];
  const activityFeed = (insights?.activity_feed ?? []).map((item) => ({
    id: item.id,
    text: item.text,
    time: item.time,
    type: item.type,
  }));
  const weeklyTotal = Math.round(weeklyActivity.reduce((sum, item) => sum + item.value, 0));
  const weeklyPeak = Math.round(Math.max(...weeklyActivity.map((item) => item.value), 0));

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedWorkshop, setSelectedWorkshop] = useState<Workshop | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [createModal, setCreateModal] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Workshop | null>(null);
  const [activeStatFilter, setActiveStatFilter] = useState<string | null>(null);
  const [highlightedActivity, setHighlightedActivity] = useState<string | null>(null);

  const [formName, setFormName] = useState("");
  const [formInstitution, setFormInstitution] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formStatus, setFormStatus] = useState("Active");

  const displayWorkshops = searchQuery
    ? workshops.filter(w =>
        w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        w.institution.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : workshops;

  const createMutation = useMutation({
    mutationFn: createWorkshop,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workshops"] });
      setCreateModal(false);
      showToast("success", "Workshop Created", `"${formName}" has been added to the platform.`);
    },
    onError: (error: unknown) => {
      showToast("error", "Create failed", error instanceof Error ? error.message : "Please try again.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { title?: string | null; description?: string | null; start_date?: string | null; end_date?: string | null } }) =>
      updateWorkshop(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workshops"] });
      setEditModal(false);
      showToast("success", "Workshop Updated", `"${formName}" has been updated successfully.`);
    },
    onError: (error: unknown) => {
      showToast("error", "Update failed", error instanceof Error ? error.message : "Please try again.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteWorkshop,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["workshops"] });
      setDeleteDialog(false);
      showToast("success", "Workshop Deleted", `"${deleteTarget?.name ?? "Workshop"}" has been removed.`);
      setDeleteTarget(null);
    },
    onError: (error: unknown) => {
      showToast("error", "Delete failed", error instanceof Error ? error.message : "Please try again.");
    },
  });

  const parseStatusDates = (status: string) => {
    const now = new Date();
    if (status === "Completed") {
      const end = new Date(now);
      end.setDate(now.getDate() - 1);
      const start = new Date(end);
      start.setDate(end.getDate() - 30);
      return { start, end };
    }
    if (status === "Upcoming") {
      const start = new Date(now);
      start.setDate(now.getDate() + 1);
      const end = new Date(start);
      end.setDate(start.getDate() + 30);
      return { start, end };
    }
    const start = new Date(now);
    start.setDate(now.getDate() - 1);
    const end = new Date(now);
    end.setDate(now.getDate() + 30);
    return { start, end };
  };

  const resolveInstitutionId = (name: string) => {
    const trimmed = name.trim().toLowerCase();
    if (!trimmed) return undefined;
    return institutions.find((item) => item.name.toLowerCase() === trimmed)?.id;
  };

  const handleView = (w: Workshop) => {
    setSelectedWorkshop(w);
    setDrawerOpen(true);
  };

  const handleEdit = (w: Workshop) => {
    setSelectedWorkshop(w);
    setFormName(w.name);
    setFormInstitution(w.institution);
    setFormDescription(w.description);
    setFormStatus(w.status);
    setEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!selectedWorkshop) return;

    let startDate = selectedWorkshop.startDate;
    let endDate = selectedWorkshop.endDate;
    if (formStatus !== selectedWorkshop.status) {
      const dates = parseStatusDates(formStatus);
      startDate = dates.start.toISOString();
      endDate = dates.end.toISOString();
    }

    await updateMutation.mutateAsync({
      id: selectedWorkshop.id,
      payload: {
        title: formName,
        description: formDescription,
        start_date: startDate || null,
        end_date: endDate || null,
      },
    });
  };

  const handleDelete = (w: Workshop) => {
    setDeleteTarget(w);
    setDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    await deleteMutation.mutateAsync(deleteTarget.id);
  };

  const handleCreate = () => {
    setFormName(""); setFormInstitution(""); setFormDescription(""); setFormStatus("Upcoming");
    setCreateModal(true);
  };

  const handleSaveCreate = async () => {
    const institutionId = resolveInstitutionId(formInstitution);
    // Abort if an institution name was typed but no matching record was found.
    if (formInstitution.trim() && institutionId === undefined) {
      showToast("error", "Invalid Institution", `No institution found matching "${formInstitution}". Please check the name.`);
      return;
    }
    const dates = parseStatusDates(formStatus);

    await createMutation.mutateAsync({
      title: formName,
      description: formDescription || null,
      institution_id: institutionId,
      start_date: dates.start.toISOString(),
      end_date: dates.end.toISOString(),
    });
  };

  const handleStatClick = (key: string) => {
    setActiveStatFilter(activeStatFilter === key ? null : key);
    showToast("info", "Filter Applied", `Showing data for ${statCards.find(s => s.key === key)?.label}`);
  };

  const columns = [
    { key: "name", header: "Workshop" },
    { key: "institution", header: "Institution" },
    { key: "startDate", header: "Start Date" },
    { key: "status", header: "Status", render: (r: Workshop) => (
      <VBadge variant={r.status === "Active" ? "success" : r.status === "Upcoming" ? "warning" : "outline"}>
        {r.status}
      </VBadge>
    )},
    { key: "studentsEnrolled", header: "Students" },
    { key: "actions", header: "Actions", render: (r: Workshop) => (
      <div className="flex gap-1">
        <button onClick={() => handleView(r)} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors" title="View">
          <Eye className="h-4 w-4" />
        </button>
        <button onClick={() => handleEdit(r)} className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-info transition-colors" title="Edit">
          <Pencil className="h-4 w-4" />
        </button>
        <button onClick={() => handleDelete(r)} className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors" title="Delete">
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    )},
  ];

  const quickActions = [
    { label: "Create Workshop", icon: Plus, action: handleCreate },
    { label: "View Reports", icon: TrendingUp, action: () => { navigate("/reports"); showToast("info", "Navigating to Reports"); } },
    { label: "Manage Students", icon: Users, action: () => { navigate("/manage/students"); } },
    { label: "Issue Certificates", icon: GraduationCap, action: () => { navigate("/certificates"); } },
  ];

  return (
    <DashboardLayout title="Admin Dashboard">
      {/* Stat Cards - clickable */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 mb-8">
        {statCards.map(({ key, label, icon: Icon }) => (
          <VCard
            key={key}
            hover
            className={`p-5 cursor-pointer transition-all ${activeStatFilter === key ? "ring-2 ring-primary shadow-lg" : ""}`}
            onClick={() => handleStatClick(key)}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconColors[statCards.findIndex((item) => item.key === key)]}`}>
                <Icon className="h-5 w-5" />
              </div>
            </div>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="text-3xl font-bold text-foreground mt-1">{stats ? stats[key] : "—"}</p>
          </VCard>
        ))}
      </div>

      {/* Charts + Activity + Quick Actions */}
      <div className="grid gap-5 lg:grid-cols-3 mb-8">
        {/* Area Chart */}
        <VCard className="p-0 lg:col-span-2">
          <div className="flex items-center justify-between px-5 pt-5 pb-2">
            <div>
              <h3 className="text-base font-semibold text-foreground">Platform Activity</h3>
              <p className="text-sm text-muted-foreground">Weekly overview</p>
            </div>
          </div>
          <div className="flex gap-3 px-5 pb-3 flex-wrap">
            <div className="rounded-xl bg-primary/10 px-4 py-2">
              <p className="text-xs text-primary font-semibold">This Week</p>
              <p className="text-lg font-bold text-foreground">{weeklyTotal}</p>
            </div>
            <div className="rounded-xl bg-muted px-4 py-2">
              <p className="text-xs text-muted-foreground">Peak Day</p>
              <p className="text-lg font-bold text-foreground">{weeklyPeak}</p>
            </div>
          </div>
          <div className="h-52 px-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weeklyActivity}>
                <defs>
                  <linearGradient id="adminAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", fontSize: 13, background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                <Area type="monotone" dataKey="value" stroke="hsl(var(--primary))" fill="url(#adminAreaGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </VCard>

        {/* Quick Actions */}
        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-4">Quick Actions</h3>
          <div className="space-y-2">
            {quickActions.map((qa) => (
              <button
                key={qa.label}
                onClick={qa.action}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-foreground hover:bg-accent transition-all group"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all">
                  <qa.icon className="h-4 w-4" />
                </div>
                <span className="flex-1 text-left">{qa.label}</span>
                <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            ))}
          </div>
        </VCard>
      </div>

      {/* Demographics + Activity Feed */}
      <div className="grid gap-5 lg:grid-cols-2 mb-8">
        <VCard className="p-0">
          <div className="px-5 pt-5 pb-4">
            <h3 className="text-base font-semibold text-foreground">Student Demographics</h3>
            <p className="text-sm text-muted-foreground">Institution distribution</p>
          </div>
          <div className="h-52 px-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={demographicData}>
                <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", fontSize: 13, background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                <Bar dataKey="male" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Male" />
                <Bar dataKey="female" fill="hsl(var(--info))" radius={[4, 4, 0, 0]} name="Female" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </VCard>

        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-4">Activity Feed</h3>
          {activityFeed.length === 0 ? (
            <p className="text-sm text-muted-foreground">No recent activity available yet.</p>
          ) : (
            <div className="space-y-1">
              {activityFeed.map((item) => (
                <button
                  key={item.id}
                  onClick={() => { setHighlightedActivity(item.id); showToast("info", item.text); }}
                  className={`flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition-all ${
                    highlightedActivity === item.id ? "bg-primary/10 ring-1 ring-primary/30" : "hover:bg-accent"
                  }`}
                >
                  <div className={`mt-1 h-2 w-2 rounded-full shrink-0 ${
                    item.type === "workshop" ? "bg-primary" :
                    item.type === "certificate" ? "bg-success" :
                    item.type === "enrollment" ? "bg-info" :
                    item.type === "assessment" ? "bg-warning" : "bg-muted-foreground"
                  }`} />
                  <div className="min-w-0">
                    <p className="text-sm text-foreground truncate">{item.text}</p>
                    <p className="text-xs text-muted-foreground">{item.time}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </VCard>
      </div>

      {/* Workshop Table with actions */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">All Workshops</h2>
        <VButton onClick={handleCreate}>
          <Plus className="h-4 w-4" /> Create Workshop
        </VButton>
      </div>
      <div className="overflow-x-auto">
        <VTable columns={columns} data={displayWorkshops} />
      </div>

      {/* View Drawer */}
      <VDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} title={selectedWorkshop?.name || "Workshop Details"}>
        {selectedWorkshop && (
          <div className="space-y-6">
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Description</p>
              <p className="text-sm text-foreground">{selectedWorkshop.description}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Institution</p>
                <p className="text-sm font-medium text-foreground">{selectedWorkshop.institution}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Status</p>
                <VBadge variant={selectedWorkshop.status === "Active" ? "success" : selectedWorkshop.status === "Upcoming" ? "warning" : "outline"}>
                  {selectedWorkshop.status}
                </VBadge>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Start Date</p>
                <p className="text-sm text-foreground">{selectedWorkshop.startDate}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">End Date</p>
                <p className="text-sm text-foreground">{selectedWorkshop.endDate}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Students Enrolled</p>
                <p className="text-2xl font-bold text-foreground">{selectedWorkshop.studentsEnrolled}</p>
              </div>
            </div>
            <div className="flex gap-3 pt-4 border-t border-border">
              <VButton variant="secondary" onClick={() => { setDrawerOpen(false); handleEdit(selectedWorkshop); }}>
                <Pencil className="h-4 w-4" /> Edit
              </VButton>
              <VButton variant="destructive" onClick={() => { setDrawerOpen(false); handleDelete(selectedWorkshop); }}>
                <Trash2 className="h-4 w-4" /> Delete
              </VButton>
            </div>
          </div>
        )}
      </VDrawer>

      {/* Edit Modal */}
      <VModal isOpen={editModal} onClose={() => setEditModal(false)} title="Edit Workshop">
        <div className="space-y-4">
          <VInput id="edit-name" label="Workshop Name" value={formName} onChange={(e) => setFormName(e.target.value)} />
          <VInput id="edit-inst" label="Institution" value={formInstitution} onChange={(e) => setFormInstitution(e.target.value)} />
          <div className="space-y-1.5"><label className="vidya-label">Description</label><textarea value={formDescription} onChange={(e) => setFormDescription(e.target.value)} rows={3} className="vidya-input resize-none" /></div>
          <VSelect id="edit-status" label="Status" value={formStatus} onChange={(e) => setFormStatus(e.target.value)} options={[
            { value: "Active", label: "Active" },
            { value: "Upcoming", label: "Upcoming" },
            { value: "Completed", label: "Completed" },
          ]} />
          <div className="flex justify-end gap-3 pt-2">
            <VButton variant="ghost" onClick={() => setEditModal(false)}>Cancel</VButton>
            <VButton onClick={handleSaveEdit}>Save Changes</VButton>
          </div>
        </div>
      </VModal>

      {/* Create Modal */}
      <VModal isOpen={createModal} onClose={() => setCreateModal(false)} title="Create Workshop">
        <div className="space-y-4">
          <VInput id="create-name" label="Workshop Name" placeholder="e.g. React Fundamentals" value={formName} onChange={(e) => setFormName(e.target.value)} />
          <VSelect 
            id="create-inst" 
            label="Institution" 
            value={formInstitution} 
            onChange={(e) => setFormInstitution(e.target.value)} 
            options={[{ value: "", label: "Select Institution" }, ...institutions.map(i => ({ value: i.name, label: i.name }))]}
          />
          <div className="space-y-1.5"><label className="vidya-label">Description</label><textarea placeholder="Workshop description..." value={formDescription} onChange={(e) => setFormDescription(e.target.value)} rows={3} className="vidya-input resize-none" /></div>
          <VSelect id="create-status" label="Status" value={formStatus} onChange={(e) => setFormStatus(e.target.value)} options={[
            { value: "Upcoming", label: "Upcoming" },
            { value: "Active", label: "Active" },
          ]} />
          <div className="flex justify-end gap-3 pt-2">
            <VButton variant="ghost" onClick={() => setCreateModal(false)}>Cancel</VButton>
            <VButton onClick={handleSaveCreate} disabled={!formName || !formInstitution}>Create Workshop</VButton>
          </div>
        </div>
      </VModal>

      {/* Delete Confirmation */}
      <VConfirmDialog
        isOpen={deleteDialog}
        onClose={() => setDeleteDialog(false)}
        onConfirm={confirmDelete}
        title="Delete Workshop"
        message={`Are you sure you want to delete "${deleteTarget?.name}"? This action cannot be undone.`}
        confirmText="Delete"
      />
    </DashboardLayout>
  );
};

export default AdminDashboard;


