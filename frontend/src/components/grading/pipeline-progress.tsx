import { Badge } from "@/components/ui/badge";
import { Loader2, Check } from "lucide-react";
import type { PipelineStep, GradingResult } from "@/features/grading/types";

interface PipelineProgressProps {
  pipelineStep: PipelineStep;
  ocrText: string | null;
  ocrConfidence: number | null;
  result: GradingResult | null;
}

export function PipelineProgress({
  pipelineStep,
  ocrText,
  ocrConfidence,
  result,
}: PipelineProgressProps) {
  if (pipelineStep === "idle") return null;

  return (
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
          <p className="text-xs font-mono font-medium truncate">{ocrText}</p>
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
  );
}
