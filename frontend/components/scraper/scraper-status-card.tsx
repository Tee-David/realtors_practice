"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrapeStatus } from "@/lib/types";
import { Clock, CheckCircle2, XCircle, Database } from "lucide-react";

interface ScraperStatusCardProps {
  scrapeStatus: ScrapeStatus | null;
}

export function ScraperStatusCard({ scrapeStatus }: ScraperStatusCardProps) {
  if (!scrapeStatus) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-slate-200">Scraper Status</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400">Loading status...</p>
        </CardContent>
      </Card>
    );
  }

  const { is_running, current_run, last_run } = scrapeStatus;

  // Derive status string
  const getStatus = () => {
    if (is_running) return "running";
    if (last_run?.success === true) return "completed";
    if (last_run?.success === false) return "error";
    return "idle";
  };

  const status = getStatus();
  const activeRun = current_run || last_run;

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-slate-200 flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Scraper Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">State:</span>
            <Badge
              variant={status === "running" ? "default" : "secondary"}
              className={
                status === "running"
                  ? "bg-blue-500 hover:bg-blue-600"
                  : status === "completed"
                  ? "bg-green-500 hover:bg-green-600"
                  : status === "error"
                  ? "bg-red-500 hover:bg-red-600"
                  : "bg-slate-600 hover:bg-slate-700"
              }
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Badge>
          </div>

          {/* Show current run details if running */}
          {is_running && current_run && (
            <>
              {current_run.batch_info?.current_batch_sites && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Current Sites:</span>
                  <span className="text-slate-300 font-semibold">
                    {current_run.batch_info.current_batch_sites.join(", ")}
                  </span>
                </div>
              )}
              {current_run.progress && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Sites:</span>
                  <span className="text-slate-300 font-semibold">
                    {current_run.progress.completed_sites} /{" "}
                    {current_run.progress.total_sites}
                  </span>
                </div>
              )}
              {current_run.started_at && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Started:</span>
                  <span className="text-slate-300">
                    {new Date(current_run.started_at).toLocaleString()}
                  </span>
                </div>
              )}
              {current_run.timing?.estimated_completion && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">ETA:</span>
                  <span className="text-slate-300">
                    {new Date(
                      current_run.timing.estimated_completion
                    ).toLocaleTimeString()}
                  </span>
                </div>
              )}
              {current_run.progress && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Progress:</span>
                  <span className="text-green-300 font-bold">
                    {Math.round(
                      (current_run.progress.completed_sites /
                        current_run.progress.total_sites) *
                        100
                    )}
                    %
                  </span>
                </div>
              )}
            </>
          )}

          {/* Show last run details if not running */}
          {!is_running && last_run && (
            <>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Last Completed:</span>
                <span className="text-slate-300">
                  {new Date(last_run.completed_at).toLocaleString()}
                </span>
              </div>
              {last_run.final_stats && (
                <>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">Sites:</span>
                    <span className="text-slate-300 font-semibold">
                      {last_run.final_stats.successful_sites} /{" "}
                      {last_run.final_stats.total_sites}
                    </span>
                  </div>
                  {last_run.final_stats.failed_sites > 0 && (
                    <div className="flex items-center gap-2">
                      <span className="text-slate-400">Failed:</span>
                      <span className="text-red-300 font-bold">
                        {last_run.final_stats.failed_sites}
                      </span>
                    </div>
                  )}
                </>
              )}
              {last_run.timing && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Duration:</span>
                  <span className="text-slate-300">
                    {Math.round(last_run.timing.elapsed_seconds)}s
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
