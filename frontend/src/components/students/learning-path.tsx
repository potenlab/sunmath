import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Route } from "lucide-react";
import type { LearningPathItem } from "@/features/students/types";

interface LearningPathProps {
  items: LearningPathItem[];
}

export function LearningPath({ items }: LearningPathProps) {
  const t = useTranslations("studentDetail");

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Route className="size-4 text-emerald-500" />
          {t("recommendedLearningPath")}
        </CardTitle>
        <CardDescription>{t("recommendedLearningPathDesc")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, idx) => (
          <div key={item.step} className="flex gap-3">
            <div className="flex flex-col items-center">
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${
                  idx === 0
                    ? "bg-gradient-to-br from-amber-400 to-orange-500"
                    : idx === items.length - 1
                      ? "bg-gradient-to-br from-emerald-400 to-teal-500"
                      : "bg-gradient-to-br from-violet-400 to-purple-500"
                }`}
              >
                {item.step}
              </div>
              {idx < items.length - 1 && (
                <div className="h-full w-px bg-border my-1" />
              )}
            </div>
            <div className="pb-4">
              <p className="text-sm font-semibold">{item.concept}</p>
              <p className="text-xs text-muted-foreground">{item.desc}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
