import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { AlertTriangle } from "lucide-react";
import type { DuplicateInfo } from "@/features/admin/types";

interface DuplicateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  duplicateInfo: DuplicateInfo | null;
  newProblemContent: string;
  onCancel: () => void;
  onRegisterAnyway: () => void;
}

export function DuplicateDialog({
  open,
  onOpenChange,
  duplicateInfo,
  newProblemContent,
  onCancel,
  onRegisterAnyway,
}: DuplicateDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
            <div className="flex items-center justify-between rounded-lg bg-amber-50 p-3">
              <span className="text-sm font-medium text-amber-800">
                Similarity Score
              </span>
              <span className="text-lg font-bold text-amber-600">
                {duplicateInfo.similarity.toFixed(2)}
              </span>
            </div>

            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">
                Existing Problem
              </p>
              <div className="rounded-md border bg-muted/30 p-2 text-sm">
                {duplicateInfo.existingProblem.content}
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">
                New Problem
              </p>
              <div className="rounded-md border bg-muted/30 p-2 text-sm">
                {newProblemContent}
              </div>
            </div>

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
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            onClick={onRegisterAnyway}
            className="bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:opacity-90"
          >
            Register Anyway
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
