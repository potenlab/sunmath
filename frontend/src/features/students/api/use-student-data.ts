import { useQuery, useMutation } from "@tanstack/react-query";
import { get } from "@/lib/api";
import type {
  DiagnosisResponse,
  WrongAnswerListResponse,
  MasteryListResponse,
  LearningPathResponse,
} from "../types";

export function useDiagnosisQuery(studentId: number) {
  return useQuery({
    queryKey: ["students", studentId, "diagnosis"],
    queryFn: () =>
      get<DiagnosisResponse>(`/students/${studentId}/diagnosis`),
    enabled: false,
  });
}

export function useWrongAnswers(studentId: number) {
  return useQuery({
    queryKey: ["students", studentId, "wrong-answers"],
    queryFn: () =>
      get<WrongAnswerListResponse>(`/students/${studentId}/wrong-answers`),
  });
}

export function useMastery(studentId: number) {
  return useQuery({
    queryKey: ["students", studentId, "mastery"],
    queryFn: () =>
      get<MasteryListResponse>(`/students/${studentId}/mastery`),
  });
}

export function useLearningPath(studentId: number) {
  return useQuery({
    queryKey: ["students", studentId, "learning-path"],
    queryFn: () =>
      get<LearningPathResponse>(`/students/${studentId}/learning-path`),
    enabled: false,
  });
}
