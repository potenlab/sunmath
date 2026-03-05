export interface RegisteredProblem {
  id: number;
  content: string;
  correctAnswer: string;
  expectedForm: string;
  targetGrade: string;
  gradingHints: string;
  concepts: string[];
}

export interface DuplicateInfo {
  similarity: number;
  existingProblem: RegisteredProblem;
  sharedConcepts: string[];
  differences: string[];
}
