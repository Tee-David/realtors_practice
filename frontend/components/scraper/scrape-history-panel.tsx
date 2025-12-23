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
      .then((data: ScrapeHistory) => {
        setHistory(data.scrapes || []);
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
      <CardContent>
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
                <div>
                  <span className="text-green-400">
                    {run.total_listings ?? 0}
                  </span>{" "}
                  /{" "}
                  <span className="text-slate-400">
                    {run.sites.length ?? 0}
                  </span>{" "}
                  sites
                </div>
                <Button size="sm" variant="outline">
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
