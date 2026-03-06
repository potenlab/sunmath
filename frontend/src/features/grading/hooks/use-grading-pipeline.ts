import { useState, useCallback, useRef } from "react";
import type { GradingResult, ProblemResponse, PipelineStep } from "../types";
import { useGradeMutation } from "../api/use-grade";
import { useSaveTrainingSample } from "@/features/student/api/use-training-sample";
import { useQuery } from "@tanstack/react-query";
import { get, postFormData } from "@/lib/api";

export function useGradingPipeline() {
  const [selectedProblemId, setSelectedProblemId] = useState<string>("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [pipelineStep, setPipelineStep] = useState<PipelineStep>("idle");
  const [ocrText, setOcrText] = useState<string | null>(null);
  const [ocrConfidence, setOcrConfidence] = useState<number | null>(null);
  const [result, setResult] = useState<GradingResult | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [stats, setStats] = useState({
    cacheHits: 0,
    sympyJudgments: 0,
    llmJudgments: 0,
  });

  // Fetch the selected problem from the API
  const problemId = selectedProblemId ? parseInt(selectedProblemId, 10) : null;
  const { data: selectedProblem } = useQuery({
    queryKey: ["problems", problemId],
    queryFn: () => get<ProblemResponse>(`/problems/${problemId}`),
    enabled: problemId !== null && !isNaN(problemId),
  });

  const gradeMutation = useGradeMutation();
  const saveTrainingSample = useSaveTrainingSample();

  const handleFileSelected = useCallback(
    (file: File) => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setUploadedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setPipelineStep("idle");
      setOcrText(null);
      setOcrConfidence(null);
      setResult(null);
    },
    [previewUrl]
  );

  const handleClearFile = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setUploadedFile(null);
    setPreviewUrl(null);
    setPipelineStep("idle");
    setOcrText(null);
    setOcrConfidence(null);
    setResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (cameraInputRef.current) cameraInputRef.current.value = "";
  }, [previewUrl]);

  const handleSelectProblem = useCallback((val: string) => {
    setSelectedProblemId(val);
    setPipelineStep("idle");
    setOcrText(null);
    setOcrConfidence(null);
    setResult(null);
  }, []);

  const handleGradeAnswer = useCallback(async () => {
    if (!selectedProblem || !uploadedFile) return;

    setPipelineStep("ocr");
    setOcrText(null);
    setOcrConfidence(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", uploadedFile);
    const ocrResult = await postFormData<{ text: string; confidence: number }>(
      "/ocr/recognize",
      formData,
    );
    setOcrText(ocrResult.text);
    setOcrConfidence(ocrResult.confidence);

    setPipelineStep("grading");

    try {
      // Call real backend grading API
      // student_id=1 is a placeholder — wire to real student context when available
      const gradeResponse = await gradeMutation.mutateAsync({
        student_id: 1,
        question_id: selectedProblem.id,
        submitted_answer: ocrResult.text,
      });

      const gradingResult: GradingResult = {
        is_correct: gradeResponse.is_correct,
        judged_by: gradeResponse.judged_by,
        reasoning: gradeResponse.reasoning,
        problem: selectedProblem,
        ocr_text: ocrResult.text,
        ocr_confidence: ocrResult.confidence,
      };

      setResult(gradingResult);
      setPipelineStep("done");

      // Fire-and-forget: save training sample if answer was correct and image was uploaded
      if (gradeResponse.is_correct && uploadedFile && selectedProblem) {
        saveTrainingSample
          .mutateAsync({ file: uploadedFile, question_id: selectedProblem.id })
          .catch((err) => console.warn("Training sample save failed (non-critical):", err));
      }

      setStats((prev) => {
        if (gradeResponse.cached) {
          return { ...prev, cacheHits: prev.cacheHits + 1 };
        }
        if (gradeResponse.judged_by === "llm") {
          return { ...prev, llmJudgments: prev.llmJudgments + 1 };
        }
        return { ...prev, sympyJudgments: prev.sympyJudgments + 1 };
      });
    } catch {
      setPipelineStep("idle");
    }
  }, [selectedProblem, uploadedFile, gradeMutation]);

  const isProcessing = pipelineStep === "ocr" || pipelineStep === "grading";

  return {
    selectedProblemId,
    selectedProblem: selectedProblem ?? null,
    uploadedFile,
    previewUrl,
    pipelineStep,
    ocrText,
    ocrConfidence,
    result,
    fileInputRef,
    cameraInputRef,
    stats,
    isProcessing,
    handleSelectProblem,
    handleFileSelected,
    handleClearFile,
    handleGradeAnswer,
  };
}
