import { useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Gauge } from "lucide-react";

interface SettingsFormProps {
  similarityThreshold: number;
  onSimilarityChange: (value: number) => void;
  confidenceThreshold: number;
  onConfidenceChange: (value: number) => void;
  duplicateMode: "warn" | "block";
  onDuplicateModeChange: (mode: "warn" | "block") => void;
  onSave: () => void;
}

export function SettingsForm({
  similarityThreshold,
  onSimilarityChange,
  confidenceThreshold,
  onConfidenceChange,
  duplicateMode,
  onDuplicateModeChange,
  onSave,
}: SettingsFormProps) {
  const t = useTranslations("admin");

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Gauge className="size-4 text-primary" />
          {t("gradingSettings")}
        </CardTitle>
        <CardDescription>{t("gradingSettingsDesc")}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Similarity Threshold Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">
              {t("similarityLabel")}
            </label>
            <span className="rounded-md bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700">
              {similarityThreshold.toFixed(2)}
            </span>
          </div>
          <Slider
            value={[similarityThreshold * 100]}
            onValueChange={(vals) => onSimilarityChange(vals[0] / 100)}
            min={0}
            max={100}
            step={1}
            className="w-full"
          />
          <p className="text-[11px] text-muted-foreground">
            {t("similarityHint")}
          </p>
        </div>
        <Separator />

        {/* Confidence Threshold Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">
              {t("confidenceThreshold")}
            </label>
            <span className="rounded-md bg-violet-100 px-2 py-0.5 text-xs font-semibold text-violet-700">
              {confidenceThreshold.toFixed(2)}
            </span>
          </div>
          <Slider
            value={[confidenceThreshold * 100]}
            onValueChange={(vals) => onConfidenceChange(vals[0] / 100)}
            min={0}
            max={100}
            step={1}
            className="w-full"
          />
          <p className="text-[11px] text-muted-foreground">
            {t("confidenceHint")}
          </p>
        </div>
        <Separator />

        {/* Duplicate Detection Mode */}
        <div className="space-y-3">
          <label className="text-sm font-medium">
            {t("duplicateDetectionMode")}
          </label>
          <div className="flex items-center gap-3">
            <Badge
              className={
                duplicateMode === "warn"
                  ? "bg-amber-100 text-amber-700 hover:bg-amber-100"
                  : "cursor-pointer bg-transparent text-muted-foreground hover:bg-amber-50"
              }
              variant={duplicateMode === "warn" ? "default" : "outline"}
            >
              {t("warn")}
            </Badge>
            <Switch
              checked={duplicateMode === "block"}
              onCheckedChange={(checked) =>
                onDuplicateModeChange(checked ? "block" : "warn")
              }
            />
            <Badge
              className={
                duplicateMode === "block"
                  ? "bg-red-100 text-red-700 hover:bg-red-100"
                  : "cursor-pointer bg-transparent text-muted-foreground hover:bg-red-50"
              }
              variant={duplicateMode === "block" ? "default" : "outline"}
            >
              {t("block")}
            </Badge>
          </div>
          <p className="text-[11px] text-muted-foreground">
            {t("duplicateHint")}
          </p>
        </div>
        <Separator />

        <Button
          onClick={onSave}
          className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-sm hover:opacity-90"
        >
          Save Settings
        </Button>
      </CardContent>
    </Card>
  );
}
