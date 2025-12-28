import useSWR from "swr";
import { apiClientAxios } from "@/lib/api-axios";
import type { QueryResult } from "@/lib/types";

/**
 * useSWRProperties - fetches property data, supports polling for new results after a scrape.
 * @param params - query params for filtering properties
 * @param refreshInterval - polling interval in ms (0 = no polling)
 */
export function useSWRProperties(
  params: Record<string, any> = {},
  refreshInterval = 0
) {
  const { data, error, isLoading, mutate } = useSWR<QueryResult>(
    ["properties", params],
    async (key) => {
      return apiClientAxios.getProperties(
        (key as [string, Record<string, any>])[1]
      );
    },
    { refreshInterval }
  );

  return {
    properties: data?.properties || [],
    total: data?.total || 0,
    loading: isLoading,
    error,
    mutate,
  };
}
