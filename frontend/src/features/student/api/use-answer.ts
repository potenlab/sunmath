import { useMutation, useQueryClient } from "@tanstack/react-query";
import { post } from "@/lib/api";
import type { GradeResponse } from "../types";

interface SubmitAnswerParams {
  student_id: number;
  question_id: number;
  submitted_answer: string;
}

export function useSubmitAnswer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: SubmitAnswerParams) =>
      post<GradeResponse>("/grading/grade", params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["student", "mastery"] });
      queryClient.invalidateQueries({ queryKey: ["students"] });
    },
  });
}
