import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/api";

export interface StudentResponse {
  id: number;
  name: string;
  grade_level: number | null;
  created_at: string;
}

export interface StudentListResponse {
  students: StudentResponse[];
  total: number;
}

export interface StudentCreate {
  name: string;
  grade_level?: number | null;
}

export interface StudentUpdate {
  name?: string;
  grade_level?: number | null;
}

export function useStudents() {
  return useQuery({
    queryKey: ["students", "list"],
    queryFn: () => get<StudentListResponse>("/students"),
  });
}

export function useCreateStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: StudentCreate) =>
      post<StudentResponse>("/students", body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students", "list"] });
    },
  });
}

export function useUpdateStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...body }: StudentUpdate & { id: number }) =>
      put<StudentResponse>(`/students/${id}`, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students", "list"] });
    },
  });
}

export function useDeleteStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => del(`/students/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["students", "list"] });
    },
  });
}
