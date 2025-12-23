"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { HealthAlert } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertTriangle, XCircle, Info, Check } from "lucide-react";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<HealthAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = () => {
    setLoading(true);
    apiClient
      .healthAlerts()
      .then((res: HealthAlert[]) => {
        // Ensure we always set an array
        setAlerts(Array.isArray(res) ? res : []);
      })
      .catch((err: any) => {
        setError(err?.message || "Error fetching alerts");
        setAlerts([]); // Reset to empty array on error
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAlerts();
    // Auto-refresh every 2 minutes
    const interval = setInterval(fetchAlerts, 120000);
    return () => clearInterval(interval);
  }, []);

  const getIcon = (type: string) => {
    switch (type) {
      case "error":
        return <XCircle className="w-5 h-5 text-red-400" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Info className="w-5 h-5 text-blue-400" />;
    }
  };

  const getColorClass = (type: string) => {
    switch (type) {
      case "error":
        return "bg-red-500/10 border-red-500/20";
      case "warning":
        return "bg-yellow-500/10 border-yellow-500/20";
      default:
        return "bg-blue-500/10 border-blue-500/20";
    }
  };

  const unacknowledgedCount = Array.isArray(alerts)
    ? alerts.filter((a) => !a.acknowledged).length
    : 0;
  const errorCount = Array.isArray(alerts)
    ? alerts.filter((a) => a.type === "error").length
    : 0;
  const warningCount = Array.isArray(alerts)
    ? alerts.filter((a) => a.type === "warning").length
    : 0;

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Health Alerts</h1>
          <p className="text-slate-400 mt-1">
            System warnings, errors, and notifications
          </p>
        </div>
        <Button
          onClick={fetchAlerts}
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

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="text-sm text-slate-400">Total Alerts</div>
          <div className="text-2xl font-bold text-white mt-1">
            {alerts.length}
          </div>
        </div>
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <div className="text-sm text-red-400">Errors</div>
          <div className="text-2xl font-bold text-red-300 mt-1">
            {errorCount}
          </div>
        </div>
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
          <div className="text-sm text-yellow-400">Warnings</div>
          <div className="text-2xl font-bold text-yellow-300 mt-1">
            {warningCount}
          </div>
        </div>
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="text-sm text-blue-400">Unacknowledged</div>
          <div className="text-2xl font-bold text-blue-300 mt-1">
            {unacknowledgedCount}
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Alerts List */}
      {Array.isArray(alerts) && alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`${getColorClass(
                alert.type
              )} border rounded-lg p-5 transition-all hover:scale-[1.01]`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <div className="mt-0.5">{getIcon(alert.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 text-xs font-medium bg-slate-900/50 rounded uppercase">
                        {alert.type}
                      </span>
                      {alert.acknowledged && (
                        <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-300 rounded flex items-center gap-1">
                          <Check className="w-3 h-3" />
                          Acknowledged
                        </span>
                      )}
                    </div>
                    <div className="text-white font-medium mb-2">
                      {alert.message}
                    </div>
                    <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                      {alert.site_key && (
                        <div>
                          <span className="text-slate-500">Site:</span>{" "}
                          {alert.site_key}
                        </div>
                      )}
                      <div>
                        <span className="text-slate-500">Time:</span>{" "}
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-slate-800 rounded-lg">
          <Check className="w-12 h-12 text-green-400 mx-auto mb-3" />
          <p className="text-slate-300 font-medium">All clear!</p>
          <p className="text-slate-400 text-sm mt-1">No alerts at this time</p>
        </div>
      )}
    </div>
  );
}
