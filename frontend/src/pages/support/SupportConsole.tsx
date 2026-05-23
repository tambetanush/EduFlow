import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, RotateCcw, AlertTriangle, Shield } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VBadge from "@/components/ui-custom/VBadge";
import { useVToast } from "@/components/ui-custom/VToast";
import {
  fetchSupportAuditLogs,
  fetchSupportCacheStats,
  fetchSupportConfig,
  fetchSupportJobDetail,
  fetchSupportJobs,
  fetchSupportRateLimitEvents,
  rerunSupportJob,
} from "@/services/api";

const getJobVariant = (status?: string) => {
  if (status === "completed") return "success" as const;
  if (status === "failed") return "destructive" as const;
  if (status === "processing") return "warning" as const;
  return "outline" as const;
};

const formatDateTime = (value?: string | null) => {
  if (!value) return "-";
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  return new Date(parsed).toLocaleString();
};

const SupportConsole = () => {
  const { showToast } = useVToast();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<"jobs" | "audit" | "rate_limits" | "cache" | "config">("jobs");

  const [statusFilter, setStatusFilter] = useState("");
  const [featureTypeFilter, setFeatureTypeFilter] = useState("");
  const [institutionIdFilter, setInstitutionIdFilter] = useState("");
  const [requesterUserIdFilter, setRequesterUserIdFilter] = useState("");
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const configQuery = useQuery({
    queryKey: ["supportConfig"],
    queryFn: fetchSupportConfig,
    enabled: activeTab === "config",
  });

  const cacheQuery = useQuery({
    queryKey: ["supportCacheStats"],
    queryFn: fetchSupportCacheStats,
    enabled: activeTab === "cache",
    refetchInterval: 10_000,
  });

  const jobsQuery = useQuery({
    queryKey: ["supportJobs", statusFilter, featureTypeFilter, institutionIdFilter, requesterUserIdFilter],
    queryFn: () =>
      fetchSupportJobs({
        status: statusFilter || undefined,
        feature_type: featureTypeFilter || undefined,
        institution_id: institutionIdFilter || undefined,
        requester_user_id: requesterUserIdFilter || undefined,
        limit: 50,
      }),
    enabled: activeTab === "jobs",
    refetchInterval: 5_000,
  });

  const jobDetailQuery = useQuery({
    queryKey: ["supportJobDetail", selectedJobId],
    queryFn: () => fetchSupportJobDetail(selectedJobId || ""),
    enabled: Boolean(activeTab === "jobs" && selectedJobId),
    refetchInterval: (query) => {
      const s = (query.state.data as any)?.status as string | undefined;
      return s === "pending" || s === "processing" ? 2500 : false;
    },
  });

  const auditQuery = useQuery({
    queryKey: ["supportAuditLogs"],
    queryFn: () => fetchSupportAuditLogs({ limit: 50, since_hours: 72 }),
    enabled: activeTab === "audit",
    refetchInterval: 15_000,
  });

  const rateLimitQuery = useQuery({
    queryKey: ["supportRateLimitEvents"],
    queryFn: () => fetchSupportRateLimitEvents({ limit: 50, since_hours: 72 }),
    enabled: activeTab === "rate_limits",
    refetchInterval: 15_000,
  });

  const rerunMutation = useMutation({
    mutationFn: (jobId: string) => rerunSupportJob(jobId),
    onSuccess: async (data) => {
      await queryClient.invalidateQueries({ queryKey: ["supportJobs"] });
      await queryClient.invalidateQueries({ queryKey: ["supportJobDetail", data.generation_id] });
      showToast("success", "Re-run queued", data.message);
    },
    onError: (error: unknown) => {
      showToast("error", "Re-run failed", error instanceof Error ? error.message : "Unable to re-run job.");
    },
  });

  const jobRows = jobsQuery.data?.items ?? [];
  const selectedJob = jobDetailQuery.data ?? null;

  const featureTypeOptions = useMemo(
    () => [
      { value: "", label: "All features" },
      { value: "admin_report", label: "Admin report" },
      { value: "student_explanation", label: "Student explanation" },
    ],
    [],
  );

  const statusOptions = useMemo(
    () => [
      { value: "", label: "All statuses" },
      { value: "pending", label: "pending" },
      { value: "processing", label: "processing" },
      { value: "completed", label: "completed" },
      { value: "failed", label: "failed" },
    ],
    [],
  );

  return (
    <DashboardLayout title="Support Console" subtitle="Audit logs, job status, traces, reruns, and operational stats">
      <div className="flex flex-wrap gap-2 mb-5">
        {[
          { key: "jobs", label: "Jobs" },
          { key: "audit", label: "Audit Logs" },
          { key: "rate_limits", label: "Rate Limits" },
          // { key: "cache", label: "Cache Stats" },
          // { key: "config", label: "Config" },
        ].map((t) => (
          <VButton
            key={t.key}
            size="sm"
            variant={activeTab === (t.key as any) ? "default" : "secondary"}
            onClick={() => setActiveTab(t.key as any)}
          >
            {t.label}
          </VButton>
        ))}
        <div className="ml-auto">
          <VButton
            size="sm"
            variant="ghost"
            onClick={() => {
              jobsQuery.refetch();
              auditQuery.refetch();
              rateLimitQuery.refetch();
              cacheQuery.refetch();
              configQuery.refetch();
            }}
          >
            <RefreshCw className="h-4 w-4" /> Refresh
          </VButton>
        </div>
      </div>

      {activeTab === "jobs" && (
        <div className="grid gap-6 lg:grid-cols-3">
          <VCard className="p-5 lg:col-span-1">
            <h3 className="text-base font-semibold text-foreground mb-4 flex items-center gap-2">
              <Shield className="h-5 w-5" /> Filters
            </h3>
            <div className="space-y-3">
              <div>
                <label className="vidya-label">Status</label>
                <VSelect value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} options={statusOptions} />
              </div>
              <div>
                <label className="vidya-label">Feature</label>
                <VSelect value={featureTypeFilter} onChange={(e) => setFeatureTypeFilter(e.target.value)} options={featureTypeOptions} />
              </div>
              <div>
                <label className="vidya-label">Institution ID</label>
                <VInput value={institutionIdFilter} onChange={(e) => setInstitutionIdFilter(e.target.value)} placeholder="optional" />
              </div>
              <div>
                <label className="vidya-label">Requester User ID</label>
                <VInput value={requesterUserIdFilter} onChange={(e) => setRequesterUserIdFilter(e.target.value)} placeholder="optional" />
              </div>
            </div>
          </VCard>

          <VCard className="p-5 lg:col-span-1">
            <h3 className="text-base font-semibold text-foreground mb-4">Jobs</h3>
            {jobsQuery.isLoading && <p className="text-sm text-muted-foreground">Loading jobs...</p>}
            {!jobsQuery.isLoading && jobRows.length === 0 && <p className="text-sm text-muted-foreground">No jobs found.</p>}
            <div className="space-y-2">
              {jobRows.map((j) => (
                <button
                  key={j.id}
                  className={`w-full rounded-xl border p-3 text-left transition ${selectedJobId === j.id ? "border-primary bg-primary/5" : "border-border hover:bg-accent/20"}`}
                  onClick={() => setSelectedJobId(j.id)}
                >
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-foreground line-clamp-1">{j.feature_type}</p>
                    <VBadge variant={getJobVariant(j.status)}>{j.status}</VBadge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Updated: {formatDateTime(j.updated_at)}</p>
                  {j.progress?.message && (
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{String(j.progress.message)}</p>
                  )}
                </button>
              ))}
            </div>
          </VCard>

          <VCard className="p-5 lg:col-span-1">
            <h3 className="text-base font-semibold text-foreground mb-4">Job Detail</h3>
            {!selectedJobId && <p className="text-sm text-muted-foreground">Select a job to view details.</p>}
            {selectedJobId && jobDetailQuery.isLoading && <p className="text-sm text-muted-foreground">Loading job...</p>}
            {selectedJob && (
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <VBadge variant={getJobVariant(selectedJob.status)}>{selectedJob.status}</VBadge>
                  <span className="text-xs text-muted-foreground">{selectedJob.feature_type}</span>
                </div>

                <div className="text-xs text-muted-foreground space-y-1">
                  <p>Job ID: <span className="text-foreground">{selectedJob.id}</span></p>
                  <p>Requester: <span className="text-foreground">{selectedJob.requester_user_id}</span></p>
                  <p>Institution: <span className="text-foreground">{selectedJob.institution_id || "-"}</span></p>
                  <p>Updated: <span className="text-foreground">{formatDateTime(selectedJob.updated_at)}</span></p>
                </div>

                {selectedJob.progress && (
                  <div className="rounded-xl border border-border bg-accent/30 p-3">
                    <p className="text-xs text-muted-foreground">
                      {typeof selectedJob.progress.message === "string" ? selectedJob.progress.message : "Working..."}
                      {typeof selectedJob.progress.percent === "number" ? ` (${selectedJob.progress.percent}%)` : ""}
                    </p>
                  </div>
                )}

                {selectedJob.status === "failed" && (
                  <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-3">
                    <p className="text-sm text-destructive font-medium flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" /> Failed
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {typeof (selectedJob.error_details as any)?.message === "string"
                        ? String((selectedJob.error_details as any)?.message)
                        : "Unknown error."}
                    </p>
                    <div className="mt-3">
                      <VButton
                        size="sm"
                        variant="secondary"
                        isLoading={rerunMutation.isPending}
                        onClick={() => rerunMutation.mutate(selectedJob.id)}
                      >
                        <RotateCcw className="h-4 w-4" /> Re-run
                      </VButton>
                    </div>
                  </div>
                )}

                {selectedJob.error_trace && (
                  <div className="rounded-xl border border-border p-3">
                    <p className="text-xs text-muted-foreground mb-2">Sanitized Trace</p>
                    <pre className="text-[11px] whitespace-pre-wrap text-foreground max-h-64 overflow-auto">
                      {selectedJob.error_trace}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </VCard>
        </div>
      )}

      {activeTab === "audit" && (
        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-4">Audit Logs (last 72h)</h3>
          {auditQuery.isLoading && <p className="text-sm text-muted-foreground">Loading audit logs...</p>}
          {!auditQuery.isLoading && (auditQuery.data?.items?.length ?? 0) === 0 && <p className="text-sm text-muted-foreground">No logs.</p>}
          <div className="space-y-2">
            {(auditQuery.data?.items ?? []).map((a) => (
              <div key={a.id} className="rounded-xl border border-border p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-foreground">{a.action}</p>
                  <span className="text-xs text-muted-foreground">{formatDateTime(a.created_at)}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">Actor: {a.actor_user_id || "-"}</p>
                {a.target_type && <p className="text-xs text-muted-foreground mt-1">Target: {a.target_type}:{a.target_id}</p>}
                {a.metadata_ && Object.keys(a.metadata_).length > 0 && (
                  <pre className="text-[10px] text-muted-foreground mt-2 bg-accent/30 p-2 rounded overflow-auto whitespace-pre-wrap">
                    {JSON.stringify(a.metadata_, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </VCard>
      )}

      {activeTab === "rate_limits" && (
        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-4">Rate Limit Events (last 72h)</h3>
          {rateLimitQuery.isLoading && <p className="text-sm text-muted-foreground">Loading events...</p>}
          {!rateLimitQuery.isLoading && (rateLimitQuery.data?.items?.length ?? 0) === 0 && <p className="text-sm text-muted-foreground">No events.</p>}
          <div className="space-y-2">
            {(rateLimitQuery.data?.items ?? []).map((e) => (
              <div key={e.id} className="rounded-xl border border-border p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-foreground line-clamp-1">{e.key}</p>
                  <VBadge variant={e.allowed ? "success" : "destructive"}>{e.allowed ? "allowed" : "blocked"}</VBadge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Retry after: {e.retry_after_seconds}s • Rule: {e.rule_max_requests}/{e.rule_window_seconds}s
                </p>
                <p className="text-xs text-muted-foreground mt-1">{formatDateTime(e.created_at)}</p>
              </div>
            ))}
          </div>
        </VCard>
      )}

      {/* {activeTab === "cache" && (
        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-4">Cache / Queue Stats</h3>
          {cacheQuery.isLoading && <p className="text-sm text-muted-foreground">Loading stats...</p>}
          {cacheQuery.data && (
            <div className="grid gap-4 md:grid-cols-2">
              <VCard className="p-4">
                <p className="text-xs text-muted-foreground">AI generations</p>
                <p className="text-2xl font-bold text-foreground mt-1">{cacheQuery.data.ai_generations.total}</p>
                <p className="text-xs text-muted-foreground mt-2">
                  Cached admin: {cacheQuery.data.ai_generations.cached_completed?.admin_report ?? 0} • Cached expl: {cacheQuery.data.ai_generations.cached_completed?.student_explanation ?? 0}
                </p>
              </VCard>
              <VCard className="p-4">
                <p className="text-xs text-muted-foreground">Redis</p>
                <p className="text-2xl font-bold text-foreground mt-1">{cacheQuery.data.redis.dlq_length}</p>
                <p className="text-xs text-muted-foreground mt-2">Dead-letter queue length</p>
              </VCard>
            </div>
          )}
        </VCard>
      )} */}

      {/* {activeTab === "config" && (
        <VCard className="p-5">
          <h3 className="text-base font-semibold text-foreground mb-4">Config (sanitized)</h3>
          {configQuery.isLoading && <p className="text-sm text-muted-foreground">Loading config...</p>}
          {configQuery.data && (
            <div className="space-y-2 text-sm">
              <p>Queue: <span className="text-foreground font-semibold">{configQuery.data.celery_queue}</span></p>
              <p>Redis configured: <span className="text-foreground font-semibold">{String(configQuery.data.redis_configured)}</span></p>
              <p>SMTP configured: <span className="text-foreground font-semibold">{String(configQuery.data.smtp_configured)}</span></p>
              <p>AI retries: <span className="text-foreground font-semibold">{configQuery.data.ai_max_retries}</span></p>
              <p>Retry base delay: <span className="text-foreground font-semibold">{configQuery.data.ai_retry_base_delay_seconds}s</span></p>
            </div>
          )}
        </VCard>
      )} */}
    </DashboardLayout>
  );
};

export default SupportConsole;

