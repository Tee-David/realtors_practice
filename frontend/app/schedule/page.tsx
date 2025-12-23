"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { ScheduleJob } from "@/lib/types";

export default function SchedulePage() {
  const [jobs, setJobs] = useState<ScheduleJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    apiClient
      .listScheduledJobs()
      .then((res: ScheduleJob[]) => setJobs(res))
      .catch((err: any) =>
        setError(err?.message || "Error fetching schedule jobs")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold text-white">Scheduled Jobs</h1>
      <p className="text-slate-400 text-sm mt-1">
        View and manage scheduled scraping jobs
      </p>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}
      {jobs.length > 0 ? (
        <ul className="mt-4 space-y-2">
          {jobs.map((job) => (
            <li
              key={job.job_id}
              className="bg-slate-900 rounded-lg p-4 text-slate-300"
            >
              <div>
                <strong>ID:</strong> {job.job_id}
              </div>
              <div>
                <strong>Status:</strong> {job.status}
              </div>
              <div>
                <strong>Created:</strong> {job.created_at}
              </div>
              {job.executed_at && (
                <div>
                  <strong>Executed:</strong> {job.executed_at}
                </div>
              )}
              {job.status === "failed" && job.result?.error && (
                <div className="text-red-400">
                  <strong>Error:</strong> {job.result.error}
                </div>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <div>No scheduled jobs found.</div>
      )}
    </div>
  );
}
