import { useMemo, useState } from "react";
import { Eye, Search, Mail, Send } from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VTable from "@/components/ui-custom/VTable";
import VBadge from "@/components/ui-custom/VBadge";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import VInput from "@/components/ui-custom/VInput";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import { useAuth } from "@/hooks/useAuth";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createApprovalRequest,
  fetchAllUsers,
  fetchEnrollments,
  fetchInstitutions,
  sendParentEmailMessage,
  fetchParentContactDirectory,
  fetchWorkshops,
  updateUser,
} from "@/services/api";

interface StudentRow {
  id: string;
  name: string;
  email: string;
  institution: string;
  workshop: string;
  status: "Active" | "Inactive" | "Completed";
  parentEmail: string;
  parentName: string;
}


const mapEnrollmentStatus = (raw?: string | null): StudentRow["status"] => {
  const value = (raw || "").toLowerCase();
  if (value === "completed") return "Completed";
  if (value === "active") return "Active";
  if (value === "dropped") return "Inactive";
  return "Inactive";
};

const StudentManagement = () => {
  const role = useRole();
  const { user } = useAuth();
  const { showToast } = useVToast();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [selected, setSelected] = useState<StudentRow | null>(null);
  const [viewModal, setViewModal] = useState(false);
  const [emailModal, setEmailModal] = useState(false);
  const [emailSubject, setEmailSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");
  const [removalTarget, setRemovalTarget] = useState<StudentRow | null>(null);
  const [removalConfirm, setRemovalConfirm] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [editParentName, setEditParentName] = useState("");
  const [editParentEmail, setEditParentEmail] = useState("");

  const isInstitutionAdmin = role === "institution_admin";

  const usersQuery = useQuery({
    queryKey: ["adminUsers"],
    queryFn: () => fetchAllUsers({ max: 500 }),
  });

  const institutionsQuery = useQuery({
    queryKey: ["institutions"],
    queryFn: fetchInstitutions,
  });

  const workshopsQuery = useQuery({
    queryKey: ["workshops"],
    queryFn: fetchWorkshops,
  });

  const institutionLookup = useMemo(() => {
    const items = institutionsQuery.data ?? [];
    return Object.fromEntries(items.map((i) => [i.id, i.name])) as Record<string, string>;
  }, [institutionsQuery.data]);

  const workshopLookup = useMemo(() => {
    const items = workshopsQuery.data ?? [];
    return Object.fromEntries(items.map((w) => [w.id, w.name])) as Record<string, string>;
  }, [workshopsQuery.data]);

  const studentUsers = useMemo(() => {
    const users = usersQuery.data ?? [];
    const allStudents = users.filter((u) => u.role === "student");
    if (isInstitutionAdmin) {
      const instId = user?.institution_id ?? null;
      return instId ? allStudents.filter((u) => u.institution_id === instId) : [];
    }
    return allStudents;
  }, [isInstitutionAdmin, user?.institution_id, usersQuery.data]);

  const studentIdsKey = useMemo(() => studentUsers.map((s) => s.id).sort().join(","), [studentUsers]);

  const parentContactsQuery = useQuery({
    queryKey: ["parentContacts", studentIdsKey],
    queryFn: () => fetchParentContactDirectory(studentUsers.map((student) => student.id)),
    enabled: studentUsers.length > 0,
  });
  const enrollmentsQuery = useQuery({
    queryKey: ["studentEnrollments", studentIdsKey],
    queryFn: async () => {
      const ids = studentUsers.map((s) => s.id);
      const pairs: Array<[string, { workshop_id?: string | null; status?: string | null }[]]> = [];
      const batchSize = 25;
      for (let index = 0; index < ids.length; index += batchSize) {
        const batch = ids.slice(index, index + batchSize);
        const batchResults = await Promise.all(
          batch.map(async (id) => {
            try {
              const page = await fetchEnrollments(id);
              return { id, items: page.items };
            } catch {
              return { id, items: [] };
            }
          })
        );
        for (const result of batchResults) {
          pairs.push([result.id, result.items]);
        }
      }
      return Object.fromEntries(pairs) as Record<string, { workshop_id?: string | null; status?: string | null }[]>;
    },
    enabled: studentUsers.length > 0,
  });

  const rows: StudentRow[] = useMemo(() => {
    const enrollmentMap = enrollmentsQuery.data ?? {};
    const parentContacts = parentContactsQuery.data?.items ?? [];
    const parentByStudentId = Object.fromEntries(
      parentContacts.map((entry) => [entry.student_id, entry])
    ) as Record<string, { parent_name?: string | null; parent_email?: string | null }>;

    return studentUsers.map((u) => {
      const enrollments = enrollmentMap[u.id] ?? [];
      const first = enrollments[0];
      const status = enrollments.length > 0 ? mapEnrollmentStatus(first?.status) : "Inactive";

      const firstWorkshop = first?.workshop_id ? workshopLookup[first.workshop_id] ?? "" : "";
      const workshop =
        enrollments.length > 1 && firstWorkshop ? `${firstWorkshop} +${enrollments.length - 1}` : firstWorkshop || "—";

      const contact = parentByStudentId[u.id];
      const parentEmail = contact?.parent_email?.trim() || "";
      const parentName = contact?.parent_name?.trim() || "Parent/Guardian";

      return {
        id: u.id,
        name: u.name || u.email,
        email: u.email,
        institution: u.institution_id ? institutionLookup[u.institution_id] ?? u.institution_id : "",
        workshop,
        status,
        parentEmail,
        parentName,
      };
    });
  }, [enrollmentsQuery.data, institutionLookup, parentContactsQuery.data?.items, studentUsers, workshopLookup]);

  const filtered = rows.filter((s) => {
    const matchSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) || s.email.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "All" || s.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const removalMutation = useMutation({
    mutationFn: async (target: StudentRow) => {
      return createApprovalRequest({
        request_type: "delete_student",
        payload: {
          user_id: target.id,
          name: target.name,
          email: target.email,
          institution: target.institution,
        },
      });
    },
    onSuccess: (_, target) => {
      showToast("info", "Request Sent", `Removal request for "${target.name}" sent to Platform Admin.`);
      queryClient.invalidateQueries({ queryKey: ["approvalRequests"] });
    },
    onError: (err: unknown) => {
      showToast("error", "Request Failed", err instanceof Error ? err.message : "Unable to send request.");
    },
  });
  const parentEmailMutation = useMutation({
    mutationFn: async (payload: { studentId: string; subject: string; body: string; parentEmail: string }) => {
      const response = await sendParentEmailMessage({
        studentIds: [payload.studentId],
        subject: payload.subject,
        body: payload.body,
      });
      return { ...response, parentEmail: payload.parentEmail };
    },
    onSuccess: (result) => {
      showToast("success", "Email Sent", `${result.accepted} message delivered to ${result.parentEmail}.`);
      if (result.failed > 0) {
        showToast("warning", "Some recipients skipped", `${result.failed} recipient(s) missing parent contact details.`);
      }
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      setEmailModal(false);
    },
    onError: (err: unknown) => {
      showToast("error", "Send Failed", err instanceof Error ? err.message : "Unable to send parent email.");
    },
  });

  const editMutation = useMutation({
    mutationFn: async (payload: { userId: string; parent_name: string; parent_email: string }) => {
      return updateUser(payload.userId, {
        parent_name: payload.parent_name,
        parent_email: payload.parent_email,
      });
    },
    onSuccess: (_, target) => {
      showToast("success", "Parent Updated", "Parent contact details have been updated.");
      queryClient.invalidateQueries({ queryKey: ["adminUsers"] });
      setEditModal(false);
    },
    onError: (err: unknown) => {
      showToast("error", "Update Failed", err instanceof Error ? err.message : "Unable to update parent details.");
    },
  });

  const columns = [
    { key: "name", header: "Name" },
    { key: "email", header: "Email" },
    ...(!isInstitutionAdmin ? [{ key: "institution", header: "Institution" }] : []),
    { key: "workshop", header: "Workshop" },
    {
      key: "status",
      header: "Status",
      render: (r: StudentRow) => (
        <VBadge variant={r.status === "Active" ? "success" : r.status === "Completed" ? "default" : "warning"}>
          {r.status}
        </VBadge>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (r: StudentRow) => (
        <div className="flex gap-1">
          <button
            onClick={() => {
              setSelected(r);
              setViewModal(true);
            }}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors"
          >
            <Eye className="h-4 w-4" />
          </button>
          {isInstitutionAdmin && (
            <>
              <button
                onClick={() => {
                  setSelected(r);
                  setEmailSubject(`Progress Report - ${r.name}`);
                  setEmailBody(
                    `Dear Parent,\n\nThis is an update regarding ${r.name}'s progress in the ${r.workshop} workshop.\n\nBest regards,\nInstitution Administration`
                  );
                  setEmailModal(true);
                }}
                className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-info transition-colors"
                title="Email Parent"
              >
                <Mail className="h-4 w-4" />
              </button>
              <button
                onClick={() => {
                  setSelected(r);
                  setEditParentName(r.parentName);
                  setEditParentEmail(r.parentEmail);
                  setEditModal(true);
                }}
                className="rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-primary transition-colors"
                title="Edit Parent Details"
              >
                <Eye className="h-4 w-4" />
              </button>
              <button
                onClick={() => {
                  setRemovalTarget(r);
                  setRemovalConfirm(true);
                }}
                className="rounded-lg p-1.5 text-muted-foreground hover:bg-warning/10 hover:text-warning transition-colors"
                title="Send Removal Request"
              >
                <Send className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      ),
    },
  ];

  const emptyText =
    usersQuery.isLoading || institutionsQuery.isLoading || workshopsQuery.isLoading || enrollmentsQuery.isLoading || parentContactsQuery.isLoading
      ? "Loading students..."
      : usersQuery.isError
        ? "Unable to load students."
        : "No students found.";

  return (
    <DashboardLayout title="Student Management">
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search students..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="vidya-input pl-10"
          />
        </div>
        <div className="flex gap-2">
          {["All", "Active", "Inactive", "Completed"].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${statusFilter === s ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-accent"}`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <VTable columns={columns} data={filtered} emptyText={emptyText} />
      </div>

      {/* View Modal */}
      <VModal isOpen={viewModal} onClose={() => setViewModal(false)} title="Student Details">
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-full vidya-gradient flex items-center justify-center text-primary-foreground font-bold text-lg">
                {selected.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .slice(0, 2)}
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground">{selected.name}</h3>
                <p className="text-sm text-muted-foreground">{selected.email}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Institution</p>
                <p className="text-sm font-medium text-foreground">{selected.institution}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Workshop</p>
                <p className="text-sm font-medium text-foreground">{selected.workshop}</p>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Status</p>
                <VBadge variant={selected.status === "Active" ? "success" : "warning"}>{selected.status}</VBadge>
              </div>
              <div className="rounded-xl bg-muted p-3">
                <p className="text-xs text-muted-foreground">Parent Email</p>
                <p className="text-sm text-foreground">{selected.parentEmail || "No parent email on file"}</p>
              </div>
            </div>
            {isInstitutionAdmin && (
              <VButton
                className="w-full"
                onClick={() => {
                  setViewModal(false);
                  setEmailSubject(`Progress Report - ${selected.name}`);
                  setEmailBody(
                    `Dear Parent,\n\nThis is an update regarding ${selected.name}'s progress.\n\nBest regards,\nInstitution Administration`
                  );
                  setEmailModal(true);
                }}
              >
                <Mail className="h-4 w-4" /> Email Parent
              </VButton>
            )}
          </div>
        )}
      </VModal>

      {/* Custom Email Modal */}
      <VModal isOpen={emailModal} onClose={() => setEmailModal(false)} title={`Email to ${selected?.parentEmail || "Parent/Guardian"}`}>
        <div className="space-y-4">
          <VInput label="To" value={selected?.parentEmail || "No parent email on file"} disabled />
          <VInput
            label="Subject"
            value={emailSubject}
            onChange={(e) => setEmailSubject(e.target.value)}
            placeholder="Email subject"
          />
          <div className="space-y-1.5">
            <label className="vidya-label">Message</label>
            <textarea
              value={emailBody}
              onChange={(e) => setEmailBody(e.target.value)}
              rows={6}
              className="vidya-input resize-none"
              placeholder="Write your message..."
            />
          </div>
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setEmailModal(false)}>
              Cancel
            </VButton>
            <VButton
              onClick={() => {
                if (!selected) return;
                parentEmailMutation.mutate({
                  studentId: selected.id,
                  parentEmail: selected.parentEmail,
                  subject: emailSubject,
                  body: emailBody,
                });
              }}
              isLoading={parentEmailMutation.isPending}
              disabled={!selected?.parentEmail || !emailSubject || !emailBody || parentEmailMutation.isPending}
            >
              <Mail className="h-4 w-4" /> Send Email
            </VButton>
          </div>
        </div>
      </VModal>

      {/* Removal Request Confirmation */}
      <VModal isOpen={removalConfirm} onClose={() => setRemovalConfirm(false)} title="Send Removal Request">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            This will send a removal request to the Platform Admin for{" "}
            <span className="font-semibold text-foreground">{removalTarget?.name}</span>. The student will NOT be removed
            immediately.
          </p>
          <div className="rounded-xl bg-warning/10 p-3">
            <p className="text-xs text-warning font-medium">
              The Platform Admin must approve this request before the student is removed.
            </p>
          </div>
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setRemovalConfirm(false)}>
              Cancel
            </VButton>
            <VButton
              onClick={() => {
                const target = removalTarget;
                setRemovalConfirm(false);
                if (!target) return;
                removalMutation.mutate(target);
              }}
              isLoading={removalMutation.isPending}
            >
              <Send className="h-4 w-4" /> Send Request
            </VButton>
          </div>
        </div>
      </VModal>

      {/* Edit Parent Details Modal */}
      <VModal isOpen={editModal} onClose={() => setEditModal(false)} title="Edit Parent Details">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Update parent/guardian contact information for <span className="font-semibold text-foreground">{selected?.name}</span>.
          </p>
          <VInput
            label="Parent/Guardian Name"
            value={editParentName}
            onChange={(e) => setEditParentName(e.target.value)}
            placeholder="Enter parent name"
          />
          <VInput
            label="Parent Email"
            type="email"
            value={editParentEmail}
            onChange={(e) => setEditParentEmail(e.target.value)}
            placeholder="Enter parent email"
          />
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setEditModal(false)}>
              Cancel
            </VButton>
            <VButton
              onClick={() => {
                if (!selected) return;
                editMutation.mutate({
                  userId: selected.id,
                  parent_name: editParentName,
                  parent_email: editParentEmail,
                });
              }}
              isLoading={editMutation.isPending}
              disabled={!editParentName || !editParentEmail || editMutation.isPending}
            >
              Save Changes
            </VButton>
          </div>
        </div>
      </VModal>
    </DashboardLayout>
  );
};

export default StudentManagement;




