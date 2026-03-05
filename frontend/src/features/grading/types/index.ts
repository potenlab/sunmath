export interface MockProblem {
  id: string;
  content: string;
  correct_answer: string | null;
  expected_form: string | null;
  grading_hints: string | null;
  evaluation_concepts: string[];
}

export interface GradingResult {
  is_correct: boolean;
  judged_by: string;
  reasoning: string;
  problem: MockProblem;
  ocr_text: string;
  ocr_confidence: number;
}

export type PipelineStep = "idle" | "ocr" | "grading" | "done";
