export type ExpectedForm = "factored" | "expanded" | "simplified" | "numeric" | "proof";
export type JudgedBy = "sympy" | "llm" | "cache";

export interface GradeRequest {
  student_id: number;
  question_id: number;
  submitted_answer: string;
}

export interface GradeResponse {
  is_correct: boolean;
  judged_by: JudgedBy;
  reasoning: string;
  cached: boolean;
}

export interface CacheStatsResponse {
  total_entries: number;
  hit_rate: number;
  entries_by_judge: Record<string, number>;
}

export interface ProblemResponse {
  id: number;
  content: string;
  correct_answer: string;
  expected_form: ExpectedForm;
  target_grade: number | null;
  grading_hints: string | null;
  created_at: string;
  updated_at: string;
}

export interface GradingResult {
  is_correct: boolean;
  judged_by: string;
  reasoning: string;
  problem: ProblemResponse;
  ocr_text: string;
  ocr_confidence: number;
}

export type PipelineStep = "idle" | "ocr" | "grading" | "done";
