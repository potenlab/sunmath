import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { MockProblem } from "@/features/grading/types";

interface ProblemSelectorProps {
  problems: MockProblem[];
  selectedProblemId: string;
  selectedProblem: MockProblem | undefined;
  onSelect: (value: string) => void;
}

export function ProblemSelector({
  problems,
  selectedProblemId,
  selectedProblem,
  onSelect,
}: ProblemSelectorProps) {
  const t = useTranslations("grading");

  return (
    <>
      <div className="space-y-1.5">
        <label className="text-sm font-medium">{t("problem")}</label>
        <Select value={selectedProblemId} onValueChange={onSelect}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder={t("problemPlaceholder")} />
          </SelectTrigger>
          <SelectContent>
            {problems.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.content}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedProblem && (
        <div className="rounded-lg border border-dashed border-muted-foreground/25 bg-muted/30 p-3 space-y-1">
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
          <div className="flex flex-wrap gap-1 mt-1">
            {selectedProblem.evaluation_concepts.map((c) => (
              <Badge
                key={c}
                variant="secondary"
                className="text-[10px] px-1.5 py-0"
              >
                {c}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
