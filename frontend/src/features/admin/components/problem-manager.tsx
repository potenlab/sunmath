"use client";

import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FileText } from "lucide-react";
import { useProblemRegistration } from "../hooks/use-problem-registration";
import { ProblemForm } from "@/components/admin/problem-form";
import { ProblemListItem } from "@/components/admin/problem-list-item";
import { DuplicateDialog } from "@/components/admin/duplicate-dialog";
import { ToastMessage } from "@/components/common/toast-message";

interface ProblemManagerProps {
  duplicateMode: "warn" | "block";
  onProblemsCountChange?: (count: number) => void;
}

export function ProblemManager({
  duplicateMode,
  onProblemsCountChange,
}: ProblemManagerProps) {
  const t = useTranslations("admin");
  const {
    problemContent,
    setProblemContent,
    correctAnswer,
    setCorrectAnswer,
    expectedForm,
    setExpectedForm,
    targetGrade,
    setTargetGrade,
    gradingHints,
    setGradingHints,
    problems,
    registrationMessage,
    duplicateDialogOpen,
    setDuplicateDialogOpen,
    duplicateInfo,
    setDuplicateInfo,
    handleRegisterProblem,
    handleRegisterAnyway,
    handleDeleteProblem,
  } = useProblemRegistration(duplicateMode);

  // Notify parent of problems count changes
  if (onProblemsCountChange) {
    onProblemsCountChange(problems.length);
  }

  return (
    <>
      {registrationMessage && (
        <ToastMessage
          message={registrationMessage}
          variant={registrationMessage.includes("blocked") ? "error" : "success"}
        />
      )}

      <ProblemForm
        problemContent={problemContent}
        onProblemContentChange={setProblemContent}
        correctAnswer={correctAnswer}
        onCorrectAnswerChange={setCorrectAnswer}
        expectedForm={expectedForm}
        onExpectedFormChange={setExpectedForm}
        targetGrade={targetGrade}
        onTargetGradeChange={setTargetGrade}
        gradingHints={gradingHints}
        onGradingHintsChange={setGradingHints}
        onRegister={handleRegisterProblem}
      />

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
                <ProblemListItem
                  key={problem.id}
                  problem={problem}
                  onDelete={handleDeleteProblem}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <DuplicateDialog
        open={duplicateDialogOpen}
        onOpenChange={setDuplicateDialogOpen}
        duplicateInfo={duplicateInfo}
        newProblemContent={problemContent}
        onCancel={() => {
          setDuplicateDialogOpen(false);
          setDuplicateInfo(null);
        }}
        onRegisterAnyway={handleRegisterAnyway}
      />
    </>
  );
}
