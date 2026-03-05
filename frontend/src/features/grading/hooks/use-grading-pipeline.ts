import { useState, useCallback, useRef } from "react";
import type { GradingResult, MockProblem, PipelineStep } from "../types";
import { MOCK_PROBLEMS, MOCK_OCR } from "../data/mock";
import { normalize, gradeAnswer } from "../utils/grading";

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
  const cacheRef = useRef<Map<string, GradingResult>>(new Map());
  const [stats, setStats] = useState({
    cacheHits: 0,
    sympyJudgments: 0,
    llmJudgments: 0,
  });

  const selectedProblem = MOCK_PROBLEMS.find(
    (p) => p.id === selectedProblemId
  );

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

  const handleGradeAnswer = useCallback(() => {
    if (!selectedProblem || !uploadedFile) return;

    const mockOcr = MOCK_OCR[selectedProblem.id] ?? {
      text: "Unable to parse",
      confidence: 0.5,
    };

    const cacheKey = `${selectedProblem.id}|${normalize(mockOcr.text)}`;
    if (cacheRef.current.has(cacheKey)) {
      const cached = cacheRef.current.get(cacheKey)!;
      setPipelineStep("done");
      setOcrText(cached.ocr_text);
      setOcrConfidence(cached.ocr_confidence);
      setResult({ ...cached, judged_by: "cache" });
      setStats((prev) => ({ ...prev, cacheHits: prev.cacheHits + 1 }));
      return;
    }

    setPipelineStep("ocr");
    setOcrText(null);
    setOcrConfidence(null);
    setResult(null);

    setTimeout(() => {
      setOcrText(mockOcr.text);
      setOcrConfidence(mockOcr.confidence);

      setPipelineStep("grading");

      setTimeout(() => {
        const { is_correct, judged_by, reasoning } = gradeAnswer(
          selectedProblem,
          mockOcr.text
        );

        const gradingResult: GradingResult = {
          is_correct,
          judged_by,
          reasoning,
          problem: selectedProblem,
          ocr_text: mockOcr.text,
          ocr_confidence: mockOcr.confidence,
        };

        cacheRef.current.set(cacheKey, gradingResult);
        setResult(gradingResult);
        setPipelineStep("done");

        setStats((prev) => {
          if (judged_by === "llm") {
            return { ...prev, llmJudgments: prev.llmJudgments + 1 };
          }
          return { ...prev, sympyJudgments: prev.sympyJudgments + 1 };
        });
      }, 1200);
    }, 1800);
  }, [selectedProblem, uploadedFile]);

  const isProcessing = pipelineStep === "ocr" || pipelineStep === "grading";

  return {
    selectedProblemId,
    selectedProblem,
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
    problems: MOCK_PROBLEMS,
  };
}
