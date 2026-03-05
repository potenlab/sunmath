import type { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  icon: LucideIcon;
  iconGradient: string;
  title: string;
  description: string;
}

export function PageHeader({
  icon: Icon,
  iconGradient,
  title,
  description,
}: PageHeaderProps) {
  return (
    <div>
      <div className="flex items-center gap-3">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl shadow-sm bg-gradient-to-br ${iconGradient}`}
        >
          <Icon className="size-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
    </div>
  );
}
