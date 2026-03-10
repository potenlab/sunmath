import { useState, useCallback } from "react";
import type { RegisteredProblem, DuplicateInfo, ExpectedForm } from "../types";
import type { ConceptWeightEntry } from "@/components/admin/concept-weight-picker";
import { useCreateProblem } from "../api/use-problems";
import { ApiError } from "@/lib/api";

export function useProblemRegistration(duplicateMode: "warn" | "block") {
  const [problemContent, setProblemContent] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");
  const [expectedForm, setExpectedForm] = useState("");
  const [targetGrade, setTargetGrade] = useState("");
  const [gradingHints, setGradingHints] = useState("");
  const [conceptEntries, setConceptEntries] = useState<ConceptWeightEntry[]>([]);

  const [problems, setProblems] = useState<RegisteredProblem[]>([]);

  const [registrationMessage, setRegistrationMessage] = useState<string | null>(null);
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const [duplicateInfo, setDuplicateInfo] = useState<DuplicateInfo | null>(null);
  const [duplicateBlocked, setDuplicateBlocked] = useState(false);

  const createProblem = useCreateProblem();

  const resetForm = useCallback(() => {
    setProblemContent("");
    setCorrectAnswer("");
    setExpectedForm("");
    setTargetGrade("");
    setGradingHints("");
    setConceptEntries([]);
  }, []);

  const handleRegisterProblem = useCallback(async () => {
    if (!problemContent.trim()) return;

    try {
      // Build concept_weights from picker entries if any
      const hasManualConcepts = conceptEntries.length > 0;
      const conceptWeightsPayload: Record<number, number> | undefined =
        hasManualConcepts
          ? Object.fromEntries(conceptEntries.map((e) => [e.conceptId, e.weight]))
          : undefined;

      const response = await createProblem.mutateAsync({
        content: problemContent,
        correct_answer: correctAnswer,
        expected_form: (expectedForm as ExpectedForm) || undefined,
        target_grade: targetGrade ? parseInt(targetGrade, 10) : undefined,
        grading_hints: gradingHints || undefined,
        concept_weights: conceptWeightsPayload,
        auto_extract_concepts: !hasManualConcepts,
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
          setDuplicateBlocked(false);
          setDuplicateDialogOpen(true);
          return;
        }
      }

      // Success — add to local list and reset
      if (response.problem) {
        // Build concept names + weight map for display
        let concepts: string[];
        const displayWeights: Record<string, number> = {};

        if (hasManualConcepts) {
          // Use manually selected concepts
          concepts = conceptEntries.map((e) => e.name);
          conceptEntries.forEach((e) => {
            displayWeights[e.name] = e.weight;
          });
        } else if (response.concept_extraction) {
          // Use LLM-extracted concepts
          concepts = response.concept_extraction.evaluation_concept_names ?? [];
          const evalWeights = response.concept_extraction.evaluation_concept_weights ?? {};
          const names = response.concept_extraction.evaluation_concept_names ?? [];
          const ids = response.concept_extraction.matched_evaluation_concept_ids ?? [];
          names.forEach((name, i) => {
            const cid = ids[i];
            if (cid !== undefined && evalWeights[cid] !== undefined) {
              displayWeights[name] = evalWeights[cid];
            }
          });
        } else {
          concepts = [];
        }

        const newProblem: RegisteredProblem = {
          id: response.problem.id,
          content: response.problem.content,
          correctAnswer: response.problem.correct_answer,
          expectedForm: response.problem.expected_form,
          targetGrade: response.problem.target_grade?.toString() ?? "",
          gradingHints: response.problem.grading_hints ?? "",
          concepts,
          conceptWeights: displayWeights,
        };
        setProblems((prev) => [...prev, newProblem]);
        resetForm();
        setRegistrationMessage("Problem registered successfully!");
        setTimeout(() => setRegistrationMessage(null), 3000);
      }
    } catch (err: unknown) {
      // Handle 409 Conflict (duplicate blocked by server)
      if (err instanceof ApiError && err.status === 409) {
        try {
          const body = JSON.parse(err.message);
          const detail = body.detail;
          const dupCheck = detail?.duplicate_check;
          const similarProblems = detail?.similar_problems;

          if (dupCheck && similarProblems?.length > 0) {
            const first = similarProblems[0];
            setDuplicateInfo({
              similarity: dupCheck.similarity_score,
              existingProblem: {
                id: first.question_id,
                content: `Problem #${first.question_id}`,
                correctAnswer: "",
                expectedForm: "",
                targetGrade: "",
                gradingHints: "",
                concepts: first.shared_concepts.map(String),
              },
              sharedConcepts: first.shared_concepts.map(String),
              differences: [],
            });
            setDuplicateBlocked(true);
            setDuplicateDialogOpen(true);
            return;
          }
        } catch {
          // JSON parse failed — fall through to generic message
        }
        setRegistrationMessage(
          "Registration blocked by server: Duplicate problem detected."
        );
        setTimeout(() => setRegistrationMessage(null), 5000);
      } else {
        const message = err instanceof Error ? err.message : "Registration failed";
        setRegistrationMessage(`Error: ${message}`);
        setTimeout(() => setRegistrationMessage(null), 5000);
      }
    }
  }, [
    problemContent,
    correctAnswer,
    expectedForm,
    targetGrade,
    gradingHints,
    conceptEntries,
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
    conceptEntries,
    setConceptEntries,
    problems,
    registrationMessage,
    duplicateDialogOpen,
    setDuplicateDialogOpen,
    duplicateInfo,
    setDuplicateInfo,
    duplicateBlocked,
    isRegistering: createProblem.isPending,
    handleRegisterProblem,
    handleRegisterAnyway,
    handleDeleteProblem,
  };
}
