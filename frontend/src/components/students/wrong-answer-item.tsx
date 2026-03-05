import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, Archive } from "lucide-react";
import type { WrongAnswer } from "@/features/students/types";

const STATUS_CONFIG = {
  active: { labelKey: "active", icon: AlertTriangle, className: "bg-red-100 text-red-700" },
  resolved: { labelKey: "resolved", icon: CheckCircle, className: "bg-emerald-100 text-emerald-700" },
  archived: { labelKey: "archived", icon: Archive, className: "bg-gray-100 text-gray-600" },
} as const;

interface WrongAnswerItemProps {
  answer: WrongAnswer;
}

export function WrongAnswerItem({ answer }: WrongAnswerItemProps) {
  const t = useTranslations("studentDetail");
  const status = STATUS_CONFIG[answer.status];
  const StatusIcon = status.icon;

  return (
    <div className="flex items-start gap-3 rounded-lg border p-3">
      <StatusIcon
        className={`size-4 mt-0.5 shrink-0 ${answer.status === "active" ? "text-red-500" : "text-emerald-500"}`}
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{answer.problem}</p>
        <div className="mt-1 flex items-center gap-2">
          <span className="text-[11px] text-muted-foreground">
            {answer.unit}
          </span>
          <Badge
            variant="outline"
            className={`text-[10px] px-1.5 py-0 ${status.className}`}
          >
            {t(status.labelKey)}
          </Badge>
        </div>
      </div>
    </div>
  );
}
