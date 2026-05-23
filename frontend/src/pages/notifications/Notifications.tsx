import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Bell, CheckCircle, AlertTriangle, Info, Check, Trash2, Mail } from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import VCard from '@/components/ui-custom/VCard';
import VBadge from '@/components/ui-custom/VBadge';
import VButton from '@/components/ui-custom/VButton';
import VModal from '@/components/ui-custom/VModal';
import VInput from '@/components/ui-custom/VInput';
import { useVToast } from '@/components/ui-custom/VToast';
import { useRole } from '@/hooks/useRole';
import { useAuth } from '@/hooks/useAuth';
import { deleteNotification, fetchAllUsers, fetchMyNotifications, markAllNotificationsRead, markNotificationRead, sendParentEmailMessage, fetchParentContactDirectory } from '@/services/api';
import type { Notification } from '@/mock/mockData';

const iconMap = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
};

const Notifications = () => {
  const { showToast } = useVToast();
  const { user } = useAuth();
  const role = useRole();
  const queryClient = useQueryClient();

  const { data: fetched = [] } = useQuery({
    queryKey: ['notifications', user?.id],
    queryFn: () => (user ? fetchMyNotifications() : []),
    enabled: Boolean(user),
    refetchInterval: 60_000,
  });

  const [filter, setFilter] = useState('All');
  const [emailModal, setEmailModal] = useState(false);
  const [emailTo, setEmailTo] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications', user?.id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteNotification,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['notifications', user?.id] });
    },
  });
  const sendParentEmailMutation = useMutation({
    mutationFn: sendParentEmailMessage,
  });

  const isInstitution = role === 'institution_admin';
  const parentDirectoryQuery = useQuery({
    queryKey: ['parentContactDirectory', user?.id],
    queryFn: async () => {
      const users = await fetchAllUsers({ max: 1000 });
      const studentIds = users
        .filter((item) => item.role === 'student')
        .map((item) => item.id);
      return fetchParentContactDirectory(studentIds);
    },
    enabled: isInstitution && Boolean(user?.id),
  });

  const all = fetched;
  const filtered =
    filter === 'All'
      ? all
      : filter === 'Unread'
        ? all.filter((n) => !n.read)
        : all.filter((n) => n.read);

  const markRead = (id: string) => {
    markReadMutation.mutate(id, {
      onSuccess: () => showToast('success', 'Marked as read'),
      onError: (err: unknown) =>
        showToast('destructive', 'Failed', err instanceof Error ? err.message : 'Unable to mark as read.'),
    });
  };

  const markAllRead = () => {
    markAllNotificationsRead()
      .then(async () => {
        await queryClient.invalidateQueries({ queryKey: ['notifications', user?.id] });
        showToast('success', 'All notifications marked as read');
      })
      .catch((err: unknown) => {
        showToast('destructive', 'Failed', err instanceof Error ? err.message : 'Unable to mark notifications.');
      });
  };

  const deleteNotif = (id: string) => {
    deleteMutation.mutate(id, {
      onSuccess: () => showToast('info', 'Notification removed'),
      onError: (err: unknown) =>
        showToast('destructive', 'Failed', err instanceof Error ? err.message : 'Unable to delete notification.'),
    });
  };

  const unreadCount = all.filter((n) => !n.read).length;

  return (
    <DashboardLayout title="Notifications">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
        <div className="flex gap-2">
          {['All', 'Unread', 'Read'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                filter === f
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-accent'
              }`}
            >
              {f} {f === 'Unread' && unreadCount > 0 && <span className="ml-1 text-xs">({unreadCount})</span>}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          {isInstitution && (
            <VButton
              variant="secondary"
              size="sm"
              onClick={() => {
                setEmailTo('');
                setEmailSubject('');
                setEmailBody('');
                setEmailModal(true);
              }}
            >
              <Mail className="h-3.5 w-3.5" /> Email Parents
            </VButton>
          )}
          {unreadCount > 0 && (
            <VButton variant="secondary" size="sm" onClick={markAllRead}>
              <Check className="h-3.5 w-3.5" /> Mark all read
            </VButton>
          )}
        </div>
      </div>

      <div className="max-w-3xl space-y-3">
        {filtered.length === 0 && (
          <div className="text-center py-16">
            <Bell className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
            <p className="text-muted-foreground">No notifications</p>
          </div>
        )}
        {filtered.map((n) => {
          const Icon = iconMap[n.type];
          return (
            <VCard
              key={n.id}
              className={`flex items-start gap-4 cursor-pointer transition-all ${
                !n.read ? 'border-l-4 border-l-primary' : ''
              } hover:shadow-md`}
              onClick={() => {
                if (!n.read) markRead(n.id);
                showToast(n.type as any, n.title, n.message);
              }}
            >
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
                  n.type === 'success'
                    ? 'bg-success/10'
                    : n.type === 'warning'
                      ? 'bg-warning/10'
                      : 'bg-primary/10'
                }`}
              >
                <Icon
                  className={`h-5 w-5 ${
                    n.type === 'success'
                      ? 'text-success'
                      : n.type === 'warning'
                        ? 'text-warning'
                        : 'text-primary'
                  }`}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className={`font-medium ${n.read ? 'text-muted-foreground' : 'text-foreground'}`}>{n.title}</p>
                  <div className="flex items-center gap-1">
                    {!n.read && <VBadge variant="default">New</VBadge>}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNotif(n.id);
                      }}
                      className="rounded-lg p-1 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-1">{n.message}</p>
                <p className="text-xs text-muted-foreground mt-2">{n.date}</p>
              </div>
            </VCard>
          );
        })}
      </div>

      <VModal isOpen={emailModal} onClose={() => setEmailModal(false)} title="Send Email to Parents">
        <div className="space-y-4">
          <VInput
            label="Recipient Email(s)"
            value={emailTo}
            onChange={(e) => setEmailTo(e.target.value)}
            placeholder="parent1@mail.com, parent2@mail.com"
          />
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
              placeholder="Write your email message here..."
            />
          </div>
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setEmailModal(false)}>
              Cancel
            </VButton>
            <VButton
              onClick={async () => {
                try {
                  const parsedEmails = emailTo
                    .split(',')
                    .map((item) => item.trim().toLowerCase())
                    .filter(Boolean);
                  if (parsedEmails.length === 0) {
                    showToast('warning', 'Recipients required', 'Enter at least one recipient email.');
                    return;
                  }
                  const directory = parentDirectoryQuery.data?.items ?? [];
                  const recipientStudentIds = Array.from(
                    new Set(
                      directory
                        .filter((item) => item.parent_email && parsedEmails.includes(item.parent_email.toLowerCase()))
                        .map((item) => item.student_id)
                        .filter(Boolean)
                    )
                  );
                  if (recipientStudentIds.length === 0) {
                    showToast('warning', 'No parent matches', 'None of the emails matched parent contacts.');
                    return;
                  }
                  const response = await sendParentEmailMutation.mutateAsync({
                    studentIds: recipientStudentIds,
                    subject: emailSubject,
                    body: emailBody,
                  });
                  setEmailModal(false);
                  showToast('success', 'Email Sent', `Accepted: ${response.accepted}, Failed: ${response.failed}`);
                } catch (err: unknown) {
                  showToast('destructive', 'Send Failed', err instanceof Error ? err.message : 'Unable to dispatch parent email.');
                }
              }}
              disabled={!emailSubject || !emailBody || parentDirectoryQuery.isLoading}
            >
              <Mail className="h-4 w-4" /> Send Email
            </VButton>
          </div>
        </div>
      </VModal>
    </DashboardLayout>
  );
};

export default Notifications;

