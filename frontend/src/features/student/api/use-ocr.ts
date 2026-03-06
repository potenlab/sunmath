import { useMutation } from "@tanstack/react-query";
import { postFormData } from "@/lib/api";

interface OCRResult {
  text: string;
  confidence: number;
}

export function useOCR() {
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return postFormData<OCRResult>("/ocr/recognize", formData);
    },
  });
}
