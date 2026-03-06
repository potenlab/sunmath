"use client";

import { useParams } from "next/navigation";
import { StudentDetail } from "@/features/students/components/detail.students";

export default function AdminStudentDetailPage() {
  const params = useParams();
  const id = params.id as string;

  return <StudentDetail id={id} />;
}
