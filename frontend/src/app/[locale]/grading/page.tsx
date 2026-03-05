"use client";

import { useState, useCallback, useRef } from "react";
import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ClipboardCheck,
  Zap,
  Database,
  Brain,
  CheckCircle2,
  XCircle,
  Upload,
  Camera,
  ImageIcon,
  Loader2,
  X,
  ScanLine,
  Check,
} from "lucide-react";

interface MockProblem {
  id: string;
  content: string;
  correct_answer: string | null;
  expected_form: string | null;
  grading_hints: string | null;
  evaluation_concepts: string[];
}

interface GradingResult {
  is_correct: boolean;
  judged_by: string;
  reasoning: string;
  problem: MockProblem;
  ocr_text: string;
  ocr_confidence: number;
}

const MOCK_PROBLEMS: MockProblem[] = [
  {
    id: "1",
    content: "Factor x\u00B2+2x+1",
    correct_answer: "(x+1)\u00B2",
    expected_form: "factored",
    grading_hints: "Must be in factored form",
    evaluation_concepts: ["Factoring", "Perfect square trinomial"],
  },
  {
    id: "2",
    content: "Expand (x+1)\u00B2",
    correct_answer: "x\u00B2+2x+1",
    expected_form: null,
    grading_hints: null,
    evaluation_concepts: ["Polynomial expansion"],
  },
  {
    id: "3",
    content: "Find the distance between A(1,2) and B(4,6)",
    correct_answer: "5",
    expected_form: "numeric",
    grading_hints: "Calculation must be completed to a number",
    evaluation_concepts: ["Distance formula"],
  },
  {
    id: "4",
    content:
      "Prove that the sum of interior angles of a triangle is 180\u00B0",
    correct_answer: null,
    expected_form: "proof",
    grading_hints: "Must use alternate angle property of parallel lines",
    evaluation_concepts: ["Triangle angle sum", "Parallel line properties"],
  },
];

// Mock OCR results keyed by problem id
const MOCK_OCR: Record<string, { text: string; confidence: number }> = {
  "1": { text: "x\u00B2+2x+1", confidence: 0.94 },
  "2": { text: "x\u00B2+2x+1", confidence: 0.96 },
  "3": { text: "\u221A25", confidence: 0.88 },
  "4": {
    text: "Draw a line through one vertex parallel to the opposite side. By alternate interior angles, the two angles at the vertex equal the two base angles. Together with the vertex angle, they form a straight line = 180\u00B0.",
    confidence: 0.72,
  },
};

type PipelineStep = "idle" | "ocr" | "grading" | "done";

function normalize(s: string): string {
  return s.replace(/\s+/g, "").toLowerCase();
}

function gradeAnswer(
  problem: MockProblem,
  answer: string
): { is_correct: boolean; judged_by: string; reasoning: string } {
  const trimmed = answer.trim();
  const norm = normalize(trimmed);

  switch (problem.id) {
    case "1": {
      const factoredForms = ["(x+1)\u00B2", "(x+1)^2", "(x+1)(x+1)"];
      if (factoredForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: true,
          judged_by: "sympy",
          reasoning:
            "The answer is mathematically correct and is in factored form as required.",
        };
      }
      const expandedForms = ["x\u00B2+2x+1", "x^2+2x+1"];
      if (expandedForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: false,
          judged_by: "graphrag+sympy",
          reasoning:
            "The answer is mathematically equivalent but NOT in factored form. The problem requires the answer in factored form (expected_form: factored).",
        };
      }
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning:
          "The answer is not mathematically equivalent to (x+1)\u00B2.",
      };
    }
    case "2": {
      const validForms = [
        "x\u00B2+2x+1",
        "x^2+2x+1",
        "(x+1)\u00B2",
        "(x+1)^2",
        "(x+1)(x+1)",
        "1+2x+x\u00B2",
        "1+2x+x^2",
      ];
      if (validForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: true,
          judged_by: "sympy",
          reasoning:
            "The answer is mathematically equivalent to x\u00B2+2x+1. No specific form restriction applies.",
        };
      }
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning:
          "The answer is not mathematically equivalent to x\u00B2+2x+1.",
      };
    }
    case "3": {
      if (norm === "5") {
        return {
          is_correct: true,
          judged_by: "sympy",
          reasoning: "The answer is correct. The distance is 5.",
        };
      }
      const nonNumericForms = ["\u221A25", "sqrt(25)", "\\sqrt{25}"];
      if (nonNumericForms.some((f) => normalize(f) === norm)) {
        return {
          is_correct: false,
          judged_by: "graphrag+sympy",
          reasoning:
            "The answer is mathematically equivalent but NOT in numeric form. The problem requires the answer as a number (expected_form: numeric).",
        };
      }
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning: "The answer is not equal to 5.",
      };
    }
    case "4": {
      if (trimmed.length > 0) {
        return {
          is_correct: true,
          judged_by: "llm",
          reasoning:
            "LLM evaluation: The proof demonstrates understanding of the triangle angle sum property. The argument references relevant geometric principles.",
        };
      }
      return {
        is_correct: false,
        judged_by: "llm",
        reasoning: "No answer was provided.",
      };
    }
    default:
      return {
        is_correct: false,
        judged_by: "sympy",
        reasoning: "Unknown problem.",
      };
  }
}

export default function GradingPage() {
  const t = useTranslations("grading");

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

  // Single button: OCR → Grade in one pipeline
  const handleGradeAnswer = useCallback(() => {
    if (!selectedProblem || !uploadedFile) return;

    const mockOcr = MOCK_OCR[selectedProblem.id] ?? {
      text: "Unable to parse",
      confidence: 0.5,
    };

    // Check cache first
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

    // Step 1: OCR
    setPipelineStep("ocr");
    setOcrText(null);
    setOcrConfidence(null);
    setResult(null);

    setTimeout(() => {
      setOcrText(mockOcr.text);
      setOcrConfidence(mockOcr.confidence);

      // Step 2: Grading
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

  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 shadow-sm">
            <ClipboardCheck className="size-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {t("title")}
            </h1>
            <p className="text-sm text-muted-foreground">
              {t("description")}
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* LEFT: Submission */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg">{t("gradeSubmission")}</CardTitle>
            <CardDescription>{t("gradeSubmissionDesc")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Select problem */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">{t("problem")}</label>
              <Select
                value={selectedProblemId}
                onValueChange={(val) => {
                  setSelectedProblemId(val);
                  setPipelineStep("idle");
                  setOcrText(null);
                  setOcrConfidence(null);
                  setResult(null);
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder={t("problemPlaceholder")} />
                </SelectTrigger>
                <SelectContent>
                  {MOCK_PROBLEMS.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.content}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedProblem && (
              <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-3 space-y-1">
                {selectedProblem.expected_form && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Expected form:</span>{" "}
                    {selectedProblem.expected_form}
                  </p>
                )}
                {selectedProblem.grading_hints && (
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Grading hints:</span>{" "}
                    {selectedProblem.grading_hints}
                  </p>
                )}
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedProblem.evaluation_concepts.map((c) => (
                    <Badge
                      key={c}
                      variant="secondary"
                      className="text-[10px] px-1.5 py-0"
                    >
                      {c}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Upload answer image */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                Student Answer Sheet
              </label>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelected(file);
                }}
              />
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelected(file);
                }}
              />

              {!uploadedFile ? (
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-muted-foreground/25 bg-muted/20 py-6 transition-colors hover:border-emerald-400/50 hover:bg-emerald-50/30"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100">
                      <Upload className="size-5 text-emerald-600" />
                    </div>
                    <div className="text-center">
                      <p className="text-xs font-medium">Upload Image</p>
                      <p className="text-[10px] text-muted-foreground">
                        PNG, JPG, PDF
                      </p>
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => cameraInputRef.current?.click()}
                    className="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-muted-foreground/25 bg-muted/20 py-6 transition-colors hover:border-teal-400/50 hover:bg-teal-50/30"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-100">
                      <Camera className="size-5 text-teal-600" />
                    </div>
                    <div className="text-center">
                      <p className="text-xs font-medium">Take Photo</p>
                      <p className="text-[10px] text-muted-foreground">
                        Use camera
                      </p>
                    </div>
                  </button>
                </div>
              ) : (
                <div className="relative rounded-lg border bg-muted/20 p-2">
                  <button
                    onClick={handleClearFile}
                    disabled={isProcessing}
                    className="absolute -right-2 -top-2 z-10 flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-red-600 shadow-sm hover:bg-red-200 transition-colors disabled:opacity-50"
                  >
                    <X className="size-3.5" />
                  </button>
                  {previewUrl && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={previewUrl}
                      alt="Uploaded answer"
                      className="mx-auto max-h-36 rounded-md object-contain"
                    />
                  )}
                  <p className="mt-2 text-center text-xs text-muted-foreground truncate flex items-center justify-center gap-1.5">
                    <ImageIcon className="size-3" />
                    {uploadedFile.name}
                  </p>
                </div>
              )}
            </div>

            {/* Single Grade Answer button */}
            <button
              onClick={handleGradeAnswer}
              disabled={!selectedProblem || !uploadedFile || isProcessing}
              className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 px-4 text-sm font-medium text-white shadow-sm transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  {pipelineStep === "ocr"
                    ? "Running OCR..."
                    : "Grading..."}
                </>
              ) : (
                <>
                  <ScanLine className="size-4" />
                  {t("gradeAnswer")}
                </>
              )}
            </button>

            {/* Pipeline progress steps */}
            {pipelineStep !== "idle" && (
              <div className="rounded-lg border bg-muted/20 p-3 space-y-2.5">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Pipeline
                </p>

                {/* Step 1: OCR */}
                <div className="flex items-center gap-2.5">
                  {pipelineStep === "ocr" ? (
                    <Loader2 className="size-4 shrink-0 animate-spin text-sky-600" />
                  ) : (
                    <div className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-500">
                      <Check className="size-2.5 text-white" />
                    </div>
                  )}
                  <span
                    className={`text-xs font-medium ${pipelineStep === "ocr" ? "text-sky-700" : "text-emerald-700"}`}
                  >
                    Gemini Vision OCR
                  </span>
                  {ocrConfidence !== null && (
                    <Badge
                      variant="outline"
                      className={`ml-auto text-[10px] px-1.5 py-0 ${
                        ocrConfidence >= 0.9
                          ? "border-emerald-300 text-emerald-700 bg-emerald-50"
                          : ocrConfidence >= 0.8
                            ? "border-amber-300 text-amber-700 bg-amber-50"
                            : "border-red-300 text-red-700 bg-red-50"
                      }`}
                    >
                      {(ocrConfidence * 100).toFixed(0)}%
                    </Badge>
                  )}
                </div>

                {/* OCR extracted text */}
                {ocrText && (
                  <div className="ml-6 rounded-md border bg-white/80 px-2.5 py-1.5">
                    <p className="text-[10px] text-muted-foreground mb-0.5">
                      Extracted:
                    </p>
                    <p className="text-xs font-mono font-medium truncate">
                      {ocrText}
                    </p>
                  </div>
                )}

                {/* Step 2: Grading */}
                {(pipelineStep === "grading" || pipelineStep === "done") && (
                  <div className="flex items-center gap-2.5">
                    {pipelineStep === "grading" ? (
                      <Loader2 className="size-4 shrink-0 animate-spin text-violet-600" />
                    ) : (
                      <div className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-500">
                        <Check className="size-2.5 text-white" />
                      </div>
                    )}
                    <span
                      className={`text-xs font-medium ${pipelineStep === "grading" ? "text-violet-700" : "text-emerald-700"}`}
                    >
                      Intent-Based Grading
                    </span>
                    {result && (
                      <Badge
                        variant="outline"
                        className={`ml-auto text-[10px] px-1.5 py-0 ${
                          result.judged_by === "cache"
                            ? "border-blue-300 text-blue-700 bg-blue-50"
                            : result.judged_by === "llm"
                              ? "border-violet-300 text-violet-700 bg-violet-50"
                              : "border-emerald-300 text-emerald-700 bg-emerald-50"
                        }`}
                      >
                        {result.judged_by}
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* RIGHT: Result */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg">{t("gradingResult")}</CardTitle>
            <CardDescription>{t("gradingResultDesc")}</CardDescription>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-4">
                <div
                  className={`flex items-center gap-3 rounded-lg border p-4 ${
                    result.is_correct
                      ? "border-emerald-200 bg-emerald-50"
                      : "border-red-200 bg-red-50"
                  }`}
                >
                  {result.is_correct ? (
                    <CheckCircle2 className="size-8 text-emerald-600 shrink-0" />
                  ) : (
                    <XCircle className="size-8 text-red-600 shrink-0" />
                  )}
                  <div>
                    <p
                      className={`text-lg font-bold ${
                        result.is_correct
                          ? "text-emerald-700"
                          : "text-red-700"
                      }`}
                    >
                      {result.is_correct ? t("correct") : t("wrong")}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-muted-foreground">
                        Judged by:
                      </span>
                      <Badge
                        variant="outline"
                        className={`text-[10px] px-1.5 py-0 ${
                          result.judged_by === "cache"
                            ? "border-blue-300 text-blue-700 bg-blue-50"
                            : result.judged_by === "llm"
                              ? "border-violet-300 text-violet-700 bg-violet-50"
                              : "border-emerald-300 text-emerald-700 bg-emerald-50"
                        }`}
                      >
                        {result.judged_by}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* OCR info */}
                <div className="rounded-lg border bg-sky-50/50 p-3 space-y-1">
                  <p className="text-xs font-semibold text-sky-700 flex items-center gap-1.5">
                    <ScanLine className="size-3.5" />
                    OCR Output
                  </p>
                  <p className="text-sm font-mono">{result.ocr_text}</p>
                  <p className="text-[11px] text-muted-foreground">
                    Confidence: {(result.ocr_confidence * 100).toFixed(0)}%
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Reasoning</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {result.reasoning}
                  </p>
                </div>

                <div className="space-y-2 rounded-lg border bg-muted/30 p-3">
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Problem Metadata
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-muted-foreground">
                        Expected form:
                      </span>
                      <p className="font-medium">
                        {result.problem.expected_form ?? "None"}
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">
                        Grading hints:
                      </span>
                      <p className="font-medium">
                        {result.problem.grading_hints ?? "None"}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {result.problem.evaluation_concepts.map((c) => (
                      <Badge
                        key={c}
                        variant="secondary"
                        className="text-[10px] px-1.5 py-0"
                      >
                        {c}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-muted/50">
                  <ClipboardCheck className="size-8 text-muted-foreground/40" />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  {t("noResult")}
                </p>
                <p className="mt-1 text-xs text-muted-foreground/60">
                  {t("noResultHint")}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Cache Statistics */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">
          {t("cacheStatistics")}
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="border-none bg-gradient-to-br from-blue-50 to-sky-50 shadow-sm">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
                <Database className="size-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-700">
                  {stats.cacheHits}
                </p>
                <p className="text-xs text-blue-600/70">
                  {t("cacheHitRate")}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-none bg-gradient-to-br from-emerald-50 to-teal-50 shadow-sm">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
                <Zap className="size-6 text-emerald-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-emerald-700">
                  {stats.sympyJudgments}
                </p>
                <p className="text-xs text-emerald-600/70">
                  {t("sympyEngine")}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card className="border-none bg-gradient-to-br from-violet-50 to-purple-50 shadow-sm">
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100">
                <Brain className="size-6 text-violet-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-violet-700">
                  {stats.llmJudgments}
                </p>
                <p className="text-xs text-violet-600/70">
                  {t("llmFallback")}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Intent-based examples */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">
            {t("intentBasedExamples")}
          </CardTitle>
          <CardDescription>{t("intentBasedExamplesDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-4 rounded-lg border p-4">
              <Badge className="bg-red-100 text-red-700 hover:bg-red-100 shrink-0">
                {t("wrong")}
              </Badge>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {t("example1Problem")}
                </p>
                <p className="text-xs text-muted-foreground">
                  {t("example1Hint")}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4 rounded-lg border p-4">
              <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100 shrink-0">
                {t("correct")}
              </Badge>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {t("example2Problem")}
                </p>
                <p className="text-xs text-muted-foreground">
                  {t("example2Hint")}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4 rounded-lg border p-4">
              <Badge className="bg-red-100 text-red-700 hover:bg-red-100 shrink-0">
                {t("wrong")}
              </Badge>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {t("example3Problem")}
                </p>
                <p className="text-xs text-muted-foreground">
                  {t("example3Hint")}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
