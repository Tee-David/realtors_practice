"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { HealthCheck } from "@/lib/types";
import { RefreshCw, CheckCircle, AlertTriangle, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function HealthPage() {
  const [health, setHealth] = useState<HealthCheck | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = () => {
    setLoading(true);
    setError(null);
    apiClient
      .healthCheck()
      .then((res: HealthCheck) => setHealth(res))
      .catch((err: any) =>
        setError(err?.message || "Error fetching health status")
      )
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHealth();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = health?.status === "healthy";

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">API Health Status</h1>
          <p className="text-slate-400 mt-1">
            Monitor backend health and diagnostics
          </p>
        </div>
        <Button
          onClick={fetchHealth}
          disabled={loading}
          variant="outline"
          size="sm"
        >
          <RefreshCw
            className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-red-400" />
            <div>
              <div className="font-semibold text-red-400">Connection Error</div>
              <div className="text-sm text-red-300 mt-1">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && !health && (
        <div className="bg-slate-800 rounded-lg p-8 text-center">
          <Activity className="w-8 h-8 animate-pulse text-blue-500 mx-auto mb-2" />
          <p className="text-slate-400">Checking health status...</p>
        </div>
      )}

      {/* Health Status */}
      {health && (
        <>
          <div
            className={`rounded-lg p-6 ${
              isHealthy
                ? "bg-green-500/10 border border-green-500/20"
                : "bg-red-500/10 border border-red-500/20"
            }`}
          >
            <div className="flex items-center gap-3">
              {isHealthy ? (
                <CheckCircle className="w-8 h-8 text-green-400" />
              ) : (
                <AlertTriangle className="w-8 h-8 text-red-400" />
              )}
              <div>
                <div
                  className={`text-2xl font-bold ${
                    isHealthy ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {isHealthy
                    ? "All Systems Operational"
                    : "System Issues Detected"}
                </div>
                <div className="text-sm text-slate-400 mt-1">
                  Status: <span className="font-medium">{health.status}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-800 rounded-lg p-6">
              <div className="text-sm text-slate-400 mb-1">Version</div>
              <div className="text-xl font-semibold text-white">
                {health.version || "1.0.0"}
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-6">
              <div className="text-sm text-slate-400 mb-1">Last Check</div>
              <div className="text-xl font-semibold text-white">
                {health.timestamp
                  ? new Date(health.timestamp).toLocaleTimeString()
                  : "Now"}
              </div>
            </div>
          </div>

          {/* Raw Response */}
          <details className="bg-slate-800 rounded-lg p-6">
            <summary className="cursor-pointer text-white font-medium mb-2">
              View Raw Response
            </summary>
            <pre className="text-xs text-slate-300 overflow-auto p-4 bg-slate-900 rounded-lg mt-2">
              {JSON.stringify(health, null, 2)}
            </pre>
          </details>
        </>
      )}
    </div>
  );
}
