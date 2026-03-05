import { useState, useCallback } from "react";
import type { RegisteredProblem, DuplicateInfo } from "../types";
import { SEED_PROBLEM } from "../data/mock";

export function useProblemRegistration(duplicateMode: "warn" | "block") {
  const [problemContent, setProblemContent] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");
  const [expectedForm, setExpectedForm] = useState("");
  const [targetGrade, setTargetGrade] = useState("");
  const [gradingHints, setGradingHints] = useState("");

  const [problems, setProblems] = useState<RegisteredProblem[]>([SEED_PROBLEM]);
  const [nextId, setNextId] = useState(2);

  const [registrationMessage, setRegistrationMessage] = useState<string | null>(null);
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const [duplicateInfo, setDuplicateInfo] = useState<DuplicateInfo | null>(null);

  const isFactoringRelated = useCallback((content: string) => {
    const lower = content.toLowerCase();
    return (
      lower.includes("factor") ||
      lower.includes("factorise") ||
      lower.includes("factorize")
    );
  }, []);

  const resetForm = useCallback(() => {
    setProblemContent("");
    setCorrectAnswer("");
    setExpectedForm("");
    setTargetGrade("");
    setGradingHints("");
  }, []);

  const addProblem = useCallback(() => {
    const concepts = isFactoringRelated(problemContent)
      ? ["Factoring", "Quadratic expressions", "Polynomial operations"]
      : ["Geometry", "Circle properties"];

    const newProblem: RegisteredProblem = {
      id: nextId,
      content: problemContent,
      correctAnswer,
      expectedForm,
      targetGrade,
      gradingHints,
      concepts,
    };

    setProblems((prev) => [...prev, newProblem]);
    setNextId((prev) => prev + 1);
    resetForm();
    setRegistrationMessage("Problem registered successfully!");
    setTimeout(() => setRegistrationMessage(null), 3000);
  }, [
    problemContent,
    correctAnswer,
    expectedForm,
    targetGrade,
    gradingHints,
    nextId,
    isFactoringRelated,
    resetForm,
  ]);

  const handleRegisterProblem = useCallback(() => {
    if (!problemContent.trim()) return;

    const hasFactoringProblem = problems.some((p) =>
      isFactoringRelated(p.content)
    );

    if (isFactoringRelated(problemContent) && hasFactoringProblem) {
      const existing = problems.find((p) => isFactoringRelated(p.content))!;

      if (duplicateMode === "block") {
        setRegistrationMessage(
          "Registration blocked: Duplicate problem detected (similarity: 0.92). Change mode to 'Warn' to override."
        );
        setTimeout(() => setRegistrationMessage(null), 5000);
        return;
      }

      setDuplicateInfo({
        similarity: 0.92,
        existingProblem: existing,
        sharedConcepts: [
          "Factoring",
          "Quadratic expressions",
          "Polynomial operations",
        ],
        differences: [
          "Different coefficients (5x+6 vs 7x+12)",
          "Different factor pairs ((2,3) vs (3,4))",
          "Same difficulty level",
        ],
      });
      setDuplicateDialogOpen(true);
    } else {
      addProblem();
    }
  }, [problemContent, problems, duplicateMode, isFactoringRelated, addProblem]);

  const handleRegisterAnyway = useCallback(() => {
    setDuplicateDialogOpen(false);
    setDuplicateInfo(null);
    addProblem();
  }, [addProblem]);

  const handleDeleteProblem = useCallback((id: number) => {
    setProblems((prev) => prev.filter((p) => p.id !== id));
  }, []);

  return {
    problemContent,
    setProblemContent,
    correctAnswer,
    setCorrectAnswer,
    expectedForm,
    setExpectedForm,
    targetGrade,
    setTargetGrade,
    gradingHints,
    setGradingHints,
    problems,
    registrationMessage,
    duplicateDialogOpen,
    setDuplicateDialogOpen,
    duplicateInfo,
    setDuplicateInfo,
    handleRegisterProblem,
    handleRegisterAnyway,
    handleDeleteProblem,
  };
}
