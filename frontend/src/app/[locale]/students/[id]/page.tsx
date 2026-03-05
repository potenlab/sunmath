"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  Brain,
  GitBranch,
  Route,
  BookOpen,
  AlertTriangle,
  CheckCircle,
  Archive,
  Play,
  Loader2,
  Zap,
  XCircle,
} from "lucide-react";
import { Link } from "@/i18n/navigation";

export default function StudentDiagnosisPage() {
  const params = useParams();
  const id = params.id as string;
  const t = useTranslations("studentDetail");

  const [analysisState, setAnalysisState] = useState<"idle" | "loading" | "done">("idle");

  const handleRunAnalysis = () => {
    setAnalysisState("loading");
    setTimeout(() => {
      setAnalysisState("done");
    }, 1500);
  };

  const mockWrongAnswers = [
    { id: 1, problem: "Quadratic inequality: x^2 - 5x + 6 > 0", unit: t("quadraticInequalities"), status: "active" as const },
    { id: 2, problem: "Find the vertex of y = x^2 - 4x + 7", unit: t("quadraticFunctions"), status: "active" as const },
    { id: 3, problem: "Complete: x^2 + y^2 - 6x + 4y = 12", unit: t("circleEquations"), status: "active" as const },
    { id: 4, problem: "Factor: x^2 + 6x + 9", unit: t("factoringQuadratics"), status: "resolved" as const },
  ];

  const mockConcepts = [
    { name: t("completingTheSquare"), count: 3, pct: 100 },
    { name: t("factoringQuadratics"), count: 2, pct: 66 },
    { name: t("multiplicationFormulas"), count: 2, pct: 66 },
    { name: t("coordinateGeometry"), count: 1, pct: 33 },
  ];

  const mockLearningPath = [
    { step: 1, concept: t("learningStep1"), desc: t("learningStep1Desc") },
    { step: 2, concept: t("learningStep2"), desc: t("learningStep2Desc") },
    { step: 3, concept: t("learningStep3"), desc: t("learningStep3Desc") },
    { step: 4, concept: t("learningStep4"), desc: t("learningStep4Desc") },
  ];

  const statusConfig = {
    active: { label: t("active"), icon: AlertTriangle, className: "bg-red-100 text-red-700" },
    resolved: { label: t("resolved"), icon: CheckCircle, className: "bg-emerald-100 text-emerald-700" },
    archived: { label: t("archived"), icon: Archive, className: "bg-gray-100 text-gray-600" },
  };

  const practiceItems = [
    { problem: t("practice1"), concept: t("multiplicationFormulas"), difficulty: t("easy") },
    { problem: t("practice2"), concept: t("completingTheSquare"), difficulty: t("medium") },
    { problem: t("practice3"), concept: t("completingTheSquare"), difficulty: t("medium") },
    { problem: t("practice4"), concept: t("completingTheSquare"), difficulty: t("hard") },
  ];

  const difficultyColor = (d: string) => {
    if (d === t("easy")) return "bg-emerald-50 text-emerald-600";
    if (d === t("medium")) return "bg-amber-50 text-amber-600";
    return "bg-red-50 text-red-600";
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <Link
          href="/students"
          className="mb-3 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          {t("backToStudents")}
        </Link>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-violet-400 to-purple-500 text-lg font-bold text-white shadow-sm">
            A
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight">Student A</h1>
              <Badge className="bg-red-100 text-red-700 hover:bg-red-100">{t("active")}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              High School 2 &middot; {t("studentId")}: {id}
            </p>
          </div>
        </div>
      </div>

      {/* Wrong Answers List (always visible) */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <AlertTriangle className="size-4 text-red-500" />
            {t("wrongAnswersTitle")}
          </CardTitle>
          <CardDescription>
            {mockWrongAnswers.filter(a => a.status === "active").length} {t("active").toLowerCase()},{" "}
            {mockWrongAnswers.filter(a => a.status === "resolved").length} {t("resolved").toLowerCase()}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {mockWrongAnswers.map((answer) => {
            const status = statusConfig[answer.status];
            const StatusIcon = status.icon;
            return (
              <div key={answer.id} className="flex items-start gap-3 rounded-lg border p-3">
                <StatusIcon className={`size-4 mt-0.5 shrink-0 ${answer.status === "active" ? "text-red-500" : "text-emerald-500"}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{answer.problem}</p>
                  <div className="mt-1 flex items-center gap-2">
                    <span className="text-[11px] text-muted-foreground">{answer.unit}</span>
                    <Badge variant="outline" className={`text-[10px] px-1.5 py-0 ${status.className}`}>{status.label}</Badge>
                  </div>
                </div>
              </div>
            );
          })}

          {/* Run Analysis Button */}
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

          {/* Loading State */}
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

      {/* ===== Diagnosis Section (revealed after analysis) ===== */}
      {analysisState === "done" && (
        <div
          className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500"
        >
          {/* Side-by-Side Comparison Panel */}
          <div className="grid gap-4 lg:grid-cols-2">
            {/* Naive Analysis (LEFT) */}
            <Card className="border-2 border-red-200 bg-red-50/40 shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base text-red-700">
                  <XCircle className="size-4 text-red-500" />
                  Naive Analysis
                </CardTitle>
                <CardDescription className="text-red-600/70">
                  Simple unit-level weakness listing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-red-800 font-medium">
                    &quot;Student is weak in:&quot;
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {[t("quadraticInequalities"), t("quadraticFunctions"), t("circleEquations")].map((unit) => (
                      <Badge key={unit} className="bg-red-100 text-red-700 hover:bg-red-100 border border-red-200">
                        {unit}
                      </Badge>
                    ))}
                  </div>
                  <div className="mt-3 rounded-lg bg-red-100/60 p-3">
                    <p className="text-xs text-red-600">
                      {t("naiveAnalysis")}
                    </p>
                    <p className="mt-2 text-xs text-red-500/80">
                      No root cause identified. Student must study 3 separate units independently.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* GraphRAG Analysis (RIGHT) */}
            <Card className="border-2 border-emerald-200 bg-emerald-50/40 shadow-sm ring-2 ring-emerald-100">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base text-emerald-700">
                  <Zap className="size-4 text-emerald-500" />
                  GraphRAG Analysis
                </CardTitle>
                <CardDescription className="text-emerald-600/70">
                  Prerequisite graph backtracking
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-emerald-800 font-medium">
                    &quot;Root cause identified:&quot;
                  </p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100 border border-emerald-300 font-bold">
                      {t("completingTheSquare")}
                    </Badge>
                    <span className="text-xs text-emerald-600">is the shared root cause</span>
                  </div>
                  <div className="mt-3 rounded-lg bg-emerald-100/60 p-3">
                    <p className="text-xs text-emerald-700 font-semibold">
                      {t("graphragAnalysis")}
                    </p>
                    <p className="mt-2 text-xs text-emerald-600/80">
                      Fix 1 concept, resolve all 3 units. Efficient and targeted remediation.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Root Cause Banner */}
          <Card className="border-none bg-gradient-to-r from-amber-50 via-orange-50 to-red-50 shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-100">
                  <Brain className="size-6 text-amber-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-amber-900">{t("rootCauseIdentified")}</h3>
                  <p className="mt-1 text-sm text-amber-800" dangerouslySetInnerHTML={{ __html: t.raw("rootCauseDesc") }} />
                  <p className="mt-2 text-xs text-amber-700/70">{t("prerequisiteChain")}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Concept Frequency + Root Cause Tracing */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <GitBranch className="size-4 text-violet-500" />
                  {t("conceptFrequency")}
                </CardTitle>
                <CardDescription>{t("conceptFrequencyDesc")}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {mockConcepts.map((concept) => (
                  <div key={concept.name} className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{concept.name}</span>
                      <span className="text-xs text-muted-foreground">{concept.count}x</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted">
                      <div className="h-full rounded-full bg-gradient-to-r from-violet-400 to-purple-500 transition-all" style={{ width: `${concept.pct}%` }} />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Root Cause Tracing Graph */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Brain className="size-4 text-amber-500" />
                  {t("rootCauseTracing")}
                </CardTitle>
                <CardDescription>{t("rootCauseTracingDesc")}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center py-6">
                  <div className="flex items-center gap-3 flex-wrap justify-center">
                    <div className="flex flex-col items-center gap-1">
                      <div className="rounded-lg border-2 border-amber-300 bg-amber-50 px-4 py-2 text-center">
                        <p className="text-xs font-semibold text-amber-700">{t("rootCauseLabel")}</p>
                        <p className="text-sm font-bold text-amber-900">{t("multiplicationFormulas")}</p>
                        <p className="text-[10px] text-amber-600">{t("mastery")}: 0.45</p>
                      </div>
                    </div>
                    <div className="text-2xl text-muted-foreground/40">&rarr;</div>
                    <div className="flex flex-col items-center gap-1">
                      <div className="rounded-lg border-2 border-red-300 bg-red-50 px-4 py-2 text-center">
                        <p className="text-xs font-semibold text-red-700">{t("coreWeakness")}</p>
                        <p className="text-sm font-bold text-red-900">{t("completingTheSquare")}</p>
                        <p className="text-[10px] text-red-600">{t("mastery")}: 0.30</p>
                      </div>
                    </div>
                    <div className="text-2xl text-muted-foreground/40">&rarr;</div>
                    <div className="flex flex-col gap-2">
                      {[t("quadraticInequalities"), t("quadraticFunctions"), t("circleEquations")].map((unit) => (
                        <div key={unit} className="rounded-lg border bg-muted/50 px-3 py-1.5 text-center">
                          <p className="text-xs font-medium">{unit}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Learning Path + Practice */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Route className="size-4 text-emerald-500" />
                  {t("recommendedLearningPath")}
                </CardTitle>
                <CardDescription>{t("recommendedLearningPathDesc")}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {mockLearningPath.map((item, idx) => (
                  <div key={item.step} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${
                        idx === 0
                          ? "bg-gradient-to-br from-amber-400 to-orange-500"
                          : idx === mockLearningPath.length - 1
                            ? "bg-gradient-to-br from-emerald-400 to-teal-500"
                            : "bg-gradient-to-br from-violet-400 to-purple-500"
                      }`}>
                        {item.step}
                      </div>
                      {idx < mockLearningPath.length - 1 && <div className="h-full w-px bg-border my-1" />}
                    </div>
                    <div className="pb-4">
                      <p className="text-sm font-semibold">{item.concept}</p>
                      <p className="text-xs text-muted-foreground">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <BookOpen className="size-4 text-blue-500" />
                  {t("recommendedPractice")}
                </CardTitle>
                <CardDescription>{t("recommendedPracticeDesc")}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {practiceItems.map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-lg border p-3 hover:bg-accent/30 transition-colors">
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-blue-50 text-[11px] font-bold text-blue-600">
                      {idx + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{item.problem}</p>
                      <div className="mt-1 flex items-center gap-2">
                        <Badge variant="outline" className="text-[10px] px-1.5 py-0">{item.concept}</Badge>
                        <Badge variant="outline" className={`text-[10px] px-1.5 py-0 ${difficultyColor(item.difficulty)}`}>{item.difficulty}</Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
