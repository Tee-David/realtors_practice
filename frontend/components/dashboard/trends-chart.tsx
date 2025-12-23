"use client";

import { useMemo, useCallback } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";

import { TrendStats } from "@/lib/types";

export function TrendsChart() {
  console.log("[TrendsChart] Component mounted/updated");

  // Create stable function reference
  const getTrendStats = useCallback(() => apiClient.getTrendStats(7), []);
  const { data, refetch } = useApi<TrendStats>(getTrendStats);
  const chartData = useMemo(() => {
    if (!data || !data.trends) return [];
    return data.trends.map((d) => ({
      date: d.date,
      records: d.listings,
      sites: d.sites,
      avg_price: d.avg_price,
    }));
  }, [data]);

  console.log("[TrendsChart] Chart data:", {
    dataPointsCount: chartData.length,
    data,
  });

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-4 sm:p-6 border-b border-slate-700 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">
          7-Day Activity Trends
        </h3>
        <Button
          onClick={() => {
            refetch();
            toast.success("Trends refreshed");
          }}
          variant="outline"
          size="sm"
          className="border-slate-600 text-white hover:bg-slate-700"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="hidden sm:inline">Refresh</span>
        </Button>
      </div>
      <div className="p-4 sm:p-6">
        {chartData.length === 0 ? (
          <div className="text-slate-400">No trend data available.</div>
        ) : (
          <>
            {/* Summary Section */}
            {data?.summary && (
              <div className="mb-4 flex flex-wrap gap-4 text-xs text-slate-400">
                <span>Total Days: {data.summary.total_days}</span>
                <span>
                  Avg Daily Listings: {data.summary.avg_daily_listings}
                </span>
                {data.summary.peak_day && (
                  <span>
                    Peak: {data.summary.peak_day} ({data.summary.peak_listings}{" "}
                    listings)
                  </span>
                )}
              </div>
            )}
            <div className="w-full overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-700">
                    <th className="text-left py-2 pr-4">Date</th>
                    <th className="text-left py-2 pr-4">Listings</th>
                    <th className="text-left py-2 pr-4">Sites</th>
                    <th className="text-left py-2 pr-4">Avg Price</th>
                  </tr>
                </thead>
                <tbody>
                  {chartData.map((row, idx) => (
                    <tr key={idx} className="border-b border-slate-800">
                      <td className="py-2 pr-4 text-slate-300">{row.date}</td>
                      <td className="py-2 pr-4 text-blue-300 font-bold">
                        {row.records}
                      </td>
                      <td className="py-2 pr-4 text-green-300">{row.sites}</td>
                      <td className="py-2 pr-4 text-slate-300">
                        {row.avg_price
                          ? `₦${row.avg_price.toLocaleString()}`
                          : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
