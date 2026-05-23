import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Download, Award, Send, Plus, Trophy, Sparkles, CheckCircle2, Eye, FileText } from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import VTable from '@/components/ui-custom/VTable';
import VButton from '@/components/ui-custom/VButton';
import VBadge from '@/components/ui-custom/VBadge';
import VCard from '@/components/ui-custom/VCard';
import VModal from '@/components/ui-custom/VModal';
import VSelect from '@/components/ui-custom/VSelect';
import { useVToast } from '@/components/ui-custom/VToast';
import {
  fetchCertificateDownload,
  fetchCertificates,
  fetchWorkshops,
  fetchStudents,
  fetchEnrollments,
  generateCertificate,
  recommendCertificate,
} from '@/services/api';
import { useRole } from '@/hooks/useRole';
import { useAuth } from '@/hooks/useAuth';
import { useEffect, useState } from 'react';
import type { Workshop } from '@/mock/mockData';

type CertificateRow = Awaited<ReturnType<typeof fetchCertificates>>[number];

interface WorkshopStudent {
  studentId: string;
  studentName: string;
  enrolledAt: string;
  status: string;
}

const adminColumns = (
  onView: (certificate: CertificateRow) => void,
  onDownload: (certificate: CertificateRow) => void, 
  downloadingId: string | null
) => [
  { key: 'certificateId', header: 'Certificate ID' },
  { key: 'studentName', header: 'Student' },
  { key: 'workshop', header: 'Workshop' },
  { key: 'completionDate', header: 'Completed' },
  {
    key: 'status',
    header: 'Status',
    render: (r: CertificateRow) => <VBadge variant={r.status === 'Issued' ? 'success' : 'warning'}>{r.status}</VBadge>,
  },
  {
    key: 'actions',
    header: 'Actions',
    render: (r: CertificateRow) => (
      <div className="flex gap-1">
        <VButton variant="ghost" size="sm" onClick={() => onView(r)} title="View">
          <Eye className="h-3.5 w-3.5" />
        </VButton>
        {r.status === 'Issued' && (
          <VButton variant="secondary" size="sm" onClick={() => onDownload(r)} disabled={downloadingId === r.id}>
            <Download className="h-3.5 w-3.5" />
          </VButton>
        )}
      </div>
    ),
  },
];

const educatorColumns = (
  onRecommend: (certificate: CertificateRow) => void,
  onDownload: (certificate: CertificateRow) => void,
  downloadingId: string | null
) => [
  { key: 'certificateId', header: 'Certificate ID' },
  { key: 'studentName', header: 'Student' },
  { key: 'workshop', header: 'Workshop' },
  {
    key: 'status',
    header: 'Status',
    render: (r: CertificateRow) => <VBadge variant={r.status === 'Issued' ? 'success' : 'warning'}>{r.status}</VBadge>,
  },
  {
    key: 'actions',
    header: 'Actions',
    render: (r: CertificateRow) =>
      r.status === 'Pending' ? (
        <VButton variant="primary" size="sm" onClick={() => onRecommend(r)}>
          <Send className="h-3.5 w-3.5" /> Recommend
        </VButton>
      ) : (
        <VButton variant="secondary" size="sm" onClick={() => onDownload(r)} disabled={downloadingId === r.id}>
          <Download className="h-3.5 w-3.5" /> Download
        </VButton>
      ),
  },
];

const StudentCertificates = ({
  certificates,
  onDownload,
}: {
  certificates: CertificateRow[];
  onDownload: (certificate: CertificateRow) => void;
}) => {
  const myCerts = certificates.filter((c) => c.status === 'Issued');

  if (myCerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/10">
          <Trophy className="h-10 w-10 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-foreground mb-3">Your Trophy Case Awaits!</h2>
        <p className="text-muted-foreground max-w-md mb-6 leading-relaxed">
          You haven't earned any certificates yet - complete a workshop and ace the assessments to earn your first certificate.
        </p>
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <VButton onClick={() => (window.location.href = '/workshops')}>
            <Sparkles className="h-4 w-4" /> Browse Workshops
          </VButton>
          <VButton variant="secondary" onClick={() => (window.location.href = '/assessments')}>
            View Assessments
          </VButton>
        </div>
        <div className="mt-10 vidya-card p-6 max-w-sm w-full">
          <p className="text-sm italic text-muted-foreground leading-relaxed">
            "The beautiful thing about learning is that nobody can take it away from you."
          </p>
          <p className="text-xs text-primary font-semibold mt-3">- B.B. King</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {myCerts.map((cert) => (
          <VCard key={cert.id} hover className="p-5 relative overflow-hidden">
            <div className="absolute top-0 right-0 h-24 w-24 bg-primary/5 rounded-bl-[60px]" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                  <Award className="h-5 w-5 text-primary" />
                </div>
                <VBadge variant="success">
                  <CheckCircle2 className="h-3 w-3 mr-1" /> Verified
                </VBadge>
              </div>
              <h3 className="text-base font-bold text-foreground mb-1">{cert.workshop}</h3>
              <p className="text-xs text-muted-foreground mb-1">ID: {cert.certificateId}</p>
              <p className="text-xs text-muted-foreground mb-4">Completed: {cert.completionDate}</p>
              <VButton variant="secondary" size="sm" className="w-full" onClick={() => onDownload(cert)}>
                <Download className="h-3.5 w-3.5" /> Download Certificate
              </VButton>
            </div>
          </VCard>
        ))}
      </div>
    </div>
  );
};

const GenerateCertificateModal = ({
  isOpen,
  onClose,
  onIssue,
}: {
  isOpen: boolean;
  onClose: () => void;
  onIssue: (payload: { workshopId: string; studentId: string }) => Promise<void>;
}) => {
  const [workshopId, setWorkshopId] = useState('');
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [viewMode, setViewMode] = useState<'select' | 'students'>('select');
  const { showToast } = useVToast();

  useEffect(() => {
    if (isOpen) {
      setWorkshopId('');
      setSelectedStudentId('');
      setSubmitting(false);
      setViewMode('select');
    }
  }, [isOpen]);

  const { data: workshops = [] } = useQuery({ queryKey: ['workshops'], queryFn: fetchWorkshops, enabled: isOpen });
  const { data: students = [] } = useQuery({ queryKey: ['students'], queryFn: fetchStudents, enabled: isOpen });
  const { data: certificates = [] } = useQuery({ queryKey: ['certificates'], queryFn: () => fetchCertificates({ asStaff: true }), enabled: isOpen });
  const { data: enrollmentsData } = useQuery({ 
    queryKey: ['enrollments-all'], 
    queryFn: async () => {
      // Fetch enrollments for all students - we'll need to get them per student or get all
      // For now, let's just get all students' enrollments
      const allEnrollments: { studentId: string; workshopId: string; status: string }[] = [];
      for (const student of students) {
        try {
          const page = await fetchEnrollments(student.id);
          allEnrollments.push(...page.items.map(e => ({ 
            studentId: student.id, 
            workshopId: e.workshop_id, 
            status: e.status 
          })));
        } catch {
          // Skip if fails
        }
      }
      return allEnrollments;
    }, 
    enabled: isOpen && students.length > 0 
  });

  const completedWorkshops = workshops; // Show all workshops for certificate generation
  
  // Get students enrolled in the selected workshop
  const selectedWorkshop = workshops.find(w => w.id === workshopId);
  const enrolledStudents = students.filter(s => {
    // Filter to only students enrolled in this workshop
    if (!workshopId) return true;
    return enrollmentsData?.some(e => e.studentId === s.id && e.workshopId === workshopId) ?? true;
  });

  // Get students who already have certificates for this workshop
  const certifiedStudentIds = new Set(
    certificates
      .filter(c => c.workshopId === workshopId && c.status === 'Issued')
      .map(c => c.studentId)
  );

  // Filter out students who already have certificates
  const eligibleStudents = enrolledStudents.filter(s => !certifiedStudentIds.has(s.id));

  const handleViewStudents = () => {
    if (!workshopId) {
      showToast('warning', 'Select Workshop', 'Please select a workshop first.');
      return;
    }
    setViewMode('students');
  };

  const handleIssueCertificate = async () => {
    if (!workshopId || !selectedStudentId) return;
    setSubmitting(true);
    try {
      await onIssue({ workshopId, studentId: selectedStudentId });
    } finally {
      setSubmitting(false);
    }
  };

  if (viewMode === 'students') {
    return (
      <VModal isOpen={isOpen} onClose={onClose} title={`Students - ${selectedWorkshop?.name || 'Workshop'}`}>
        <div className="space-y-4">
          {eligibleStudents.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Trophy className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No eligible students to generate certificates for.</p>
              <p className="text-sm mt-1">All students either already have certificates or are not enrolled.</p>
            </div>
          ) : (
            <div className="max-h-96 overflow-y-auto space-y-2">
              {eligibleStudents.map(student => (
                <div 
                  key={student.id}
                  className={`p-3 border rounded-lg flex items-center justify-between cursor-pointer transition-colors ${
                    selectedStudentId === student.id 
                      ? 'border-primary bg-primary/5' 
                      : 'hover:bg-muted/50'
                  }`}
                  onClick={() => setSelectedStudentId(student.id)}
                >
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-sm font-medium text-primary">
                        {student.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{student.name}</p>
                      <p className="text-xs text-muted-foreground">ID: {student.id.slice(0, 8)}...</p>
                    </div>
                  </div>
                  {selectedStudentId === student.id && (
                    <VButton size="sm" onClick={(e) => {
                      e.stopPropagation();
                      handleIssueCertificate();
                    }} disabled={submitting}>
                      <Award className="h-4 w-4" /> Generate
                    </VButton>
                  )}
                </div>
              ))}
            </div>
          )}
          <div className="flex justify-between pt-2">
            <VButton variant="ghost" onClick={() => setViewMode('select')}>
              Back to Workshops
            </VButton>
            {selectedStudentId && (
              <VButton onClick={handleIssueCertificate} disabled={submitting}>
                <Award className="h-4 w-4" /> Issue Certificate
              </VButton>
            )}
          </div>
        </div>
      </VModal>
    );
  }

  return (
    <VModal isOpen={isOpen} onClose={onClose} title="Generate Certificate" className="max-w-2xl">
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Select a completed workshop to view enrolled students and generate certificates.
        </p>
        
        <VSelect
          label="Workshop"
          value={workshopId}
          onChange={(e) => { setWorkshopId(e.target.value); setSelectedStudentId(''); }}
          options={[
            { value: '', label: 'Select completed workshop' },
            ...completedWorkshops.map((w) => ({ value: w.id, label: `${w.name} (${w.institution})` })),
          ]}
        />

        {workshopId && (
          <div className="bg-muted/30 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="font-medium">{selectedWorkshop?.name}</p>
                <p className="text-sm text-muted-foreground">{selectedWorkshop?.institution}</p>
              </div>
              <VButton variant="secondary" size="sm" onClick={handleViewStudents}>
                <Eye className="h-4 w-4 mr-1" /> View Students ({eligibleStudents.length})
              </VButton>
            </div>
            <div className="text-xs text-muted-foreground mt-2">
              {eligibleStudents.length} eligible student(s) to generate certificates for
            </div>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <VButton variant="ghost" onClick={onClose}>
            Cancel
          </VButton>
        </div>
      </div>
    </VModal>
  );
};

const Certificates = () => {
  const { showToast } = useVToast();
  const queryClient = useQueryClient();

  const role = useRole();
  const { user } = useAuth();
  const [showGenerate, setShowGenerate] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [viewingCertificate, setViewingCertificate] = useState<CertificateRow | null>(null);

  const { data: certificates = [] } = useQuery({
    queryKey: ['certificates', user?.id, role],
    queryFn: () => {
      if (!user) return [];
      if (role === 'student') {
        return fetchCertificates({ studentId: user.id });
      }
      return fetchCertificates({ asStaff: true });
    },
    enabled: Boolean(user),
  });

  const downloadMutation = useMutation({ mutationFn: fetchCertificateDownload });
  const recommendMutation = useMutation({
    mutationFn: recommendCertificate,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['certificates'] });
      showToast('success', 'Recommendation Sent', 'Certificate recommendation dispatched to institution admins.');
    },
    onError: (err: unknown) => {
      showToast('error', 'Recommend Failed', err instanceof Error ? err.message : 'Unable to send recommendation.');
    },
  });

  const handleIssue = async (payload: { workshopId: string; studentId: string }) => {
    try {
      await generateCertificate({ workshopId: payload.workshopId, studentId: payload.studentId });
      await queryClient.invalidateQueries({ queryKey: ['certificates'] });
      showToast('success', 'Certificate Issued', 'Certificate generation started.');
      setShowGenerate(false);
    } catch (err: unknown) {
      showToast('error', 'Failed to Issue Certificate', err instanceof Error ? err.message : 'Unable to issue certificate.');
    }
  };

  const handleDownload = async (certificate: CertificateRow) => {
    try {
      setDownloadingId(certificate.id);
      
      // First try to use the pre-computed downloadUrl if available
      if (certificate.downloadUrl) {
        // Construct full URL - if it's a relative path, prepend the API base
        let fullUrl = certificate.downloadUrl;
        if (!fullUrl.startsWith('http')) {
          const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
          fullUrl = `${apiBase.replace(/\/+$/, '')}/${fullUrl.replace(/^\/+/, '')}`;
        }
        window.open(fullUrl, '_blank', 'noopener,noreferrer');
        setDownloadingId(null);
        return;
      }
      
      // Fall back to API call
      const response = await downloadMutation.mutateAsync(certificate.id);
      if (response.download_url) {
        window.open(response.download_url, '_blank', 'noopener,noreferrer');
      } else {
        showToast('error', 'Download Failed', 'No download URL returned.');
      }
    } catch (err: unknown) {
      console.error('Download error:', err);
      showToast('error', 'Download Failed', err instanceof Error ? err.message : 'Unable to download certificate.');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleRecommend = (certificate: CertificateRow) => {
    if (!certificate.studentId || !certificate.workshopId) {
      showToast('error', 'Recommend Failed', 'Student/workshop mapping missing for this certificate.');
      return;
    }
    recommendMutation.mutate({
      studentId: certificate.studentId,
      workshopId: certificate.workshopId,
      note: `Recommended from educator certificates panel (${certificate.id}).`,
    });
  };

  const handleView = (certificate: CertificateRow) => {
    setViewingCertificate(certificate);
  };

  if (role === 'student') {
    return (
      <DashboardLayout title="My Certificates">
        <StudentCertificates certificates={certificates} onDownload={handleDownload} />
      </DashboardLayout>
    );
  }

  if (role === 'educator') {
    return (
      <DashboardLayout title="Certificates">
        <p className="text-sm text-muted-foreground mb-4">
          Review and recommend students for certification. Institutions will issue the final certificate.
        </p>
        <VTable columns={educatorColumns(handleRecommend, handleDownload, downloadingId)} data={certificates} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Certificates">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <p className="text-sm text-muted-foreground">Manage and issue certificates for completed workshops.</p>
        {role === 'institution_admin' && (
          <VButton onClick={() => setShowGenerate(true)}>
            <Plus className="h-4 w-4" /> Generate Certificate
          </VButton>
        )}
        {role === 'admin' && (
          <VButton onClick={() => setShowGenerate(true)}>
            <Plus className="h-4 w-4" /> Generate Certificate
          </VButton>
        )}
      </div>
      <VTable columns={adminColumns(handleView, handleDownload, downloadingId)} data={certificates} />
      <GenerateCertificateModal isOpen={showGenerate} onClose={() => setShowGenerate(false)} onIssue={handleIssue} />
      {viewingCertificate && (
        <ViewCertificateModal 
          certificate={viewingCertificate} 
          onClose={() => setViewingCertificate(null)} 
          onDownload={handleDownload}
        />
      )}
    </DashboardLayout>
  );
};

const ViewCertificateModal = ({
  certificate,
  onClose,
  onDownload,
}: {
  certificate: CertificateRow;
  onClose: () => void;
  onDownload: (certificate: CertificateRow) => void;
}) => {
  const { showToast } = useVToast();
  const [downloading, setDownloading] = useState(false);

  const handleDownloadClick = async () => {
    setDownloading(true);
    try {
      await onDownload(certificate);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <VModal isOpen={true} onClose={onClose} title="Certificate Details" className="max-w-2xl">
      <div className="space-y-6">
        {/* Certificate Preview Card */}
        <div className="bg-gradient-to-br from-primary/5 to-primary/10 rounded-xl p-8 border border-primary/20">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-4">
              <Award className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">Certificate of Completion</h2>
            <p className="text-muted-foreground mb-6">This is to certify that</p>
            <h3 className="text-xl font-semibold text-foreground mb-4">{certificate.studentName}</h3>
            <p className="text-muted-foreground mb-2">has successfully completed the workshop</p>
            <h4 className="text-lg font-medium text-foreground mb-4">{certificate.workshop}</h4>
            <p className="text-sm text-muted-foreground">Completed on: {certificate.completionDate}</p>
          </div>
        </div>

        {/* Certificate Info */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-muted/30 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">Certificate ID</p>
            <p className="font-mono text-sm">{certificate.certificateId}</p>
          </div>
          <div className="p-4 bg-muted/30 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">Status</p>
            <VBadge variant={certificate.status === 'Issued' ? 'success' : 'warning'}>
              {certificate.status}
            </VBadge>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-2">
          <VButton variant="ghost" onClick={onClose}>
            Close
          </VButton>
          {certificate.status === 'Issued' && (
            <VButton onClick={handleDownloadClick} disabled={downloading}>
              <Download className="h-4 w-4 mr-2" />
              {downloading ? 'Downloading...' : 'Download Certificate'}
            </VButton>
          )}
        </div>
      </div>
    </VModal>
  );
};

export default Certificates;
