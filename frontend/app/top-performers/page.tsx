"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { SiteStats } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  RefreshCw,
  Trophy,
  TrendingUp,
  Calendar,
  CheckCircle,
} from "lucide-react";

export default function TopPerformersPage() {
  const [sites, setSites] = useState<SiteStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTopPerformers = () => {
    setLoading(true);
    apiClient
      .topPerformers()
      .then((res: SiteStats[]) => setSites(res))
      .catch((err: any) =>
        setError(err?.message || "Error fetching top performers")
      )
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTopPerformers();
  }, []);

  const getRankMedal = (index: number) => {
    switch (index) {
      case 0:
        return "🥇";
      case 1:
        return "🥈";
      case 2:
        return "🥉";
      default:
        return `#${index + 1}`;
    }
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 90) return "text-green-400";
    if (rate >= 70) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Trophy className="w-8 h-8 text-yellow-400" />
            Top Performing Sites
          </h1>
          <p className="text-slate-400 mt-1">
            Sites ranked by success rate and listing counts
          </p>
        </div>
        <Button
          onClick={fetchTopPerformers}
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
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Top Performers List */}
      {sites.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sites.map((site, index) => (
            <div
              key={site.site_key}
              className={`bg-slate-800 rounded-lg p-6 hover:scale-105 transition-transform ${
                index === 0
                  ? "border-2 border-yellow-500/30"
                  : index === 1
                  ? "border-2 border-slate-400/30"
                  : index === 2
                  ? "border-2 border-orange-500/30"
                  : "border border-slate-700"
              }`}
            >
              {/* Rank Badge */}
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl">{getRankMedal(index)}</span>
                <span
                  className={`px-3 py-1 text-sm font-bold rounded ${getSuccessRateColor(
                    site.success_rate
                  )} bg-slate-900`}
                >
                  {site.success_rate}%
                </span>
              </div>

              {/* Site Name */}
              <h3 className="text-xl font-bold text-white mb-4">{site.name}</h3>

              {/* Stats */}
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Total Listings
                  </span>
                  <span className="text-white font-medium">
                    {site.total_listings.toLocaleString()}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    Success Rate
                  </span>
                  <span
                    className={`font-medium ${getSuccessRateColor(
                      site.success_rate
                    )}`}
                  >
                    {site.success_rate}%
                  </span>
                </div>

                {site.latest_scrape && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Latest Scrape
                    </span>
                    <span className="text-white font-medium">
                      {new Date(site.latest_scrape).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              {/* Site Key */}
              <div className="mt-4 pt-4 border-t border-slate-700">
                <span className="text-xs text-slate-500">
                  Key: {site.site_key}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-slate-800 rounded-lg">
          <Trophy className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-300 font-medium">
            No performance data available
          </p>
          <p className="text-slate-400 text-sm mt-1">
            Run some scrapes to see top performers
          </p>
        </div>
      )}
    </div>
  );
}
