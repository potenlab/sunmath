import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { ChevronRight } from "lucide-react";
import { Link } from "@/i18n/navigation";
import type { StudentSummary } from "@/features/students/types";

interface StudentCardProps {
  student: StudentSummary;
}

const STATUS_CONFIG = {
  "needs-attention": {
    labelKey: "needsAttention",
    className: "bg-red-100 text-red-700 hover:bg-red-100",
  },
  improving: {
    labelKey: "improving",
    className: "bg-amber-100 text-amber-700 hover:bg-amber-100",
  },
  "on-track": {
    labelKey: "onTrack",
    className: "bg-emerald-100 text-emerald-700 hover:bg-emerald-100",
  },
} as const;

export function StudentCard({ student }: StudentCardProps) {
  const t = useTranslations("students");
  const status = STATUS_CONFIG[student.status];

  return (
    <Link
      href={`/students/${student.id}`}
      className="group flex items-center gap-4 rounded-xl border p-4 transition-all hover:border-primary/30 hover:bg-accent/50 hover:shadow-sm"
    >
      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-violet-100 to-purple-100 text-sm font-bold text-violet-600">
        {student.name.charAt(student.name.length - 1)}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-semibold">{student.name}</p>
          <Badge className={status.className}>{t(status.labelKey)}</Badge>
        </div>
        <p className="text-xs text-muted-foreground">
          {student.grade}
          {student.rootCause && (
            <span>
              {" "}&middot; {t("rootCause")}:{" "}
              <span className="font-medium text-foreground/70">
                {student.rootCause}
              </span>
            </span>
          )}
        </p>
      </div>
      <div className="text-right shrink-0">
        <p className="text-lg font-bold">{student.wrongAnswers}</p>
        <p className="text-[11px] text-muted-foreground">{t("wrongAnswers")}</p>
      </div>
      <ChevronRight className="size-4 text-muted-foreground/40 transition-transform group-hover:translate-x-0.5" />
    </Link>
  );
}
