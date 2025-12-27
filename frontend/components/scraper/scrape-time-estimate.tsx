"use client";

import React, { useState } from "react";
import { apiClient } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

interface ScrapeTimeEstimateProps {
  pageCap: number;
  geocode: boolean;
  sites?: string[];
}

interface TimeEstimateResponse {
  estimated_duration_minutes: number;
  estimated_duration_hours: number;
  estimated_duration_text: string;
  site_count: number;
  batch_type: string;
  sessions: number;
  sites_per_session: number;
  max_parallel_sessions: number;
  session_time_minutes: number;
  session_timeout_limit: number;
  total_timeout_limit: number;
  timeout_risk: "safe" | "warning" | "danger";
  timeout_message: string | null;
  recommendations: string[];
  configuration: any;
  breakdown?: {
    scraping_per_site?: number;
    geocoding_per_site?: number;
    upload_per_site?: number;
    watcher_overhead?: number;
    buffer_multiplier?: number;
  };
}

export function ScrapeTimeEstimate({
  pageCap,
  geocode,
  sites,
}: ScrapeTimeEstimateProps) {
  const [estimate, setEstimate] = useState<TimeEstimateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTestModal, setShowTestModal] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testError, setTestError] = useState<string | null>(null);
  const [testParams, setTestParams] = useState({
    rateLimit: 5,
    concurrency: 2,
    dryRun: true,
  });

  // Track last payload for manual refresh
  const lastPayloadRef = React.useRef<any>(null);

  const fetchEstimate = async () => {
    setLoading(true);
    setError(null);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
      const url = baseUrl
        ? `${baseUrl.replace(/\/$/, "")}/github/estimate-scrape-time`
        : "/api/github/estimate-scrape-time";
      const payload = {
        page_cap: pageCap,
        geocode: geocode ? 1 : 0,
        sites: sites || [],
      };
      lastPayloadRef.current = payload;
      console.log("[ScrapeTimeEstimate] Fetching:", url, payload);
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      console.log("[ScrapeTimeEstimate] Response status:", response.status);
      if (!response.ok) {
        let errMsg = "Failed to estimate time";
        if (response.status === 404 || response.status === 0) {
          errMsg =
            "Network error: Could not reach backend. Check API URL and server status.";
        }
        throw new Error(errMsg);
      }
      const data = await response.json();
      console.log("[ScrapeTimeEstimate] Response data:", data);
      setEstimate(data);
    } catch (err) {
      console.error("[ScrapeTimeEstimate] Error:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleTestScrape = async () => {
    setTestLoading(true);
    setTestError(null);
    setTestResult(null);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
      const url = baseUrl
        ? `${baseUrl.replace(/\/$/, "")}/scrape/test`
        : "/api/scrape/test";
      const payload = {
        page_cap: pageCap,
        geocode: geocode ? 1 : 0,
        sites: sites || [],
        rate_limit: testParams.rateLimit,
        concurrency: testParams.concurrency,
        dry_run: testParams.dryRun,
      };
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Test scrape failed");
      const data = await response.json();
      setTestResult(data);
    } catch (err) {
      setTestError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setTestLoading(false);
    }
  };

  // Fetch on mount and when params change
  React.useEffect(() => {
    fetchEstimate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageCap, geocode, JSON.stringify(sites)]);

  // Manual refresh handler
  const handleRefresh = () => {
    fetchEstimate();
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "safe":
        return "bg-green-700 text-white";
      case "warning":
        return "bg-yellow-600 text-black";
      case "danger":
        return "bg-red-700 text-white";
      default:
        return "bg-slate-700 text-white";
    }
  };

  return (
    <Card className="bg-slate-800/70 border-slate-700 mt-2">
      <CardHeader>
        <CardTitle className="text-slate-200 flex items-center gap-2">
          Scrape Time Estimate
          <button
            className="ml-3 px-2 py-1 text-xs rounded bg-slate-700 text-slate-200 hover:bg-slate-600 border border-slate-600"
            onClick={handleRefresh}
            disabled={loading}
            title="Refresh estimate"
          >
            {loading ? "..." : "Refresh"}
          </button>
          {/* <button
            className="ml-2 px-2 py-1 text-xs rounded bg-purple-700 text-white hover:bg-purple-600 border border-purple-600"
            onClick={() => setShowTestModal(true)}
            disabled={loading}
            title="Test Scrape"
          >
            Test Scrape
          </button> */}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <div className="text-blue-400">Estimating...</div>}
        {error && <div className="text-red-400">Error: {error}</div>}
        {estimate && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Estimated Time:</span>
              <span className="text-slate-200 font-bold">
                {estimate.estimated_duration_text}
              </span>
              {estimate.timeout_risk && (
                <Badge className={getRiskColor(estimate.timeout_risk)}>
                  {estimate.timeout_risk.toUpperCase()}
                </Badge>
              )}
            </div>
            {estimate.timeout_message && (
              <div className="text-yellow-400 text-sm">
                {estimate.timeout_message}
              </div>
            )}
            {estimate.recommendations && estimate.recommendations.length > 0 && (
              <ul className="list-disc ml-6 text-slate-300 text-sm">
                {estimate.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            )}
            <div className="text-xs text-slate-500 mt-2">
              Sites: {estimate.site_count} | Sessions: {estimate.sessions} |
              Batch: {estimate.batch_type}
            </div>
            {/* Granular breakdowns */}
            {estimate.breakdown && (
              <div className="mt-3 text-xs text-slate-400">
                <div className="font-semibold mb-1">Breakdown:</div>
                <ul className="ml-4 list-disc">
                  {estimate.breakdown.scraping_per_site !== undefined && (
                    <li>
                      Scraping per site: {estimate.breakdown.scraping_per_site} min
                    </li>
                  )}
                  {estimate.breakdown.geocoding_per_site !== undefined && (
                    <li>
                      Geocoding per site: {estimate.breakdown.geocoding_per_site} min
                    </li>
                  )}
                  {estimate.breakdown.upload_per_site !== undefined && (
                    <li>
                      Upload per site: {estimate.breakdown.upload_per_site} min
                    </li>
                  )}
                  {estimate.breakdown.watcher_overhead !== undefined && (
                    <li>
                      Watcher overhead: {estimate.breakdown.watcher_overhead} min
                    </li>
                  )}
                  {estimate.breakdown.buffer_multiplier !== undefined && (
                    <li>
                      Buffer multiplier: {estimate.breakdown.buffer_multiplier}
                    </li>
                  )}
                </ul>
              </div>
            )}
            {(estimate.session_time_minutes !== undefined ||
              estimate.session_timeout_limit !== undefined ||
              estimate.total_timeout_limit !== undefined ||
              estimate.sites_per_session !== undefined ||
              estimate.max_parallel_sessions !== undefined) && (
              <div className="mt-3 text-xs text-slate-400 space-y-1">
                {estimate.session_time_minutes !== undefined && estimate.session_timeout_limit !== undefined && (
                  <div>
                    Session time: {estimate.session_time_minutes} min (limit:{" "}
                    {estimate.session_timeout_limit} min)
                  </div>
                )}
                {estimate.total_timeout_limit !== undefined && (
                  <div>Total timeout limit: {estimate.total_timeout_limit} min</div>
                )}
                {estimate.sites_per_session !== undefined && (
                  <div>Sites per session: {estimate.sites_per_session}</div>
                )}
                {estimate.max_parallel_sessions !== undefined && (
                  <div>Max parallel sessions: {estimate.max_parallel_sessions}</div>
                )}
              </div>
            )}
          </div>
        )}
        {/* Test Scrape Modal (custom structure) */}
        {showTestModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
            <div className="w-full max-w-md bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-slate-700">
                <h3 className="text-lg font-semibold text-white">
                  Test Scrape (Dry Run)
                </h3>
                <button
                  onClick={() => setShowTestModal(false)}
                  className="text-slate-400 hover:text-white p-1"
                  disabled={testLoading}
                >
                  ×
                </button>
              </div>
              <div className="p-4 space-y-3">
                <label className="block text-sm text-slate-300">
                  Rate Limit (req/sec):
                  <Input
                    type="number"
                    min={1}
                    value={testParams.rateLimit}
                    onChange={(e) =>
                      setTestParams((p) => ({
                        ...p,
                        rateLimit: Number(e.target.value),
                      }))
                    }
                    className="mt-1"
                  />
                </label>
                <label className="block text-sm text-slate-300">
                  Concurrency:
                  <Input
                    type="number"
                    min={1}
                    value={testParams.concurrency}
                    onChange={(e) =>
                      setTestParams((p) => ({
                        ...p,
                        concurrency: Number(e.target.value),
                      }))
                    }
                    className="mt-1"
                  />
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={testParams.dryRun}
                    onChange={(e) =>
                      setTestParams((p) => ({
                        ...p,
                        dryRun: e.target.checked,
                      }))
                    }
                  />
                  Dry Run (no data saved)
                </label>
                <button
                  className="bg-purple-600 text-white px-4 py-2 rounded mt-2"
                  onClick={handleTestScrape}
                  disabled={testLoading}
                >
                  {testLoading ? "Testing..." : "Run Test Scrape"}
                </button>
                {testError && (
                  <div className="text-red-400">Error: {testError}</div>
                )}
                {testResult && (
                  <div className="bg-slate-900 rounded p-3 mt-2 text-xs text-slate-200">
                    <pre>{JSON.stringify(testResult, null, 2)}</pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
