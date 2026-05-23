import VCard from "@/components/ui-custom/VCard";
import type { BackendStudentExplanationResult } from "@/api/types";

interface StudentExplanationPanelProps {
  explanation: BackendStudentExplanationResult;
}

const toPercentage = (confidence: number) => {
  const bounded = Math.max(0, Math.min(confidence, 1));
  return Math.round(bounded * 100);
};

const StudentExplanationPanel = ({ explanation }: StudentExplanationPanelProps) => {
  return (
    <VCard className="mt-3 border border-primary/20 bg-primary/5 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-primary mb-3">AI Explanation</p>
      <div className="space-y-3 text-sm">
        <div>
          <p className="text-xs text-muted-foreground">Why It Was Wrong</p>
          <p className="text-foreground">{explanation.why_it_was_wrong}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Correct Reasoning</p>
          <p className="text-foreground">{explanation.correct_reasoning}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Common Mistake</p>
          <p className="text-foreground">{explanation.common_mistake}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Hint For Retry</p>
          <p className="text-foreground">{explanation.hint_for_retry}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Confidence</p>
          <p className="text-foreground">{toPercentage(explanation.confidence)}%</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Follow-up Questions</p>
          {explanation.follow_up_questions.length > 0 ? (
            <ul className="list-disc list-inside text-foreground space-y-1">
              {explanation.follow_up_questions.map((item, index) => (
                <li key={`${index}-${item}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="text-foreground">No follow-up questions suggested.</p>
          )}
        </div>
      </div>
    </VCard>
  );
};

export default StudentExplanationPanel;
