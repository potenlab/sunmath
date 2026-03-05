import type { RegisteredProblem } from "../types";

export const SEED_PROBLEM: RegisteredProblem = {
  id: 1,
  content: "Factor x\u00B2+5x+6",
  correctAnswer: "(x+2)(x+3)",
  expectedForm: "factored",
  targetGrade: "9",
  gradingHints: "Accept any order of factors",
  concepts: [
    "Factoring",
    "Quadratic expressions",
    "Quadratic formula",
    "Factor theorem",
  ],
};

export const EXPECTED_FORMS = [
  "factored",
  "expanded",
  "simplified",
  "numeric",
  "proof",
  "null",
] as const;
