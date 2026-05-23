import { useState, useEffect } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
    Award,
    ArrowRight,
    CheckCircle2,
    XCircle,
    Trophy,
    Star,
    MessageSquare,
    Sparkles,
} from "lucide-react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import VCard from "@/components/ui-custom/VCard";
import VButton from "@/components/ui-custom/VButton";
import VBadge from "@/components/ui-custom/VBadge";
import VModal from "@/components/ui-custom/VModal";
import { useVToast } from "@/components/ui-custom/VToast";
import { useRole } from "@/hooks/useRole";
import StudentExplanationPanel from "@/components/assessments/StudentExplanationPanel";
import {
    createStudentAnswerExplanation,
    fetchAssessmentLeaderboard,
    fetchSubmissionResult,
    fetchStudentExplanationResult,
    fetchStudentExplanationStatus,
} from "@/services/api";
import type { BackendStudentExplanationResult, BackendSubmissionResult } from "@/api/types";

type ResultState = {
    assessmentId?: string;
    assessmentTitle?: string;
    result?: BackendSubmissionResult;
};

const Results = () => {
    const location = useLocation();
    const state = (location.state ?? null) as ResultState | null;
    const [searchParams] = useSearchParams();
    const submissionIdFromUrl = searchParams.get("submissionId");
    const navigate = useNavigate();
    const { showToast } = useVToast();
    const role = useRole();
    const [animatedScore, setAnimatedScore] = useState(0);
    const [showDetails, setShowDetails] = useState(false);
    const [showLeaderboard, setShowLeaderboard] = useState(false);
    const [feedbackModal, setFeedbackModal] = useState(false);
    const [feedbackRating, setFeedbackRating] = useState(0);
    const [feedbackText, setFeedbackText] = useState("");
    const [explanationsByQuestion, setExplanationsByQuestion] = useState<
        Record<string, BackendStudentExplanationResult>
    >({});
    const [explanationErrorsByQuestion, setExplanationErrorsByQuestion] =
        useState<Record<string, string>>({});
    const [loadingExplanationForQuestion, setLoadingExplanationForQuestion] =
        useState<string | null>(null);

    const resultQuery = useQuery({
        queryKey: ["submissionResult", submissionIdFromUrl],
        queryFn: () => fetchSubmissionResult(submissionIdFromUrl ?? ""),
        enabled: Boolean(submissionIdFromUrl),
    });

    const backendResult = resultQuery.data ?? state?.result;
    const submissionId = backendResult?.submission_id ?? submissionIdFromUrl ?? null;
    const assessmentId = state?.assessmentId ?? backendResult?.assessment_id;

    // Backend always returns score as 0-100 percentage (e.g., 33.3 for 2/6 correct)
    // This is the single source of truth for all displays
    const percentage = backendResult?.score ?? 0;

    // Single source of truth for pass/fail — used everywhere (ring color, badge, message, buttons)
    const isPassed = backendResult
        ? (backendResult.pass_fail ?? (percentage >= 60))
        : false;

    const ringRadius = 70;
    const ringCircumference = 2 * Math.PI * ringRadius;
    // Ring offset: convert percentage (0-100) to fraction (0-1) then calculate offset
    const ringOffset = backendResult
        ? ringCircumference - (percentage / 100) * ringCircumference
        : ringCircumference;

    const leaderboardQuery = useQuery({
        queryKey: ["assessmentLeaderboard", assessmentId],
        queryFn: () => fetchAssessmentLeaderboard(assessmentId ?? ""),
        enabled: Boolean(showLeaderboard && isPassed && assessmentId),
    });
    const leaderboardEntries = leaderboardQuery.data?.entries ?? [];

    const explanationMutation = useMutation({
        mutationFn: (payload: { submissionId: string; questionId: string }) =>
            createStudentAnswerExplanation({
                submission_id: payload.submissionId,
                question_id: payload.questionId,
            }),
        onSuccess: async (data, variables) => {
            if (data.explanation) {
                setExplanationsByQuestion((prev) => ({
                    ...prev,
                    [variables.questionId]:
                        data.explanation as BackendStudentExplanationResult,
                }));
                setExplanationErrorsByQuestion((prev) => {
                    const next = { ...prev };
                    delete next[variables.questionId];
                    return next;
                });
                showToast(
                    data.from_cache ? "info" : "success",
                    data.from_cache ? "Loaded Cached Explanation" : "Explanation Ready",
                    data.from_cache
                        ? "Reused a previous explanation."
                        : "Generated a new explanation.",
                );
                return;
            }

            showToast(
                "warning",
                "Explanation Queued",
                "Generating in background. This will auto-refresh for a short time.",
            );

            const maxAttempts = 30;
            for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
                await new Promise((r) => setTimeout(r, 2000));
                const status = await fetchStudentExplanationStatus(data.explanation_id);
                if (status.status === "failed") {
                    throw new Error(
                        typeof status.error_details?.message === "string"
                            ? status.error_details.message
                            : "Explanation generation failed.",
                    );
                }
                if (status.status !== "completed") continue;
                const result = await fetchStudentExplanationResult(data.explanation_id);
                setExplanationsByQuestion((prev) => ({
                    ...prev,
                    [variables.questionId]: result.explanation,
                }));
                setExplanationErrorsByQuestion((prev) => {
                    const next = { ...prev };
                    delete next[variables.questionId];
                    return next;
                });
                showToast("success", "Explanation Ready", "Generated a new explanation.");
                return;
            }

            throw new Error("Explanation is still processing. Please try again in a moment.");
        },
        onError: (error, variables) => {
            setExplanationErrorsByQuestion((prev) => ({
                ...prev,
                [variables.questionId]:
                    error instanceof Error ? error.message : "Unable to generate explanation.",
            }));
            showToast(
                "error",
                "Explanation Failed",
                error instanceof Error ? error.message : "Unable to generate explanation.",
            );
        },
        onSettled: () => {
            setLoadingExplanationForQuestion(null);
        },
    });

    useEffect(() => {
        if (!backendResult) return;
        
        // Set animated score to the final percentage value immediately
        // This ensures center text, ring, and stat card all show the same value
        setAnimatedScore(Math.round(percentage * 10) / 10); // Keep decimal precision
        setShowDetails(true);
        
        // Show leaderboard and feedback after a short delay
        if (isPassed && role === "student") {
            setTimeout(() => setShowLeaderboard(true), 400);
            setTimeout(() => setFeedbackModal(true), 1000);
        }
    }, [percentage, isPassed, role, backendResult]);

    if (submissionIdFromUrl && resultQuery.isLoading) {
        return (
            <DashboardLayout title="Results">
                <div className="flex flex-col items-center justify-center py-16">
                    <div className="vidya-spinner mb-4" />
                    <p className="text-muted-foreground">Loading results...</p>
                </div>
            </DashboardLayout>
        );
    }

    if (submissionIdFromUrl && resultQuery.isError) {
        return (
            <DashboardLayout title="Results">
                <div className="flex flex-col items-center justify-center py-16">
                    <p className="text-muted-foreground mb-4">We could not load this result.</p>
                    <VButton onClick={() => navigate("/assessments")}>Go back to assessments</VButton>
                </div>
            </DashboardLayout>
        );
    }

    if (submissionIdFromUrl && !backendResult && !resultQuery.isLoading) {
        return (
            <DashboardLayout title="Results">
                <div className="flex flex-col items-center justify-center py-16">
                    <p className="text-muted-foreground mb-4">
                        No results available or invalid session.
                    </p>
                    <VButton onClick={() => navigate("/assessments")}>
                        Back to Assessments
                    </VButton>
                </div>
            </DashboardLayout>
        );
    }

    if (!backendResult) {
        return (
            <DashboardLayout title="Results">
                <div className="flex flex-col items-center justify-center py-16">
                    <div className="vidya-spinner mb-4" />
                    <p className="text-muted-foreground">Loading results...</p>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout title="Assessment Results">
            <div className="max-w-3xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}>
                    <VCard className="p-8 mb-8 text-center relative overflow-hidden">
                        <div className="absolute inset-0 vidya-gradient-soft" />
                        <div className="relative">
                            <div className="mx-auto mb-6 relative h-40 w-40">
                                <svg
                                    className="h-40 w-40 -rotate-90"
                                    viewBox="0 0 160 160">
                                    {/* Background track */}
                                    <circle
                                        cx="80"
                                        cy="80"
                                        r="70"
                                        fill="none"
                                        stroke="hsl(var(--muted))"
                                        strokeWidth="8"
                                    />
                                    {/* Progress arc — color driven by single isPassed variable */}
                                    <circle
                                        cx="80"
                                        cy="80"
                                        r="70"
                                        fill="none"
                                        stroke={isPassed ? "hsl(var(--success))" : "hsl(var(--destructive))"}
                                        strokeWidth="8"
                                        strokeDasharray={`${ringCircumference}`}
                                        strokeDashoffset={`${ringOffset}`}
                                        strokeLinecap="round"
                                        className="transition-all duration-300"
                                    />
                                </svg>
                                {/* FIX: Single percentage display — removed duplicate nested span */}
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className="text-4xl font-bold text-foreground">
                                        {Math.round(animatedScore)}%
                                    </span>
                                    <span className="text-xs text-muted-foreground">Score</span>
                                </div>
                            </div>

                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 1.2 }}>
                                {/* FIX: isPassed is the single source of truth for badge */}
                                <VBadge
                                    variant={isPassed ? "success" : "destructive"}
                                    className="text-base px-4 py-1.5">
                                    {isPassed ? (
                                        <>
                                            <CheckCircle2 className="h-4 w-4 mr-1" /> Passed!
                                        </>
                                    ) : (
                                        <>
                                            <XCircle className="h-4 w-4 mr-1" /> Failed
                                        </>
                                    )}
                                </VBadge>
                                <p className="mt-3 text-sm text-muted-foreground">
                                    {isPassed
                                        ? "Great work! You passed this assessment."
                                        : "Keep going — review the questions below and try again."}
                                </p>
                            </motion.div>

                            {/* FIX: All three stat cards use normalized percentage */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6 text-left">
                                <VCard className="p-4">
                                    <p className="text-xs text-muted-foreground">Score</p>
                                    <p className="text-xl font-semibold text-foreground">
                                        {Math.round(percentage)}%
                                    </p>
                                </VCard>
                                <VCard className="p-4">
                                    <p className="text-xs text-muted-foreground">Correct</p>
                                    <p className="text-xl font-semibold text-foreground">
                                        {backendResult.correct_count}/{backendResult.total}
                                    </p>
                                </VCard>
                                <VCard className="p-4">
                                    <p className="text-xs text-muted-foreground">Status</p>
                                    <p className={`text-xl font-semibold ${isPassed ? "text-success" : "text-destructive"}`}>
                                        {isPassed ? "Passed" : "Failed"}
                                    </p>
                                </VCard>
                            </div>
                        </div>
                    </VCard>
                </motion.div>

                {showLeaderboard && isPassed && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}>
                        <VCard className="p-6 mb-8">
                            <div className="flex items-center gap-2 mb-4">
                                <Trophy className="h-5 w-5 text-warning" />
                                <h3 className="text-lg font-semibold text-foreground">
                                    Leaderboard
                                </h3>
                            </div>
                            <div className="space-y-2">
                                {leaderboardEntries.map((entry) => (
                                    <div
                                        key={entry.rank}
                                        className="flex items-center gap-4 rounded-xl px-4 py-3 transition-all hover:bg-accent">
                                        <span
                                            className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${
                                                entry.rank === 1
                                                    ? "bg-warning/10 text-warning"
                                                    : entry.rank === 2
                                                      ? "bg-muted text-muted-foreground"
                                                      : entry.rank === 3
                                                        ? "bg-warning/5 text-warning/70"
                                                        : "bg-muted text-muted-foreground"
                                            }`}>
                                            {entry.rank <= 3 ? (
                                                <Trophy className="h-4 w-4" />
                                            ) : (
                                                entry.rank
                                            )}
                                        </span>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-foreground">
                                                {entry.student_name}
                                            </p>
                                        </div>
                                        <span className="text-sm font-bold text-foreground">
                                            {Math.round(entry.average_percentage)}%
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                            {entry.attempts} attempts
                                        </span>
                                    </div>
                                ))}
                                {!leaderboardEntries.length && (
                                    <p className="text-sm text-muted-foreground">
                                        {leaderboardQuery.isLoading
                                            ? "Loading leaderboard..."
                                            : "No leaderboard entries yet."}
                                    </p>
                                )}
                            </div>
                        </VCard>
                    </motion.div>
                )}

                {showDetails && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                        className="space-y-4 mb-8">
                        <h3 className="text-lg font-semibold text-foreground">
                            Question review
                        </h3>
                        {(backendResult.per_question ?? []).map((q, idx) => {
                            // Support both single ID (MCQ) and multiple IDs (MSQ)
                            const selectedIds = q.student_answer_ids && q.student_answer_ids.length > 0 
                                ? q.student_answer_ids 
                                : (q.student_answer_id ? [q.student_answer_id] : []);
                            const correctIds = q.correct_answer_ids && q.correct_answer_ids.length > 0 
                                ? q.correct_answer_ids 
                                : (q.correct_answer_id ? [q.correct_answer_id] : []);
                            
                            const isCorrect = q.is_correct;
                            const canRequestExplanation = Boolean(
                                role === "student" && !isCorrect && submissionId,
                            );
                            return (
                                <VCard
                                    key={q.question_id}
                                    className={`p-5 border-l-4 ${isCorrect ? "border-l-success" : "border-l-destructive"}`}>
                                    <div className="flex items-start gap-3">
                                        <div
                                            className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${isCorrect ? "bg-success/10" : "bg-destructive/10"}`}>
                                            {isCorrect ? (
                                                <CheckCircle2 className="h-4 w-4 text-success" />
                                            ) : (
                                                <XCircle className="h-4 w-4 text-destructive" />
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-medium text-foreground mb-2">
                                                {idx + 1}. {q.question_text}
                                            </p>

                                            <div className="mt-3 space-y-2">
                                                {q.options.map((opt) => {
                                                    const optionId = String(opt.id);
                                                    const isStudentPick = selectedIds.includes(optionId);
                                                    const isCorrectOption = correctIds.includes(optionId);
                                                    const isWrongStudentPick = isStudentPick && !isCorrectOption;

                                                    let optClass = "bg-background border-border text-foreground";
                                                    if (isCorrectOption) {
                                                        optClass = "bg-success/10 border-success text-success";
                                                    } else if (isWrongStudentPick) {
                                                        optClass = "bg-destructive/10 border-destructive text-destructive";
                                                    }

                                                    return (
                                                        <div
                                                            key={opt.id}
                                                            className={`flex items-center justify-between rounded-lg border px-3 py-2 text-sm ${optClass}`}>
                                                            <span>{opt.text}</span>
                                                            {isCorrectOption && (
                                                                <CheckCircle2 className="h-4 w-4 shrink-0" />
                                                            )}
                                                            {isWrongStudentPick && (
                                                                <XCircle className="h-4 w-4 shrink-0" />
                                                            )}
                                                        </div>
                                                    );
                                                })}
                                            </div>

                                            {q.explanation && (
                                                <div className="mt-3 rounded-lg border border-border bg-muted/40 p-3">
                                                    <p className="text-xs font-semibold text-muted-foreground mb-1">
                                                        Explanation
                                                    </p>
                                                    <p className="text-sm text-foreground">{q.explanation}</p>
                                                </div>
                                            )}

                                            {canRequestExplanation && (
                                                <div className="mt-3">
                                                    <VButton
                                                        size="sm"
                                                        variant="secondary"
                                                        isLoading={loadingExplanationForQuestion === q.question_id}
                                                        onClick={() => {
                                                            if (!submissionId) return;
                                                            setLoadingExplanationForQuestion(q.question_id);
                                                            explanationMutation.mutate({
                                                                submissionId,
                                                                questionId: q.question_id,
                                                            });
                                                        }}>
                                                        <Sparkles className="h-4 w-4" /> Explain This
                                                    </VButton>
                                                    {explanationErrorsByQuestion[q.question_id] && (
                                                        <p className="text-xs text-destructive mt-2">
                                                            {explanationErrorsByQuestion[q.question_id]}
                                                        </p>
                                                    )}
                                                    {explanationsByQuestion[q.question_id] && (
                                                        <StudentExplanationPanel
                                                            explanation={explanationsByQuestion[q.question_id]}
                                                        />
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </VCard>
                            );
                        })}
                        {(backendResult.per_question ?? []).length === 0 && (
                            <VCard className="p-4">
                                <p className="text-sm text-muted-foreground">
                                    Detailed review not available for this attempt.
                                </p>
                            </VCard>
                        )}
                    </motion.div>
                )}

                <div className="flex flex-col sm:flex-row gap-3">
                    <VButton onClick={() => navigate("/assessments")}>
                        <ArrowRight className="h-4 w-4" /> Back to Assessments
                    </VButton>
                    {isPassed && (
                        <VButton
                            variant="secondary"
                            onClick={() => {
                                navigate("/certificates");
                                showToast("success", "Certificate", "Check your certificates!");
                            }}>
                            <Award className="h-4 w-4" /> View Certificate
                        </VButton>
                    )}
                    {!isPassed && (
                        <VButton
                            variant="secondary"
                            onClick={() =>
                                navigate(
                                    assessmentId
                                        ? `/assessments/attempt/${assessmentId}`
                                        : "/assessments",
                                )
                            }>
                            Retry Assessment
                        </VButton>
                    )}
                </div>
            </div>

            <VModal
                isOpen={feedbackModal}
                onClose={() => setFeedbackModal(false)}
                title="How was your experience?"
                className="max-w-md">
                <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        Help us improve! Rate the assessment and share your thoughts.
                    </p>
                    <div className="flex items-center justify-center gap-2">
                        {[1, 2, 3, 4, 5].map((s) => (
                            <button
                                key={s}
                                onClick={() => setFeedbackRating(s)}
                                className="transition-transform hover:scale-110">
                                <Star
                                    className={`h-8 w-8 ${s <= feedbackRating ? "fill-warning text-warning" : "text-muted-foreground"}`}
                                />
                            </button>
                        ))}
                    </div>
                    <div>
                        <label className="vidya-label">Comments (optional)</label>
                        <textarea
                            value={feedbackText}
                            onChange={(e) => setFeedbackText(e.target.value)}
                            rows={3}
                            className="vidya-input resize-none"
                            placeholder="Any suggestions or feedback..."
                        />
                    </div>
                    <div className="flex justify-end gap-3">
                        <VButton variant="ghost" onClick={() => setFeedbackModal(false)}>
                            Skip
                        </VButton>
                        <VButton
                            onClick={() => {
                                setFeedbackModal(false);
                                showToast("success", "Thank You!", "Your feedback has been submitted.");
                            }}>
                            <MessageSquare className="h-4 w-4" /> Submit Feedback
                        </VButton>
                    </div>
                </div>
            </VModal>
        </DashboardLayout>
    );
};

export default Results;