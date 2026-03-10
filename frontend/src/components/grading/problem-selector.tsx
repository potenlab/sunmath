import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import type { ProblemResponse } from "@/features/grading/types";

interface ProblemSelectorProps {
  selectedProblemId: string;
  selectedProblem: ProblemResponse | null;
  onSelect: (value: string) => void;
}

export function ProblemSelector({
  selectedProblemId,
  selectedProblem,
  onSelect,
}: ProblemSelectorProps) {
  const t = useTranslations("grading");
  const tg = useTranslations("gradingComponents");

  return (
    <>
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{t("problem")}</label>
        <Input
          type="number"
          min={1}
          placeholder={tg("enterProblemId")}
          value={selectedProblemId}
          onChange={(e) => onSelect(e.target.value)}
        />
      </div>

      {selectedProblem && (
        <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-3 space-y-1">
          <p className="text-xs font-medium">{selectedProblem.content}</p>
          {selectedProblem.expected_form && (
            <p className="text-xs text-muted-foreground">
              <span className="font-medium">{tg("expectedForm")}</span>{" "}
              {selectedProblem.expected_form}
            </p>
          )}
          {selectedProblem.grading_hints && (
            <p className="text-xs text-muted-foreground">
              <span className="font-medium">{tg("gradingHints")}</span>{" "}
              {selectedProblem.grading_hints}
            </p>
          )}
        </div>
      )}
    </>
  );
}
