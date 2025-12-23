"use client";

import { useCallback } from "react";
import { usePolling, useApi } from "@/lib/hooks/useApi";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface SiteLogsModalProps {
  siteKey: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function SiteLogsModal({
  siteKey,
  isOpen,
  onClose,
}: SiteLogsModalProps) {
  const getSiteLogs = useCallback((): Promise<Log[] | { logs?: Log[] }> => {
    if (!siteKey) return Promise.resolve([] as Log[]);
    return apiClient.getSiteLogs(siteKey, 200) as Promise<
      Log[] | { logs?: Log[] }
    >;
  }, [siteKey]);

  type Log = { timestamp?: string; site_key?: string; message?: string };
  const { data: logs } = usePolling<Log[] | { logs?: Log[] }>(
    getSiteLogs,
    5000,
    Boolean(isOpen && siteKey)
  );

  // Use stable function reference for manual refetch with proper dependencies
  const getRefetchLogs = useCallback(async () => {
    if (!siteKey) return { logs: [] };
    return await apiClient.getSiteLogs(siteKey, 200);
  }, [siteKey]);

  const { refetch } = useApi(getRefetchLogs, {
    immediate: false,
  });

  if (!isOpen) return null;

  const logsArray: Log[] = Array.isArray(logs)
    ? (logs as Log[])
    : (logs as unknown as { logs?: Log[] })?.logs || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-3xl bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-700 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white">
              Logs: {siteKey}
            </h3>
            <p className="text-slate-400 text-sm">
              Live site-specific logs (updates every 5s)
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => {
                refetch();
                toast.success("Logs refreshed");
              }}
              variant="outline"
              size="sm"
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="hidden sm:inline">Refresh</span>
            </Button>
            <Button
              onClick={onClose}
              variant="ghost"
              className="text-slate-300 hover:text-white"
            >
              Close
            </Button>
          </div>
        </div>
        <div className="p-4 sm:p-6">
          <div className="bg-slate-900 rounded-lg p-3 sm:p-4 h-[60vh] overflow-y-auto font-mono text-xs sm:text-sm">
            {logsArray.length > 0 ? (
              logsArray.map((log: Log, idx: number) => {
                const ts = log.timestamp
                  ? new Date(log.timestamp).toLocaleTimeString()
                  : "";
                const prefix = log.site_key ? `[${log.site_key}] ` : "";
                const message = log.message || JSON.stringify(log);
                return (
                  <div key={idx} className="text-slate-300 break-all">
                    {`[${ts}] ${prefix}${message}`}
                  </div>
                );
              })
            ) : (
              <div className="text-slate-400">No logs available.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
