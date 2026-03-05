"use client";

import { GradingResultCard } from "@/components/grading/grading-result-card";
import type { GradingResult } from "../types";

interface ResultPanelProps {
  result: GradingResult | null;
}

export function ResultPanel({ result }: ResultPanelProps) {
  return <GradingResultCard result={result} />;
}
