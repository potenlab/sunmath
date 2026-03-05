import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { GitBranch } from "lucide-react";
import type { MockConcept } from "@/features/students/types";

interface ConceptFrequencyChartProps {
  concepts: MockConcept[];
}

export function ConceptFrequencyChart({ concepts }: ConceptFrequencyChartProps) {
  const t = useTranslations("studentDetail");

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <GitBranch className="size-4 text-violet-500" />
          {t("conceptFrequency")}
        </CardTitle>
        <CardDescription>{t("conceptFrequencyDesc")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {concepts.map((concept) => (
          <div key={concept.name} className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{concept.name}</span>
              <span className="text-xs text-muted-foreground">{concept.count}x</span>
            </div>
            <div className="h-2 rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-gradient-to-r from-violet-400 to-purple-500 transition-all"
                style={{ width: `${concept.pct}%` }}
              />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
