import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CheckCircle2, XCircle, ClipboardCheck, ScanLine } from "lucide-react";
import type { GradingResult } from "@/features/grading/types";

interface GradingResultCardProps {
  result: GradingResult | null;
}

export function GradingResultCard({ result }: GradingResultCardProps) {
  const t = useTranslations("grading");

  return (
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
                    result.is_correct ? "text-emerald-700" : "text-red-700"
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
                  <span className="text-muted-foreground">Expected form:</span>
                  <p className="font-medium">
                    {result.problem.expected_form ?? "None"}
                  </p>
                </div>
                <div>
                  <span className="text-muted-foreground">Grading hints:</span>
                  <p className="font-medium">
                    {result.problem.grading_hints ?? "None"}
                  </p>
                </div>
              </div>
              {result.problem.target_grade && (
                <div>
                  <span className="text-muted-foreground">Target grade:</span>
                  <p className="font-medium">{result.problem.target_grade}</p>
                </div>
              )}
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
  );
}
