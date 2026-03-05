import type { StudentSummary, WrongAnswer, MockConcept, LearningPathItem, PracticeItem } from "../types";

export function getMockStudents(t: (key: string) => string): StudentSummary[] {
  return [
    {
      id: "1",
      name: t("studentA"),
      grade: t("highSchool2"),
      wrongAnswers: 8,
      rootCause: t("completingTheSquare"),
      mastery: 0.3,
      status: "needs-attention",
    },
    {
      id: "2",
      name: t("studentB"),
      grade: t("highSchool1"),
      wrongAnswers: 5,
      rootCause: t("radianMeasure"),
      mastery: 0.45,
      status: "improving",
    },
    {
      id: "3",
      name: t("studentC"),
      grade: t("middleSchool3"),
      wrongAnswers: 2,
      rootCause: null,
      mastery: 0.82,
      status: "on-track",
    },
  ];
}

export function getMockWrongAnswers(t: (key: string) => string): WrongAnswer[] {
  return [
    { id: 1, problem: "Quadratic inequality: x^2 - 5x + 6 > 0", unit: t("quadraticInequalities"), status: "active" },
    { id: 2, problem: "Find the vertex of y = x^2 - 4x + 7", unit: t("quadraticFunctions"), status: "active" },
    { id: 3, problem: "Complete: x^2 + y^2 - 6x + 4y = 12", unit: t("circleEquations"), status: "active" },
    { id: 4, problem: "Factor: x^2 + 6x + 9", unit: t("factoringQuadratics"), status: "resolved" },
  ];
}

export function getMockConcepts(t: (key: string) => string): MockConcept[] {
  return [
    { name: t("completingTheSquare"), count: 3, pct: 100 },
    { name: t("factoringQuadratics"), count: 2, pct: 66 },
    { name: t("multiplicationFormulas"), count: 2, pct: 66 },
    { name: t("coordinateGeometry"), count: 1, pct: 33 },
  ];
}

export function getMockLearningPath(t: (key: string) => string): LearningPathItem[] {
  return [
    { step: 1, concept: t("learningStep1"), desc: t("learningStep1Desc") },
    { step: 2, concept: t("learningStep2"), desc: t("learningStep2Desc") },
    { step: 3, concept: t("learningStep3"), desc: t("learningStep3Desc") },
    { step: 4, concept: t("learningStep4"), desc: t("learningStep4Desc") },
  ];
}

export function getMockPracticeItems(t: (key: string) => string): PracticeItem[] {
  return [
    { problem: t("practice1"), concept: t("multiplicationFormulas"), difficulty: t("easy") },
    { problem: t("practice2"), concept: t("completingTheSquare"), difficulty: t("medium") },
    { problem: t("practice3"), concept: t("completingTheSquare"), difficulty: t("medium") },
    { problem: t("practice4"), concept: t("completingTheSquare"), difficulty: t("hard") },
  ];
}
