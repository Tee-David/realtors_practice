import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrapeHistory, ScrapeHistoryItem } from "@/lib/types";

export function ScrapeHistoryPanel() {
  const [history, setHistory] = useState<ScrapeHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    apiClient
      .getScrapeHistory(10)
      .then((data: any) => {
        // Backend returns {history: [...]} with simple site metadata
        // Transform to match frontend ScrapeHistoryItem format
        const rawHistory = data.history || data.scrapes || [];
        const transformed = rawHistory.map((item: any, index: number) => ({
          id: item.id || item.site_key || `history-${index}`,
          start_time: item.start_time || item.timestamp,
          end_time: item.end_time || item.timestamp,
          duration_seconds: item.duration_seconds || 0,
          sites: item.sites || (item.site_key ? [item.site_key] : []),
          total_listings: item.total_listings || item.count || 0,
          status: item.status || 'completed',
          error: item.error
        }));
        setHistory(transformed);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || "Failed to fetch history");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle>Recent Scrape Runs</CardTitle>
      </CardHeader>
      <CardContent className="max-h-96 overflow-y-auto">
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-400">Error: {error}</div>}
        {!loading && !error && history.length === 0 && (
          <div>No recent runs found.</div>
        )}
        <ul className="space-y-2">
          {history.map((run) => (
            <li key={run.id} className="border-b pb-2">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold">
                    {run.status === "completed"
                      ? "✅"
                      : run.status === "failed"
                      ? "❌"
                      : "⚠️"}
                  </span>{" "}
                  {new Date(run.start_time).toLocaleString()}
                  <br />
                  {run.end_time && (
                    <span className="text-xs text-slate-400">
                      Completed: {new Date(run.end_time).toLocaleString()}
                    </span>
                  )}
                </div>
                <div className="text-sm">
                  <span className="text-green-400 font-semibold">
                    {run.total_listings ?? 0}
                  </span>{" "}
                  <span className="text-slate-400">properties</span>
                  <br />
                  <span className="text-xs text-slate-500">
                    from {run.sites.length ?? 0} site{run.sites.length !== 1 ? 's' : ''}
                    {run.sites.length > 0 && run.sites.length <= 3 ? ` (${run.sites.join(', ')})` : ''}
                  </span>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    // TODO: Implement view details modal
                    alert(`Details for run ${run.id}\nSites: ${run.sites.join(', ')}\nListings: ${run.total_listings}\nDuration: ${run.duration_seconds}s`);
                  }}
                >
                  View Details
                </Button>
              </div>
              {run.error && (
                <div className="text-red-400 text-xs">Error: {run.error}</div>
              )}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
