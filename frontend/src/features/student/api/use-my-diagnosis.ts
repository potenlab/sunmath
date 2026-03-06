import { useQuery } from "@tanstack/react-query";
import { get } from "@/lib/api";
import type { DiagnosisResponse, WrongAnswerListResponse, MasteryListResponse } from "@/features/students/types";

export function useMyDiagnosis(studentId: number | null) {
  return useQuery({
    queryKey: ["student", "diagnosis", studentId],
    queryFn: () => get<DiagnosisResponse>(`/students/${studentId}/diagnosis`),
    enabled: studentId !== null,
  });
}

export function useMyWrongAnswers(studentId: number | null) {
  return useQuery({
    queryKey: ["student", "wrong-answers", studentId],
    queryFn: () =>
      get<WrongAnswerListResponse>(`/students/${studentId}/wrong-answers`),
    enabled: studentId !== null,
  });
}

export function useMyMastery(studentId: number | null) {
  return useQuery({
    queryKey: ["student", "mastery", studentId],
    queryFn: () =>
      get<MasteryListResponse>(`/students/${studentId}/mastery`),
    enabled: studentId !== null,
  });
}
