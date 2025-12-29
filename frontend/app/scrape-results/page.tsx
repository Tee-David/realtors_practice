"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, Download, RefreshCw } from "lucide-react";
import { RealEstateApiClient } from "@/lib/api";

export default function ScrapeResultsPage() {
  const [batchDownloadStatus, setBatchDownloadStatus] = useState<string>("");
  const [exportFormats] = useState<["csv", "xlsx", "json", "parquet"]>([
    "csv",
    "xlsx",
    "json",
    "parquet",
  ]);
  const [scrapeHistory, setScrapeHistory] = useState<any[]>([]);
  const [selectedRun, setSelectedRun] = useState<any>(null);
  const [errorModalOpen, setErrorModalOpen] = useState(false);
  const [errorModalContent, setErrorModalContent] = useState("");
  const [scrapeStatus, setScrapeStatus] = useState<any>(null);
  const [dataAvailability, setDataAvailability] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const apiClient = new RealEstateApiClient();

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [status, data, historyResp] = await Promise.all([
          apiClient.getScrapeStatus(),
          apiClient.getAvailableData(),
          apiClient.getScrapeHistory(5).catch(() => []),
        ]);
        setScrapeStatus(status);
        setDataAvailability(data);
        setScrapeHistory(Array.isArray(historyResp) ? historyResp : []);
      } catch (err: any) {
        setError(err.message || "Failed to load data");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString();
  const formatDuration = (start: string, end: string) => {
    const ms = new Date(end).getTime() - new Date(start).getTime();
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const rawSites: any[] = Array.isArray(dataAvailability?.raw_sites)
    ? dataAvailability.raw_sites
    : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 p-6 flex items-center justify-center">
        <span className="text-slate-400 text-lg">
          Loading scrape results...
        </span>
      </div>
    );
  }

  const isEmpty =
    (!scrapeHistory || scrapeHistory.length === 0) &&
    (!rawSites || rawSites.length === 0);

  return (
    <div className="min-h-screen bg-slate-950 p-4 sm:p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
              Scrape Results
            </h1>
            <p className="text-slate-400 text-sm sm:text-base">
              View the status and history of your property data scrapes.
              Download results or{" "}
              <button
                onClick={() =>
                  window.dispatchEvent(
                    new CustomEvent("navigate", {
                      detail: { page: "data-explorer" },
                    })
                  )
                }
                className="underline text-blue-400 hover:text-blue-300 cursor-pointer bg-transparent border-0 p-0"
              >
                explore the data
              </button>{" "}
              directly.
            </p>
          </div>
          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            className="bg-slate-900 border-slate-700 hover:bg-slate-800"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>

        {/* Error Display */}
        {error && (
          <Card className="border-red-500/50 bg-slate-900">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-400">
                <XCircle className="h-5 w-5" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {isEmpty ? (
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 text-center">
            <p className="text-lg font-medium text-slate-300 mb-2">
              No scrape results yet
            </p>
            <p className="text-slate-400 mb-4">
              Start a new scrape in{" "}
              <button
                onClick={() =>
                  window.dispatchEvent(
                    new CustomEvent("navigate", { detail: { page: "scraper" } })
                  )
                }
                className="underline text-blue-400 hover:text-blue-300 cursor-pointer bg-transparent border-0 p-0"
              >
                Scraper Control
              </button>{" "}
              to collect property data.
            </p>
            <button
              onClick={() =>
                window.dispatchEvent(
                  new CustomEvent("navigate", { detail: { page: "scraper" } })
                )
              }
              className="inline-block mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition cursor-pointer"
            >
              Go to Scraper Control
            </button>
          </div>
        ) : (
          <>
            {/* Batch Download Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-end gap-2">
              <Button
                size="sm"
                variant="outline"
                className="bg-slate-900 border-slate-700 hover:bg-slate-800"
                onClick={async () => {
                  setBatchDownloadStatus("Processing...");
                  try {
                    const format = exportFormats[0];
                    const job = await apiClient.generateExport({ format });
                    setBatchDownloadStatus(
                      job.status === "completed" ? "Download ready" : job.status
                    );
                    if (job.download_url)
                      window.open(job.download_url, "_blank");
                  } catch (e: any) {
                    setBatchDownloadStatus(e.message || "Failed");
                  }
                }}
              >
                <Download className="h-4 w-4 mr-2" />
                Download All Exports
              </Button>
              {batchDownloadStatus && (
                <span className="text-xs text-slate-400">
                  {batchDownloadStatus}
                </span>
              )}
              <button
                onClick={() =>
                  window.dispatchEvent(
                    new CustomEvent("navigate", {
                      detail: { page: "data-explorer" },
                    })
                  )
                }
                className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm transition cursor-pointer"
              >
                View Data Explorer
              </button>
            </div>

            {/* Last Scrape Run Status */}
            {scrapeStatus?.last_run && (
              <Card className="border-slate-800 bg-slate-900">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white flex items-center gap-2">
                      {scrapeStatus.last_run.success ? (
                        <CheckCircle2 className="h-6 w-6 text-green-500" />
                      ) : (
                        <XCircle className="h-6 w-6 text-red-500" />
                      )}
                      Last Scrape Run
                    </CardTitle>
                    <Badge
                      variant={
                        scrapeStatus.last_run.success
                          ? "default"
                          : "destructive"
                      }
                      className={
                        scrapeStatus.last_run.success ? "bg-green-600" : ""
                      }
                    >
                      {scrapeStatus.last_run.success ? "SUCCESS" : "FAILED"}
                    </Badge>
                  </div>
                  <CardDescription className="text-slate-400">
                    Run ID: {scrapeStatus.last_run.run_id}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-slate-400 mb-1">Started</div>
                      <div className="text-white font-medium">
                        {formatDate(scrapeStatus.last_run.started_at)}
                      </div>
                    </div>
                    {scrapeStatus.last_run.completed_at && (
                      <div>
                        <div className="text-sm text-slate-400 mb-1">
                          Completed
                        </div>
                        <div className="text-white font-medium">
                          {formatDate(scrapeStatus.last_run.completed_at)}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Scrape History */}
            {scrapeHistory.length > 0 && (
              <Card className="border-slate-800 bg-slate-900">
                <CardHeader>
                  <CardTitle className="text-white">Scrape History</CardTitle>
                  <CardDescription className="text-slate-400">
                    View details from previous scrape runs
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {scrapeHistory.map((run: any) => (
                      <Button
                        key={run.run_id}
                        size="sm"
                        variant={
                          selectedRun?.run_id === run.run_id
                            ? "default"
                            : "outline"
                        }
                        className={
                          selectedRun?.run_id === run.run_id
                            ? "bg-blue-600"
                            : "bg-slate-800 border-slate-700"
                        }
                        onClick={() => setSelectedRun(run)}
                      >
                        Run #{run.run_id} ({run.success ? "Success" : "Failed"})
                      </Button>
                    ))}
                  </div>
                  {selectedRun && (
                    <div className="mt-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-slate-400">Started:</span>{" "}
                          <span className="text-slate-200">
                            {formatDate(selectedRun.started_at)}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400">Completed:</span>{" "}
                          <span className="text-slate-200">
                            {formatDate(selectedRun.completed_at)}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400">Duration:</span>{" "}
                          <span className="text-slate-200">
                            {formatDuration(
                              selectedRun.started_at,
                              selectedRun.completed_at
                            )}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-400">Return Code:</span>{" "}
                          <span className="text-slate-200">
                            {selectedRun.return_code}
                          </span>
                        </div>
                        <div className="sm:col-span-2">
                          <span className="text-slate-400">Sites:</span>{" "}
                          <span className="text-slate-200">
                            {Array.isArray(selectedRun.sites)
                              ? selectedRun.sites.join(", ")
                              : "-"}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Raw Site Data */}
            <Card className="border-slate-800 bg-slate-900">
              <CardHeader>
                <CardTitle className="text-white">Raw Site Data</CardTitle>
                <CardDescription className="text-slate-400">
                  Downloaded raw data files from each property site
                </CardDescription>
              </CardHeader>
              <CardContent>
                {rawSites.length > 0 ? (
                  <div className="space-y-2">
                    {rawSites.map((site: any) => (
                      <details
                        key={site.site_key}
                        className={`p-3 rounded-lg border ${
                          site.failed
                            ? "bg-red-900/20 border-red-700"
                            : "bg-slate-800/50 border-slate-700"
                        } group`}
                        open={site.failed}
                      >
                        <summary className="flex flex-col sm:flex-row items-start sm:items-center justify-between cursor-pointer gap-2">
                          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 flex-1">
                            <span
                              className={`font-medium ${
                                site.failed ? "text-red-400" : "text-white"
                              }`}
                            >
                              {site.site_key}
                            </span>
                            {site.failed && (
                              <span className="px-2 py-0.5 rounded bg-red-900 text-xs text-red-300">
                                Failed
                              </span>
                            )}
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            className="bg-slate-900 border-slate-700 hover:bg-slate-800"
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </Button>
                        </summary>
                        <div className="mt-3 ml-2 space-y-1 text-sm text-slate-400">
                          <div>
                            <span className="text-slate-500">Latest file:</span>{" "}
                            <span className="text-slate-200 break-all">
                              {site.latest_file}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-500">File count:</span>{" "}
                            <span className="text-slate-200">
                              {site.file_count}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-500">
                              Last updated:
                            </span>{" "}
                            <span className="text-slate-200">
                              {new Date(
                                site.last_updated * 1000
                              ).toLocaleString()}
                            </span>
                          </div>
                          {site.file_size && (
                            <div>
                              <span className="text-slate-500">File size:</span>{" "}
                              <span className="text-slate-200">
                                {site.file_size} KB
                              </span>
                            </div>
                          )}
                          {site.last_error && (
                            <div className="mt-2 p-2 bg-red-900/30 rounded border border-red-800">
                              <span className="font-medium text-red-400">
                                Error:
                              </span>{" "}
                              <span className="text-red-300">
                                {site.last_error}
                              </span>
                            </div>
                          )}
                          {site.error_details && (
                            <div className="mt-1 text-red-300 text-xs">
                              {site.error_details}
                            </div>
                          )}
                        </div>
                      </details>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-400 bg-slate-800/30 rounded-lg border border-slate-800">
                    <p className="text-lg font-medium mb-1">
                      No raw site data found
                    </p>
                    <p className="text-sm">
                      Raw data will appear here after running a scrape
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Error Modal */}
      {errorModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="bg-slate-900 p-6 rounded-lg shadow-lg max-w-lg w-full border border-slate-700">
            <h2 className="text-lg font-bold mb-3 text-red-400">
              Error Details
            </h2>
            <div className="text-slate-300 whitespace-pre-wrap text-sm max-h-96 overflow-y-auto">
              {errorModalContent}
            </div>
            <Button
              className="mt-4 w-full"
              onClick={() => setErrorModalOpen(false)}
            >
              Close
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
