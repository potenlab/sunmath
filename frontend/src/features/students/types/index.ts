export interface StudentSummary {
  id: string;
  name: string;
  grade: string;
  wrongAnswers: number;
  rootCause: string | null;
  mastery: number;
  status: "needs-attention" | "improving" | "on-track";
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
