"use client";

import { useMemo } from "react";
import { useApi } from "@/lib/swr";
import { OverviewStats, ScrapeStatus } from "@/lib/types";

export default function Home() {
  const { data: overview, error: overviewError, isLoading: overviewLoading } = useApi<OverviewStats>(
    "/stats/overview"
  );
  const { data: status, error: statusError } = useApi<ScrapeStatus>("/scrape/status", {
    refreshInterval: 3000,
  });

  const cards = useMemo(() => {
    return [
      {
        label: "Total Listings",
        value: overview?.total_listings ?? "—",
      },
      {
        label: "Total Sites",
        value: overview?.total_sites ?? "—",
      },
      {
        label: "Active Sites",
        value: overview?.active_sites ?? "—",
      },
    ];
  }, [overview]);

  return (
    <div className="space-y-6">
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="rounded-lg border bg-white p-4">
            <div className="text-sm text-gray-500">{c.label}</div>
            <div className="mt-2 text-2xl font-semibold">{c.value}</div>
          </div>
        ))}
      </section>

      <section className="rounded-lg border bg-white p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold">Scrape Status</h2>
        </div>
        <div className="mt-3 text-sm text-gray-700">
          {overviewLoading ? (
            <div>Loading...</div>
          ) : overviewError ? (
            <div className="text-red-600">Failed to load overview.</div>
          ) : (
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <div className="text-gray-500">Running</div>
                <div className="font-medium">{status?.running ? "Yes" : "No"}</div>
              </div>
              <div>
                <div className="text-gray-500">Current Site</div>
                <div className="font-medium">{status?.current_site ?? "—"}</div>
              </div>
              <div>
                <div className="text-gray-500">Progress</div>
                <div className="font-medium">{status?.progress ?? 0}%</div>
              </div>
              <div>
                <div className="text-gray-500">Message</div>
                <div className="font-medium break-words">{status?.message ?? "—"}</div>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
