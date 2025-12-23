"use client";

import { useMemo, useState, useEffect, useCallback } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { apiClient } from "@/lib/api";
import {
  RefreshCw,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";

import { SiteStats } from "@/lib/types";

export function SiteStatistics() {
  console.log("[SiteStatistics] Component mounted/updated");

  // Create stable function reference
  const getSiteStats = useCallback(() => apiClient.getSiteStats(), []);
  const { data, refetch } = useApi<SiteStats[]>(getSiteStats);
  const stats = useMemo(() => (Array.isArray(data) ? data : []), [data]);

  console.log("[SiteStatistics] Stats data:", {
    statsCount: stats.length,
    data,
  });

  type SortKey =
    | "name"
    | "success_rate"
    | "total_listings"
    | "average_price"
    | "listings_24h";
  const [sortKey, setSortKey] = useState<SortKey>("success_rate");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<10 | 25>(10);

  // Reset to first page when data or pageSize changes
  useEffect(() => {
    setPage(1);
  }, [stats.length, pageSize, sortKey, sortDir]);

  const sortedStats = useMemo(() => {
    const arr = [...stats];
    const getVal = (s: SiteStats, key: SortKey) => {
      if (key === "name") return (s.name || s.site_key || "").toLowerCase();
      if (key === "total_listings") return s.total_listings ?? 0;
      if (key === "average_price") return s.average_price ?? 0;
      if (key === "listings_24h") return s.listings_24h ?? 0;
      if (key === "success_rate") return s.success_rate ?? 0;
      return 0;
    };
    arr.sort((a, b) => {
      const va = getVal(a, sortKey);
      const vb = getVal(b, sortKey);
      if (va < vb) return sortDir === "asc" ? -1 : 1;
      if (va > vb) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return arr;
  }, [stats, sortKey, sortDir]);

  const total = sortedStats.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = Math.min(page, totalPages);
  const startIdx = (currentPage - 1) * pageSize;
  const endIdx = Math.min(startIdx + pageSize, total);
  const pageRows = sortedStats.slice(startIdx, endIdx);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-4 sm:p-6 border-b border-slate-700 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Site Statistics</h3>
        <Button
          onClick={refetch}
          variant="outline"
          size="sm"
          className="border-slate-600 text-white hover:bg-slate-700 flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="hidden sm:inline">Refresh</span>
        </Button>
      </div>
      <div className="p-4 sm:p-6 overflow-x-auto">
        <div className="flex items-center justify-between mb-3">
          <div className="text-slate-400 text-sm">
            Rows {total === 0 ? 0 : startIdx + 1}-{endIdx} of {total}
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              <span className="text-slate-400 text-sm">Per page:</span>
              <Button
                variant={pageSize === 10 ? "secondary" : "outline"}
                size="sm"
                onClick={() => setPageSize(10)}
                className="h-7 px-2 text-white"
              >
                10
              </Button>
              <Button
                variant={pageSize === 25 ? "secondary" : "outline"}
                size="sm"
                onClick={() => setPageSize(25)}
                className="h-7 px-2 text-white"
              >
                25
              </Button>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
                className="h-7 px-2 text-white"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-slate-300 text-sm">
                {currentPage}/{totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage >= totalPages}
                className="h-7 px-2 text-white"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-400 border-b border-slate-700">
              <th className="text-left py-2 pr-4">
                <button
                  className="inline-flex items-center gap-1 hover:text-slate-200"
                  onClick={() => toggleSort("name")}
                  title="Sort by site"
                >
                  Site
                  <ArrowUpDown className="w-3.5 h-3.5" />
                </button>
              </th>
              <th className="text-left py-2 pr-4">
                <button
                  className="inline-flex items-center gap-1 hover:text-slate-200"
                  onClick={() => toggleSort("success_rate")}
                  title="Sort by success rate"
                >
                  Success Rate
                  <ArrowUpDown className="w-3.5 h-3.5" />
                </button>
              </th>
              <th className="text-left py-2 pr-4">
                <button
                  className="inline-flex items-center gap-1 hover:text-slate-200"
                  onClick={() => toggleSort("total_listings")}
                  title="Sort by total listings"
                >
                  Listings
                  <ArrowUpDown className="w-3.5 h-3.5" />
                </button>
              </th>
              <th className="text-left py-2 pr-4">
                <button
                  className="inline-flex items-center gap-1 hover:text-slate-200"
                  onClick={() => toggleSort("average_price")}
                  title="Sort by average price"
                >
                  Avg Price
                  <ArrowUpDown className="w-3.5 h-3.5" />
                </button>
              </th>
              <th className="text-left py-2 pr-4">
                <button
                  className="inline-flex items-center gap-1 hover:text-slate-200"
                  onClick={() => toggleSort("listings_24h")}
                  title="Sort by 24h listings"
                >
                  24h Listings
                  <ArrowUpDown className="w-3.5 h-3.5" />
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {pageRows && pageRows.length > 0 ? (
              pageRows.map((s: SiteStats) => (
                <tr key={s.site_key} className="border-b border-slate-800">
                  <td className="py-2 pr-4 text-slate-300 font-semibold">
                    {s.name || s.site_key}
                  </td>
                  <td className="py-2 pr-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-bold ${
                        s.success_rate > 80
                          ? "bg-green-700 text-green-200"
                          : s.success_rate > 50
                          ? "bg-yellow-700 text-yellow-200"
                          : "bg-red-700 text-red-200"
                      }`}
                    >
                      {(s.success_rate ?? 0).toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2 pr-4 text-blue-300 font-bold">
                    {s.total_listings ?? 0}
                  </td>
                  <td className="py-2 pr-4 text-slate-300">
                    {s.average_price
                      ? `₦${s.average_price.toLocaleString()}`
                      : "-"}
                  </td>
                  <td className="py-2 pr-4 text-purple-300">
                    {s.listings_24h ?? 0}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="py-4 text-slate-400 text-center">
                  No site statistics available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
