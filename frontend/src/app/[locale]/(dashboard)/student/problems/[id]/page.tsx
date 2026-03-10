"use client";

import { useState, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { ArrowLeft, Send, Loader2, Upload, Camera, X, TrendingUp, TrendingDown } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useStudentProblem } from "@/features/student/api/use-problems";
import { useSubmitAnswer } from "@/features/student/api/use-answer";
import { useOCR } from "@/features/student/api/use-ocr";
import { useSaveTrainingSample } from "@/features/student/api/use-training-sample";
import { useAuth } from "@/features/auth/context/auth-context";
import { GradingResultCard } from "@/components/grading/grading-result-card";
import type { MasteryUpdate } from "@/features/student/types";

export default function StudentProblemDetailPage() {
  const params = useParams();
  const problemId = parseInt(params.id as string, 10);
  const { user } = useAuth();
  const t = useTranslations("studentProblemDetail");
  const tc = useTranslations("common");
  const { data: problem, isLoading } = useStudentProblem(problemId);
  const submitMutation = useSubmitAnswer();
  const ocrMutation = useOCR();
  const saveTrainingSample = useSaveTrainingSample();

  const [answer, setAnswer] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [ocrText, setOcrText] = useState<string | null>(null);
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [result, setResult] = useState<{
    is_correct: boolean;
    judged_by: string;
    reasoning: string;
    mastery_updates: MasteryUpdate[];
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setUploadedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    },
    [previewUrl]
  );

  const handleClearFile = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setUploadedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, [previewUrl]);

  const handleSubmit = async () => {
    if (!user?.student_id || !problem) return;

    let submittedAnswer = answer.trim();

    // If an image is uploaded and no text was typed, run OCR first
    if (!submittedAnswer && uploadedFile) {
      try {
        setIsRecognizing(true);
        const ocrResult = await ocrMutation.mutateAsync(uploadedFile);
        submittedAnswer = ocrResult.text;
        setOcrText(ocrResult.text);
        setAnswer(ocrResult.text);
      } catch {
        setIsRecognizing(false);
        return;
      } finally {
        setIsRecognizing(false);
      }
    }

    if (!submittedAnswer) return;

    try {
      const res = await submitMutation.mutateAsync({
        student_id: user.student_id,
        question_id: problem.id,
        submitted_answer: submittedAnswer,
      });
      setResult(res);

      // Fire-and-forget: save training sample if correct and image was uploaded
      if (res.is_correct && uploadedFile) {
        saveTrainingSample
          .mutateAsync({ file: uploadedFile, question_id: problem.id })
          .catch((err) => console.warn("Training sample save failed (non-critical):", err));
      }
    } catch {
      // error handled by mutation state
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="py-12 text-center">
        <p className="text-muted-foreground">{t("problemNotFound")}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <Link
        href="/student/problems"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="size-3.5" />
        {t("backToProblems")}
      </Link>

      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="outline">{problem.expected_form}</Badge>
            {problem.target_grade && (
              <Badge variant="secondary">{tc("grade", { grade: problem.target_grade })}</Badge>
            )}
          </div>
          <CardTitle className="text-xl">{t("problemTitle", { id: problem.id })}</CardTitle>
          <CardDescription className="text-base mt-2 whitespace-pre-wrap">
            {problem.content}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {problem.grading_hints && (
            <div className="rounded-lg bg-blue-50 dark:bg-blue-950/30 p-3 text-sm text-blue-700 dark:text-blue-300">
              {t("hint", { hint: problem.grading_hints })}
            </div>
          )}

          {/* Text answer input */}
          <div>
            <label className="block text-sm font-medium mb-1.5">
              {t("yourAnswer")}
            </label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder={t("answerPlaceholder")}
              rows={3}
              className="w-full rounded-lg border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 resize-none"
            />
          </div>

          {/* Image upload */}
          <div>
            <label className="block text-sm font-medium mb-1.5">
              {t("uploadLabel")}
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            {previewUrl ? (
              <div className="relative">
                <img
                  src={previewUrl}
                  alt="Answer preview"
                  className="rounded-lg border max-h-48 object-contain"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-1 right-1 h-7 w-7 bg-white/80 hover:bg-white"
                  onClick={handleClearFile}
                >
                  <X className="size-4" />
                </Button>
              </div>
            ) : (
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="size-4 mr-1" />
                  {t("uploadImage")}
                </Button>
              </div>
            )}
          </div>

          <Button
            className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium"
            onClick={handleSubmit}
            disabled={
              (!answer.trim() && !uploadedFile) || isRecognizing || submitMutation.isPending
            }
          >
            {isRecognizing ? (
              <>
                <Loader2 className="size-4 animate-spin mr-1" />
                {t("recognizing")}
              </>
            ) : submitMutation.isPending ? (
              <>
                <Loader2 className="size-4 animate-spin mr-1" />
                {t("grading")}
              </>
            ) : (
              <>
                <Send className="size-4 mr-1" />
                {t("submitAnswer")}
              </>
            )}
          </Button>

          {ocrMutation.isError && (
            <div className="rounded-lg bg-red-50 dark:bg-red-950/30 p-3 text-sm text-red-600 dark:text-red-400">
              {t("ocrFailed")}
            </div>
          )}

          {submitMutation.isError && (
            <div className="rounded-lg bg-red-50 dark:bg-red-950/30 p-3 text-sm text-red-600 dark:text-red-400">
              {t("submitFailed")}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Result */}
      {result && (
        <Card className="shadow-sm animate-in fade-in slide-in-from-bottom-4">
          <CardContent className="pt-6">
            <GradingResultCard
              result={{
                is_correct: result.is_correct,
                judged_by: result.judged_by,
                reasoning: result.reasoning,
                problem,
                ocr_text: ocrText || answer,
                ocr_confidence: 1.0,
              }}
            />
          </CardContent>
        </Card>
      )}

      {/* Mastery Updates */}
      {result && result.mastery_updates && result.mastery_updates.length > 0 && (
        <Card className="shadow-sm animate-in fade-in slide-in-from-bottom-4 delay-150">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              {result.is_correct ? (
                <TrendingUp className="size-4 text-green-500" />
              ) : (
                <TrendingDown className="size-4 text-red-500" />
              )}
              {t("masteryUpdated")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {result.mastery_updates.map((mu) => (
              <div key={mu.concept_id} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium truncate mr-2">
                    {mu.concept_name}
                  </span>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-muted-foreground">
                      {Math.round(mu.old_mastery * 100)}%
                    </span>
                    <span className="text-muted-foreground">&rarr;</span>
                    <span className="font-medium">
                      {Math.round(mu.new_mastery * 100)}%
                    </span>
                    <Badge
                      variant={mu.delta > 0 ? "default" : "destructive"}
                      className="text-xs px-1.5 py-0"
                    >
                      {mu.delta > 0 ? "+" : ""}
                      {Math.round(mu.delta * 100)}%
                    </Badge>
                  </div>
                </div>
                <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.round(mu.new_mastery * 100)}%`,
                      background:
                        mu.delta > 0
                          ? "linear-gradient(90deg, #22c55e, #4ade80)"
                          : "linear-gradient(90deg, #ef4444, #f87171)",
                    }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
