"use client";

import { useAdminSettings } from "../hooks/use-admin-settings";
import { SettingsForm } from "@/components/admin/settings-form";
import { ToastMessage } from "@/components/common/toast-message";

export function AdminSettings() {
  const {
    similarityThreshold,
    setSimilarityThreshold,
    confidenceThreshold,
    setConfidenceThreshold,
    duplicateMode,
    setDuplicateMode,
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
        onDuplicateModeChange={setDuplicateMode}
        onSave={handleSaveSettings}
      />
    </>
  );
}
