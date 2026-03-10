import { useTranslations } from "next-intl";
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
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FileText, Loader2 } from "lucide-react";
import { EXPECTED_FORMS } from "@/features/admin/types";
import type { ConceptOption } from "@/features/admin/types";
import {
  ConceptWeightPicker,
  type ConceptWeightEntry,
} from "@/components/admin/concept-weight-picker";

interface ProblemFormProps {
  problemContent: string;
  onProblemContentChange: (value: string) => void;
  correctAnswer: string;
  onCorrectAnswerChange: (value: string) => void;
  expectedForm: string;
  onExpectedFormChange: (value: string) => void;
  targetGrade: string;
  onTargetGradeChange: (value: string) => void;
  gradingHints: string;
  onGradingHintsChange: (value: string) => void;
  conceptEntries: ConceptWeightEntry[];
  onConceptEntriesChange: (entries: ConceptWeightEntry[]) => void;
  availableConcepts: ConceptOption[];
  conceptsLoading?: boolean;
  isRegistering?: boolean;
  onRegister: () => void;
}

export function ProblemForm({
  problemContent,
  onProblemContentChange,
  correctAnswer,
  onCorrectAnswerChange,
  expectedForm,
  onExpectedFormChange,
  targetGrade,
  onTargetGradeChange,
  gradingHints,
  onGradingHintsChange,
  conceptEntries,
  onConceptEntriesChange,
  availableConcepts,
  conceptsLoading,
  isRegistering,
  onRegister,
}: ProblemFormProps) {
  const t = useTranslations("admin");

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <FileText className="size-4 text-primary" />
          {t("problemRegistration")}
        </CardTitle>
        <CardDescription>{t("problemRegistrationDesc")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-medium">{t("problemContent")}</label>
          <Textarea
            placeholder={t("problemContentPlaceholder")}
            value={problemContent}
            onChange={(e) => onProblemContentChange(e.target.value)}
            className="min-h-[80px] resize-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">{t("expectedForm")}</label>
            <Select value={expectedForm} onValueChange={onExpectedFormChange}>
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

          <div className="space-y-1.5">
            <label className="text-sm font-medium">{t("targetGrade")}</label>
            <Input
              placeholder={t("targetGradePlaceholder")}
              value={targetGrade}
              onChange={(e) => onTargetGradeChange(e.target.value)}
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">{t("correctAnswer")}</label>
          <Input
            placeholder={t("correctAnswerPlaceholder")}
            value={correctAnswer}
            onChange={(e) => onCorrectAnswerChange(e.target.value)}
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">{t("gradingHints")}</label>
          <Input
            placeholder={t("gradingHintsPlaceholder")}
            value={gradingHints}
            onChange={(e) => onGradingHintsChange(e.target.value)}
          />
        </div>

        <ConceptWeightPicker
          concepts={availableConcepts}
          entries={conceptEntries}
          onChange={onConceptEntriesChange}
          isLoading={conceptsLoading}
        />

        <Button
          onClick={onRegister}
          disabled={!problemContent.trim() || isRegistering}
          className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm hover:opacity-90"
        >
          {isRegistering ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              {t("registering")}
            </>
          ) : (
            t("registerProblem")
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
