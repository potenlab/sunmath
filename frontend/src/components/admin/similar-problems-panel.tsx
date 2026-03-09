import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { GitCompareArrows } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type {
  SimilarProblemResponse,
  QuestionMetadataResponse,
  ConceptOption,
} from "@/features/admin/types";

interface SimilarProblemsPanelProps {
  similarData: SimilarProblemResponse | undefined;
  currentMetadata: QuestionMetadataResponse | undefined;
  conceptNameMap: Map<number, string>;
  isLoading: boolean;
}

function scoreColor(score: number) {
  if (score >= 0.8) return "from-emerald-400 to-green-500";
  if (score >= 0.5) return "from-amber-400 to-orange-500";
  return "from-gray-300 to-gray-400";
}

function scoreBadgeVariant(score: number): "default" | "secondary" | "outline" {
  if (score >= 0.8) return "default";
  if (score >= 0.5) return "secondary";
  return "outline";
}

export function SimilarProblemsPanel({
  similarData,
  currentMetadata,
  conceptNameMap,
  isLoading,
}: SimilarProblemsPanelProps) {
  const t = useTranslations("problemDetail");

  const problems = similarData?.problems ?? [];
  const details = similarData?.details ?? [];

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <GitCompareArrows className="size-4 text-purple-500" />
          {t("similarProblems")}
        </CardTitle>
        <CardDescription>{t("whyWeightsMatter")}</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-500" />
          </div>
        ) : problems.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            {t("noSimilar")}
          </p>
        ) : (
          <div className="space-y-3">
            {problems.slice(0, 10).map((problem, idx) => {
              const detail = details[idx];
              const score = detail?.similarity_score ?? 0;
              const pct = (score * 100).toFixed(1);

              return (
                <Link
                  key={problem.id}
                  href={`/admin/problems/${problem.id}`}
                  className="block rounded-lg border p-3 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        <span className="text-muted-foreground">
                          #{problem.id}
                        </span>{" "}
                        {problem.content}
                      </p>
                    </div>
                    <Badge variant={scoreBadgeVariant(score)} className="shrink-0">
                      {pct}%
                    </Badge>
                  </div>

                  <div className="mt-2 h-2 rounded-full bg-muted">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${scoreColor(score)} transition-all`}
                      style={{ width: `${score * 100}%` }}
                    />
                  </div>

                  {detail && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {detail.shared_concepts.map((id) => (
                        <Badge
                          key={`shared-${id}`}
                          variant="secondary"
                          className="text-[10px] px-1.5 py-0"
                        >
                          {t("sharedConcepts")}:{" "}
                          {conceptNameMap.get(id) ?? `#${id}`}
                        </Badge>
                      ))}
                      {detail.only_in_new.map((id) => (
                        <Badge
                          key={`new-${id}`}
                          variant="outline"
                          className="text-[10px] px-1.5 py-0 border-amber-300 text-amber-600"
                        >
                          {t("onlyInThis")}:{" "}
                          {conceptNameMap.get(id) ?? `#${id}`}
                        </Badge>
                      ))}
                      {detail.only_in_existing.map((id) => (
                        <Badge
                          key={`existing-${id}`}
                          variant="outline"
                          className="text-[10px] px-1.5 py-0 border-blue-300 text-blue-600"
                        >
                          {t("onlyInOther")}:{" "}
                          {conceptNameMap.get(id) ?? `#${id}`}
                        </Badge>
                      ))}
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
