import { useState, useCallback } from "react";
import type { RegisteredProblem, DuplicateInfo, ExpectedForm } from "../types";
import { useCreateProblem } from "../api/use-problems";

export function useProblemRegistration(duplicateMode: "warn" | "block") {
  const [problemContent, setProblemContent] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");
  const [expectedForm, setExpectedForm] = useState("");
  const [targetGrade, setTargetGrade] = useState("");
  const [gradingHints, setGradingHints] = useState("");

  const [problems, setProblems] = useState<RegisteredProblem[]>([]);

  const [registrationMessage, setRegistrationMessage] = useState<string | null>(null);
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const [duplicateInfo, setDuplicateInfo] = useState<DuplicateInfo | null>(null);

  const createProblem = useCreateProblem();

  const resetForm = useCallback(() => {
    setProblemContent("");
    setCorrectAnswer("");
    setExpectedForm("");
    setTargetGrade("");
    setGradingHints("");
  }, []);

  const handleRegisterProblem = useCallback(async () => {
    if (!problemContent.trim()) return;

    try {
      const response = await createProblem.mutateAsync({
        content: problemContent,
        correct_answer: correctAnswer,
        expected_form: (expectedForm as ExpectedForm) || undefined,
        target_grade: targetGrade ? parseInt(targetGrade, 10) : undefined,
        grading_hints: gradingHints || undefined,
        auto_extract_concepts: true,
      });

      // Handle duplicate detection
      if (response.duplicate_check.is_duplicate) {
        if (duplicateMode === "block") {
          setRegistrationMessage(
            `Registration blocked: Duplicate problem detected (similarity: ${response.duplicate_check.similarity_score.toFixed(2)}). Change mode to 'Warn' to override.`
          );
          setTimeout(() => setRegistrationMessage(null), 5000);
          return;
        }

        // In warn mode, show the duplicate dialog
        // Use the first similar problem for display
        if (response.similar_problems.length > 0) {
          const existingId = response.similar_problems[0].question_id;
          setDuplicateInfo({
            similarity: response.duplicate_check.similarity_score,
            existingProblem: {
              id: existingId,
              content: `Problem #${existingId}`,
              correctAnswer: "",
              expectedForm: "",
              targetGrade: "",
              gradingHints: "",
              concepts: response.similar_problems[0].shared_concepts.map(String),
            },
            sharedConcepts: response.similar_problems[0].shared_concepts.map(String),
            differences: [],
          });
          setDuplicateDialogOpen(true);
          return;
        }
      }

      // Success — add to local list and reset
      if (response.problem) {
        const concepts = response.concept_extraction?.evaluation_concept_names ?? [];
        const newProblem: RegisteredProblem = {
          id: response.problem.id,
          content: response.problem.content,
          correctAnswer: response.problem.correct_answer,
          expectedForm: response.problem.expected_form,
          targetGrade: response.problem.target_grade?.toString() ?? "",
          gradingHints: response.problem.grading_hints ?? "",
          concepts,
        };
        setProblems((prev) => [...prev, newProblem]);
        resetForm();
        setRegistrationMessage("Problem registered successfully!");
        setTimeout(() => setRegistrationMessage(null), 3000);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Registration failed";
      // Handle 409 Conflict (duplicate blocked by server)
      if (message.includes("409")) {
        setRegistrationMessage(
          "Registration blocked by server: Duplicate problem detected."
        );
      } else {
        setRegistrationMessage(`Error: ${message}`);
      }
      setTimeout(() => setRegistrationMessage(null), 5000);
    }
  }, [
    problemContent,
    correctAnswer,
    expectedForm,
    targetGrade,
    gradingHints,
    duplicateMode,
    createProblem,
    resetForm,
  ]);

  const handleRegisterAnyway = useCallback(async () => {
    setDuplicateDialogOpen(false);
    setDuplicateInfo(null);
    // Re-submit — the server already registered it in "warn" mode
    // The problem was already created; just add to local state
    setRegistrationMessage("Problem registered (duplicate warning acknowledged).");
    resetForm();
    setTimeout(() => setRegistrationMessage(null), 3000);
  }, [resetForm]);

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
