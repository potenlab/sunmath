export interface Problem {
  id: string;
  content: string;
  correct_answer: string;
  expected_form: "factored" | "expanded" | "simplified" | "numeric" | "proof" | null;
  target_grade: string;
  grading_hints: string | null;
  evaluation_concepts: string[];
  required_concepts: string[];
  unit_ids: string[];
}

export interface SimilarProblem {
  problem: Problem;
  similarity_score: number;
  shared_concepts: string[];
  differences: string[];
}

export interface GradingResult {
  correct: boolean;
  judged_by: "sympy" | "maxima" | "llm" | "cache" | "graphrag+sympy";
  reasoning: string;
  problem_id: string;
  student_answer: string;
  expected_form: string | null;
  grading_hints: string | null;
}

export interface Student {
  id: string;
  name: string;
  grade: string;
  wrong_answer_count: number;
}

export interface DiagnosisReport {
  student_id: string;
  core_weaknesses: {
    concept: string;
    mastery_level: number;
    prerequisite_chain: string[];
    affected_units: string[];
  }[];
  recommended_learning_path: {
    step: number;
    concept: string;
    description: string;
  }[];
  recommended_problems: Problem[];
}

export interface BenchmarkResult {
  model: string;
  subject: string;
  accuracy: number;
  cost_per_problem: number;
  latency_ms: number;
}

export interface VotingResult {
  subject: string;
  single_model_accuracy: number;
  voting_accuracy: number;
  cost_increase_percent: number;
}

export interface AdminSettings {
  similarity_threshold: number;
  similarity_mode: "block" | "warn";
  confidence_threshold: number;
}
