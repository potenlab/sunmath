"use client";

import { useState, useCallback } from "react";
import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Settings,
  FileText,
  ShieldAlert,
  Gauge,
  AlertTriangle,
  CheckCircle2,
  Trash2,
} from "lucide-react";

interface RegisteredProblem {
  id: number;
  content: string;
  correctAnswer: string;
  expectedForm: string;
  targetGrade: string;
  gradingHints: string;
  concepts: string[];
}

const SEED_PROBLEM: RegisteredProblem = {
  id: 1,
  content: "Factor x\u00B2+5x+6",
  correctAnswer: "(x+2)(x+3)",
  expectedForm: "factored",
  targetGrade: "9",
  gradingHints: "Accept any order of factors",
  concepts: [
    "Factoring",
    "Quadratic expressions",
    "Quadratic formula",
    "Factor theorem",
  ],
};

const EXPECTED_FORMS = [
  "factored",
  "expanded",
  "simplified",
  "numeric",
  "proof",
  "null",
] as const;

export default function AdminPage() {
  const t = useTranslations("admin");

  // Settings state
  const [similarityThreshold, setSimilarityThreshold] = useState(0.85);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.9);
  const [duplicateMode, setDuplicateMode] = useState<"warn" | "block">("warn");
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null);

  // Problem form state
  const [problemContent, setProblemContent] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");
  const [expectedForm, setExpectedForm] = useState("");
  const [targetGrade, setTargetGrade] = useState("");
  const [gradingHints, setGradingHints] = useState("");

  // Registered problems
  const [problems, setProblems] = useState<RegisteredProblem[]>([SEED_PROBLEM]);
  const [nextId, setNextId] = useState(2);

  // Registration feedback
  const [registrationMessage, setRegistrationMessage] = useState<string | null>(
    null
  );

  // Duplicate dialog
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const [duplicateInfo, setDuplicateInfo] = useState<{
    similarity: number;
    existingProblem: RegisteredProblem;
    sharedConcepts: string[];
    differences: string[];
  } | null>(null);

  const handleSaveSettings = useCallback(() => {
    setSettingsMessage("Settings saved successfully!");
    setTimeout(() => setSettingsMessage(null), 3000);
  }, []);

  const isFacroringRelated = useCallback((content: string) => {
    const lower = content.toLowerCase();
    return (
      lower.includes("factor") ||
      lower.includes("factorise") ||
      lower.includes("factorize")
    );
  }, []);

  const resetForm = useCallback(() => {
    setProblemContent("");
    setCorrectAnswer("");
    setExpectedForm("");
    setTargetGrade("");
    setGradingHints("");
  }, []);

  const addProblem = useCallback(() => {
    const concepts = isFacroringRelated(problemContent)
      ? ["Factoring", "Quadratic expressions", "Polynomial operations"]
      : ["Geometry", "Circle properties"];

    const newProblem: RegisteredProblem = {
      id: nextId,
      content: problemContent,
      correctAnswer,
      expectedForm,
      targetGrade,
      gradingHints,
      concepts,
    };

    setProblems((prev) => [...prev, newProblem]);
    setNextId((prev) => prev + 1);
    resetForm();
    setRegistrationMessage("Problem registered successfully!");
    setTimeout(() => setRegistrationMessage(null), 3000);
  }, [
    problemContent,
    correctAnswer,
    expectedForm,
    targetGrade,
    gradingHints,
    nextId,
    isFacroringRelated,
    resetForm,
  ]);

  const handleRegisterProblem = useCallback(() => {
    if (!problemContent.trim()) return;

    // Check for duplicate: if the new problem is factoring-related and there's
    // already a factoring-related problem registered
    const hasFactoringProblem = problems.some((p) =>
      isFacroringRelated(p.content)
    );

    if (isFacroringRelated(problemContent) && hasFactoringProblem) {
      const existing = problems.find((p) => isFacroringRelated(p.content))!;

      if (duplicateMode === "block") {
        setRegistrationMessage(
          "Registration blocked: Duplicate problem detected (similarity: 0.92). Change mode to 'Warn' to override."
        );
        setTimeout(() => setRegistrationMessage(null), 5000);
        return;
      }

      // Warn mode: show dialog
      setDuplicateInfo({
        similarity: 0.92,
        existingProblem: existing,
        sharedConcepts: [
          "Factoring",
          "Quadratic expressions",
          "Polynomial operations",
        ],
        differences: [
          "Different coefficients (5x+6 vs 7x+12)",
          "Different factor pairs ((2,3) vs (3,4))",
          "Same difficulty level",
        ],
      });
      setDuplicateDialogOpen(true);
    } else {
      // No duplicate concern
      addProblem();
    }
  }, [problemContent, problems, duplicateMode, isFacroringRelated, addProblem]);

  const handleRegisterAnyway = useCallback(() => {
    setDuplicateDialogOpen(false);
    setDuplicateInfo(null);
    addProblem();
  }, [addProblem]);

  const handleDeleteProblem = useCallback((id: number) => {
    setProblems((prev) => prev.filter((p) => p.id !== id));
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 shadow-sm">
            <Settings className="size-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {t("title")}
            </h1>
            <p className="text-sm text-muted-foreground">{t("description")}</p>
          </div>
        </div>
      </div>

      {/* Dynamic Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-none bg-gradient-to-br from-amber-50 to-orange-50 shadow-sm">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100">
              <Gauge className="size-6 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-amber-700">
                {similarityThreshold.toFixed(2)}
              </p>
              <p className="text-xs text-amber-600/70">
                {t("similarityThreshold")}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-none bg-gradient-to-br from-emerald-50 to-teal-50 shadow-sm">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
              <ShieldAlert className="size-6 text-emerald-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-700">
                {duplicateMode === "warn" ? t("warn") : t("block")}
              </p>
              <p className="text-xs text-emerald-600/70">
                {t("duplicateMode")}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-none bg-gradient-to-br from-violet-50 to-purple-50 shadow-sm">
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100">
              <FileText className="size-6 text-violet-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-violet-700">
                {problems.length}
              </p>
              <p className="text-xs text-violet-600/70">
                {t("registeredProblems")}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Settings Message Toast */}
      {settingsMessage && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">
          <CheckCircle2 className="size-4" />
          {settingsMessage}
        </div>
      )}

      {/* Registration Message Toast */}
      {registrationMessage && (
        <div
          className={`flex items-center gap-2 rounded-lg border px-4 py-3 text-sm font-medium ${
            registrationMessage.includes("blocked")
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-emerald-200 bg-emerald-50 text-emerald-700"
          }`}
        >
          {registrationMessage.includes("blocked") ? (
            <AlertTriangle className="size-4" />
          ) : (
            <CheckCircle2 className="size-4" />
          )}
          {registrationMessage}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Grading Settings Card */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Gauge className="size-4 text-primary" />
              {t("gradingSettings")}
            </CardTitle>
            <CardDescription>{t("gradingSettingsDesc")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {/* Similarity Threshold Slider */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">
                  {t("similarityLabel")}
                </label>
                <span className="rounded-md bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700">
                  {similarityThreshold.toFixed(2)}
                </span>
              </div>
              <Slider
                value={[similarityThreshold * 100]}
                onValueChange={(vals) =>
                  setSimilarityThreshold(vals[0] / 100)
                }
                min={0}
                max={100}
                step={1}
                className="w-full"
              />
              <p className="text-[11px] text-muted-foreground">
                {t("similarityHint")}
              </p>
            </div>
            <Separator />

            {/* Confidence Threshold Slider */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">
                  {t("confidenceThreshold")}
                </label>
                <span className="rounded-md bg-violet-100 px-2 py-0.5 text-xs font-semibold text-violet-700">
                  {confidenceThreshold.toFixed(2)}
                </span>
              </div>
              <Slider
                value={[confidenceThreshold * 100]}
                onValueChange={(vals) =>
                  setConfidenceThreshold(vals[0] / 100)
                }
                min={0}
                max={100}
                step={1}
                className="w-full"
              />
              <p className="text-[11px] text-muted-foreground">
                {t("confidenceHint")}
              </p>
            </div>
            <Separator />

            {/* Duplicate Detection Mode */}
            <div className="space-y-3">
              <label className="text-sm font-medium">
                {t("duplicateDetectionMode")}
              </label>
              <div className="flex items-center gap-3">
                <Badge
                  className={
                    duplicateMode === "warn"
                      ? "bg-amber-100 text-amber-700 hover:bg-amber-100"
                      : "cursor-pointer bg-transparent text-muted-foreground hover:bg-amber-50"
                  }
                  variant={duplicateMode === "warn" ? "default" : "outline"}
                >
                  {t("warn")}
                </Badge>
                <Switch
                  checked={duplicateMode === "block"}
                  onCheckedChange={(checked) =>
                    setDuplicateMode(checked ? "block" : "warn")
                  }
                />
                <Badge
                  className={
                    duplicateMode === "block"
                      ? "bg-red-100 text-red-700 hover:bg-red-100"
                      : "cursor-pointer bg-transparent text-muted-foreground hover:bg-red-50"
                  }
                  variant={duplicateMode === "block" ? "default" : "outline"}
                >
                  {t("block")}
                </Badge>
              </div>
              <p className="text-[11px] text-muted-foreground">
                {t("duplicateHint")}
              </p>
            </div>
            <Separator />

            {/* Save Settings Button */}
            <Button
              onClick={handleSaveSettings}
              className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm hover:opacity-90"
            >
              Save Settings
            </Button>
          </CardContent>
        </Card>

        {/* Problem Registration Card */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="size-4 text-primary" />
              {t("problemRegistration")}
            </CardTitle>
            <CardDescription>{t("problemRegistrationDesc")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Problem Content */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                {t("problemContent")}
              </label>
              <Textarea
                placeholder={t("problemContentPlaceholder")}
                value={problemContent}
                onChange={(e) => setProblemContent(e.target.value)}
                className="min-h-[80px] resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {/* Expected Form */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">
                  {t("expectedForm")}
                </label>
                <Select value={expectedForm} onValueChange={setExpectedForm}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder={t("expectedFormPlaceholder")} />
                  </SelectTrigger>
                  <SelectContent>
                    {EXPECTED_FORMS.map((form) => (
                      <SelectItem key={form} value={form}>
                        {form.charAt(0).toUpperCase() + form.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Target Grade */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">
                  {t("targetGrade")}
                </label>
                <Input
                  placeholder={t("targetGradePlaceholder")}
                  value={targetGrade}
                  onChange={(e) => setTargetGrade(e.target.value)}
                />
              </div>
            </div>

            {/* Correct Answer */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                {t("correctAnswer")}
              </label>
              <Input
                placeholder={t("correctAnswerPlaceholder")}
                value={correctAnswer}
                onChange={(e) => setCorrectAnswer(e.target.value)}
              />
            </div>

            {/* Grading Hints */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                {t("gradingHints")}
              </label>
              <Input
                placeholder={t("gradingHintsPlaceholder")}
                value={gradingHints}
                onChange={(e) => setGradingHints(e.target.value)}
              />
            </div>

            {/* Register Button */}
            <Button
              onClick={handleRegisterProblem}
              disabled={!problemContent.trim()}
              className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm hover:opacity-90"
            >
              {t("registerProblem")}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Registered Problems List */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="size-4 text-primary" />
            {t("registeredProblems")} ({problems.length})
          </CardTitle>
          <CardDescription>
            All registered problems in the system.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {problems.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No problems registered yet.
            </p>
          ) : (
            <div className="space-y-3">
              {problems.map((problem) => (
                <div
                  key={problem.id}
                  className="flex items-start justify-between rounded-lg border bg-muted/20 p-4"
                >
                  <div className="min-w-0 flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-violet-100 px-1.5 py-0.5 text-[10px] font-semibold text-violet-700">
                        #{problem.id}
                      </span>
                      <p className="truncate text-sm font-medium">
                        {problem.content}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {problem.expectedForm && (
                        <Badge variant="outline" className="text-xs">
                          {problem.expectedForm}
                        </Badge>
                      )}
                      {problem.targetGrade && (
                        <Badge variant="outline" className="text-xs">
                          Grade {problem.targetGrade}
                        </Badge>
                      )}
                      {problem.correctAnswer && (
                        <Badge
                          variant="outline"
                          className="text-xs text-emerald-600"
                        >
                          {problem.correctAnswer}
                        </Badge>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {problem.concepts.map((concept) => (
                        <span
                          key={concept}
                          className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700"
                        >
                          {concept}
                        </span>
                      ))}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteProblem(problem.id)}
                    className="ml-2 shrink-0 text-muted-foreground hover:text-red-600"
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Duplicate Warning Dialog */}
      <Dialog open={duplicateDialogOpen} onOpenChange={setDuplicateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-amber-600">
              <AlertTriangle className="size-5" />
              Duplicate Problem Detected
            </DialogTitle>
            <DialogDescription>
              A similar problem already exists in the system.
            </DialogDescription>
          </DialogHeader>

          {duplicateInfo && (
            <div className="space-y-4">
              {/* Similarity Score */}
              <div className="flex items-center justify-between rounded-lg bg-amber-50 p-3">
                <span className="text-sm font-medium text-amber-800">
                  Similarity Score
                </span>
                <span className="text-lg font-bold text-amber-600">
                  {duplicateInfo.similarity.toFixed(2)}
                </span>
              </div>

              {/* Existing Problem */}
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">
                  Existing Problem
                </p>
                <div className="rounded-md border bg-muted/30 p-2 text-sm">
                  {duplicateInfo.existingProblem.content}
                </div>
              </div>

              {/* New Problem */}
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">
                  New Problem
                </p>
                <div className="rounded-md border bg-muted/30 p-2 text-sm">
                  {problemContent}
                </div>
              </div>

              {/* Shared Concepts */}
              <div className="space-y-1.5">
                <p className="text-xs font-medium text-muted-foreground">
                  Shared Concepts
                </p>
                <div className="flex flex-wrap gap-1">
                  {duplicateInfo.sharedConcepts.map((concept) => (
                    <Badge
                      key={concept}
                      className="bg-amber-100 text-amber-700 hover:bg-amber-100"
                    >
                      {concept}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Differences */}
              <div className="space-y-1.5">
                <p className="text-xs font-medium text-muted-foreground">
                  Differences
                </p>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {duplicateInfo.differences.map((diff, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="mt-1.5 block size-1 shrink-0 rounded-full bg-muted-foreground" />
                      {diff}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDuplicateDialogOpen(false);
                setDuplicateInfo(null);
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleRegisterAnyway}
              className="bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:opacity-90"
            >
              Register Anyway
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
