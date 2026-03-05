import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const COLOR_SCHEMES = {
  amber: {
    card: "from-amber-50 to-orange-50",
    iconBg: "bg-amber-100",
    iconText: "text-amber-600",
    value: "text-amber-700",
    label: "text-amber-600/70",
  },
  emerald: {
    card: "from-emerald-50 to-teal-50",
    iconBg: "bg-emerald-100",
    iconText: "text-emerald-600",
    value: "text-emerald-700",
    label: "text-emerald-600/70",
  },
  violet: {
    card: "from-violet-50 to-purple-50",
    iconBg: "bg-violet-100",
    iconText: "text-violet-600",
    value: "text-violet-700",
    label: "text-violet-600/70",
  },
  red: {
    card: "from-red-50 to-rose-50",
    iconBg: "bg-red-100",
    iconText: "text-red-600",
    value: "text-red-700",
    label: "text-red-600/70",
  },
  blue: {
    card: "from-blue-50 to-sky-50",
    iconBg: "bg-blue-100",
    iconText: "text-blue-600",
    value: "text-blue-700",
    label: "text-blue-600/70",
  },
} as const;

interface StatCardProps {
  icon: LucideIcon;
  value: string | number;
  label: string;
  colorScheme: keyof typeof COLOR_SCHEMES;
}

export function StatCard({ icon: Icon, value, label, colorScheme }: StatCardProps) {
  const colors = COLOR_SCHEMES[colorScheme];

  return (
    <Card
      className={`border-none bg-gradient-to-br ${colors.card} shadow-sm`}
    >
      <CardContent className="flex items-center gap-4 pt-6">
        <div
          className={`flex h-12 w-12 items-center justify-center rounded-xl ${colors.iconBg}`}
        >
          <Icon className={`size-6 ${colors.iconText}`} />
        </div>
        <div>
          <p className={`text-2xl font-bold ${colors.value}`}>{value}</p>
          <p className={`text-xs ${colors.label}`}>{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}
