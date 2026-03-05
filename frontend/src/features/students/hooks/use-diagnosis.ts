import { useState } from "react";

export function useDiagnosis() {
  const [analysisState, setAnalysisState] = useState<"idle" | "loading" | "done">("idle");

  const handleRunAnalysis = () => {
    setAnalysisState("loading");
    setTimeout(() => {
      setAnalysisState("done");
    }, 1500);
  };

  return { analysisState, handleRunAnalysis };
}
