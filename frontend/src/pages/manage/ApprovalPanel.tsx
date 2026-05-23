import { useMemo, useState } from "react";
import { CheckCircle2, XCircle, Clock, UserMinus, BookOpen, Trash2, UserPlus } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VConfirmDialog from "@/components/ui-custom/VConfirmDialog";
import { useVToast } from "@/components/ui-custom/VToast";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { approveApprovalRequest, fetchAllUsers, fetchApprovalRequests, rejectApprovalRequest } from "@/services/api";

type UiRequestStatus = "pending" | "approved" | "rejected";

const formatDate = (value?: string | null) => {
  if (!value) return "";
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  return new Date(parsed).toISOString().slice(0, 10);
};

const ApprovalPanel = () => {
  const { showToast } = useVToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"pending" | "all">("pending");
  const [confirmDialog, setConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{ id: string; action: "approve" | "reject" } | null>(null);

  const requestsQuery = useQuery({
    queryKey: ["approvalRequests"],
    queryFn: () => fetchApprovalRequests({ limit: 200 }),
  });

  const usersQuery = useQuery({
    queryKey: ["adminUsers"],
    queryFn: () => fetchAllUsers({ max: 500 }),
  });

  const userLookup = useMemo(() => {
    const users = usersQuery.data ?? [];
    return Object.fromEntries(users.map((u) => [u.id, u.name || u.email])) as Record<string, string>;
  }, [usersQuery.data]);

  const requests = useMemo(() => {
    const items = requestsQuery.data?.items ?? [];
    // Sort newest first.
    return [...items].sort((a, b) => String(b.created_at || "").localeCompare(String(a.created_at || "")));
  }, [requestsQuery.data?.items]);

  const pending = requests.filter((r) => r.status === "pending");
  const displayRequests = activeTab === "pending" ? pending : requests;

  const getIcon = (type: string) => {
    switch (type) {
      case "signup":
        return <UserPlus className="h-5 w-5 text-primary" />;
      case "delete_student":
        return <BookOpen className="h-5 w-5 text-warning" />;
      case "delete_educator":
        return <UserMinus className="h-5 w-5 text-destructive" />;
      case "delete_workshop":
        return <Trash2 className="h-5 w-5 text-warning" />;
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "signup":
        return "Sign-Up";
      case "delete_student":
        return "Delete Student";
      case "delete_educator":
        return "Delete Educator";
      case "delete_workshop":
        return "Delete Workshop";
      default:
        return type;
    }
  };

  const actionMutation = useMutation({
    mutationFn: async (payload: { id: string; action: "approve" | "reject" }) => {
      return payload.action === "approve" ? approveApprovalRequest(payload.id) : rejectApprovalRequest(payload.id);
    },
    onSuccess: (_, payload) => {
      showToast(
        payload.action === "approve" ? "success" : "info",
        payload.action === "approve" ? "Approved" : "Rejected",
        `Request has been ${payload.action === "approve" ? "approved" : "rejected"}.`
      );
      setConfirmDialog(false);
      queryClient.invalidateQueries({ queryKey: ["approvalRequests"] });
    },
    onError: (err: unknown) => {
      showToast("destructive", "Action Failed", err instanceof Error ? err.message : "Unable to process action.");
      setConfirmDialog(false);
    },
  });

  const openConfirm = (id: string, action: "approve" | "reject") => {
    setConfirmAction({ id, action });
    setConfirmDialog(true);
  };

  const summaryApproved = requests.filter((r) => r.status === "approved").length;
  const summaryRejected = requests.filter((r) => r.status === "rejected").length;

  return (
    <DashboardLayout title="Approvals & Requests">
      {/* Summary */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-3 mb-6">
        <VCard hover className="p-5 cursor-pointer" onClick={() => setActiveTab("pending")}>
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-warning" />
            <p className="text-sm text-muted-foreground">Pending</p>
          </div>
          <p className="text-2xl font-bold text-warning">{pending.length}</p>
        </VCard>
        <VCard hover className="p-5 cursor-pointer" onClick={() => setActiveTab("all")}>
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="h-4 w-4 text-success" />
            <p className="text-sm text-muted-foreground">Approved</p>
          </div>
          <p className="text-2xl font-bold text-success">{summaryApproved}</p>
        </VCard>
        <VCard hover className="p-5 cursor-pointer" onClick={() => setActiveTab("all")}>
          <div className="flex items-center gap-2 mb-2">
            <XCircle className="h-4 w-4 text-destructive" />
            <p className="text-sm text-muted-foreground">Rejected</p>
          </div>
          <p className="text-2xl font-bold text-destructive">{summaryRejected}</p>
        </VCard>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-border">
        {(["pending", "all"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${activeTab === t ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"}`}
          >
            {t === "pending" ? `Pending (${pending.length})` : "All Requests"}
          </button>
        ))}
      </div>

      {/* Request Cards */}
      <div className="space-y-3">
        {displayRequests.map((req) => {
          const payload = (req.payload || {}) as Record<string, any>;
          const name =
            payload.name ||
            payload.workshop_title ||
            payload.workshop_name ||
            payload.email ||
            getTypeLabel(req.request_type);
          const details = payload.details || payload.institution || payload.reason || "";
          const requestedBy = req.requested_by ? userLookup[req.requested_by] ?? req.requested_by : "—";
          const date = formatDate(req.created_at);
          const status = req.status as UiRequestStatus;
          return (
            <VCard key={req.id} className="p-5">
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex items-center gap-3 flex-1">
                  <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center shrink-0">
                    {getIcon(req.request_type)}
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-sm font-semibold text-foreground">{name}</h4>
                      <VBadge variant="outline">{getTypeLabel(req.request_type)}</VBadge>
                      {payload.role && <VBadge variant="default">{payload.role}</VBadge>}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {details} {date ? `- ${date}` : ""}
                    </p>
                    <p className="text-xs text-muted-foreground">Requested by: {requestedBy}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {status === "pending" ? (
                    <>
                      <VButton size="sm" onClick={() => openConfirm(req.id, "approve")} isLoading={actionMutation.isPending}>
                        <CheckCircle2 className="h-3.5 w-3.5" /> Approve
                      </VButton>
                      <VButton variant="destructive" size="sm" onClick={() => openConfirm(req.id, "reject")} isLoading={actionMutation.isPending}>
                        <XCircle className="h-3.5 w-3.5" /> Reject
                      </VButton>
                    </>
                  ) : (
                    <VBadge variant={status === "approved" ? "success" : "destructive"}>
                      {status === "approved" ? "Approved" : "Rejected"}
                    </VBadge>
                  )}
                </div>
              </div>
            </VCard>
          );
        })}

        {displayRequests.length === 0 && (
          <div className="text-center py-12">
            <CheckCircle2 className="h-12 w-12 text-success mx-auto mb-3" />
            <p className="text-lg font-semibold text-foreground">
              {requestsQuery.isLoading ? "Loading..." : "All caught up!"}
            </p>
            <p className="text-sm text-muted-foreground">
              {requestsQuery.isError ? "Unable to load requests." : "No pending requests."}
            </p>
          </div>
        )}
      </div>

      <VConfirmDialog
        isOpen={confirmDialog}
        onClose={() => setConfirmDialog(false)}
        onConfirm={() => confirmAction && actionMutation.mutate(confirmAction)}
        title={confirmAction?.action === "approve" ? "Confirm Approval" : "Confirm Rejection"}
        message={`Are you sure you want to ${confirmAction?.action} this request?`}
        confirmText={confirmAction?.action === "approve" ? "Approve" : "Reject"}
      />
    </DashboardLayout>
  );
};

export default ApprovalPanel;
