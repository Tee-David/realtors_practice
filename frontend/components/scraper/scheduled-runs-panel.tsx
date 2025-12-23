import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { ScheduleJob } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function ScheduledRunsPanel() {
  const [jobs, setJobs] = useState<ScheduleJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [canceling, setCanceling] = useState<number | null>(null);

  useEffect(() => {
    setLoading(true);
    apiClient
      .listScheduledJobs()
      .then((data) => {
        if (Array.isArray(data)) {
          setJobs(data);
        } else {
          setJobs([]);
        }
        setError(null);
      })
      .catch((err) => {
        setError(err.message || "Failed to fetch scheduled jobs");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCancel = async (jobId: number) => {
    setCanceling(jobId);
    try {
      await apiClient.cancelScheduledJob(jobId);
      setJobs((prev) => prev.filter((job) => job.job_id !== jobId));
    } catch (err: any) {
      setError(err.message || "Failed to cancel job");
    } finally {
      setCanceling(null);
    }
  };

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle>Scheduled Scrape Runs</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-400">Error: {error}</div>}
        {!loading && !error && jobs.length === 0 && (
          <div>No scheduled runs found.</div>
        )}
        <ul className="space-y-2">
          {jobs.map((job) => (
            <li key={job.job_id} className="border-b pb-2">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold">
                    {job.status === "pending"
                      ? "🕒"
                      : job.status === "running"
                      ? "⏳"
                      : job.status === "completed"
                      ? "✅"
                      : job.status === "cancelled"
                      ? "🚫"
                      : "❌"}
                  </span>{" "}
                  {new Date(job.schedule_time).toLocaleString()}
                  <br />
                  <span className="text-xs text-slate-400">
                    Created: {new Date(job.created_at).toLocaleString()}
                  </span>
                  {job.executed_at && (
                    <span className="text-xs text-slate-400 ml-2">
                      Executed: {new Date(job.executed_at).toLocaleString()}
                    </span>
                  )}
                </div>
                <div>
                  <span className="text-green-400">
                    {job.sites.length ?? 0}
                  </span>{" "}
                  site(s)
                </div>
                {job.status === "pending" && (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={canceling === job.job_id}
                    onClick={() => handleCancel(job.job_id)}
                  >
                    {canceling === job.job_id ? "Canceling..." : "Cancel"}
                  </Button>
                )}
              </div>
              {job.result && (
                <div className="text-slate-400 text-xs mt-1">
                  Result: {job.result.status}
                </div>
              )}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
