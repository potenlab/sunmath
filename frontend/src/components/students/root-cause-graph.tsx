import { useTranslations } from "next-intl";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Brain } from "lucide-react";

export function RootCauseGraph() {
  const t = useTranslations("studentDetail");

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Brain className="size-4 text-amber-500" />
          {t("rootCauseTracing")}
        </CardTitle>
        <CardDescription>{t("rootCauseTracingDesc")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-center py-6">
          <div className="flex items-center gap-3 flex-wrap justify-center">
            <div className="flex flex-col items-center gap-1">
              <div className="rounded-lg border-2 border-amber-300 bg-amber-50 px-4 py-2 text-center">
                <p className="text-xs font-semibold text-amber-700">{t("rootCauseLabel")}</p>
                <p className="text-sm font-bold text-amber-900">{t("multiplicationFormulas")}</p>
                <p className="text-[10px] text-amber-600">{t("mastery")}: 0.45</p>
              </div>
            </div>
            <div className="text-2xl text-muted-foreground/40">&rarr;</div>
            <div className="flex flex-col items-center gap-1">
              <div className="rounded-lg border-2 border-red-300 bg-red-50 px-4 py-2 text-center">
                <p className="text-xs font-semibold text-red-700">{t("coreWeakness")}</p>
                <p className="text-sm font-bold text-red-900">{t("completingTheSquare")}</p>
                <p className="text-[10px] text-red-600">{t("mastery")}: 0.30</p>
              </div>
            </div>
            <div className="text-2xl text-muted-foreground/40">&rarr;</div>
            <div className="flex flex-col gap-2">
              {[t("quadraticInequalities"), t("quadraticFunctions"), t("circleEquations")].map((unit) => (
                <div key={unit} className="rounded-lg border bg-muted/50 px-3 py-1.5 text-center">
                  <p className="text-xs font-medium">{unit}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
