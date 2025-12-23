"use client";

import { getStatusColor } from "@/lib/utils";
import { ScrapeStatus } from "@/lib/types";

interface RecentActivityProps {
  scrapeStatus?: ScrapeStatus;
}

export function RecentActivity({ scrapeStatus }: RecentActivityProps) {
  const activities = [];

  // Add current run if running
  if (scrapeStatus?.is_running && scrapeStatus.current_run) {
    const run = scrapeStatus.current_run;
    activities.push({
      id: "current",
      date: new Date(run.started_at).toLocaleString(),
      scraper: Array.isArray(run.sites) ? run.sites.join(", ") : run.sites,
      status: "Running",
    });
  }

  // Add last run if available
  if (scrapeStatus?.last_run) {
    const run = scrapeStatus.last_run;
    activities.push({
      id: "last",
      date: new Date(run.completed_at).toLocaleString(),
      scraper: Array.isArray(run.sites) ? run.sites.join(", ") : run.sites,
      status: run.success ? "Success" : "Failed",
    });
  }

  // Add site metadata as activities
  if (scrapeStatus?.site_metadata) {
    Object.entries(scrapeStatus.site_metadata).forEach(
      ([siteKey, metadata]) => {
        if (metadata.last_scrape) {
          activities.push({
            id: `${siteKey}-${metadata.last_scrape}`,
            date: new Date(metadata.last_scrape).toLocaleString(),
            scraper: siteKey,
            status: "Success",
          });
        }
      }
    );
  }

  // Sort by date (most recent first)
  activities.sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-6 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-white">Recent Activity</h3>
      </div>

      <div className="p-6">
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4 text-sm font-medium text-slate-400 pb-2 border-b border-slate-700">
            <span>Date</span>
            <span>Scraper</span>
            <span>Status</span>
          </div>

          {activities.length > 0 ? (
            activities.slice(0, 5).map((activity) => (
              <div key={activity.id} className="grid grid-cols-3 gap-4 text-sm">
                <span className="text-slate-300">{activity.date}</span>
                <span className="text-slate-300">{activity.scraper}</span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium text-center flex items-center justify-center ${getStatusColor(
                    activity.status
                  )}`}
                >
                  {activity.status}
                </span>
              </div>
            ))
          ) : (
            <div className="text-slate-400 text-center py-4">
              No recent activity
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
