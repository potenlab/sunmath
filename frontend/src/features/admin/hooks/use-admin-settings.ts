import { useState, useCallback } from "react";

export function useAdminSettings() {
  const [similarityThreshold, setSimilarityThreshold] = useState(0.85);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.9);
  const [duplicateMode, setDuplicateMode] = useState<"warn" | "block">("warn");
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null);

  const handleSaveSettings = useCallback(() => {
    setSettingsMessage("Settings saved successfully!");
    setTimeout(() => setSettingsMessage(null), 3000);
  }, []);

  return {
    similarityThreshold,
    setSimilarityThreshold,
    confidenceThreshold,
    setConfidenceThreshold,
    duplicateMode,
    setDuplicateMode,
    settingsMessage,
    handleSaveSettings,
  };
}
