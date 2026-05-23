import { useMemo, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from "recharts";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import { useVToast } from "@/components/ui-custom/VToast";
import { Download } from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { exportPerformanceReport, fetchAllUsers, fetchStudentAnalytics, fetchWorkshopAnalytics, fetchWorkshops } from "@/services/api";

const PerformanceReports = () => {
  const { showToast } = useVToast();
  const [hoveredStudent, setHoveredStudent] = useState<string | null>(null);
  const exportMutation = useMutation({
    mutationFn: exportPerformanceReport,
    onSuccess: (result) => {
      window.open(result.download_url, "_blank", "noopener,noreferrer");
      showToast("success", "Report Exported", "Performance CSV export started.");
    },
    onError: (error: unknown) => {
      showToast("destructive", "Export Failed", error instanceof Error ? error.message : "Unable to export report.");
    },
  });

  const workshopsQuery = useQuery({
    queryKey: ["workshops"],
    queryFn: fetchWorkshops,
  });

  const studentsQuery = useQuery({
    queryKey: ["students"],
    queryFn: async () => {
      const users = await fetchAllUsers({ max: 500 });
      return users.filter((u) => u.role === "student");
    },
  });

  const workshopIdsKey = useMemo(
    () => (workshopsQuery.data ?? []).map((workshop) => workshop.id).slice(0, 20).sort().join(","),
    [workshopsQuery.data]
  );

  const workshopAnalyticsQuery = useQuery({
    queryKey: ["workshopAnalytics", workshopIdsKey],
    queryFn: async () => {
      const workshops = (workshopsQuery.data ?? []).slice(0, 20);
      return Promise.all(
        workshops.map(async (workshop) => {
          try {
            const data = await fetchWorkshopAnalytics(workshop.id);
            return { workshopId: workshop.id, title: workshop.name, data };
          } catch {
            return { workshopId: workshop.id, title: workshop.name, data: null };
          }
        })
      );
    },
    enabled: (workshopsQuery.data?.length ?? 0) > 0,
  });

  const studentIdsKey = useMemo(
    () => (studentsQuery.data ?? []).map((student) => student.id).slice(0, 10).sort().join(","),
    [studentsQuery.data]
  );

  const studentAnalyticsQuery = useQuery({
    queryKey: ["studentAnalytics", studentIdsKey],
    queryFn: async () => {
      const students = (studentsQuery.data ?? []).slice(0, 10);
      return Promise.all(
        students.map(async (student) => {
          try {
            const data = await fetchStudentAnalytics(student.id);
            return { studentId: student.id, name: student.name || student.email, data };
          } catch {
            return { studentId: student.id, name: student.name || student.email, data: null };
          }
        })
      );
    },
    enabled: (studentsQuery.data?.length ?? 0) > 0,
  });

  const reportData = useMemo(() => {
    const rows = workshopAnalyticsQuery.data ?? [];

    const totals = rows.reduce(
      (acc, row) => {
        const data = row.data;
        if (!data) return acc;

        acc.totalEnrolled += data.totalEnrolled;
        acc.totalCompleted += data.completed;
        acc.totalSubmissions += data.totalSubmissions;
        acc.sumAveragePercentage += data.averagePercentage;
        acc.sumPassRateWeighted += data.passRatePercentage * data.totalSubmissions;
        acc.averageCount += data.totalSubmissions > 0 ? 1 : 0;

        if (data.totalEnrolled > acc.topEnrollment) {
          acc.topEnrollment = data.totalEnrolled;
          acc.topWorkshop = row.title;
        }
        return acc;
      },
      {
        totalEnrolled: 0,
        totalCompleted: 0,
        totalSubmissions: 0,
        sumAveragePercentage: 0,
        sumPassRateWeighted: 0,
        averageCount: 0,
        topEnrollment: 0,
        topWorkshop: "",
      }
    );

    const avgScore = totals.averageCount > 0 ? Math.round(totals.sumAveragePercentage / totals.averageCount) : 0;
    const completion = totals.totalEnrolled > 0 ? Math.round((totals.totalCompleted / totals.totalEnrolled) * 100) : 0;
    const passRate = totals.totalSubmissions > 0 ? Math.round(totals.sumPassRateWeighted / totals.totalSubmissions) : 0;

    return [
      { label: "Average Score", value: `${avgScore}%`, description: "Across available assessments" },
      { label: "Completion Rate", value: `${completion}%`, description: "Workshop completion from live enrollments" },
      { label: "Top Workshop", value: totals.topWorkshop || "—", description: "Highest enrollment from live workshops" },
      { label: "Pass Rate", value: `${passRate}%`, description: "Across live submission records" },
    ];
  }, [workshopAnalyticsQuery.data]);

  const studentPerformance = useMemo(() => {
    const rows = (studentAnalyticsQuery.data ?? [])
      .filter((item) => item.data)
      .map((item) => ({
        name: item.name,
        avgScore: item.data?.averagePercentage ?? 0,
        workshopsCompleted: item.data?.enrolledWorkshops ?? 0,
        passed: item.data?.passed ?? 0,
        failed: item.data?.failed ?? 0,
        trend: item.data?.trend ?? [],
      }));

    rows.sort((a, b) => b.avgScore - a.avgScore);
    return rows.slice(0, 5);
  }, [studentAnalyticsQuery.data]);

  const barData = useMemo(() => {
    const now = new Date();
    const buckets = Array.from({ length: 6 }).map((_, idx) => {
      const date = new Date(now);
      date.setMonth(now.getMonth() - (5 - idx));
      const key = date.toISOString().slice(0, 7);
      return { key, month: date.toLocaleString("en-US", { month: "short" }), scores: [] as number[] };
    });

    const scorePoints = studentPerformance.flatMap((student) => student.trend);
    for (const [index, point] of scorePoints.entries()) {
      let bucket = null as (typeof buckets)[number] | null;
      if (point.label && /^\d{4}-\d{2}/.test(point.label)) {
        const parsed = new Date(point.label);
        const key = Number.isNaN(parsed.getTime()) ? null : parsed.toISOString().slice(0, 7);
        bucket = key ? buckets.find((entry) => entry.key === key) ?? null : null;
      }
      if (!bucket) {
        const fallbackIndex = Math.max(0, buckets.length - scorePoints.length + index);
        bucket = buckets[Math.min(buckets.length - 1, fallbackIndex)];
      }
      bucket.scores.push(point.score);
    }

    if (scorePoints.length === 0) {
      return buckets.map((bucket, idx) => ({ month: bucket.month, score: studentPerformance[idx]?.avgScore ?? 0 }));
    }

    return buckets.map((bucket) => {
      const avg = bucket.scores.length > 0 ? Math.round(bucket.scores.reduce((sum, score) => sum + score, 0) / bucket.scores.length) : 0;
      return { month: bucket.month, score: avg };
    });
  }, [studentPerformance]);

  const pieData = useMemo(() => {
    const passed = studentPerformance.reduce((sum, row) => sum + row.passed, 0);
    const failed = studentPerformance.reduce((sum, row) => sum + row.failed, 0);
    const total = passed + failed;
    const passPct = total > 0 ? Math.round((passed / total) * 100) : 0;
    const failPct = total > 0 ? 100 - passPct : 0;
    return [
      { name: "Passed", value: passPct, color: "hsl(var(--success))" },
      { name: "Failed", value: failPct, color: "hsl(var(--destructive))" },
    ];
  }, [studentPerformance]);

  const isLoading = workshopsQuery.isLoading || studentsQuery.isLoading || workshopAnalyticsQuery.isLoading || studentAnalyticsQuery.isLoading;

  return (
    <DashboardLayout title="Performance Reports">
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-muted-foreground">Comprehensive performance analytics {isLoading ? "(loading...)" : ""}</p>
        <VButton variant="secondary" onClick={() => exportMutation.mutate()} isLoading={exportMutation.isPending}>
          <Download className="h-4 w-4" /> Export CSV
        </VButton>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {reportData.map((item) => (
          <VCard key={item.label} hover className="p-5 cursor-pointer" onClick={() => showToast("info", item.label, item.description)}>
            <p className="text-sm text-muted-foreground">{item.label}</p>
            <p className="text-2xl font-bold text-foreground mt-1">{item.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
          </VCard>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2 mb-8">
        <VCard className="p-0">
          <div className="px-5 pt-5 pb-2">
            <h3 className="text-base font-semibold text-foreground">Monthly Score Trend</h3>
            <p className="text-sm text-muted-foreground">Average across live student submissions</p>
          </div>
          <div className="h-56 px-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} domain={[0, 100]} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                <Bar dataKey="score" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </VCard>

        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-2">Pass/Fail Distribution</h3>
          <p className="text-sm text-muted-foreground mb-4">Across live student submissions</p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={3}>
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-2">
            {pieData.map((entry) => (
              <div key={entry.name} className="flex items-center gap-2 text-sm">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-muted-foreground">{entry.name}: {entry.value}%</span>
              </div>
            ))}
          </div>
        </VCard>
      </div>

      <h2 className="text-lg font-semibold text-foreground mb-4">Student Performance</h2>
      <VCard className="overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="vidya-table-header px-6 py-3 text-left">Student</th>
              <th className="vidya-table-header px-6 py-3 text-left">Avg Score</th>
              <th className="vidya-table-header px-6 py-3 text-left">Workshops</th>
              <th className="vidya-table-header px-6 py-3 text-left">Progress</th>
            </tr>
          </thead>
          <tbody>
            {studentPerformance.map((student) => (
              <tr
                key={student.name}
                onMouseEnter={() => setHoveredStudent(student.name)}
                onMouseLeave={() => setHoveredStudent(null)}
                onClick={() => showToast("info", student.name, `Average score: ${student.avgScore}%, Workshops: ${student.workshopsCompleted}`)}
                className={`border-b border-border last:border-0 cursor-pointer transition-colors ${hoveredStudent === student.name ? "bg-primary/5" : "hover:bg-accent/50"}`}
              >
                <td className="px-6 py-4 text-foreground font-medium">{student.name}</td>
                <td className="px-6 py-4 text-foreground">{student.avgScore}%</td>
                <td className="px-6 py-4 text-foreground">{student.workshopsCompleted}</td>
                <td className="px-6 py-4">
                  <div className="w-32 h-2 rounded-full bg-secondary">
                    <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${student.avgScore}%` }} />
                  </div>
                </td>
              </tr>
            ))}
            {studentPerformance.length === 0 && (
              <tr>
                <td className="px-6 py-6 text-muted-foreground" colSpan={4}>
                  {isLoading ? "Loading..." : "No student analytics found."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </VCard>
    </DashboardLayout>
  );
};

export default PerformanceReports;

