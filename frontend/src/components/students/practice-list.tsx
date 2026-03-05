import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { BookOpen } from "lucide-react";
import type { PracticeItem } from "@/features/students/types";

interface PracticeListProps {
  items: PracticeItem[];
}

export function PracticeList({ items }: PracticeListProps) {
  const t = useTranslations("studentDetail");

  const difficultyColor = (d: string) => {
    if (d === t("easy")) return "bg-emerald-50 text-emerald-600";
    if (d === t("medium")) return "bg-amber-50 text-amber-600";
    return "bg-red-50 text-red-600";
  };

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <BookOpen className="size-4 text-blue-500" />
          {t("recommendedPractice")}
        </CardTitle>
        <CardDescription>{t("recommendedPracticeDesc")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {items.map((item, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3 rounded-lg border p-3 hover:bg-accent/30 transition-colors"
          >
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-blue-50 text-[11px] font-bold text-blue-600">
              {idx + 1}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">{item.problem}</p>
              <div className="mt-1 flex items-center gap-2">
                <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                  {item.concept}
                </Badge>
                <Badge
                  variant="outline"
                  className={`text-[10px] px-1.5 py-0 ${difficultyColor(item.difficulty)}`}
                >
                  {item.difficulty}
                </Badge>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
