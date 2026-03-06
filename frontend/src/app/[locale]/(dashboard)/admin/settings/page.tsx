"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Settings, Gauge, ShieldAlert } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { AdminSettings } from "@/features/admin/components/admin-settings";

export default function AdminSettingsPage() {
  const t = useTranslations("admin");
  const [duplicateMode, setDuplicateMode] = useState<"warn" | "block">("warn");

  return (
    <div className="space-y-8">
      <PageHeader
        icon={Settings}
        iconGradient="from-amber-400 to-orange-500"
        title="Settings"
        description="Configure grading and duplicate detection settings"
      />

      <div className="grid gap-4 md:grid-cols-2">
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
      </div>

      <AdminSettings
        duplicateMode={duplicateMode}
        onDuplicateModeChange={setDuplicateMode}
      />
    </div>
  );
}
