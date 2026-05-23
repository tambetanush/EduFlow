import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarClock, PauseCircle, PlayCircle, RefreshCw } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VBadge from "@/components/ui-custom/VBadge";
import { useRole } from "@/hooks/useRole";
import { useVToast } from "@/components/ui-custom/VToast";
import {
  createScheduledAIReport,
  fetchInstitutions,
  fetchScheduledAIReportRuns,
  fetchScheduledAIReports,
  updateScheduledAIReport,
} from "@/services/api";

const formatDateTime = (value?: string | null) => {
  if (!value) return "-";
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  return new Date(parsed).toLocaleString();
};

const getStatusVariant = (status?: string) => {
  if (status === "active") return "success" as const;
  if (status === "paused") return "outline" as const;
  return "outline" as const;
};

const ScheduledAIReports = () => {
  const role = useRole();
  const { showToast } = useVToast();
  const queryClient = useQueryClient();

  const isPlatformAdmin = role === "admin";
  const isInstitutionAdmin = role === "institution_admin";

  const [selectedInstitutionId, setSelectedInstitutionId] = useState("");
  const [frequency, setFrequency] = useState<"daily" | "weekly">("daily");
  const [timeOfDay, setTimeOfDay] = useState("09:00");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [weekdaysText, setWeekdaysText] = useState("0"); // Mon=0
  const [windowDays, setWindowDays] = useState("7");
  const [focusAreasText, setFocusAreasText] = useState("");
  const [recipientsText, setRecipientsText] = useState("");
  const [selectedScheduleId, setSelectedScheduleId] = useState<string | null>(null);

  const institutionsQuery = useQuery({
    queryKey: ["institutionsForScheduledReports"],
    queryFn: fetchInstitutions,
    enabled: isPlatformAdmin,
  });

  const schedulesQuery = useQuery({
    queryKey: ["scheduledAIReports"],
    queryFn: () => fetchScheduledAIReports({ limit: 50 }),
    enabled: isPlatformAdmin || isInstitutionAdmin,
    refetchInterval: 10_000,
  });

  const runsQuery = useQuery({
    queryKey: ["scheduledAIReportRuns", selectedScheduleId],
    queryFn: () => fetchScheduledAIReportRuns(selectedScheduleId || "", { limit: 50 }),
    enabled: Boolean(selectedScheduleId),
    refetchInterval: 5_000,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createScheduledAIReport({
        ...(isPlatformAdmin && selectedInstitutionId ? { institution_id: selectedInstitutionId } : {}),
        frequency,
        timezone,
        time_of_day: timeOfDay,
        weekdays: frequency === "weekly"
          ? weekdaysText
              .split(",")
              .map((v) => v.trim())
              .filter(Boolean)
              .map((v) => Number(v))
              .filter((v) => Number.isFinite(v)) as number[]
          : [],
        window_days: Math.max(0, Number(windowDays || 0)),
        focus_areas: focusAreasText
          .split(",")
          .map((v) => v.trim())
          .filter(Boolean),
        recipients: recipientsText
          .split(",")
          .map((v) => v.trim())
          .filter(Boolean),
      }),
    onSuccess: async (data) => {
      await queryClient.invalidateQueries({ queryKey: ["scheduledAIReports"] });
      setSelectedScheduleId(data.id);
      showToast("success", "Schedule Created", `Next run: ${formatDateTime(data.next_run_at)}`);
    },
    onError: (error: unknown) => {
      showToast("destructive", "Create Failed", error instanceof Error ? error.message : "Unable to create schedule.");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: (payload: { scheduleId: string; nextStatus: "active" | "paused" }) =>
      updateScheduledAIReport(payload.scheduleId, { status: payload.nextStatus }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["scheduledAIReports"] });
    },
    onError: (error: unknown) => {
      showToast("destructive", "Update Failed", error instanceof Error ? error.message : "Unable to update schedule.");
    },
  });

  const institutionOptions = useMemo(
    () => [
      { value: "", label: "Platform scope (all institutions)" },
      ...(institutionsQuery.data ?? []).map((inst) => ({ value: inst.id, label: inst.name })),
    ],
    [institutionsQuery.data],
  );

  const schedules = schedulesQuery.data?.items ?? [];
  const selectedSchedule = schedules.find((s) => s.id === selectedScheduleId) ?? null;
  const runs = runsQuery.data?.items ?? [];

  return (
    <DashboardLayout title="Scheduled AI Reports" subtitle="Automated background report generation for admins">
      <div className="grid gap-6 lg:grid-cols-3">
        <VCard className="p-5 lg:col-span-1">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
              <CalendarClock className="h-5 w-5" /> Create Schedule
            </h3>
            <VButton size="sm" variant="ghost" onClick={() => schedulesQuery.refetch()} isLoading={schedulesQuery.isFetching}>
              <RefreshCw className="h-4 w-4" /> Refresh
            </VButton>
          </div>

          <div className="mt-4 space-y-3">
            {isPlatformAdmin && (
              <div>
                <label className="vidya-label">Institution</label>
                <VSelect value={selectedInstitutionId} onChange={(e) => setSelectedInstitutionId(e.target.value)} options={institutionOptions} />
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="vidya-label">Frequency</label>
                <VSelect
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value as "daily" | "weekly")}
                  options={[
                    { value: "daily", label: "Daily" },
                    { value: "weekly", label: "Weekly" },
                  ]}
                />
              </div>
              <div>
                <label className="vidya-label">Time (HH:MM)</label>
                <VInput value={timeOfDay} onChange={(e) => setTimeOfDay(e.target.value)} placeholder="09:00" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="vidya-label">Timezone</label>
                <VInput value={timezone} onChange={(e) => setTimezone(e.target.value)} placeholder="Asia/Kolkata" />
              </div>
              <div>
                <label className="vidya-label">Window (days)</label>
                <VInput value={windowDays} onChange={(e) => setWindowDays(e.target.value)} placeholder="7" />
              </div>
            </div>

            {frequency === "weekly" && (
              <div>
                <label className="vidya-label">Weekdays (Mon=0 .. Sun=6)</label>
                <VInput value={weekdaysText} onChange={(e) => setWeekdaysText(e.target.value)} placeholder="0,2,4" />
              </div>
            )}

            <div>
              <label className="vidya-label">Focus areas (comma-separated)</label>
              <VInput value={focusAreasText} onChange={(e) => setFocusAreasText(e.target.value)} placeholder="attendance, completion, risks" />
            </div>

            <div>
              <label className="vidya-label">Recipients (user_id or email, comma-separated)</label>
              <VInput value={recipientsText} onChange={(e) => setRecipientsText(e.target.value)} placeholder="user-uuid, admin@school.edu" />
            </div>

            <VButton className="w-full" onClick={() => createMutation.mutate()} isLoading={createMutation.isPending}>
              Create Schedule
            </VButton>
          </div>
        </VCard>

        <VCard className="p-5 lg:col-span-1">
          <h3 className="text-base font-semibold text-foreground mb-4">Schedules</h3>
          {schedulesQuery.isLoading && <p className="text-sm text-muted-foreground">Loading schedules...</p>}
          {!schedulesQuery.isLoading && schedules.length === 0 && <p className="text-sm text-muted-foreground">No schedules yet.</p>}

          <div className="space-y-2">
            {schedules.map((s) => {
              const isActive = selectedScheduleId === s.id;
              return (
                <button
                  key={s.id}
                  className={`w-full rounded-xl border p-3 text-left transition ${isActive ? "border-primary bg-primary/5" : "border-border hover:bg-accent/20"}`}
                  onClick={() => setSelectedScheduleId(s.id)}
                >
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-foreground line-clamp-1">{s.report_type}</p>
                    <VBadge variant={getStatusVariant(s.status)}>{s.status}</VBadge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Next: {formatDateTime(s.next_run_at)}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <VButton
                      size="sm"
                      variant="secondary"
                      isLoading={toggleMutation.isPending && toggleMutation.variables?.scheduleId === s.id}
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        toggleMutation.mutate({
                          scheduleId: s.id,
                          nextStatus: s.status === "active" ? "paused" : "active",
                        });
                      }}
                    >
                      {s.status === "active" ? <PauseCircle className="h-4 w-4" /> : <PlayCircle className="h-4 w-4" />}
                      {s.status === "active" ? "Pause" : "Resume"}
                    </VButton>
                  </div>
                </button>
              );
            })}
          </div>
        </VCard>

        <VCard className="p-5 lg:col-span-1">
          <h3 className="text-base font-semibold text-foreground mb-4">Runs</h3>
          {!selectedSchedule && <p className="text-sm text-muted-foreground">Select a schedule to view runs.</p>}
          {selectedSchedule && runsQuery.isLoading && <p className="text-sm text-muted-foreground">Loading runs...</p>}
          {selectedSchedule && !runsQuery.isLoading && runs.length === 0 && <p className="text-sm text-muted-foreground">No runs yet.</p>}

          <div className="space-y-2">
            {runs.map((r) => (
              <div key={r.id} className="rounded-xl border border-border p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-foreground line-clamp-1">{r.status}</p>
                  <span className="text-xs text-muted-foreground">{formatDateTime(r.due_at)}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">Report ID: {r.ai_generation_id}</p>
                <div className="mt-2">
                  <a className="text-xs text-primary underline" href={`/reports/ai?report_id=${encodeURIComponent(r.ai_generation_id)}`}>
                    Open report
                  </a>
                </div>
              </div>
            ))}
          </div>
        </VCard>
      </div>
    </DashboardLayout>
  );
};

export default ScheduledAIReports;

