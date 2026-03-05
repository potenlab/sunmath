"use client";

import { useAdminSettings } from "../hooks/use-admin-settings";
import { SettingsForm } from "@/components/admin/settings-form";
import { ToastMessage } from "@/components/common/toast-message";

interface AdminSettingsProps {
  duplicateMode: "warn" | "block";
  onDuplicateModeChange: (mode: "warn" | "block") => void;
}

export function AdminSettings({
  duplicateMode,
  onDuplicateModeChange,
}: AdminSettingsProps) {
  const {
    similarityThreshold,
    setSimilarityThreshold,
    confidenceThreshold,
    setConfidenceThreshold,
    settingsMessage,
    handleSaveSettings,
  } = useAdminSettings();

  return (
    <>
      {settingsMessage && (
        <ToastMessage message={settingsMessage} variant="success" />
      )}
      <SettingsForm
        similarityThreshold={similarityThreshold}
        onSimilarityChange={setSimilarityThreshold}
        confidenceThreshold={confidenceThreshold}
        onConfidenceChange={setConfidenceThreshold}
        duplicateMode={duplicateMode}
        onDuplicateModeChange={onDuplicateModeChange}
        onSave={handleSaveSettings}
      />
    </>
  );
}
