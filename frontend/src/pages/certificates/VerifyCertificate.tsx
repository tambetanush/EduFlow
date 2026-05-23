import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, Search, CheckCircle, XCircle, ArrowLeft, LogIn } from 'lucide-react';
import VCard from '@/components/ui-custom/VCard';
import VInput from '@/components/ui-custom/VInput';
import VButton from '@/components/ui-custom/VButton';
import VBadge from '@/components/ui-custom/VBadge';
import { verifyCertificate } from '@/services/api';

const VerifyCertificate = () => {
  const navigate = useNavigate();
  const [certId, setCertId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [searched, setSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleVerify = async () => {
    const code = certId.trim();
    if (!code) return;
    setIsLoading(true);
    try {
      const found = await verifyCertificate(code);
      setResult(found);
    } catch {
      setResult(null);
    } finally {
      setSearched(true);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </button>
          <button
            onClick={() => navigate('/login')}
            className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
          >
            <LogIn className="h-4 w-4" />
            Sign In
          </button>
        </div>

        <div className="text-center mb-8">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary">
            <GraduationCap className="h-7 w-7 text-primary-foreground" />
          </div>
          <h1 className="text-2xl font-bold text-foreground">Verify Certificate</h1>
          <p className="mt-1 text-sm text-muted-foreground">Enter a certificate ID to verify its authenticity</p>
        </div>

        <VCard className="p-6">
          <div className="flex gap-3 mb-6">
            <VInput
              id="cert-id"
              placeholder="e.g. VSETU-2026-001"
              value={certId}
              onChange={(e) => setCertId(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleVerify()}
              className="flex-1"
            />
            <VButton onClick={handleVerify} isLoading={isLoading}>
              <Search className="h-4 w-4" /> Verify
            </VButton>
          </div>

          {searched && result && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-success">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">Certificate Verified</span>
              </div>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-muted-foreground">Student: </span>
                  <span className="text-foreground font-medium">{result.student_name || result.student_id}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Workshop: </span>
                  <span className="text-foreground font-medium">{result.workshop_title || result.workshop_id}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Completed: </span>
                  <span className="text-foreground font-medium">{result.issue_date || ''}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Status: </span>
                  <VBadge variant="success">Issued</VBadge>
                </div>
              </div>
            </div>
          )}

          {searched && !result && (
            <div className="flex items-center gap-2 text-destructive">
              <XCircle className="h-5 w-5" />
              <span className="font-medium">Certificate not found</span>
            </div>
          )}
        </VCard>
      </div>
    </div>
  );
};

export default VerifyCertificate;
