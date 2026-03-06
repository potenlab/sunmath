import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/api";
import type {
  ProblemCreate,
  ProblemListResponse,
  ProblemRegistrationResponse,
  ProblemResponse,
  ProblemUpdate,
  SimilarProblemResponse,
} from "../types";

export function useProblems(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["problems", "list", page, pageSize],
    queryFn: () =>
      get<ProblemListResponse>(`/problems?page=${page}&page_size=${pageSize}`),
  });
}

export function useCreateProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ProblemCreate) =>
      post<ProblemRegistrationResponse>("/problems", body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems", "list"] });
    },
  });
}

export function useUpdateProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: ProblemUpdate & { id: number }) =>
      put<ProblemResponse>(`/problems/${id}`, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
    },
  });
}

export function useDeleteProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => del(`/problems/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems", "list"] });
    },
  });
}

export function useProblem(problemId: number | null) {
  return useQuery({
    queryKey: ["problems", problemId],
    queryFn: () => get<ProblemResponse>(`/problems/${problemId}`),
    enabled: problemId !== null,
  });
}

export function useSimilarProblems(problemId: number | null) {
  return useQuery({
    queryKey: ["problems", problemId, "similar"],
    queryFn: () =>
      get<SimilarProblemResponse>(`/problems/${problemId}/similar`),
    enabled: problemId !== null,
  });
}
