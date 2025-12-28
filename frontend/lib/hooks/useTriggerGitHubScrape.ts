import { useState } from "react";
import { apiClient } from "@/lib/api";

export function useTriggerGitHubScrape() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const triggerScrape = async ({
    pageCap = 20,
    geocode = 1,
    sites = [],
  }: {
    pageCap?: number;
    geocode?: number;
    sites?: string[];
  }) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      // The backend expects page_cap, geocode, sites
      const res = await apiClient.triggerGitHubScrape(sites);
      setResult(res);
      setLoading(false);
      return res;
    } catch (err: any) {
      setError(err.message || "Failed to trigger GitHub Actions scrape");
      setLoading(false);
      throw err;
    }
  };

  return { triggerScrape, loading, error, result };
}
