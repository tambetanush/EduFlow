import { useState, useEffect, useCallback, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import { AlertTriangle, Clock, ChevronLeft, ChevronRight, Flag, Send, Shield, Maximize2 } from "lucide-react";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VModal from "@/components/ui-custom/VModal";
import { useVToast } from "@/components/ui-custom/VToast";
import {
  startAssessmentAttempt,
  saveAssessmentAnswers,
  submitAssessmentAttempt,
  type StartAttemptResponse,
} from "@/services/api";

const TOTAL_TIME = 600; // 10 minutes
const MAX_WARNINGS = 3;

const AssessmentAttempt = () => {
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const { assessmentId } = useParams<{ assessmentId: string }>();

  const [attemptData, setAttemptData] = useState<StartAttemptResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, string[]>>({});
  const [flagged, setFlagged] = useState<Set<string>>(new Set());
  const [currentQ, setCurrentQ] = useState(0);
  const [timeLeft, setTimeLeft] = useState(TOTAL_TIME);
  const [started, setStarted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [warnings, setWarnings] = useState(0);
  const [warningModal, setWarningModal] = useState(false);
  const [warningMessage, setWarningMessage] = useState("");
  const [rulesModal, setRulesModal] = useState(true);
  const [submitModal, setSubmitModal] = useState(false);
  const [autoSubmitting, setAutoSubmitting] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [fullscreenRequired, setFullscreenRequired] = useState(false);
  const warningsRef = useRef(0); // Use ref to avoid stale closure
  const deadlineRef = useRef<number | null>(null);

  // Sync ref with state for display
  useEffect(() => {
    warningsRef.current = warnings;
  }, [warnings]);

  useEffect(() => {
    if (!assessmentId) return;
    const storedDeadline = sessionStorage.getItem(`assessment_deadline_${assessmentId}`);
    if (!storedDeadline) return;
    const parsedDeadline = Number(storedDeadline);
    if (Number.isNaN(parsedDeadline) || parsedDeadline <= 0) return;

    let cancelled = false;
    deadlineRef.current = parsedDeadline;
    setTimeLeft(Math.max(0, Math.round((parsedDeadline - Date.now()) / 1000)));

    const restoreAttempt = async () => {
      try {
        const data = await startAssessmentAttempt(assessmentId);
        if (cancelled) return;
        setAttemptData(data);
        setStarted(true);
        setRulesModal(false);
        setFullscreenRequired(true);
        document.documentElement.requestFullscreen().catch(() => {
          // Fullscreen denied - warning handling will enforce it.
        });
      } catch {
        if (cancelled) return;
        sessionStorage.removeItem(`assessment_deadline_${assessmentId}`);
      }
    };

    void restoreAttempt();

    return () => {
      cancelled = true;
    };
  }, [assessmentId]);

  // Track fullscreen state
  useEffect(() => {
    if (!started) return;
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    setIsFullscreen(!!document.fullscreenElement);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, [started]);

  const startMutation = useMutation({
    mutationFn: async () => {
      if (!assessmentId) throw new Error("Assessment ID is missing.");
      return startAssessmentAttempt(assessmentId);
    },
    onSuccess: (data) => {
      setAttemptData(data);
      setStarted(true);
      setRulesModal(false);
      setFullscreenRequired(true);
      const existingDeadline = assessmentId ? sessionStorage.getItem(`assessment_deadline_${assessmentId}`) : null;
      const parsedExisting = Number(existingDeadline);
      const deadline = Number.isFinite(parsedExisting) && parsedExisting > Date.now()
        ? parsedExisting
        : Date.now() + TOTAL_TIME * 1000;
      deadlineRef.current = deadline;
      if (assessmentId) {
        sessionStorage.setItem(`assessment_deadline_${assessmentId}`, String(deadline));
      }
      setTimeLeft(Math.max(0, Math.round((deadline - Date.now()) / 1000)));
      showToast("info", "Assessment Started", "Good luck!");
      // Request fullscreen to prevent tab switching
      document.documentElement.requestFullscreen().catch(() => {
        // Fullscreen denied - will show warning modal
      });
    },
    onError: (error: unknown) => {
      showToast("error", "Unable to start assessment", error instanceof Error ? error.message : "Please try again.");
    },
  });

  const handleSubmit = useCallback(async () => {
    if (!assessmentId || !attemptData || isSubmitting) return;

    try {
      setIsSubmitting(true);
      const payload = Object.entries(answers).map(([questionId, selectedOptionIds]) => ({
        questionId,
        selectedOptionIds,
      }));
      console.log("Submitting assessment answers", {
        assessmentId,
        submissionId: attemptData.submission_id,
        answers: payload,
      });

      await saveAssessmentAnswers(attemptData.submission_id, payload);
      const result = await submitAssessmentAttempt(assessmentId, attemptData.submission_id);
      if (assessmentId) {
        sessionStorage.removeItem(`assessment_deadline_${assessmentId}`);
      }

      navigate(
        `/assessments/results?submissionId=${encodeURIComponent(attemptData.submission_id)}`,
        {
          replace: true,
          state: {
            assessmentId,
            assessmentTitle: attemptData.title,
            result,
            answers,
            questions: attemptData.questions,
          },
        },
      );
    } catch (error: unknown) {
      showToast("error", "Submission failed", error instanceof Error ? error.message : "Please retry.");
    } finally {
      setIsSubmitting(false);
      setAutoSubmitting(false);
    }
  }, [assessmentId, attemptData, answers, isSubmitting, navigate, showToast]);

  useEffect(() => {
    if (!started || isSubmitting || !deadlineRef.current) return;

    const id = window.setInterval(() => {
      const nextTimeLeft = Math.max(0, Math.round((deadlineRef.current! - Date.now()) / 1000));
      setTimeLeft(nextTimeLeft);
      if (nextTimeLeft === 0) {
        window.clearInterval(id);
        setAutoSubmitting(true);
      }
    }, 1000);

    setTimeLeft(Math.max(0, Math.round((deadlineRef.current - Date.now()) / 1000)));

    return () => window.clearInterval(id);
  }, [started, isSubmitting]);

  useEffect(() => {
    if (autoSubmitting) {
      showToast("warning", "Time's Up!", "Auto-submitting your assessment...");
      const timeout = setTimeout(() => void handleSubmit(), 1200);
      return () => clearTimeout(timeout);
    }
  }, [autoSubmitting, handleSubmit, showToast]);

  useEffect(() => {
    if (!started) return;

    const handleTabSwitch = () => {
      // Detect tab switch via blur or visibility change
      const newWarnings = warningsRef.current + 1;
      setWarnings(newWarnings);
      setWarningMessage(`Tab switch detected! Warning ${newWarnings}/${MAX_WARNINGS}. ${newWarnings >= MAX_WARNINGS ? "Your test will be auto-submitted." : "Please stay on this tab."}`);
      setWarningModal(true);
      if (newWarnings >= MAX_WARNINGS) {
        setTimeout(() => void handleSubmit(), 1200);
      }
    };

    // Listen for visibility change (tab switching)
    const handleVisibility = () => {
      if (document.hidden) {
        handleTabSwitch();
      }
    };

    // Listen for blur (window loses focus)
    const handleBlur = () => {
      handleTabSwitch();
    };

    // Prevent fullscreen exit - warn if user exits fullscreen
    const handleFullscreenChange = () => {
      if (fullscreenRequired && !document.fullscreenElement) {
        handleTabSwitch();
      }
    };

    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("blur", handleBlur);
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    
    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("blur", handleBlur);
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, [started, handleSubmit, fullscreenRequired]);

  // Cleanup fullscreen on unmount
  useEffect(() => {
    return () => {
      if (document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
      }
    };
  }, []);

  useEffect(() => {
    if (!started) return;
    const handler = (e: ClipboardEvent) => {
      e.preventDefault();
      const newWarnings = warningsRef.current + 1;
      setWarnings(newWarnings);
      setWarningMessage(`Copy attempt detected! Warning ${newWarnings}/${MAX_WARNINGS}.`);
      setWarningModal(true);
      showToast("warning", "Copy Blocked", "Copying is not allowed during the assessment.");
      if (newWarnings >= MAX_WARNINGS) {
        setTimeout(() => void handleSubmit(), 1200);
      }
    };
    document.addEventListener("copy", handler);
    return () => document.removeEventListener("copy", handler);
  }, [started, showToast, handleSubmit]);

  const handleSelect = (qId: string, optId: string, type?: string | null) => {
    const isMSQ = (type ?? "").toUpperCase() === "MSQ";
    setAnswers((prev) => {
      if (!isMSQ) {
        return { ...prev, [qId]: [optId] };
      }
      const current = prev[qId] ?? [];
      const next = current.includes(optId)
        ? current.filter((id) => id !== optId)
        : [...current, optId];
      return { ...prev, [qId]: next };
    });
  };

  const toggleFlag = (qId: string) => {
    setFlagged((prev) => {
      const next = new Set(prev);
      if (next.has(qId)) next.delete(qId);
      else next.add(qId);
      return next;
    });
    showToast("info", flagged.has(qId) ? "Unflagged" : "Flagged for review");
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const questions = attemptData?.questions ?? [];
  const answeredCount = Object.values(answers).filter((selectedIds) => selectedIds.length > 0).length;
  const currentQuestion = questions[currentQ];
  const isUrgent = timeLeft < 60;

  if (!assessmentId) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <VCard className="p-6 max-w-md text-center">
          <p className="text-sm text-muted-foreground mb-4">Assessment link is invalid.</p>
          <VButton onClick={() => navigate("/assessments")}>Back to Assessments</VButton>
        </VCard>
      </div>
    );
  }


  if (started && questions.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <VCard className="p-6 max-w-md text-center">
          <p className="text-sm text-muted-foreground mb-4">No questions are available for this assessment yet.</p>
          <VButton onClick={() => navigate("/assessments")}>Back to Assessments</VButton>
        </VCard>
      </div>
    );
  }
  // Show rules modal if not started OR if fullscreen is required but not in fullscreen
  if (!started || !currentQuestion || (fullscreenRequired && !isFullscreen)) {
    // If fullscreen is required but not in fullscreen, show a blocking message
    if (fullscreenRequired && !isFullscreen) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <VCard className="p-8 text-center max-w-md">
            <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center">
              <Maximize2 className="h-8 w-8 text-destructive" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">Fullscreen Required</h3>
            <p className="text-sm text-muted-foreground mb-6">Please enter fullscreen mode to continue the assessment.</p>
            <VButton onClick={() => document.documentElement.requestFullscreen()}>
              <Maximize2 className="h-4 w-4 mr-2" /> Enter Fullscreen
            </VButton>
          </VCard>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <VModal isOpen={rulesModal} onClose={() => {}} title="Assessment Rules" className="max-w-md">
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-warning/10 border border-warning/20">
              <Shield className="h-5 w-5 text-warning shrink-0" />
              <p className="text-sm text-foreground">This is a proctored assessment. Please read the rules carefully.</p>
            </div>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              <li className="flex items-start gap-2"><span className="text-primary font-bold">1.</span> You have <strong className="text-foreground">10 minutes</strong> to complete {questions.length || "all"} questions.</li>
              <li className="flex items-start gap-2"><span className="text-primary font-bold">2.</span> <strong className="text-foreground">Fullscreen required</strong> — assessment will run in fullscreen mode.</li>
              <li className="flex items-start gap-2"><span className="text-primary font-bold">3.</span> <strong className="text-foreground">Do not switch tabs</strong> — this will trigger a warning.</li>
              <li className="flex items-start gap-2"><span className="text-primary font-bold">4.</span> <strong className="text-foreground">Copying is not allowed</strong> — attempts will be detected.</li>
              <li className="flex items-start gap-2"><span className="text-primary font-bold">5.</span> After <strong className="text-foreground">{MAX_WARNINGS} warnings</strong>, your test will be auto-submitted.</li>
              <li className="flex items-start gap-2"><span className="text-primary font-bold">6.</span> When time runs out, your answers will be <strong className="text-foreground">automatically submitted</strong>.</li>
            </ul>
            <div className="flex justify-end gap-3 pt-2">
              <VButton variant="ghost" onClick={() => navigate("/assessments")}>Cancel</VButton>
              <VButton onClick={() => startMutation.mutate()} disabled={startMutation.isPending}>
                <Maximize2 className="h-4 w-4" /> {startMutation.isPending ? "Starting..." : "Start Assessment"}
              </VButton>
            </div>
          </div>
        </VModal>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {autoSubmitting && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-foreground/40 backdrop-blur-sm">
          <VCard className="p-8 text-center max-w-sm mx-4 animate-in zoom-in-95 duration-300">
            <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-warning/10 flex items-center justify-center">
              <Clock className="h-8 w-8 text-warning animate-pulse" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">Time's Up!</h3>
            <p className="text-sm text-muted-foreground">Auto-submitting your answers...</p>
          </VCard>
        </div>
      )}

      <div className="sticky top-0 z-40 flex items-center justify-between border-b border-border bg-card/90 backdrop-blur-md px-4 sm:px-6 py-3">
        <div className="flex items-center gap-3">
          <h2 className="text-sm sm:text-base font-semibold text-foreground">{attemptData.title || "Assessment"}</h2>
          {warnings > 0 && (
            <span className="inline-flex items-center gap-1 rounded-full bg-warning/10 px-2.5 py-0.5 text-xs font-semibold text-warning">
              <AlertTriangle className="h-3 w-3" />
              {warnings}/{MAX_WARNINGS} warnings
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-sm font-bold ${isUrgent ? "bg-destructive/10 text-destructive animate-pulse" : "bg-primary/10 text-primary"}`}>
            <Clock className="h-4 w-4" />
            {formatTime(timeLeft)}
          </div>
          <VButton size="sm" onClick={() => setSubmitModal(true)} disabled={isSubmitting}>
            <Send className="h-3.5 w-3.5" /> Submit
          </VButton>
        </div>
      </div>

      <div className="max-w-5xl mx-auto p-4 sm:p-6 grid gap-5 lg:grid-cols-[1fr_200px]">
        <VCard className="p-6">
          <div className="flex items-center justify-between mb-6">
            <p className="text-sm text-muted-foreground">Question {currentQ + 1} of {questions.length}</p>
            <button
              onClick={() => toggleFlag(currentQuestion.id)}
              className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all ${
                flagged.has(currentQuestion.id) ? "bg-warning/10 text-warning" : "text-muted-foreground hover:bg-accent"
              }`}
            >
              <Flag className="h-3.5 w-3.5" />
              {flagged.has(currentQuestion.id) ? "Flagged" : "Flag"}
            </button>
          </div>
          <motion.div
            key={currentQuestion.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <h3 className="text-lg font-semibold text-foreground mb-6">{currentQuestion.text}</h3>
            <div className="space-y-3">
              {currentQuestion.options.map((opt, oi) => (
                <button
                  key={opt.id}
                  onClick={() => handleSelect(currentQuestion.id, opt.id, currentQuestion.type)}
                  className={`w-full text-left rounded-xl border px-5 py-4 text-sm transition-all ${
                    (answers[currentQuestion.id] ?? []).includes(opt.id)
                      ? "border-primary bg-primary/5 text-primary ring-1 ring-primary/30"
                      : "border-border text-foreground hover:bg-accent hover:border-primary/20"
                  }`}
                >
                  <span className="inline-flex items-center gap-3">
                    <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                      (answers[currentQuestion.id] ?? []).includes(opt.id)
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    }`}>
                      {String.fromCharCode(65 + oi)}
                    </span>
                    {opt.text}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>
          <div className="flex justify-between mt-8">
            <VButton variant="secondary" disabled={currentQ === 0} onClick={() => setCurrentQ(currentQ - 1)}>
              <ChevronLeft className="h-4 w-4" /> Previous
            </VButton>
            {currentQ < questions.length - 1 ? (
              <VButton onClick={() => setCurrentQ(currentQ + 1)}>
                Next <ChevronRight className="h-4 w-4" />
              </VButton>
            ) : (
              <VButton onClick={() => setSubmitModal(true)} disabled={isSubmitting}>
                <Send className="h-4 w-4" /> Submit
              </VButton>
            )}
          </div>
        </VCard>

        <VCard className="p-4 h-fit">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Questions</p>
          <div className="grid grid-cols-3 gap-2">
            {questions.map((q, i) => (
              <button
                key={q.id}
                onClick={() => setCurrentQ(i)}
                className={`flex h-9 w-full items-center justify-center rounded-lg text-xs font-bold transition-all ${
                  currentQ === i
                    ? "bg-primary text-primary-foreground ring-2 ring-primary/30"
                    : (answers[q.id] ?? []).length > 0
                    ? "bg-success/10 text-success border border-success/30"
                    : flagged.has(q.id)
                    ? "bg-warning/10 text-warning border border-warning/30"
                    : "bg-muted text-muted-foreground hover:bg-accent"
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
          <div className="mt-4 space-y-1.5 text-xs text-muted-foreground">
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded bg-success/10 border border-success/30" /> Answered ({answeredCount})</div>
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded bg-warning/10 border border-warning/30" /> Flagged ({flagged.size})</div>
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded bg-muted" /> Unanswered ({questions.length - answeredCount})</div>
          </div>
        </VCard>
      </div>

      <VModal isOpen={warningModal} onClose={() => setWarningModal(false)} title="?? Warning" className="max-w-sm">
        <div className="flex items-start gap-3 mb-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-warning/10">
            <AlertTriangle className="h-5 w-5 text-warning" />
          </div>
          <p className="text-sm text-foreground">{warningMessage}</p>
        </div>
        <div className="flex justify-end">
          <VButton onClick={() => setWarningModal(false)}>I Understand</VButton>
        </div>
      </VModal>

      <VModal isOpen={submitModal} onClose={() => setSubmitModal(false)} title="Submit Assessment" className="max-w-sm">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            You have answered <strong className="text-foreground">{answeredCount}</strong> out of <strong className="text-foreground">{questions.length}</strong> questions.
          </p>
          {answeredCount < questions.length && (
            <div className="flex items-start gap-2 p-3 rounded-xl bg-warning/10 border border-warning/20">
              <AlertTriangle className="h-4 w-4 text-warning mt-0.5 shrink-0" />
              <p className="text-sm text-warning">You have {questions.length - answeredCount} unanswered question(s).</p>
            </div>
          )}
          <div className="flex justify-end gap-3">
            <VButton variant="ghost" onClick={() => setSubmitModal(false)}>Review Answers</VButton>
            <VButton onClick={() => { setSubmitModal(false); void handleSubmit(); }} disabled={isSubmitting}>
              {isSubmitting ? "Submitting..." : "Submit Now"}
            </VButton>
          </div>
        </div>
      </VModal>
    </div>
  );
};

export default AssessmentAttempt;


