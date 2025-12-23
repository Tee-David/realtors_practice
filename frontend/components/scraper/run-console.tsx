"use client";

import { useState, useCallback } from "react";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api";
import { useApi, usePolling } from "@/lib/hooks/useApi";
import {
  LogEntry,
  LogResponse,
  ScrapeHistory,
  ScrapeHistoryItem,
} from "@/lib/types";
import { toast } from "sonner";

interface RunConsoleProps {
  isRunning: boolean;
}

export function RunConsole({ isRunning }: RunConsoleProps) {
  const [activeTab, setActiveTab] = useState("current");

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
              {currentLogs && currentLogs.length > 0 ? (
                currentLogs.map((log: LogEntry, index: number) => (
                  <div
                    key={`log-${index}`}
                    className="text-green-400 break-all"
                  >
                    {formatLogEntry(log)}
                  </div>
                ))
              ) : (
                <div className="text-slate-400">No recent logs</div>
              )}
              {isRunning && (
                <div className="text-blue-400 animate-pulse">
                  {"> Running..."}
                </div>
              )}
            </div>
          )}

          {activeTab === "errors" && (
            <div className="space-y-1">
              {errorLogs && errorLogs.length > 0 ? (
                errorLogs.map((log: LogEntry, index: number) => (
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
