"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Settings, Gauge, ShieldAlert, FileText } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { AdminSettings } from "@/features/admin/components/admin-settings";
import { ProblemManager } from "@/features/admin/components/problem-manager";

export default function AdminPage() {
  const t = useTranslations("admin");
  const [duplicateMode, setDuplicateMode] = useState<"warn" | "block">("warn");
  const [problemsCount, setProblemsCount] = useState(1);

  return (
    <div className="space-y-8">
      <PageHeader
        icon={Settings}
        iconGradient="from-amber-400 to-orange-500"
        title={t("title")}
        description={t("description")}
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          icon={Gauge}
          value="0.85"
          label={t("similarityThreshold")}
          colorScheme="amber"
        />
        <StatCard
          icon={ShieldAlert}
          value={duplicateMode === "warn" ? t("warn") : t("block")}
          label={t("duplicateMode")}
          colorScheme="emerald"
        />
        <StatCard
          icon={FileText}
          value={problemsCount}
          label={t("registeredProblems")}
          colorScheme="violet"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <AdminSettings
          duplicateMode={duplicateMode}
          onDuplicateModeChange={setDuplicateMode}
        />
        <ProblemManager
          duplicateMode={duplicateMode}
          onProblemsCountChange={setProblemsCount}
        />
      </div>
    </div>
  );
}
