import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { BookOpen, ClipboardList, Award, TrendingUp, Play, CheckCircle2, Clock, Star, Search, FileText, Users, Download, Eye, Link2, ExternalLink, PlayCircle, StickyNote } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import { useVToast } from "@/components/ui-custom/VToast";
import { useAuth } from "@/hooks/useAuth";
import {
  enrollInWorkshop,
  fetchCertificates,
  fetchEnrollments,
  fetchMaterialDownload,
  fetchStudentAnalytics,
  fetchStudentLearningCourses,
  fetchStudentStats,
  fetchStudentProgress,
  fetchWorkshopModules,
  fetchWorkshops,
  resolveBackendMediaUrl,
  updateStudentProgress,
  type StudentLearningCourse,
  type StudentLearningModule,
} from "@/services/api";
import type { Workshop, Certificate } from "@/mock/mockData";

const iconColors = [
  "bg-primary/10 text-primary",
  "bg-info/10 text-info",
  "bg-warning/10 text-warning",
  "bg-success/10 text-success",
];

const trends = ["+2", "+5", "+4.2%", "+1"];

const statCards = [
  { key: "enrolledWorkshops", label: "Enrolled Workshops", icon: BookOpen },
  { key: "completedAssessments", label: "Assessments Done", icon: ClipboardList },
  { key: "averageScore", label: "Average Score", icon: TrendingUp },
  { key: "certificatesEarned", label: "Certificates", icon: Award },
] as const;

type MyCourse = {
  id: string;
  workshopId: string;
  name: string;
  progress: number;
  status: "In Progress" | "Completed";
  modules: number;
  completed: number;
};

const StudentDashboard = () => {
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const { user } = useAuth();

  const { data: stats } = useQuery({
    queryKey: ["studentStats", user?.id],
    queryFn: () => fetchStudentStats(user?.id ?? ""),
    enabled: Boolean(user),
  });

  const { data: studentAnalytics } = useQuery({
    queryKey: ["studentAnalytics", user?.id],
    queryFn: () => fetchStudentAnalytics(user?.id ?? ""),
    enabled: Boolean(user),
  });

  const { data: workshops = [] } = useQuery({ queryKey: ["workshops"], queryFn: fetchWorkshops });
  const { data: enrollments, refetch: refetchEnrollments } = useQuery({
    queryKey: ["enrollments", user?.id],
    queryFn: () => fetchEnrollments(user?.id ?? ""),
    enabled: Boolean(user),
  });

  const { data: learningCourses = [] } = useQuery({
    queryKey: ["studentLearningCourses", user?.id],
    queryFn: () => fetchStudentLearningCourses(user?.id ?? ""),
    enabled: Boolean(user),
  });

  const [activeTab, setActiveTab] = useState<"overview" | "browse" | "mycourses" | "learning" | "certificates">("overview");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [enrollModal, setEnrollModal] = useState<Workshop | null>(null);
  const [learningCourse, setLearningCourse] = useState<MyCourse | null>(null);
  const [activeModule, setActiveModule] = useState(0);
  const [activeMaterial, setActiveMaterial] = useState(0);
  const [moduleSavePending, setModuleSavePending] = useState(false);
  const [resolvedMaterialUrl, setResolvedMaterialUrl] = useState("");
  const [materialTextPreview, setMaterialTextPreview] = useState("");
  const [materialLoading, setMaterialLoading] = useState(false);
  const [previewCert, setPreviewCert] = useState<Certificate | null>(null);

  const { data: studentProgress = [] } = useQuery({
    queryKey: ["studentProgress", user?.id],
    queryFn: fetchStudentProgress,
    enabled: Boolean(user?.id),
  });

  const progressByWorkshop = useMemo(
    () => Object.fromEntries(studentProgress.map((item) => [item.workshop_id, item.current_module_index])),
    [studentProgress],
  );

  const progressMutation = useMutation({
    mutationFn: (payload: { workshopId: string; moduleIndex: number }) =>
      updateStudentProgress(payload),
  });

  const { data: certificates = [] } = useQuery({
    queryKey: ["certificates", user?.id],
    queryFn: () => fetchCertificates({ studentId: user?.id ?? "" }),
    enabled: Boolean(user),
  });

  const { data: modalModules = [] } = useQuery({
    queryKey: ["workshopModules", enrollModal?.id],
    queryFn: () => fetchWorkshopModules(enrollModal?.id ?? ""),
    enabled: Boolean(enrollModal?.id),
  });

  const enrolledIds = useMemo(
    () => (enrollments?.items.map((item) => item.workshop_id).filter(Boolean) as string[]) ?? [],
    [enrollments]
  );

  const learningCourseMap = useMemo(
    () => Object.fromEntries(learningCourses.map((course) => [course.workshopId, course])),
    [learningCourses]
  );

  const myCourses = useMemo<MyCourse[]>(() => {
    const map = new Map<string, MyCourse>();

    for (const enrollment of enrollments?.items ?? []) {
      const workshopId = enrollment.workshop_id ?? "";
      if (!workshopId) continue;

      const workshop = workshops.find((w) => w.id === workshopId);
      if (!workshop) continue;

      const courseData = learningCourseMap[workshopId];
      const moduleCount = Math.max(1, courseData?.modules.length ?? 1);
      const statusRaw = (enrollment.status ?? "").toLowerCase();
      const isCompleted = statusRaw === "completed";
      const currentIndex = Math.max(0, Math.min(progressByWorkshop[workshopId] ?? 0, Math.max(0, moduleCount - 1)));
      const progress = moduleCount > 0 ? Math.round((currentIndex / moduleCount) * 100) : 0;
      const completedModules = Math.min(moduleCount, currentIndex);

      map.set(workshopId, {
        id: workshopId,
        workshopId,
        name: workshop.name,
        progress: isCompleted ? 100 : progress,
        status: isCompleted ? "Completed" : "In Progress",
        modules: moduleCount,
        completed: isCompleted ? moduleCount : completedModules,
      });
    }

    return Array.from(map.values()).sort((a, b) => {
      if (a.status !== b.status) return a.status === "In Progress" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
  }, [enrollments, workshops, learningCourseMap, progressByWorkshop]);

  const categories = useMemo(() => {
    const institutions = Array.from(new Set(workshops.map((w) => w.institution).filter(Boolean)));
    return ["All", ...institutions];
  }, [workshops]);

  const filteredWorkshops = useMemo(() => {
    return workshops.filter((workshop) => {
      const matchSearch = workshop.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchCategory = selectedCategory === "All" || workshop.institution === selectedCategory;
      return matchSearch && matchCategory;
    });
  }, [workshops, searchQuery, selectedCategory]);

  const selectedLearningData = learningCourse ? learningCourseMap[learningCourse.workshopId] : null;
  const modules: StudentLearningModule[] = selectedLearningData?.modules ?? [];

  const progressData = useMemo(() => {
    return (studentAnalytics?.trend ?? []).map((point) => ({ week: point.label, score: point.score }));
  }, [studentAnalytics]);

  const isProgressEmpty = progressData.length === 0;

  useEffect(() => {
    if (!learningCourse?.workshopId) {
      setActiveModule(0);
      return;
    }
    const saved = progressByWorkshop[learningCourse.workshopId] ?? 0;
    setActiveModule(saved);
  }, [learningCourse?.workshopId]);

  const handleEnroll = async (workshop: Workshop) => {
    if (!user) {
      showToast("warning", "Sign in Required", "Please sign in to enroll.");
      return;
    }
    setEnrollModal(null);
    try {
      await enrollInWorkshop(user.id, workshop.id);
      await Promise.all([refetchEnrollments()]);
      showToast("success", "Enrolled!", `You have been enrolled in "${workshop.name}".`);
    } catch (err: unknown) {
      showToast("error", "Enrollment Failed", err instanceof Error ? err.message : "Unable to enroll right now.");
    }
  };

  const currentModule = modules[activeModule];
  const currentMaterial = currentModule?.materials?.[activeMaterial] ?? null;

  const isAbsoluteUrl = (value: string) =>
    value.startsWith("http://") || value.startsWith("https://");

  const toYouTubeEmbedUrl = (url: string): string | null => {
    try {
      const parsed = new URL(url);
      if (parsed.hostname.includes("youtube.com")) {
        const id = parsed.searchParams.get("v");
        return id ? `https://www.youtube.com/embed/${id}` : null;
      }
      if (parsed.hostname.includes("youtu.be")) {
        const id = parsed.pathname.replace("/", "").trim();
        return id ? `https://www.youtube.com/embed/${id}` : null;
      }
      return null;
    } catch {
      return null;
    }
  };

  useEffect(() => {
    setActiveMaterial(0);
  }, [currentModule?.id]);

  useEffect(() => {
    let cancelled = false;
    const resolveMaterial = async () => {
      setResolvedMaterialUrl("");
      setMaterialTextPreview("");

      if (!currentModule || !currentMaterial) return;

      const fallbackUrl = currentMaterial.content
        ? (isAbsoluteUrl(currentMaterial.content)
          ? currentMaterial.content
          : resolveBackendMediaUrl(currentMaterial.content))
        : "";

      setMaterialLoading(true);
      try {
        const response = await fetchMaterialDownload(currentModule.id, currentMaterial.id);
        const resolved = response.download_url
          ? (isAbsoluteUrl(response.download_url)
            ? response.download_url
            : resolveBackendMediaUrl(response.download_url))
          : fallbackUrl;
        if (!cancelled) setResolvedMaterialUrl(resolved);
      } catch {
        if (!cancelled) setResolvedMaterialUrl(fallbackUrl);
      } finally {
        if (!cancelled) setMaterialLoading(false);
      }

      if (currentMaterial.type === "text") {
        const textLikeContent = currentMaterial.content || "";
        if (!textLikeContent || textLikeContent.includes("/") || isAbsoluteUrl(textLikeContent)) {
          const candidateUrl = fallbackUrl;
          if (candidateUrl) {
            try {
              const textResponse = await fetch(candidateUrl);
              const textValue = await textResponse.text();
              if (!cancelled) setMaterialTextPreview(textValue);
              return;
            } catch {
              // Fallback to raw text content below.
            }
          }
        }
        if (!cancelled) setMaterialTextPreview(textLikeContent);
      }
    };

    void resolveMaterial();
    return () => {
      cancelled = true;
    };
  }, [currentModule?.id, currentMaterial?.id]);

  const openCurrentMaterial = () => {
    if (!currentMaterial) {
      showToast("warning", "No material", "No material available for this module yet.");
      return;
    }
    const targetUrl = resolvedMaterialUrl || (currentMaterial.content
      ? (isAbsoluteUrl(currentMaterial.content)
        ? currentMaterial.content
        : resolveBackendMediaUrl(currentMaterial.content))
      : "");
    if (!targetUrl) {
      showToast("warning", "Unavailable", "Material URL is unavailable.");
      return;
    }
    window.open(targetUrl, "_blank", "noopener,noreferrer");
  };

  return (
    <DashboardLayout title="Student Dashboard">
      <div className="flex gap-1 mb-6 border-b border-border overflow-x-auto">
        {[
          { key: "overview", label: "Overview" },
          { key: "browse", label: "Browse Courses" },
          { key: "mycourses", label: "My Courses" },
          { key: "learning", label: "Continue Learning" },
          { key: "certificates", label: "Certificates" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as "overview" | "browse" | "mycourses" | "learning" | "certificates")}
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
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 mb-8">
            {statCards.map(({ key, label, icon: Icon }, i) => (
              <VCard key={key} hover className="p-5 cursor-pointer" onClick={() => setActiveTab(key === "enrolledWorkshops" ? "mycourses" : "overview")}>
                <div className="flex items-center justify-between mb-4">
                  <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${iconColors[i]}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold bg-success/10 text-success">
                    <TrendingUp className="h-3 w-3" />
                    {trends[i]}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{label}</p>
                <p className="text-3xl font-bold text-foreground mt-1">{stats ? (key === "averageScore" ? `${stats[key]}%` : stats[key]) : "--"}</p>
              </VCard>
            ))}
          </div>

          <div className="grid gap-5 lg:grid-cols-2 mb-8">
            <VCard className="p-0">
              <div className="px-5 pt-5 pb-2">
                <h3 className="text-base font-semibold text-foreground">My Progress</h3>
                <p className="text-sm text-muted-foreground">
                  {isProgressEmpty ? "No progress data available yet" : "Score trend from student analytics"}
                </p>
              </div>
              <div className="h-48 px-2">
                {isProgressEmpty ? (
                  <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                    No assessment attempts yet.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={progressData}>
                      <defs>
                        <linearGradient id="studentGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.2} />
                          <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="week" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} domain={[0, 100]} />
                      <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))", color: "hsl(var(--foreground))" }} />
                      <Area type="monotone" dataKey="score" stroke="hsl(var(--primary))" fill="url(#studentGrad)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </VCard>

            <VCard className="p-5">
              <h3 className="text-base font-semibold text-foreground mb-4">Active Courses</h3>
              <div className="space-y-3">
                {myCourses.filter((course) => course.status === "In Progress").map((course) => (
                  <button
                    key={course.id}
                    onClick={() => { setLearningCourse(course); setActiveTab("learning"); }}
                    className="flex w-full items-center gap-4 rounded-xl p-3 hover:bg-accent transition-all text-left group"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary shrink-0">
                      <BookOpen className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{course.name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex-1 h-1.5 rounded-full bg-secondary">
                          <div className="h-1.5 rounded-full bg-primary transition-all" style={{ width: `${course.progress}%` }} />
                        </div>
                        <span className="text-xs text-muted-foreground">{course.progress}%</span>
                      </div>
                    </div>
                    <Play className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
              <VButton variant="secondary" className="w-full mt-4" onClick={() => setActiveTab("browse")}>Browse More Courses</VButton>
            </VCard>
          </div>
        </>
      )}

      {activeTab === "browse" && (
        <>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="vidya-input pl-10"
              />
            </div>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                    selectedCategory === category
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground hover:bg-accent"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filteredWorkshops.map((workshop) => {
              const isEnrolled = enrolledIds.includes(workshop.id);
              return (
                <VCard key={workshop.id} hover className="p-5 flex flex-col">
                  <div className="flex items-center justify-between mb-3">
                    <VBadge variant={workshop.status === "Active" ? "success" : workshop.status === "Upcoming" ? "warning" : "outline"}>{workshop.status}</VBadge>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Star className="h-3.5 w-3.5 fill-warning text-warning" /> 4.8
                    </div>
                  </div>
                  <h3 className="text-base font-bold text-foreground mb-1">{workshop.name}</h3>
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2 flex-1">{workshop.description}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                    <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> {Math.max(1, Math.ceil((Date.parse(workshop.endDate) - Date.parse(workshop.startDate)) / (1000 * 60 * 60 * 24 * 7) || 4))} weeks</span>
                    <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" /> {workshop.studentsEnrolled} enrolled</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-3">{workshop.institution}</p>
                  {isEnrolled ? (
                    <VButton variant="secondary" className="w-full" onClick={() => { setActiveTab("mycourses"); }}>
                      <CheckCircle2 className="h-4 w-4" /> Enrolled
                    </VButton>
                  ) : (
                    <VButton className="w-full" onClick={() => setEnrollModal(workshop)}>Enroll Now</VButton>
                  )}
                </VCard>
              );
            })}
          </div>
        </>
      )}

      {activeTab === "mycourses" &&
        (myCourses.length === 0 ? (
          <VCard className="p-8 text-center">
            <h3 className="text-lg font-semibold text-foreground mb-2">No courses yet</h3>
            <p className="text-sm text-muted-foreground mb-5">Enroll in a workshop to see it here.</p>
            <VButton onClick={() => setActiveTab("browse")}>Browse Courses</VButton>
          </VCard>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {myCourses.map((course) => (
              <VCard key={course.id} hover className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <VBadge variant={course.status === "Completed" ? "success" : "default"}>{course.status}</VBadge>
                  <span className="text-sm font-bold text-primary">{course.progress}%</span>
                </div>
                <h3 className="text-base font-bold text-foreground mb-2">{course.name}</h3>
                <p className="text-sm text-muted-foreground mb-3">{course.completed}/{course.modules} modules completed</p>
                <div className="h-2 rounded-full bg-secondary mb-4">
                  <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${course.progress}%` }} />
                </div>
                <VButton
                  variant={course.status === "Completed" ? "secondary" : "primary"}
                  className="w-full"
                  onClick={() => {
                    if (course.status === "Completed") {
                      navigate("/certificates");
                    } else {
                      setLearningCourse(course);
                      setActiveTab("learning");
                    }
                  }}
                >
                  {course.status === "Completed" ? <><CheckCircle2 className="h-4 w-4" /> View Certificate</> : <><Play className="h-4 w-4" /> Continue Learning</>}
                </VButton>
              </VCard>
            ))}
          </div>
        ))}

      {activeTab === "learning" && (
        <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
          <VCard className="p-3 h-fit">
            <h3 className="text-sm font-semibold text-foreground px-3 py-2 mb-1">{learningCourse?.name || "Select a course"}</h3>
            <div className="space-y-0.5">
              {modules.map((module, idx) => (
                <button
                  key={module.id}
                  onClick={() => setActiveModule(idx)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all ${
                    activeModule === idx
                      ? "bg-primary text-primary-foreground font-medium"
                      : idx < (learningCourse?.completed || 0)
                      ? "text-foreground hover:bg-accent"
                      : "text-muted-foreground hover:bg-accent"
                  }`}
                >
                  <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs ${
                    activeModule === idx
                      ? "bg-primary-foreground/20"
                      : idx < (learningCourse?.completed || 0)
                      ? "bg-success/10 text-success"
                      : "bg-muted text-muted-foreground"
                  }`}>
                    {idx < (learningCourse?.completed || 0) ? <CheckCircle2 className="h-3.5 w-3.5" /> : idx + 1}
                  </span>
                  <span className="flex-1 text-left truncate">{module.title}</span>
                  <span className={`text-xs ${activeModule === idx ? "text-primary-foreground/70" : "text-muted-foreground"}`}>
                    {module.materials.length > 0 ? `${module.materials.length} items` : "No items"}
                  </span>
                </button>
              ))}
            </div>
          </VCard>

          <VCard className="p-6">
            {currentModule ? (
              <>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Module {activeModule + 1} of {modules.length}</p>
                    <h2 className="text-xl font-bold text-foreground">{currentModule.title}</h2>
                  </div>
                  <VBadge variant={activeModule < (learningCourse?.completed || 0) ? "success" : "default"}>
                    {activeModule < (learningCourse?.completed || 0) ? "Completed" : "In Progress"}
                  </VBadge>
                </div>

                <div className="prose prose-sm max-w-none">
                  <p className="text-foreground leading-relaxed">{selectedLearningData?.workshopDescription || "Continue with the selected module materials below."}</p>
                </div>

                <div className="mt-6 grid gap-4 lg:grid-cols-[260px_1fr]">
                  <div className="rounded-xl border border-border bg-muted/20 p-3">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Materials</p>
                    <div className="space-y-1">
                      {currentModule.materials.map((material, idx) => (
                        <button
                          key={material.id}
                          onClick={() => setActiveMaterial(idx)}
                          className={`flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm transition-colors ${
                            activeMaterial === idx ? "bg-primary text-primary-foreground" : "hover:bg-accent text-foreground"
                          }`}>
                          {material.type === "video" && <PlayCircle className="h-4 w-4" />}
                          {material.type === "pdf" && <FileText className="h-4 w-4" />}
                          {material.type === "link" && <Link2 className="h-4 w-4" />}
                          {material.type === "text" && <StickyNote className="h-4 w-4" />}
                          <span className="truncate">{material.title}</span>
                        </button>
                      ))}
                      {currentModule.materials.length === 0 && (
                        <p className="px-2 py-3 text-xs text-muted-foreground">No materials in this module yet.</p>
                      )}
                    </div>
                  </div>

                  <div className="rounded-xl border border-border bg-muted/50 p-4">
                    {!currentMaterial ? (
                      <p className="text-sm text-muted-foreground">Select a material to preview.</p>
                    ) : (
                      <>
                        <div className="mb-3 flex items-center justify-between gap-2">
                          <p className="text-sm font-semibold text-foreground truncate">{currentMaterial.title}</p>
                          <VBadge variant="outline">{String(currentMaterial.type || "").toUpperCase()}</VBadge>
                        </div>

                        {currentMaterial.type === "video" && (
                          <>
                            {resolvedMaterialUrl && toYouTubeEmbedUrl(resolvedMaterialUrl) ? (
                              <iframe
                                title={currentMaterial.title}
                                className="h-[320px] w-full rounded-lg border border-border"
                                src={toYouTubeEmbedUrl(resolvedMaterialUrl) || ""}
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                              />
                            ) : (
                              <video className="w-full rounded-lg" controls src={resolvedMaterialUrl}>
                                Your browser does not support video playback.
                              </video>
                            )}
                          </>
                        )}

                        {currentMaterial.type === "pdf" && (
                          <iframe
                            title={currentMaterial.title}
                            className="h-[420px] w-full rounded-lg border border-border"
                            src={resolvedMaterialUrl}
                          />
                        )}

                        {currentMaterial.type === "link" && (
                          <div className="rounded-lg border border-border bg-background p-4 text-center">
                            <p className="mb-3 text-sm text-muted-foreground break-all">{resolvedMaterialUrl || currentMaterial.content}</p>
                            <VButton variant="secondary" onClick={openCurrentMaterial}>
                              <ExternalLink className="h-4 w-4" /> Open Link
                            </VButton>
                          </div>
                        )}

                        {currentMaterial.type === "text" && (
                          <div className="min-h-[220px] whitespace-pre-wrap rounded-lg border border-border bg-background p-4 text-sm text-foreground">
                            {materialLoading ? "Loading..." : (materialTextPreview || currentMaterial.content || "No text content available.")}
                          </div>
                        )}

                        <div className="mt-3">
                          <VButton variant="secondary" onClick={openCurrentMaterial}>
                            <Download className="h-4 w-4" /> Open Material
                          </VButton>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex justify-between mt-6 pt-6 border-t border-border">
                  <VButton variant="secondary" disabled={activeModule === 0} onClick={() => setActiveModule(Math.max(0, activeModule - 1))}>Previous Module</VButton>
                  {activeModule < modules.length - 1 ? (
                    <VButton
                      disabled={moduleSavePending}
                      onClick={async () => {
                        if (!learningCourse) return;
                        const nextIndex = Math.min(modules.length - 1, activeModule + 1);
                        setModuleSavePending(true);
                        try {
                          await progressMutation.mutateAsync({ workshopId: learningCourse.workshopId, moduleIndex: nextIndex });
                          setActiveModule(nextIndex);
                          showToast("success", "Module Complete!");
                        } catch (error: unknown) {
                          showToast("error", "Progress update failed", error instanceof Error ? error.message : "Please try again.");
                        } finally {
                          setModuleSavePending(false);
                        }
                      }}
                    >
                      {moduleSavePending ? "Saving..." : "Next Module"}
                    </VButton>
                  ) : (
                    <VButton onClick={() => { navigate("/assessments"); showToast("success", "Course Complete!", "Time to take the assessment."); }}>Take Assessment</VButton>
                  )}
                </div>
              </>
            ) : (
              <div className="py-16 text-center">
                <p className="text-sm text-muted-foreground mb-4">Select an enrolled course to continue learning.</p>
                <VButton onClick={() => setActiveTab("mycourses")}>Go to My Courses</VButton>
              </div>
            )}
          </VCard>
        </div>
      )}

      {activeTab === "certificates" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-foreground">My Certificates</h2>
            <span className="text-sm text-muted-foreground">{certificates.length} certificate(s) earned</span>
          </div>

          {certificates.length === 0 ? (
            <VCard className="p-12 text-center">
              <Award className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
              <h3 className="text-lg font-semibold text-foreground mb-2">No Certificates Yet</h3>
              <p className="text-muted-foreground mb-4">Complete courses and pass assessments to earn certificates.</p>
              <VButton onClick={() => setActiveTab("mycourses")}>Go to My Courses</VButton>
            </VCard>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {certificates.map((cert) => (
                <VCard key={cert.id} className="p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-success/10">
                      <Award className="w-8 h-8 text-success" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-foreground truncate">{cert.workshop}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Issued: {cert.completionDate || "N/A"}
                      </p>
                      <div className="flex gap-2 mt-3">
                        <VButton
                          variant="secondary"
                          className="text-sm"
                          onClick={() => setPreviewCert(cert)}
                        >
                          <FileText className="w-4 h-4" />
                          View
                        </VButton>
                        {cert.downloadUrl && (
                          <a
                            href={resolveBackendMediaUrl(cert.downloadUrl)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 text-sm"
                          >
                            <VButton variant="primary" className="text-sm">
                              <Download className="w-4 h-4" />
                              Download
                            </VButton>
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </VCard>
              ))}
            </div>
          )}
        </div>
      )}

      <VModal isOpen={!!enrollModal} onClose={() => setEnrollModal(null)} title="Enroll in Workshop">
        {enrollModal && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-foreground">{enrollModal.name}</h3>
            <p className="text-sm text-muted-foreground">{enrollModal.description}</p>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Institution</p><p className="font-medium text-foreground">{enrollModal.institution}</p></div>
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Duration</p><p className="font-medium text-foreground">{enrollModal.startDate} - {enrollModal.endDate}</p></div>
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Students</p><p className="font-medium text-foreground">{enrollModal.studentsEnrolled} enrolled</p></div>
              <div className="rounded-xl bg-muted p-3"><p className="text-xs text-muted-foreground">Status</p><p className="font-medium text-foreground">{enrollModal.status}</p></div>
            </div>
            <div className="bg-primary/5 rounded-xl p-4 border border-primary/20">
              <h4 className="text-sm font-semibold text-foreground mb-2">Syllabus</h4>
              <ul className="space-y-1.5 text-sm text-muted-foreground">
                {(modalModules.length > 0 ? modalModules.slice(0, 4).map((module) => module.title || "Untitled Module") : ["Syllabus will be available after module setup"]).map((label, index) => (
                  <li key={`${label}-${index}`} className="flex items-center gap-2"><CheckCircle2 className="h-3.5 w-3.5 text-primary" /> {label}</li>
                ))}
              </ul>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <VButton variant="ghost" onClick={() => setEnrollModal(null)}>Cancel</VButton>
              <VButton onClick={() => handleEnroll(enrollModal)}>Confirm Enrollment</VButton>
            </div>
          </div>
        )}
      </VModal>

      <VModal isOpen={!!previewCert} onClose={() => setPreviewCert(null)} title="Certificate Preview">
        {previewCert && (
          <div className="space-y-4">
            <div className="rounded-xl bg-muted p-4 border border-border">
              <div className="text-center py-8">
                <Award className="w-16 h-16 mx-auto mb-4 text-primary" />
                <h3 className="text-xl font-bold text-foreground mb-2">Certificate of Completion</h3>
                <p className="text-lg text-foreground mb-1">This is to certify that</p>
                <p className="text-xl font-semibold text-primary mb-2">{user?.name || "Student"}</p>
                <p className="text-muted-foreground mb-4">has successfully completed the course</p>
                <p className="text-lg font-bold text-foreground mb-2">{previewCert.workshop}</p>
                <p className="text-sm text-muted-foreground">
                  Issued on: {previewCert.completionDate || "N/A"}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Certificate ID: {previewCert.certificateId}
                </p>
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <VButton variant="ghost" onClick={() => setPreviewCert(null)}>Close</VButton>
              {previewCert.downloadUrl && (
                <a
                  href={resolveBackendMediaUrl(previewCert.downloadUrl)}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <VButton>
                    <Download className="w-4 h-4" />
                    Download
                  </VButton>
                </a>
              )}
            </div>
          </div>
        )}
      </VModal>
    </DashboardLayout>
  );
};

export default StudentDashboard;
