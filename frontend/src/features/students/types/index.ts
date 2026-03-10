export type WrongAnswerStatus = "active" | "resolved" | "archived";

export interface ConceptMasteryResponse {
  concept_id: number;
  concept_name: string;
  mastery_level: number;
  last_updated: string;
}

export interface MasteryListResponse {
  student_id: number;
  masteries: ConceptMasteryResponse[];
}

export interface WrongAnswerResponse {
  id: number;
  question_id: number;
  question_content: string;
  submitted_answer: string;
  status: WrongAnswerStatus;
  retry_count: number;
  created_at: string;
}

export interface WrongAnswerListResponse {
  student_id: number;
  wrong_answers: WrongAnswerResponse[];
  total: number;
}

export interface ConceptFrequency {
  concept_name: string;
  count: number;
  mastery: number;
}

export interface RecommendedProblemDetail {
  question_id: number;
  concept_name: string;
}

export interface DiagnosisResponse {
  student_id: number;
  core_weaknesses: string[];
  prerequisite_chains: string[][];
  learning_path: string[];
  recommended_problems: number[];
  concept_frequencies: ConceptFrequency[];
  recommended_problems_detail: RecommendedProblemDetail[];
  generated_at: string;
}

export interface LearningPathResponse {
  student_id: number;
  path: string[];
  estimated_concepts: number;
}

export interface WrongAnswer {
  id: number;
  problem: string;
  unit: string;
  status: "active" | "resolved" | "archived";
}

export interface MockConcept {
  name: string;
  count: number;
  pct: number;
}

export interface LearningPathItem {
  step: number;
  concept: string;
  desc: string;
}

export interface PracticeItem {
  problem: string;
  concept: string;
  difficulty: string;
}

export interface StudentSummaryResponse {
  id: number;
  name: string;
  grade_level: number | null;
  wrong_answers: number;
  root_cause: string | null;
  mastery: number;
  status: "needs-attention" | "improving" | "on-track";
}

export interface StudentSummaryListResponse {
  students: StudentSummaryResponse[];
  total: number;
  needs_attention: number;
  total_wrong_answers: number;
}

export interface StudentSummary {
  id: string;
  name: string;
  grade: string;
  wrongAnswers: number;
  rootCause: string | null;
  mastery: number;
  status: "needs-attention" | "improving" | "on-track";
}
