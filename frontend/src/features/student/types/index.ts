export type ExpectedForm = "factored" | "expanded" | "simplified" | "numeric" | "proof";

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

export interface ProblemListResponse {
  problems: ProblemResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface MasteryUpdate {
  concept_id: number;
  concept_name: string;
  old_mastery: number;
  new_mastery: number;
  delta: number;
}

export interface GradeResponse {
  is_correct: boolean;
  judged_by: string;
  reasoning: string;
  cached: boolean;
  mastery_updates: MasteryUpdate[];
}
