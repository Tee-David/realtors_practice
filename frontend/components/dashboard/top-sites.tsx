"use client";

import { formatNumber } from "@/lib/utils";
import { Site } from "@/lib/types";
type TopSitesProps = {
  sitesData?: {
    sites: Site[];
    total: number;
    enabled: number;
    disabled: number;
  };
};

export function TopSites({ sitesData }: TopSitesProps) {
  // Create top sites from sites data
  const topSites =
    sitesData?.sites
      .filter((site) => site.enabled)
      .map((site) => ({
        id: site.site_key,
        site: site.name,
        scraper: site.parser,
        records: site.total_scraped ?? 0,
        enabled: site.enabled,
      }))
      .sort((a, b) => b.records - a.records)
      .slice(0, 5) || [];

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-6 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-white">
          Top Performing Sites
        </h3>
      </div>

      <div className="p-6">
        <div className="space-y-4">
          <div className="grid grid-cols-4 gap-4 text-sm font-medium text-slate-400 pb-2 border-b border-slate-700">
            <span>Site</span>
            <span>Parser</span>
            <span>Records</span>
            <span>Status</span>
          </div>

          {topSites.length > 0 ? (
            topSites.map((site) => (
              <div
                key={site.id}
                className="grid grid-cols-4 gap-4 text-sm items-center"
              >
                <span className="text-slate-300 font-semibold">
                  {site.site}
                </span>
                <span className="text-slate-300">{site.scraper}</span>
                <span className="text-blue-300 font-bold">
                  {formatNumber(site.records)}
                </span>
                <span>
                  {site.enabled ? (
                    <span className="px-2 py-1 rounded-full bg-green-700 text-green-200 text-xs font-bold">
                      Enabled
                    </span>
                  ) : (
                    <span className="px-2 py-1 rounded-full bg-red-700 text-red-200 text-xs font-bold">
                      Disabled
                    </span>
                  )}
                </span>
              </div>
            ))
          ) : (
            <div className="text-slate-400 text-center py-4">
              No sites configured
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
