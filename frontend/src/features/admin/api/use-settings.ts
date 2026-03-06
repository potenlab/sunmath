import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, put } from "@/lib/api";
import type { SettingsListResponse, SettingResponse } from "../types";

export function useSettings() {
  return useQuery({
    queryKey: ["admin", "settings"],
    queryFn: () => get<SettingsListResponse>("/admin/settings"),
  });
}

export function useUpdateSetting() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) =>
      put<SettingResponse>(`/admin/settings/${key}`, { value }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "settings"] });
    },
  });
}
