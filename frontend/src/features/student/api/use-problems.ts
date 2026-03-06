import { useQuery } from "@tanstack/react-query";
import { get } from "@/lib/api";
import type { ProblemListResponse, ProblemResponse } from "../types";

export function useStudentProblems(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["student", "problems", page, pageSize],
    queryFn: () =>
      get<ProblemListResponse>(`/problems?page=${page}&page_size=${pageSize}`),
  });
}

export function useStudentProblem(problemId: number | null) {
  return useQuery({
    queryKey: ["student", "problems", problemId],
    queryFn: () => get<ProblemResponse>(`/problems/${problemId}`),
    enabled: problemId !== null,
  });
}
