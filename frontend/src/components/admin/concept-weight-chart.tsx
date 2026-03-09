import { useTranslations } from "next-intl";
import { Scale } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { ConceptWeightDetail } from "@/features/admin/types";

interface ConceptWeightChartProps {
  evaluationConcepts: ConceptWeightDetail[];
  requiredConcepts: ConceptWeightDetail[];
}

function WeightBar({
  concepts,
  gradient,
}: {
  concepts: ConceptWeightDetail[];
  gradient: string;
}) {
  const sorted = [...concepts].sort((a, b) => b.weight - a.weight);
  return (
    <div className="space-y-3">
      {sorted.map((concept) => (
        <div key={concept.id} className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{concept.name}</span>
            <span className="text-xs font-mono text-muted-foreground">
              {concept.weight.toFixed(2)}
            </span>
          </div>
          <div className="h-2.5 rounded-full bg-muted">
            <div
              className={`h-full rounded-full bg-gradient-to-r ${gradient} transition-all`}
              style={{ width: `${concept.weight * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ConceptWeightChart({
  evaluationConcepts,
  requiredConcepts,
}: ConceptWeightChartProps) {
  const t = useTranslations("problemDetail");

  const isEmpty =
    evaluationConcepts.length === 0 && requiredConcepts.length === 0;

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Scale className="size-4 text-amber-500" />
          {t("conceptWeights")}
        </CardTitle>
        <CardDescription>{t("weightExplanation")}</CardDescription>
      </CardHeader>
      <CardContent>
        {isEmpty ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            {t("noConcepts")}
          </p>
        ) : (
          <div className="space-y-5">
            {evaluationConcepts.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-amber-600">
                  {t("evaluates")}
                </h4>
                <WeightBar
                  concepts={evaluationConcepts}
                  gradient="from-amber-400 to-orange-500"
                />
              </div>
            )}

            {evaluationConcepts.length > 0 &&
              requiredConcepts.length > 0 && <Separator />}

            {requiredConcepts.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-blue-600">
                  {t("requires")}
                </h4>
                <WeightBar
                  concepts={requiredConcepts}
                  gradient="from-blue-400 to-cyan-500"
                />
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
