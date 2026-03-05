import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function IntentExamples() {
  const t = useTranslations("grading");

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="text-lg">{t("intentBasedExamples")}</CardTitle>
        <CardDescription>{t("intentBasedExamplesDesc")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center gap-4 rounded-lg border p-4">
            <Badge className="bg-red-100 text-red-700 hover:bg-red-100 shrink-0">
              {t("wrong")}
            </Badge>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {t("example1Problem")}
              </p>
              <p className="text-xs text-muted-foreground">
                {t("example1Hint")}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-lg border p-4">
            <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100 shrink-0">
              {t("correct")}
            </Badge>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {t("example2Problem")}
              </p>
              <p className="text-xs text-muted-foreground">
                {t("example2Hint")}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-lg border p-4">
            <Badge className="bg-red-100 text-red-700 hover:bg-red-100 shrink-0">
              {t("wrong")}
            </Badge>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {t("example3Problem")}
              </p>
              <p className="text-xs text-muted-foreground">
                {t("example3Hint")}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
