import { useDiagnosisQuery } from "../api/use-student-data";

export function useDiagnosis(studentId: number) {
  const { data, refetch, isFetching, isSuccess } = useDiagnosisQuery(studentId);

  const analysisState: "idle" | "loading" | "done" = isFetching
    ? "loading"
    : isSuccess && data
      ? "done"
      : "idle";

  const handleRunAnalysis = () => {
    refetch();
  };

  return { analysisState, diagnosis: data ?? null, handleRunAnalysis };
}
