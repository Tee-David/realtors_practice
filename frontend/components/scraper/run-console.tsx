"use client";

import { useState, useCallback, useEffect, useMemo } from "react";
import { RefreshCw, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api";
import { useApi, usePolling } from "@/lib/hooks/useApi";
import {
  LogEntry,
  LogResponse,
  ScrapeHistory,
  ScrapeHistoryItem,
  GitHubWorkflowLogsResponse,
} from "@/lib/types";
import { toast } from "sonner";

interface RunConsoleProps {
  isRunning: boolean;
  githubRunId?: number;
}

export function RunConsole({ isRunning, githubRunId }: RunConsoleProps) {
  const [activeTab, setActiveTab] = useState("current");
  const [maxVisibleLogs, setMaxVisibleLogs] = useState(100); // Limit visible logs for performance

  // DEBUG: Log when githubRunId changes
  useEffect(() => {
    console.log('[RunConsole] githubRunId changed:', githubRunId);
    console.log('[RunConsole] isRunning:', isRunning);
  }, [githubRunId, isRunning]);

  // Only use new polling and history logic below

  // Poll for logs
  const getCurrentLogs = useCallback(async (): Promise<LogEntry[]> => {
    const res: LogResponse = await apiClient.getLogs({ limit: 50 });
    return res.logs;
  }, []);
  const getErrorLogs = useCallback(async (): Promise<LogEntry[]> => {
    const res: LogResponse = await apiClient.getErrorLogs(20);
    return res.logs;
  }, []);

  const { data: currentLogs } = usePolling<LogEntry[]>(
    getCurrentLogs,
    isRunning ? 5000 : 15000,
    true
  );
  const { data: errorLogs } = usePolling<LogEntry[]>(
    getErrorLogs,
    isRunning ? 10000 : 30000,
    true
  );

  // Poll for scrape history
  const getHistory = useCallback(async (): Promise<ScrapeHistoryItem[]> => {
    const res: ScrapeHistory = await apiClient.getScrapeHistory(10);
    return res.scrapes;
  }, []);
  const { data: historyData, refetch: refetchHistory } =
    useApi<ScrapeHistoryItem[]>(getHistory);

  // Poll for GitHub workflow logs when run ID is available
  const getGithubLogs = useCallback(async (): Promise<GitHubWorkflowLogsResponse | null> => {
    if (!githubRunId) {
      console.log('[RunConsole] No githubRunId, skipping log fetch');
      return null;
    }
    try {
      console.log('[RunConsole] Fetching logs for run:', githubRunId);
      const logs = await apiClient.getWorkflowLogs(githubRunId, { tail: 200 });
      console.log('[RunConsole] Received logs:', logs);
      return logs;
    } catch (error) {
      console.error("[RunConsole] Failed to fetch GitHub logs:", error);
      return null;
    }
  }, [githubRunId]);

  // Determine if we should continue polling
  // Stop polling if:
  // 1. No run ID exists
  // 2. Run is completed (status === "completed")
  const [shouldPoll, setShouldPoll] = useState(false);

  const { data: githubLogsData } = usePolling<GitHubWorkflowLogsResponse | null>(
    getGithubLogs,
    githubRunId ? 10000 : 60000, // Poll every 10s if run ID exists, otherwise 60s
    shouldPoll
  );

  // Update polling state based on run ID and workflow status
  useEffect(() => {
    if (!githubRunId) {
      // No run ID, don't poll
      setShouldPoll(false);
      console.log('[RunConsole] No run ID, stopping polling');
      return;
    }

    // Check if the workflow is still active
    if (githubLogsData && githubLogsData.jobs && githubLogsData.jobs.length > 0) {
      const allJobsCompleted = githubLogsData.jobs.every(
        (job) => job.status === "completed"
      );

      if (allJobsCompleted) {
        // All jobs completed, stop polling
        setShouldPoll(false);
        console.log('[RunConsole] All jobs completed, stopping polling');
      } else {
        // Jobs still running, continue polling
        setShouldPoll(true);
        console.log('[RunConsole] Jobs still running, continuing polling');
      }
    } else {
      // Start polling when we have a run ID but no data yet
      setShouldPoll(true);
      console.log('[RunConsole] Starting polling for run ID:', githubRunId);
    }
  }, [githubRunId, githubLogsData]);

  // DEBUG: Log when githubLogsData changes
  useEffect(() => {
    console.log('[RunConsole] githubLogsData updated:', githubLogsData);
  }, [githubLogsData]);

  const handleRefresh = () => {
    toast.success("Logs refreshed");
  };

  const formatLogEntry = (log: LogEntry) => {
    const timestamp = new Date(log.timestamp).toLocaleTimeString();
    const sitePrefix = log.site ? `[${log.site}] ` : "";
    return `> [${timestamp}] ${sitePrefix}${log.message}`;
  };

  const tabs = [
    { id: "current", label: "Current Run" },
    { id: "errors", label: "Error Logs" },
    { id: "history", label: "History" },
  ];

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-4 sm:p-6 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">
            Run Console & Logs
          </h3>
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="sm"
            className="border-slate-600 text-slate-300 hover:bg-slate-700 flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>
      </div>

      {/* Mobile Tabs - Scrollable */}
      <div className="border-b border-slate-700">
        <div className="flex space-x-4 sm:space-x-8 px-4 sm:px-6 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-slate-400 hover:text-slate-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Console Content */}
      <div className="p-4 sm:p-6">
        <div className="bg-slate-900 rounded-lg p-3 sm:p-4 h-48 sm:h-64 overflow-y-auto font-mono text-xs sm:text-sm">
          {activeTab === "current" && (
            <div className="space-y-1">
              {/* Show GitHub workflow logs if available */}
              {githubRunId && githubLogsData && githubLogsData.jobs && githubLogsData.jobs.length > 0 ? (
                <div className="space-y-3">
                  <div className="text-blue-400 text-sm font-semibold flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    GitHub Workflow Run #{githubRunId}
                  </div>
                  {githubLogsData.jobs.map((job) => (
                    <div key={`job-${job.id}`} className="space-y-1">
                      {/* Job Header */}
                      <div className="flex items-center justify-between pb-1 border-b border-slate-700">
                        <div className="flex items-center gap-2">
                          <span className={`font-semibold text-xs ${
                            job.status === "completed" && job.conclusion === "success"
                              ? "text-green-400"
                              : job.status === "in_progress"
                              ? "text-blue-400"
                              : job.status === "queued"
                              ? "text-yellow-400"
                              : "text-red-400"
                          }`}>
                            {job.status === "completed" && job.conclusion === "success" ? "✓" :
                             job.status === "in_progress" ? "⟳" :
                             job.status === "queued" ? "⏱" : "✗"}
                          </span>
                          <span className="text-slate-300 text-xs font-medium">{job.name}</span>
                        </div>
                        <span className="text-slate-500 text-xs">
                          {job.log_count} lines
                        </span>
                      </div>

                      {/* Job Logs - Most Recent First */}
                      <div className="space-y-0.5 max-h-96 overflow-y-auto flex flex-col-reverse">
                        {job.logs && job.logs.length > 0 ? (
                          job.logs.map((line, lineIndex) => (
                            <div
                              key={`job-${job.id}-line-${lineIndex}`}
                              className={`text-xs font-mono ${
                                line.includes("ERROR") || line.includes("FAIL")
                                  ? "text-red-400"
                                  : line.includes("WARNING") || line.includes("WARN")
                                  ? "text-yellow-400"
                                  : line.includes("SUCCESS") || line.includes("✓")
                                  ? "text-green-400"
                                  : "text-slate-300"
                              }`}
                            >
                              {line}
                            </div>
                          ))
                        ) : (
                          <div className="text-slate-500 text-xs">No logs available yet...</div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Link to GitHub Actions */}
                  <div className="pt-2 border-t border-slate-700">
                    <a
                      href={`https://github.com/${process.env.NEXT_PUBLIC_GITHUB_OWNER || 'Tee-David'}/${process.env.NEXT_PUBLIC_GITHUB_REPO || 'realtors_practice'}/actions/runs/${githubRunId}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 text-xs flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      View full logs on GitHub
                    </a>
                  </div>
                </div>
              ) : (
                /* Fallback to local logs - Most Recent First */
                <>
                  {currentLogs && currentLogs.length > 0 ? (
                    [...currentLogs].reverse().map((log: LogEntry, index: number) => (
                      <div
                        key={`log-${index}`}
                        className="text-green-400 break-all text-sm"
                      >
                        {formatLogEntry(log)}
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-400">
                      {githubRunId ? (
                        <div className="flex items-center gap-2">
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          <span>Loading workflow logs...</span>
                        </div>
                      ) : (
                        "No active scrape running. Start a scrape to see live logs here."
                      )}
                    </div>
                  )}
                  {isRunning && !githubRunId && (
                    <div className="text-blue-400 animate-pulse">
                      {"> Running..."}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {activeTab === "errors" && (
            <div className="space-y-1">
              {errorLogs && errorLogs.length > 0 ? (
                [...errorLogs].reverse().map((log: LogEntry, index: number) => (
                  <div
                    key={`error-${index}`}
                    className="text-red-400 break-all"
                  >
                    • {formatLogEntry(log)}
                  </div>
                ))
              ) : (
                <div className="text-slate-400">No recent errors</div>
              )}
            </div>
          )}

          {activeTab === "history" && (
            <div className="space-y-2">
              {historyData && historyData.length > 0 ? (
                historyData.map((run: ScrapeHistoryItem, index: number) => {
                  const startTime = run.start_time
                    ? new Date(run.start_time).toLocaleString()
                    : "Unknown";
                  const endTime = run.end_time
                    ? new Date(run.end_time).toLocaleString()
                    : "N/A";
                  const duration = run.duration_seconds
                    ? Math.round(run.duration_seconds / 60)
                    : null;
                  const sites = Array.isArray(run.sites)
                    ? run.sites.join(", ")
                    : run.sites || "N/A";
                  const statusText =
                    run.status === "completed"
                      ? "✓ Success"
                      : run.status === "failed"
                      ? "✗ Failed"
                      : "Partial";
                  const statusColor =
                    run.status === "completed"
                      ? "text-green-400"
                      : run.status === "failed"
                      ? "text-red-400"
                      : "text-yellow-400";

                  return (
                    <div
                      key={`history-${run.id || index}`}
                      className="pb-2 border-b border-slate-800 last:border-0"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
                        <span className={`font-semibold ${statusColor}`}>
                          {statusText}
                        </span>
                        <span className="text-slate-600">•</span>
                        <span className="text-slate-400 text-xs">
                          Run ID: {run.id || "N/A"}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 mt-1 space-y-0.5">
                        <div>Started: {startTime}</div>
                        {run.end_time && <div>Completed: {endTime}</div>}
                        <div>Sites: {sites}</div>
                        <div className="flex gap-3 flex-wrap">
                          {duration !== null && (
                            <span>Duration: {duration}min</span>
                          )}
                          <span>Total Listings: {run.total_listings}</span>
                          {run.error && (
                            <span className="text-red-400">
                              Error: {run.error}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-slate-400">No run history available</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
