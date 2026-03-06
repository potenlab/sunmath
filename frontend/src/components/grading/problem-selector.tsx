import { useTranslations } from "next-intl";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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

  return (
    <>
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{t("problem")}</label>
        <Input
          type="number"
          min={1}
          placeholder="Enter problem ID..."
          value={selectedProblemId}
          onChange={(e) => onSelect(e.target.value)}
        />
      </div>

      {selectedProblem && (
        <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-3 space-y-1">
          <p className="text-xs font-medium">{selectedProblem.content}</p>
          {selectedProblem.expected_form && (
            <p className="text-xs text-muted-foreground">
              <span className="font-medium">Expected form:</span>{" "}
              {selectedProblem.expected_form}
            </p>
          )}
          {selectedProblem.grading_hints && (
            <p className="text-xs text-muted-foreground">
              <span className="font-medium">Grading hints:</span>{" "}
              {selectedProblem.grading_hints}
            </p>
          )}
        </div>
      )}
    </>
  );
}
