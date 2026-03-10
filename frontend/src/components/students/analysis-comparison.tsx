import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { XCircle, Zap } from "lucide-react";
import type { ConceptFrequency } from "@/features/students/types";

interface AnalysisComparisonProps {
  /** Top failing concepts from diagnosis (shown in naive side) */
  conceptFrequencies: ConceptFrequency[];
  /** Root cause concepts identified by GraphRAG */
  coreWeaknesses: string[];
  /** How many units/concepts are affected downstream */
  affectedCount: number;
}

export function AnalysisComparison({
  conceptFrequencies,
  coreWeaknesses,
  affectedCount,
}: AnalysisComparisonProps) {
  const t = useTranslations("analysisComparison");

  // Naive side: show the top failing concepts (up to 5)
  const topConcepts = conceptFrequencies.slice(0, 5).map((c) => c.concept_name);

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {/* Naive Analysis */}
      <Card className="border-2 border-red-200 bg-red-50/40 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base text-red-700">
            <XCircle className="size-4 text-red-500" />
            {t("naiveTitle")}
          </CardTitle>
          <CardDescription className="text-red-600/70">
            {t("naiveDesc")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-red-800 font-medium">
              {t("studentWeakIn")}
            </p>
            <div className="flex flex-wrap gap-2">
              {topConcepts.map((concept) => (
                <Badge key={concept} className="bg-red-100 text-red-700 hover:bg-red-100 border border-red-200">
                  {concept}
                </Badge>
              ))}
            </div>
            <div className="mt-3 rounded-lg bg-red-100/60 p-3">
              <p className="text-xs text-red-600">
                {t("naiveConclusion", { count: topConcepts.length })}
              </p>
              <p className="mt-2 text-xs text-red-500/80">
                {t("naiveNoRootCause", { count: topConcepts.length })}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* GraphRAG Analysis */}
      <Card className="border-2 border-emerald-200 bg-emerald-50/40 shadow-sm ring-2 ring-emerald-100">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base text-emerald-700">
            <Zap className="size-4 text-emerald-500" />
            {t("graphragTitle")}
          </CardTitle>
          <CardDescription className="text-emerald-600/70">
            {t("graphragDesc")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-emerald-800 font-medium">
              {t("rootCauseIdentified")}
            </p>
            <div className="flex items-center gap-2 flex-wrap">
              {coreWeaknesses.map((weakness) => (
                <Badge
                  key={weakness}
                  className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100 border border-emerald-300 font-bold"
                >
                  {weakness}
                </Badge>
              ))}
              <span className="text-xs text-emerald-600">
                {coreWeaknesses.length === 1
                  ? t("sharedRootCause")
                  : t("sharedRootCauses")}
              </span>
            </div>
            <div className="mt-3 rounded-lg bg-emerald-100/60 p-3">
              <p className="text-xs text-emerald-700 font-semibold">
                {t("graphragConclusion", {
                  rootCount: coreWeaknesses.length,
                  affectedCount,
                })}
              </p>
              <p className="mt-2 text-xs text-emerald-600/80">
                {t("graphragBenefit", {
                  rootCount: coreWeaknesses.length,
                  affectedCount,
                })}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
