export type ExpectedForm = "factored" | "expanded" | "simplified" | "numeric" | "proof";

export const EXPECTED_FORMS = [
  "factored",
  "expanded",
  "simplified",
  "numeric",
  "proof",
] as const;

// --- Settings ---
export interface SettingResponse {
  key: string;
  value: string;
  description: string | null;
  updated_at: string;
}

export interface SettingsListResponse {
  settings: SettingResponse[];
}

// --- Problems ---
export interface ProblemCreate {
  content: string;
  correct_answer: string;
  expected_form?: ExpectedForm | null;
  target_grade?: number | null;
  grading_hints?: string | null;
  unit_ids?: number[];
  concept_ids?: number[];
  concept_weights?: Record<number, number> | null;
  auto_extract_concepts?: boolean;
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

export interface SimilarProblemDetail {
  question_id: number;
  similarity_score: number;
  shared_concepts: number[];
  only_in_new: number[];
  only_in_existing: number[];
}

export interface DuplicateCheckResponse {
  is_duplicate: boolean;
  mode: string;
  threshold: number;
  similar_problem_id: number | null;
  similarity_score: number;
}

export interface ConceptExtractionResult {
  evaluation_concept_names: string[];
  required_concept_names: string[];
  matched_evaluation_concept_ids: number[];
  matched_required_concept_ids: number[];
  evaluation_concept_weights: Record<number, number>;
  required_concept_weights: Record<number, number>;
  inferred_expected_form: ExpectedForm | null;
  inferred_grading_hints: string | null;
}

export interface ProblemRegistrationResponse {
  problem: ProblemResponse | null;
  registered: boolean;
  duplicate_check: DuplicateCheckResponse;
  similar_problems: SimilarProblemDetail[];
  concept_extraction: ConceptExtractionResult | null;
}

export interface ProblemUpdate {
  content?: string;
  correct_answer?: string;
  expected_form?: ExpectedForm | null;
  target_grade?: number | null;
  grading_hints?: string | null;
}

export interface ProblemListResponse {
  problems: ProblemResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface SimilarProblemResponse {
  problems: ProblemResponse[];
  similarity_scores: number[];
  details: SimilarProblemDetail[];
}

// Legacy type for backward compat with ProblemListItem component
export interface RegisteredProblem {
  id: number;
  content: string;
  correctAnswer: string;
  expectedForm: string;
  targetGrade: string;
  gradingHints: string;
  concepts: string[];
  conceptWeights?: Record<string, number>;
}

export interface ConceptOption {
  id: number;
  name: string;
  category: string | null;
}

export interface DuplicateInfo {
  similarity: number;
  existingProblem: RegisteredProblem;
  sharedConcepts: string[];
  differences: string[];
}
