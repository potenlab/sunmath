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
import { AlertTriangle, ShieldX } from "lucide-react";
import type { DuplicateInfo } from "@/features/admin/types";

interface DuplicateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  duplicateInfo: DuplicateInfo | null;
  newProblemContent: string;
  onCancel: () => void;
  onRegisterAnyway: () => void;
  blocked?: boolean;
}

export function DuplicateDialog({
  open,
  onOpenChange,
  duplicateInfo,
  newProblemContent,
  onCancel,
  onRegisterAnyway,
  blocked = false,
}: DuplicateDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className={`flex items-center gap-2 ${blocked ? "text-red-600" : "text-amber-600"}`}>
            {blocked ? <ShieldX className="size-5" /> : <AlertTriangle className="size-5" />}
            {blocked ? "Registration Blocked" : "Duplicate Problem Detected"}
          </DialogTitle>
          <DialogDescription>
            {blocked
              ? "This problem was blocked because a similar problem already exists. Change the duplicate detection mode to \"Warn\" to allow overrides."
              : "A similar problem already exists in the system."}
          </DialogDescription>
        </DialogHeader>

        {duplicateInfo && (
          <div className="space-y-4">
            <div className={`flex items-center justify-between rounded-lg p-3 ${blocked ? "bg-red-50" : "bg-amber-50"}`}>
              <span className={`text-sm font-medium ${blocked ? "text-red-800" : "text-amber-800"}`}>
                Similarity Score
              </span>
              <span className={`text-lg font-bold ${blocked ? "text-red-600" : "text-amber-600"}`}>
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
                    className={blocked ? "bg-red-100 text-red-700 hover:bg-red-100" : "bg-amber-100 text-amber-700 hover:bg-amber-100"}
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
            {blocked ? "Close" : "Cancel"}
          </Button>
          {!blocked && (
            <Button
              onClick={onRegisterAnyway}
              className="bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:opacity-90"
            >
              Register Anyway
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
