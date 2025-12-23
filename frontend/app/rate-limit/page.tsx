"use client";
import React, { useState } from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RefreshCw, CheckCircle, XCircle } from "lucide-react";

const RateLimitPage: React.FC = () => {
  const { data, error, loading, refetch } = useApi(() =>
    apiClient.getRateLimitStatus()
  );
  const [testUrl, setTestUrl] = useState("");
  const [checkResult, setCheckResult] = useState<any>(null);
  const [checking, setChecking] = useState(false);

  const handleCheckUrl = async () => {
    if (!testUrl) return;
    setChecking(true);
    try {
      const result = await apiClient.checkRateLimit(testUrl);
      setCheckResult(result);
    } catch (err: any) {
      setCheckResult({ error: err.message });
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Rate Limit Status</h1>
          <p className="text-slate-400 mt-1">
            Monitor API rate limiting and request status
          </p>
        </div>
        <Button
          onClick={refetch}
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
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">
            {typeof error === "object" && "message" in error
              ? (error as any).message
              : String(error)}
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && !data && (
        <div className="bg-slate-800 rounded-lg p-8 text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
          <p className="text-slate-400">Loading rate limit status...</p>
        </div>
      )}

      {/* Rate Limit Stats */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-800 rounded-lg p-6">
            <div className="text-sm text-slate-400 mb-1">Total Requests</div>
            <div className="text-3xl font-bold text-white">
              {data.total_requests || 0}
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6">
            <div className="text-sm text-slate-400 mb-1">Rate Limited</div>
            <div className="text-3xl font-bold text-yellow-400">
              {data.rate_limited || 0}
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6">
            <div className="text-sm text-slate-400 mb-1">Domains Tracked</div>
            <div className="text-3xl font-bold text-blue-400">
              {data.domains_tracked || 0}
            </div>
          </div>
        </div>
      )}

      {/* URL Checker */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">
          Check URL Rate Limit
        </h2>
        <div className="flex gap-2">
          <Input
            type="url"
            placeholder="https://example.com/page"
            value={testUrl}
            onChange={(e) => setTestUrl(e.target.value)}
            className="flex-1 bg-slate-800 border-slate-700 text-white"
          />
          <Button onClick={handleCheckUrl} disabled={checking || !testUrl}>
            {checking ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              "Check"
            )}
          </Button>
        </div>

        {checkResult && (
          <div className="mt-4 p-4 bg-slate-900 rounded-lg">
            {checkResult.error ? (
              <div className="flex items-center text-red-400">
                <XCircle className="w-5 h-5 mr-2" />
                {checkResult.error}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center text-green-400">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  {checkResult.allowed ? "Request Allowed" : "Rate Limited"}
                </div>
                {checkResult.domain && (
                  <div className="text-sm text-slate-400">
                    Domain: {checkResult.domain}
                  </div>
                )}
                {checkResult.retry_after && (
                  <div className="text-sm text-yellow-400">
                    Retry after: {checkResult.retry_after}s
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Raw Data */}
      {data && (
        <details className="bg-slate-800 rounded-lg p-6">
          <summary className="cursor-pointer text-white font-medium mb-2">
            View Raw Data
          </summary>
          <pre className="text-xs text-slate-300 overflow-auto p-4 bg-slate-900 rounded-lg mt-2">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
};

export default RateLimitPage;
