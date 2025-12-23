"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { ScheduleJob } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { RefreshCw, Calendar, XCircle, Clock } from "lucide-react";
import { toast } from "sonner";

export default function SchedulerPage() {
  const [jobs, setJobs] = useState<ScheduleJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [canceling, setCanceling] = useState<number[]>([]);

  const fetchJobs = () => {
    setLoading(true);
    apiClient
      .listScheduledJobs()
      .then((data: ScheduleJob[]) => setJobs(data))
      .catch((err: any) => setError(err?.message || "Error fetching jobs"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchJobs();
    // Auto-refresh every minute
    const interval = setInterval(fetchJobs, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleCancelJob = async (jobId: number) => {
    setCanceling((prev) => [...prev, jobId]);
    try {
      await apiClient.cancelScheduledJob(jobId);
      toast.success("Job cancelled successfully");
      fetchJobs();
    } catch (err: any) {
      toast.error(err?.message || "Failed to cancel job");
    } finally {
      setCanceling((prev) => prev.filter((id) => id !== jobId));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case "completed":
        return "bg-green-500/10 text-green-400 border-green-500/20";
      case "running":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "failed":
        return "bg-red-500/10 text-red-400 border-red-500/20";
      case "pending":
      case "scheduled":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20";
      case "cancelled":
        return "bg-slate-500/10 text-slate-400 border-slate-500/20";
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/20";
    }
  };

  const canCancel = (status: string) => {
    return status === "pending";
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Calendar className="w-8 h-8" />
            Scheduled Jobs
          </h1>
          <p className="text-slate-400 mt-1">
            View and manage automated scraping operations
          </p>
        </div>
        <Button
          onClick={fetchJobs}
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

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="text-sm text-slate-400">Total Jobs</div>
          <div className="text-2xl font-bold text-white mt-1">
            {jobs.length}
          </div>
        </div>
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
          <div className="text-sm text-yellow-400">Pending</div>
          <div className="text-2xl font-bold text-yellow-300 mt-1">
            {jobs.filter((j) => j.status === "pending").length}
          </div>
        </div>
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="text-sm text-blue-400">Running</div>
          <div className="text-2xl font-bold text-blue-300 mt-1">
            {jobs.filter((j) => j.status === "running").length}
          </div>
        </div>
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
          <div className="text-sm text-green-400">Completed</div>
          <div className="text-2xl font-bold text-green-300 mt-1">
            {jobs.filter((j) => j.status === "completed").length}
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Jobs List */}
      {jobs.length > 0 ? (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div
              key={job.job_id}
              className="bg-slate-800 rounded-lg p-5 hover:bg-slate-750 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-white font-medium">
                      Job #{job.job_id}
                    </span>
                    <span
                      className={`px-3 py-1 text-xs font-medium rounded border ${getStatusColor(
                        job.status
                      )}`}
                    >
                      {job.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-400">Scheduled:</span>
                      <span className="text-white font-medium">
                        {new Date(job.schedule_time).toLocaleString()}
                      </span>
                    </div>
                    {job.sites && job.sites.length > 0 && (
                      <div>
                        <span className="text-slate-400">Sites:</span>{" "}
                        <span className="text-white">
                          {job.sites.join(", ")}
                        </span>
                      </div>
                    )}
                    {job.created_at && (
                      <div>
                        <span className="text-slate-400">Created:</span>{" "}
                        <span className="text-white">
                          {new Date(job.created_at).toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                {canCancel(job.status) && (
                  <Button
                    onClick={() => handleCancelJob(job.job_id)}
                    disabled={canceling.includes(job.job_id)}
                    variant="ghost"
                    size="sm"
                    className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  >
                    {canceling.includes(job.job_id) ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <XCircle className="w-4 h-4" />
                    )}
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-slate-800 rounded-lg">
          <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-300 font-medium">No scheduled jobs</p>
          <p className="text-slate-400 text-sm mt-1">
            Jobs can be scheduled through the Scraper Control panel
          </p>
        </div>
      )}
    </div>
  );
}
