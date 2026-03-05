import type { MockProblem } from "../types";

export const MOCK_PROBLEMS: MockProblem[] = [
  {
    id: "1",
    content: "Factor x\u00B2+2x+1",
    correct_answer: "(x+1)\u00B2",
    expected_form: "factored",
    grading_hints: "Must be in factored form",
    evaluation_concepts: ["Factoring", "Perfect square trinomial"],
  },
  {
    id: "2",
    content: "Expand (x+1)\u00B2",
    correct_answer: "x\u00B2+2x+1",
    expected_form: null,
    grading_hints: null,
    evaluation_concepts: ["Polynomial expansion"],
  },
  {
    id: "3",
    content: "Find the distance between A(1,2) and B(4,6)",
    correct_answer: "5",
    expected_form: "numeric",
    grading_hints: "Calculation must be completed to a number",
    evaluation_concepts: ["Distance formula"],
  },
  {
    id: "4",
    content:
      "Prove that the sum of interior angles of a triangle is 180\u00B0",
    correct_answer: null,
    expected_form: "proof",
    grading_hints: "Must use alternate angle property of parallel lines",
    evaluation_concepts: ["Triangle angle sum", "Parallel line properties"],
  },
];

export const MOCK_OCR: Record<string, { text: string; confidence: number }> = {
  "1": { text: "x\u00B2+2x+1", confidence: 0.94 },
  "2": { text: "x\u00B2+2x+1", confidence: 0.96 },
  "3": { text: "\u221A25", confidence: 0.88 },
  "4": {
    text: "Draw a line through one vertex parallel to the opposite side. By alternate interior angles, the two angles at the vertex equal the two base angles. Together with the vertex angle, they form a straight line = 180\u00B0.",
    confidence: 0.72,
  },
};
