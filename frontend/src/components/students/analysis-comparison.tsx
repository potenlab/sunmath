import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { XCircle, Zap } from "lucide-react";

export function AnalysisComparison() {
  const t = useTranslations("studentDetail");

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {/* Naive Analysis */}
      <Card className="border-2 border-red-200 bg-red-50/40 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base text-red-700">
            <XCircle className="size-4 text-red-500" />
            Naive Analysis
          </CardTitle>
          <CardDescription className="text-red-600/70">
            Simple unit-level weakness listing
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-red-800 font-medium">
              &quot;Student is weak in:&quot;
            </p>
            <div className="flex flex-wrap gap-2">
              {[t("quadraticInequalities"), t("quadraticFunctions"), t("circleEquations")].map((unit) => (
                <Badge key={unit} className="bg-red-100 text-red-700 hover:bg-red-100 border border-red-200">
                  {unit}
                </Badge>
              ))}
            </div>
            <div className="mt-3 rounded-lg bg-red-100/60 p-3">
              <p className="text-xs text-red-600">{t("naiveAnalysis")}</p>
              <p className="mt-2 text-xs text-red-500/80">
                No root cause identified. Student must study 3 separate units independently.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* GraphRAG Analysis */}
      <Card className="border-2 border-emerald-200 bg-emerald-50/40 shadow-sm ring-2 ring-emerald-100">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base text-emerald-700">
            <Zap className="size-4 text-emerald-500" />
            GraphRAG Analysis
          </CardTitle>
          <CardDescription className="text-emerald-600/70">
            Prerequisite graph backtracking
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-emerald-800 font-medium">
              &quot;Root cause identified:&quot;
            </p>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100 border border-emerald-300 font-bold">
                {t("completingTheSquare")}
              </Badge>
              <span className="text-xs text-emerald-600">is the shared root cause</span>
            </div>
            <div className="mt-3 rounded-lg bg-emerald-100/60 p-3">
              <p className="text-xs text-emerald-700 font-semibold">{t("graphragAnalysis")}</p>
              <p className="mt-2 text-xs text-emerald-600/80">
                Fix 1 concept, resolve all 3 units. Efficient and targeted remediation.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
