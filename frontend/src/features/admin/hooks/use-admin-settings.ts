import { useState, useCallback, useEffect } from "react";
import { useSettings, useUpdateSetting } from "../api/use-settings";

export function useAdminSettings() {
  const { data: settingsData, isLoading } = useSettings();
  const updateMutation = useUpdateSetting();

  const [similarityThreshold, setSimilarityThreshold] = useState(0.85);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.9);
  const [duplicateMode, setDuplicateMode] = useState<"warn" | "block">("warn");
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null);

  // Sync local state from server settings
  useEffect(() => {
    if (!settingsData?.settings) return;
    for (const s of settingsData.settings) {
      if (s.key === "similarity_threshold") {
        setSimilarityThreshold(parseFloat(s.value) || 0.85);
      } else if (s.key === "confidence_threshold") {
        setConfidenceThreshold(parseFloat(s.value) || 0.9);
      } else if (s.key === "duplicate_detection_mode") {
        setDuplicateMode(s.value === "block" ? "block" : "warn");
      }
    }
  }, [settingsData]);

  const handleSaveSettings = useCallback(async () => {
    try {
      await Promise.all([
        updateMutation.mutateAsync({
          key: "similarity_threshold",
          value: String(similarityThreshold),
        }),
        updateMutation.mutateAsync({
          key: "confidence_threshold",
          value: String(confidenceThreshold),
        }),
        updateMutation.mutateAsync({
          key: "duplicate_detection_mode",
          value: duplicateMode,
        }),
      ]);
      setSettingsMessage("Settings saved successfully!");
    } catch {
      setSettingsMessage("Failed to save settings.");
    }
    setTimeout(() => setSettingsMessage(null), 3000);
  }, [similarityThreshold, confidenceThreshold, duplicateMode, updateMutation]);

  return {
    similarityThreshold,
    setSimilarityThreshold,
    confidenceThreshold,
    setConfidenceThreshold,
    duplicateMode,
    setDuplicateMode,
    settingsMessage,
    handleSaveSettings,
    isLoading,
  };
}
