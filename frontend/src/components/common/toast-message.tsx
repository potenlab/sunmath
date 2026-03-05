import { CheckCircle2, AlertTriangle } from "lucide-react";

interface ToastMessageProps {
  message: string;
  variant: "success" | "error";
}

export function ToastMessage({ message, variant }: ToastMessageProps) {
  if (variant === "error") {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
        <AlertTriangle className="size-4" />
        {message}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">
      <CheckCircle2 className="size-4" />
      {message}
    </div>
  );
}
