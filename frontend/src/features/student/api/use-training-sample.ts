import { useMutation } from "@tanstack/react-query";
import { postFormData } from "@/lib/api";

interface SaveTrainingSampleParams {
  file: File;
  question_id: number;
}

export function useSaveTrainingSample() {
  return useMutation({
    mutationFn: ({ file, question_id }: SaveTrainingSampleParams) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("question_id", String(question_id));
      return postFormData<{ id: number; student_id: number; image_gcs_uri: string }>(
        "/ocr/training-samples",
        formData,
      );
    },
  });
}
