import { useMutation, useQuery } from "@tanstack/react-query";
import { post, get } from "@/lib/api";
import type { GradeRequest, GradeResponse, CacheStatsResponse } from "../types";

export function useGradeMutation() {
  return useMutation({
    mutationFn: (body: GradeRequest) =>
      post<GradeResponse>("/grading/grade", body),
  });
}

export function useCacheStats() {
  return useQuery({
    queryKey: ["grading", "cache-stats"],
    queryFn: () => get<CacheStatsResponse>("/grading/cache/stats"),
  });
}
