import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import StudentExplanationPanel from "@/components/assessments/StudentExplanationPanel";

describe("StudentExplanationPanel", () => {
  it("renders all structured explanation sections safely", () => {
    render(
      <StudentExplanationPanel
        explanation={{
          why_it_was_wrong: "You selected a symptom instead of the root cause.",
          correct_reasoning: "Start from the definition and verify each condition.",
          common_mistake: "Rushing to pattern matching without checking constraints.",
          hint_for_retry: "Eliminate options that violate the core definition first.",
          confidence: 0.82,
          follow_up_questions: ["Which condition is necessary?", "<script>alert(1)</script>"],
        }}
      />,
    );

    expect(screen.getByText("Why It Was Wrong")).toBeInTheDocument();
    expect(screen.getByText("Correct Reasoning")).toBeInTheDocument();
    expect(screen.getByText("Common Mistake")).toBeInTheDocument();
    expect(screen.getByText("Hint For Retry")).toBeInTheDocument();
    expect(screen.getByText("Confidence")).toBeInTheDocument();
    expect(screen.getByText("82%")).toBeInTheDocument();
    expect(screen.getByText("<script>alert(1)</script>")).toBeInTheDocument();
    expect(document.querySelector("script")).not.toBeInTheDocument();
  });
});
