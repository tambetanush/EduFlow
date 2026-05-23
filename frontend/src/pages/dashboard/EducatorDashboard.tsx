import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { BookOpen, FileText, ClipboardList, Inbox, Eye, Upload, BarChart3, Sparkles } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VTable from "@/components/ui-custom/VTable";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import { useVToast } from "@/components/ui-custom/VToast";
import { fetchDashboardStats, fetchWorkshops } from "@/services/api";
import type { Workshop } from "@/mock/mockData";

const iconColors = [
  "bg-primary/10 text-primary",
  "bg-info/10 text-info",
  "bg-warning/10 text-warning",
  "bg-destructive/10 text-destructive",
];

const statCards = [
  { key: "assignedWorkshops", label: "Assigned Workshops", icon: BookOpen },
  { key: "materialsUploaded", label: "Materials Uploaded", icon: FileText },
  { key: "activeAssessments", label: "Active Assessments", icon: ClipboardList },
  { key: "pendingSubmissions", label: "Pending Submissions", icon: Inbox },
] as const;

const quickActions = [
  { label: "AI Content Generator", icon: Sparkles, route: "/ai-content-generator" },
  { label: "Upload Material", icon: Upload, route: "/materials" },
  { label: "Create Assessment", icon: ClipboardList, route: "/assessments" },
  { label: "View Submissions", icon: Inbox, route: "/submissions" },
  { label: "Performance Reports", icon: BarChart3, route: "/reports" },
];

const EducatorDashboard = () => {
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const { data: stats } = useQuery({ queryKey: ["dashboardStats"], queryFn: fetchDashboardStats });
  const { data: workshops = [] } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });
  const chartData = useMemo(() => {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const dayBuckets = days.map((day) => ({ day, scheduled: 0, completed: 0 }));
    workshops.forEach((workshop) => {
      const start = Date.parse(workshop.startDate);
      const dayIndex = Number.isNaN(start) ? 0 : (new Date(start).getDay() + 6) % 7;
      dayBuckets[dayIndex].scheduled += 1;
      if (workshop.status === "Completed") dayBuckets[dayIndex].completed += 1;
      if (workshop.status === "Active") dayBuckets[dayIndex].completed += 0.5;
    });
    return dayBuckets.map((bucket) => ({
      day: bucket.day,
      scheduled: Math.round(bucket.scheduled * 20),
      completed: Math.round(bucket.completed * 20),
    }));
  }, [workshops]);

  const workshopColumns = [
    { key: "name", header: "Workshop Name" },
    { key: "startDate", header: "Start Date" },
    { key: "studentsEnrolled", header: "Students" },
    { key: "status", header: "Status", render: (r: Workshop) => (
      <VBadge variant={r.status === "Active" ? "success" : r.status === "Upcoming" ? "warning" : "outline"}>
        {r.status}
      </VBadge>
    )},
    {
      key: "action",
      header: "Action",
      render: (r: Workshop) => (
        <VButton variant="secondary" size="sm" onClick={() => { navigate(`/workshops/${r.id}`); showToast("info", "Opening workshop details"); }}>
          <Eye className="h-3.5 w-3.5" /> View
        </VButton>
      ),
    },
  ];

  return (
    <DashboardLayout title="Educator Dashboard">
      {/* Stat Cards */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 mb-8">
        {statCards.map(({ key, label, icon: Icon }) => (
          <VCard key={key} hover className="p-5 cursor-pointer" onClick={() => showToast("info", label, `Showing details for ${label.toLowerCase()}`)}>
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

      <div className="grid gap-5 lg:grid-cols-3 mb-8">
        {/* Activity Chart */}
        <VCard className="p-0 lg:col-span-2">
          <div className="flex items-center justify-between px-5 pt-5 pb-2">
            <div>
              <h3 className="text-base font-semibold text-foreground">Workshop Activity</h3>
              <p className="text-sm text-muted-foreground">Weekly overview</p>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-primary" /> Scheduled</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-primary/40" /> Completed</span>
            </div>
          </div>
          <div className="h-52 px-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="educGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                <Area type="monotone" dataKey="scheduled" stroke="hsl(var(--primary))" fill="url(#educGrad)" strokeWidth={2} />
                <Area type="monotone" dataKey="completed" stroke="hsl(var(--primary))" fill="none" strokeWidth={2} strokeDasharray="5 5" />
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
                onClick={() => { navigate(qa.route); showToast("info", `Opening ${qa.label}`); }}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-foreground hover:bg-accent transition-all group"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all">
                  <qa.icon className="h-4 w-4" />
                </div>
                <span className="flex-1 text-left">{qa.label}</span>
              </button>
            ))}
          </div>
        </VCard>
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">Recent Workshops</h2>
        <VButton variant="secondary" size="sm" onClick={() => navigate("/workshops")}>View All</VButton>
      </div>
      <div className="overflow-x-auto">
        <VTable columns={workshopColumns} data={workshops.slice(0, 5)} />
      </div>
    </DashboardLayout>
  );
};

export default EducatorDashboard;
