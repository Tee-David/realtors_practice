"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { SiteHealth } from "@/lib/types";

export default function SiteHealthPage() {
  const [siteKey, setSiteKey] = useState("");
  const [siteHealth, setSiteHealth] = useState<SiteHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSiteHealth = () => {
    if (!siteKey) return;
    setLoading(true);
    apiClient
      .siteHealth(siteKey)
      .then((res: SiteHealth) => setSiteHealth(res))
      .catch((err: any) =>
        setError(err?.message || "Error fetching site health")
      )
      .finally(() => setLoading(false));
  };

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold text-white">Site Health</h1>
      <p className="text-slate-400 text-sm mt-1">
        Check health status for a specific site
      </p>
      <div className="flex gap-2 items-center mb-4">
        <input
          type="text"
          value={siteKey}
          onChange={(e) => setSiteKey(e.target.value)}
          placeholder="Enter site key..."
          className="bg-slate-800 text-slate-200 rounded px-3 py-2 border border-slate-700"
        />
        <button
          onClick={fetchSiteHealth}
          disabled={!siteKey || loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Check
        </button>
      </div>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}
      {siteHealth && (
        <div className="bg-slate-900 rounded-lg p-4 text-slate-300">
          <div>
            <strong>Site Key:</strong> {siteHealth.site_key}
          </div>
          <div>
            <strong>Status:</strong> {siteHealth.status}
          </div>
          <div>
            <strong>Uptime %:</strong> {siteHealth.uptime_percentage}
          </div>
          <div>
            <strong>Consecutive Failures:</strong>{" "}
            {siteHealth.consecutive_failures}
          </div>
          {siteHealth.last_successful_scrape && (
            <div>
              <strong>Last Success:</strong> {siteHealth.last_successful_scrape}
            </div>
          )}
          {siteHealth.last_error && (
            <div className="text-red-400">
              <strong>Last Error:</strong> {siteHealth.last_error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
