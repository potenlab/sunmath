"use client";

import { useEffect } from "react";
import { useRouter } from "@/i18n/navigation";

export default function StudentPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/student/problems");
  }, [router]);

  return (
    <div className="flex h-[50vh] items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500" />
    </div>
  );
}
