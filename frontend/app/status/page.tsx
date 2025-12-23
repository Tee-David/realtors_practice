"use client";

import { useCallback, useState } from "react";
import { ScraperStatusCard } from "@/components/scraper/scraper-status-card";
import { apiClient } from "@/lib/api";
import { usePolling } from "@/lib/hooks/useApi";
import { ScrapeStatus } from "@/lib/types";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function StatusPage() {
  console.log("[StatusPage] Component rendering");
  const [manualRefreshKey, setManualRefreshKey] = useState(0);

  // Poll for scraper status
  const getScrapeStatus = useCallback(() => apiClient.getScrapeStatus(), []);
  const { data: scrapeStatus, loading: isLoading } = usePolling<ScrapeStatus>(
    getScrapeStatus,
    10000, // Poll every 10 seconds
    true
  );

  const handleRefresh = () => {
    setManualRefreshKey((prev) => prev + 1);
    // Trigger immediate re-fetch by calling the API directly
    apiClient.getScrapeStatus();
  };

  return (
    <div className="space-y-6 p-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Scraper Status</h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time status and metadata of your scrapers
          </p>
        </div>
        <Button
          onClick={handleRefresh}
          disabled={isLoading}
          variant="outline"
          size="sm"
          className="gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Status Cards */}
      <ScraperStatusCard scrapeStatus={scrapeStatus} key={manualRefreshKey} />

      {/* Raw JSON Display (optional, for debugging) */}
      {scrapeStatus && (
        <details className="bg-slate-800/30 border border-slate-700 rounded-lg p-4">
          <summary className="cursor-pointer text-slate-300 font-medium">
            View Raw JSON
          </summary>
          <pre className="mt-4 p-4 bg-slate-900 rounded-lg overflow-auto text-xs text-slate-300">
            {JSON.stringify(scrapeStatus, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}
