"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { ArrowLeft, FileText } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { ConceptWeightChart } from "@/components/admin/concept-weight-chart";
import { SimilarProblemsPanel } from "@/components/admin/similar-problems-panel";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  useProblemMetadata,
  useSimilarProblems,
  useConcepts,
} from "../api/use-problems";

interface ProblemDetailProps {
  id: string;
}

export function ProblemDetail({ id }: ProblemDetailProps) {
  const t = useTranslations("problemDetail");
  const problemId = Number(id);
  const isValid = !isNaN(problemId);

  const { data: metadata, isLoading: metadataLoading } = useProblemMetadata(
    isValid ? problemId : null,
  );
  const { data: similarData, isLoading: similarLoading } = useSimilarProblems(
    isValid ? problemId : null,
  );
  const { data: concepts = [] } = useConcepts();

  const conceptNameMap = useMemo(() => {
    const map = new Map<number, string>();
    for (const c of concepts) {
      map.set(c.id, c.name);
    }
    return map;
  }, [concepts]);

  if (!isValid) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        {t("notFound")}
      </div>
    );
  }

  if (metadataLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500" />
      </div>
    );
  }

  if (!metadata) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        {t("notFound")}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        href="/admin/problems"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="size-4" />
        {t("backToProblems")}
      </Link>

      <PageHeader
        icon={FileText}
        iconGradient="from-amber-400 to-orange-500"
        title={`Problem #${metadata.question_id}`}
        description="Concept weight analysis"
      />

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("problemInfo")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Content
            </span>
            <p className="mt-1 text-sm">{metadata.content}</p>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div>
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Correct Answer
              </span>
              <p className="mt-1 text-sm font-mono">{metadata.correct_answer}</p>
            </div>
            <div>
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Expected Form
              </span>
              <div className="mt-1">
                <Badge variant="outline">{metadata.expected_form}</Badge>
              </div>
            </div>
            {metadata.grading_hints && (
              <div>
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Grading Hints
                </span>
                <p className="mt-1 text-sm text-muted-foreground">
                  {metadata.grading_hints}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <ConceptWeightChart
        evaluationConcepts={metadata.evaluation_concepts}
        requiredConcepts={metadata.required_concepts}
      />

      <SimilarProblemsPanel
        similarData={similarData}
        currentMetadata={metadata}
        conceptNameMap={conceptNameMap}
        isLoading={similarLoading}
      />
    </div>
  );
}
