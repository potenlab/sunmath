"use client";

import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2, ScanLine } from "lucide-react";
import { ProblemSelector } from "@/components/grading/problem-selector";
import { ImageUploader } from "@/components/grading/image-uploader";
import { PipelineProgress } from "@/components/grading/pipeline-progress";
import { useGradingPipeline } from "../hooks/use-grading-pipeline";

interface SubmissionPanelProps {
  pipeline: ReturnType<typeof useGradingPipeline>;
}

export function SubmissionPanel({ pipeline }: SubmissionPanelProps) {
  const t = useTranslations("grading");

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="text-lg">{t("gradeSubmission")}</CardTitle>
        <CardDescription>{t("gradeSubmissionDesc")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <ProblemSelector
          selectedProblemId={pipeline.selectedProblemId}
          selectedProblem={pipeline.selectedProblem}
          onSelect={pipeline.handleSelectProblem}
        />

        <ImageUploader
          uploadedFile={pipeline.uploadedFile}
          previewUrl={pipeline.previewUrl}
          isProcessing={pipeline.isProcessing}
          fileInputRef={pipeline.fileInputRef}
          cameraInputRef={pipeline.cameraInputRef}
          onFileSelected={pipeline.handleFileSelected}
          onClear={pipeline.handleClearFile}
        />

        <button
          onClick={pipeline.handleGradeAnswer}
          disabled={
            !pipeline.selectedProblem ||
            !pipeline.uploadedFile ||
            pipeline.isProcessing
          }
          className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 px-4 text-sm font-medium text-white shadow-sm transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {pipeline.isProcessing ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              {pipeline.pipelineStep === "ocr"
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

        <PipelineProgress
          pipelineStep={pipeline.pipelineStep}
          ocrText={pipeline.ocrText}
          ocrConfidence={pipeline.ocrConfidence}
          result={pipeline.result}
        />
      </CardContent>
    </Card>
  );
}
