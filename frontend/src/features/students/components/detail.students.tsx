"use client";

import { useTranslations } from "next-intl";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  Brain,
  AlertTriangle,
  Play,
  Loader2,
} from "lucide-react";
import { Link } from "@/i18n/navigation";
import { useDiagnosis } from "../hooks/use-diagnosis";
import { useWrongAnswers, useMastery } from "../api/use-student-data";
import { WrongAnswerItem } from "@/components/students/wrong-answer-item";
import { AnalysisComparison } from "@/components/students/analysis-comparison";
import { ConceptFrequencyChart } from "@/components/students/concept-frequency-chart";
import { RootCauseGraph } from "@/components/students/root-cause-graph";
import { LearningPath } from "@/components/students/learning-path";
import { PracticeList } from "@/components/students/practice-list";

interface StudentDetailProps {
  id: string;
}

export function StudentDetail({ id }: StudentDetailProps) {
  const t = useTranslations("studentDetail");
  const studentId = parseInt(id, 10);
  const { analysisState, diagnosis, handleRunAnalysis } = useDiagnosis(studentId);

  const { data: wrongAnswersData, isLoading: wrongAnswersLoading } = useWrongAnswers(studentId);
  const { data: masteryData } = useMastery(studentId);

  const wrongAnswers = wrongAnswersData?.wrong_answers ?? [];
  const activeCount = wrongAnswers.filter((a) => a.status === "active").length;
  const resolvedCount = wrongAnswers.filter((a) => a.status === "resolved").length;

  // Convert diagnosis concept frequency data for the chart
  const maxFreq = Math.max(
    ...(diagnosis?.concept_frequencies ?? []).map((c) => c.count),
    1,
  );
  const conceptsForChart = (diagnosis?.concept_frequencies ?? []).map((c) => ({
    name: c.concept_name,
    count: Math.round(c.count * 10) / 10,
    pct: Math.round((c.count / maxFreq) * 100),
  }));

  // Convert diagnosis learning path to display format
  const learningPathItems = (diagnosis?.learning_path ?? []).map((concept, i) => ({
    step: i + 1,
    concept,
    desc: concept,
  }));

  // Convert recommended problems to practice items
  // Prefer detailed data (has per-problem concept); fall back to bare IDs
  const practiceItems =
    diagnosis?.recommended_problems_detail?.length
      ? diagnosis.recommended_problems_detail.map((p) => ({
          problem: `Problem #${p.question_id}`,
          concept: p.concept_name,
          difficulty: "medium",
        }))
      : (diagnosis?.recommended_problems ?? []).map((pid) => ({
          problem: `Problem #${pid}`,
          concept: diagnosis?.core_weaknesses?.[0] ?? "",
          difficulty: "medium",
        }));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <Link
          href="/admin/students"
          className="mb-3 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          {t("backToStudents")}
        </Link>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-violet-400 to-purple-500 text-lg font-bold text-white shadow-sm">
            {id.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight">Student {id}</h1>
              <Badge className="bg-red-100 text-red-700 hover:bg-red-100">
                {t("active")}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {t("studentId")}: {id}
            </p>
          </div>
        </div>
      </div>

      {/* Wrong Answers List */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <AlertTriangle className="size-4 text-red-500" />
            {t("wrongAnswersTitle")}
          </CardTitle>
          <CardDescription>
            {activeCount} {t("active").toLowerCase()},{" "}
            {resolvedCount} {t("resolved").toLowerCase()}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {wrongAnswersLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="size-6 animate-spin text-muted-foreground" />
            </div>
          ) : wrongAnswers.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No wrong answers found.
            </p>
          ) : (
            wrongAnswers.map((answer) => (
              <WrongAnswerItem
                key={answer.id}
                answer={{
                  id: answer.id,
                  problem: answer.question_content,
                  unit: `Q${answer.question_id}`,
                  status: answer.status,
                }}
              />
            ))
          )}

          {analysisState === "idle" && (
            <div className="pt-4">
              <Button
                size="lg"
                onClick={handleRunAnalysis}
                className="w-full bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white font-semibold shadow-md"
              >
                <Play className="size-4" />
                Run Cross-Unit Analysis
              </Button>
            </div>
          )}

          {analysisState === "loading" && (
            <div className="pt-4">
              <Button
                size="lg"
                disabled
                className="w-full bg-gradient-to-r from-violet-500 to-purple-600 text-white font-semibold shadow-md"
              >
                <Loader2 className="size-4 animate-spin" />
                Analyzing wrong answers...
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Diagnosis Section */}
      {analysisState === "done" && diagnosis && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <AnalysisComparison />

          {/* Root Cause Banner */}
          {diagnosis.core_weaknesses.length > 0 && (
            <Card className="border-none bg-gradient-to-r from-amber-50 via-orange-50 to-red-50 shadow-sm">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-100">
                    <Brain className="size-6 text-amber-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-amber-900">
                      {t("rootCauseIdentified")}
                    </h3>
                    <p className="mt-1 text-sm text-amber-800">
                      Core weaknesses: {diagnosis.core_weaknesses.join(", ")}
                    </p>
                    {diagnosis.prerequisite_chains.length > 0 && (
                      <p className="mt-2 text-xs text-amber-700/70">
                        {t("prerequisiteChain")}:{" "}
                        {diagnosis.prerequisite_chains[0]?.join(" → ")}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-6 lg:grid-cols-2">
            <ConceptFrequencyChart concepts={conceptsForChart} />
            <RootCauseGraph />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <LearningPath items={learningPathItems} />
            <PracticeList items={practiceItems} />
          </div>
        </div>
      )}
    </div>
  );
}
