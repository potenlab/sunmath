import type { MockProblem } from "../types";

export function normalize(s: string): string {
  return s.replace(/\s+/g, "").toLowerCase();
}

export function gradeAnswer(
  problem: MockProblem,
  answer: string
): { is_correct: boolean; judged_by: string; reasoning: string } {
  const trimmed = answer.trim();
  const norm = normalize(trimmed);

  switch (problem.id) {
    case "1": {
      const factoredForms = ["(x+1)\u00B2", "(x+1)^2", "(x+1)(x+1)"];
      if (factoredForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: true,
          judged_by: "sympy",
          reasoning:
            "The answer is mathematically correct and is in factored form as required.",
        };
      }
      const expandedForms = ["x\u00B2+2x+1", "x^2+2x+1"];
      if (expandedForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: false,
          judged_by: "graphrag+sympy",
          reasoning:
            "The answer is mathematically equivalent but NOT in factored form. The problem requires the answer in factored form (expected_form: factored).",
        };
      }
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning:
          "The answer is not mathematically equivalent to (x+1)\u00B2.",
      };
    }
    case "2": {
      const validForms = [
        "x\u00B2+2x+1",
        "x^2+2x+1",
        "(x+1)\u00B2",
        "(x+1)^2",
        "(x+1)(x+1)",
        "1+2x+x\u00B2",
        "1+2x+x^2",
      ];
      if (validForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: true,
          judged_by: "sympy",
          reasoning:
            "The answer is mathematically equivalent to x\u00B2+2x+1. No specific form restriction applies.",
        };
      }
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning:
          "The answer is not mathematically equivalent to x\u00B2+2x+1.",
      };
    }
    case "3": {
      if (norm === "5") {
        return {
          is_correct: true,
          judged_by: "sympy",
          reasoning: "The answer is correct. The distance is 5.",
        };
      }
      const nonNumericForms = ["\u221A25", "sqrt(25)", "\\sqrt{25}"];
      if (nonNumericForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: false,
          judged_by: "graphrag+sympy",
          reasoning:
            "The answer is mathematically equivalent but NOT in numeric form. The problem requires the answer as a number (expected_form: numeric).",
        };
      }
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning: "The answer is not equal to 5.",
      };
    }
    case "4": {
      if (trimmed.length > 0) {
        return {
          is_correct: true,
          judged_by: "llm",
          reasoning:
            "LLM evaluation: The proof demonstrates understanding of the triangle angle sum property. The argument references relevant geometric principles.",
        };
      }
      return {
        is_correct: false,
        judged_by: "llm",
        reasoning: "No answer was provided.",
      };
    }
    default:
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning: "Unknown problem.",
      };
  }
}
