"use client";

import { useParams } from "next/navigation";
import { ProblemDetail } from "@/features/admin/components/problem-detail";

export default function AdminProblemDetailPage() {
  const params = useParams();
  return <ProblemDetail id={params.id as string} />;
}
