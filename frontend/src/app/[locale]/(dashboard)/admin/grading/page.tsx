"use client";

import { useTranslations } from "next-intl";
import { ClipboardCheck, Database, Zap, Brain } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { SubmissionPanel } from "@/features/grading/components/submission-panel";
import { ResultPanel } from "@/features/grading/components/result-panel";
import { IntentExamples } from "@/components/grading/intent-examples";
import { useGradingPipeline } from "@/features/grading/hooks/use-grading-pipeline";

export default function AdminGradingPage() {
  const t = useTranslations("grading");
  const pipeline = useGradingPipeline();

  return (
    <div className="space-y-8">
      <PageHeader
        icon={ClipboardCheck}
        iconGradient="from-emerald-400 to-teal-500"
        title={t("title")}
        description={t("description")}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <SubmissionPanel pipeline={pipeline} />
        <ResultPanel result={pipeline.result} />
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold">{t("cacheStatistics")}</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <StatCard
            icon={Database}
            value={pipeline.stats.cacheHits}
            label={t("cacheHitRate")}
            colorScheme="blue"
          />
          <StatCard
            icon={Zap}
            value={pipeline.stats.sympyJudgments}
            label={t("sympyEngine")}
            colorScheme="emerald"
          />
          <StatCard
            icon={Brain}
            value={pipeline.stats.llmJudgments}
            label={t("llmFallback")}
            colorScheme="violet"
          />
        </div>
      </div>

      <IntentExamples />
    </div>
  );
}
