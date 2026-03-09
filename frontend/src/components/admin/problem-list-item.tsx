import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import type { RegisteredProblem } from "@/features/admin/types";

interface ProblemListItemProps {
  problem: RegisteredProblem;
  onDelete: (id: number) => void;
}

export function ProblemListItem({ problem, onDelete }: ProblemListItemProps) {
  return (
    <div className="flex items-start justify-between rounded-lg border bg-muted/20 p-4">
      <div className="min-w-0 flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className="rounded bg-violet-100 px-1.5 py-0.5 text-[10px] font-semibold text-violet-700">
            #{problem.id}
          </span>
          <p className="truncate text-sm font-medium">{problem.content}</p>
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
          {problem.concepts.map((concept) => {
            const weight = problem.conceptWeights?.[concept];
            return (
              <span
                key={concept}
                className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700"
              >
                {concept}
                {weight !== undefined && weight < 1.0 && (
                  <span className="ml-0.5 opacity-60">
                    {weight.toFixed(1)}
                  </span>
                )}
              </span>
            );
          })}
        </div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onDelete(problem.id)}
        className="ml-2 shrink-0 text-muted-foreground hover:text-red-600"
      >
        <Trash2 className="size-4" />
      </Button>
    </div>
  );
}
