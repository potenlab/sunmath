"use client";

import { useParams } from "next/navigation";
import { StudentDetail } from "@/features/students/components/detail.students";

export default function StudentDiagnosisPage() {
  const params = useParams();
  const id = params.id as string;

  return <StudentDetail id={id} />;
}
