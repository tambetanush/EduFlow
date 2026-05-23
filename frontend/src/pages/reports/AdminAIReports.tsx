import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles, RefreshCw, AlertTriangle } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import VBadge from "@/components/ui-custom/VBadge";
import { useRole } from "@/hooks/useRole";
import { useAuth } from "@/hooks/useAuth";
import { useVToast } from "@/components/ui-custom/VToast";
import {
  createAdminAIReport,
  fetchAdminAIReportResult,
  fetchAdminAIReportStatus,
  fetchAdminAIReportsHistory,
  fetchInstitutions,
} from "@/services/api";
import type {
  BackendAdminAIReportCreateRequest,
  BackendAdminAIReportHistoryItem,
} from "@/api/types";

const getStatusVariant = (status?: string) => {
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

const AdminAIReports = () => {
  const role = useRole();
  const { user } = useAuth();
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const location = useLocation();

  const [selectedInstitutionId, setSelectedInstitutionId] = useState("");
  const [historyInstitutionFilter, setHistoryInstitutionFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [focusAreasText, setFocusAreasText] = useState("");
  const [forceRegenerate, setForceRegenerate] = useState(false);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  const isPlatformAdmin = role === "admin";
  const isInstitutionAdmin = role === "institution_admin";

  const institutionsQuery = useQuery({
    queryKey: ["institutionsForAIReports"],
    queryFn: fetchInstitutions,
    enabled: isPlatformAdmin,
  });

  const historyQuery = useQuery({
    queryKey: ["adminAIReportsHistory", role, historyInstitutionFilter],
    queryFn: () =>
      fetchAdminAIReportsHistory({
        institutionId: isPlatformAdmin ? (historyInstitutionFilter || undefined) : undefined,
        limit: 50,
      }),
    enabled: isPlatformAdmin || isInstitutionAdmin,
  });

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const reportIdFromUrl = params.get("report_id");
    if (reportIdFromUrl) {
      setSelectedReportId(reportIdFromUrl);
      return;
    }
    if (!selectedReportId && historyQuery.data?.items?.length) {
      setSelectedReportId(historyQuery.data.items[0].report_id);
    }
  }, [historyQuery.data, selectedReportId, location.search]);

  const statusQuery = useQuery({
    queryKey: ["adminAIReportStatus", selectedReportId],
    queryFn: () => fetchAdminAIReportStatus(selectedReportId || ""),
    enabled: Boolean(selectedReportId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "pending" || status === "processing" ? 2500 : false;
    },
  });

  const resultQuery = useQuery({
    queryKey: ["adminAIReportResult", selectedReportId],
    queryFn: () => fetchAdminAIReportResult(selectedReportId || ""),
    enabled: Boolean(selectedReportId && statusQuery.data?.status === "completed"),
  });

  const createMutation = useMutation({
    mutationFn: (payload: BackendAdminAIReportCreateRequest) => createAdminAIReport(payload),
    onSuccess: async (data) => {
      setSelectedReportId(data.report_id);
      await queryClient.invalidateQueries({ queryKey: ["adminAIReportsHistory"] });
      const isReady = data.status === "completed";
      showToast(
        data.from_cache ? "info" : isReady ? "success" : "warning",
        data.from_cache ? "Loaded Cached Report" : isReady ? "Report Ready" : "Report Queued",
        data.from_cache
          ? "Reused a previous matching report."
          : isReady
            ? "AI report is ready."
            : "Generating in background. This page will auto-refresh.",
      );
    },
    onError: (error: unknown) => {
      showToast("destructive", "Report Generation Failed", error instanceof Error ? error.message : "Unable to generate report.");
    },
  });

  const institutionOptions = useMemo(
    () => [
      { value: "", label: "All institutions (platform scope)" },
      ...(institutionsQuery.data ?? []).map((inst) => ({ value: inst.id, label: inst.name })),
    ],
    [institutionsQuery.data],
  );

  const historyRows = historyQuery.data?.items ?? [];
  const selectedHistoryRow = historyRows.find((item) => item.report_id === selectedReportId) ?? null;

  const handleGenerate = () => {
    if (!(isPlatformAdmin || isInstitutionAdmin)) return;

    const focusAreas = focusAreasText
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    const payload: BackendAdminAIReportCreateRequest = {
      ...(dateFrom ? { date_from: dateFrom } : {}),
      ...(dateTo ? { date_to: dateTo } : {}),
      ...(focusAreas.length ? { focus_areas: focusAreas } : {}),
      ...(forceRegenerate ? { force_regenerate: true } : {}),
    };

    if (isInstitutionAdmin) {
      payload.institution_id = user?.institution_id ?? undefined;
    } else if (selectedInstitutionId) {
      payload.institution_id = selectedInstitutionId;
    }

    createMutation.mutate(payload);
  };

  const renderHistoryRow = (row: BackendAdminAIReportHistoryItem) => {
    const isActive = selectedReportId === row.report_id;
    return (
      <button
        key={row.report_id}
        onClick={() => setSelectedReportId(row.report_id)}
        className={`w-full text-left rounded-xl border p-3 transition-colors ${isActive ? "border-primary bg-primary/5" : "border-border hover:bg-accent/50"}`}
      >
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-semibold text-foreground line-clamp-1">{row.summary_preview || "AI report"}</p>
          <VBadge variant={getStatusVariant(row.status)}>{row.status}</VBadge>
        </div>
        <p className="text-xs text-muted-foreground mt-1">{formatDateTime(row.created_at)}</p>
      </button>
    );
  };

  return (
    <DashboardLayout title="AI Reports">
      <div className="space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-foreground">Admin AI Reports</h2>
            <p className="text-sm text-muted-foreground">Generate structured insights from platform analytics.</p>
          </div>
          <VButton variant="secondary" onClick={() => historyQuery.refetch()}>
            <RefreshCw className="h-4 w-4" /> Refresh
          </VButton>
        </div>

        <VCard className="p-5 space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {isPlatformAdmin && (
              <VSelect
                label="Institution Scope"
                value={selectedInstitutionId}
                onChange={(evt) => setSelectedInstitutionId(evt.target.value)}
                options={institutionOptions}
              />
            )}
            <VInput label="Date From" type="date" value={dateFrom} onChange={(evt) => setDateFrom(evt.target.value)} />
            <VInput label="Date To" type="date" value={dateTo} onChange={(evt) => setDateTo(evt.target.value)} />
            <VInput
              label="Focus Areas"
              placeholder="comma-separated (optional)"
              value={focusAreasText}
              onChange={(evt) => setFocusAreasText(evt.target.value)}
            />
          </div>

          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              checked={forceRegenerate}
              onChange={(evt) => setForceRegenerate(evt.target.checked)}
            />
            Force regenerate (skip cached report)
          </label>

          <div className="flex justify-end">
            <VButton onClick={handleGenerate} isLoading={createMutation.isPending}>
              <Sparkles className="h-4 w-4" /> Generate AI Report
            </VButton>
          </div>
        </VCard>

        <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
          <VCard className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-foreground">Report History</h3>
              {isPlatformAdmin && (
                <select
                  value={historyInstitutionFilter}
                  onChange={(evt) => setHistoryInstitutionFilter(evt.target.value)}
                  className="vidya-input h-8 text-xs w-[170px]"
                >
                  {institutionOptions.map((option) => (
                    <option key={option.value || "all"} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
              {historyQuery.isLoading && <p className="text-sm text-muted-foreground">Loading reports...</p>}
              {!historyQuery.isLoading && historyRows.length === 0 && (
                <p className="text-sm text-muted-foreground">No reports generated yet.</p>
              )}
              {historyRows.map(renderHistoryRow)}
            </div>
          </VCard>

          <VCard className="p-5">
            {!selectedReportId && <p className="text-sm text-muted-foreground">Select or generate a report to view details.</p>}

            {selectedReportId && (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <VBadge variant={getStatusVariant(statusQuery.data?.status)}>
                    {statusQuery.data?.status || selectedHistoryRow?.status || "pending"}
                  </VBadge>
                  <span className="text-xs text-muted-foreground">Report ID: {selectedReportId}</span>
                  {selectedHistoryRow?.created_at && (
                    <span className="text-xs text-muted-foreground">Created: {formatDateTime(selectedHistoryRow.created_at)}</span>
                  )}
                </div>

                {(statusQuery.isLoading || statusQuery.data?.status === "pending" || statusQuery.data?.status === "processing") && (
                  <div className="rounded-xl border border-border bg-accent/30 p-4">
                    <p className="text-sm text-foreground">Generating report...</p>
                    <p className="text-xs text-muted-foreground mt-1">This page auto-refreshes until the report is complete.</p>
                    {statusQuery.data?.progress && (
                      <p className="text-xs text-muted-foreground mt-2">
                        {typeof statusQuery.data.progress.message === "string" ? statusQuery.data.progress.message : "Working..."}
                        {typeof statusQuery.data.progress.percent === "number" ? ` (${statusQuery.data.progress.percent}%)` : ""}
                      </p>
                    )}
                  </div>
                )}

                {statusQuery.data?.status === "failed" && (
                  <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-4">
                    <p className="text-sm text-destructive font-medium flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" /> Report generation failed
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {(statusQuery.data.error_details?.message as string) || "Unknown error."}
                    </p>
                  </div>
                )}

                {statusQuery.data?.status === "completed" && resultQuery.data && (
                  <div className="space-y-5">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Summary</p>
                      <p className="text-sm text-foreground leading-relaxed">{resultQuery.data.result.summary}</p>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <VCard className="p-4">
                        <p className="text-xs text-muted-foreground mb-2">Key Insights</p>
                        <ul className="space-y-2 text-sm text-foreground list-disc list-inside">
                          {resultQuery.data.result.key_insights.map((item, idx) => (
                            <li key={`insight-${idx}`}>{item}</li>
                          ))}
                        </ul>
                      </VCard>

                      <VCard className="p-4">
                        <p className="text-xs text-muted-foreground mb-2">Risk Flags</p>
                        <ul className="space-y-2 text-sm text-foreground list-disc list-inside">
                          {resultQuery.data.result.risk_flags.map((item, idx) => (
                            <li key={`risk-${idx}`}>{item}</li>
                          ))}
                          {resultQuery.data.result.risk_flags.length === 0 && <li>No immediate risk flags.</li>}
                        </ul>
                      </VCard>
                    </div>

                    <VCard className="p-4">
                      <p className="text-xs text-muted-foreground mb-2">Recommendations</p>
                      <div className="space-y-3">
                        {resultQuery.data.result.recommendations.map((rec, idx) => (
                          <div key={`rec-${idx}`} className="rounded-lg border border-border p-3">
                            <div className="flex items-center justify-between gap-2">
                              <p className="text-sm font-semibold text-foreground">{rec.title}</p>
                              <VBadge variant={rec.priority === "high" ? "destructive" : rec.priority === "medium" ? "warning" : "outline"}>
                                {rec.priority}
                              </VBadge>
                            </div>
                            <p className="text-sm text-foreground mt-1">{rec.action}</p>
                            <p className="text-xs text-muted-foreground mt-1">{rec.rationale}</p>
                          </div>
                        ))}
                        {resultQuery.data.result.recommendations.length === 0 && (
                          <p className="text-sm text-muted-foreground">No recommendations generated.</p>
                        )}
                      </div>
                    </VCard>

                    <div className="grid gap-4 md:grid-cols-2">
                      <VCard className="p-4">
                        <p className="text-xs text-muted-foreground mb-2">Trend Highlights</p>
                        <ul className="space-y-2 text-sm text-foreground list-disc list-inside">
                          {resultQuery.data.result.trend_highlights.map((item, idx) => (
                            <li key={`trend-${idx}`}>{item}</li>
                          ))}
                        </ul>
                      </VCard>

                      <VCard className="p-4">
                        <p className="text-xs text-muted-foreground mb-2">Data Window</p>
                        <p className="text-sm text-foreground">Scope: {resultQuery.data.result.data_window.scope}</p>
                        <p className="text-sm text-foreground">Start: {resultQuery.data.result.data_window.start_date || "-"}</p>
                        <p className="text-sm text-foreground">End: {resultQuery.data.result.data_window.end_date || "-"}</p>
                      </VCard>
                    </div>

                    <VCard className="p-4">
                      <p className="text-xs text-muted-foreground mb-2">Caveats</p>
                      <ul className="space-y-2 text-sm text-foreground list-disc list-inside">
                        {resultQuery.data.result.caveats.map((item, idx) => (
                          <li key={`caveat-${idx}`}>{item}</li>
                        ))}
                        {resultQuery.data.result.caveats.length === 0 && <li>No caveats reported.</li>}
                      </ul>
                    </VCard>
                  </div>
                )}
              </div>
            )}
          </VCard>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminAIReports;

