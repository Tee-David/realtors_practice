"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import {
  Play,
  Square,
  Calendar,
  RefreshCw,
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  AlertCircle,
  Settings,
  Plus,
  ExternalLink,
  Zap,
  Database,
  Globe,
  ChevronDown,
} from "lucide-react";
import { ScheduledRunsPanel } from "./scheduled-runs-panel";
import { ErrorAlertPanel } from "./error-alert-panel";
import { ScrapeHistoryPanel } from "./scrape-history-panel";
import { Button } from "@/components/ui/button";
import { SiteConfiguration } from "./site-configuration";
import { GlobalParameters } from "./global-parameters";
import { ScrapeTimeEstimate } from "./scrape-time-estimate";
import { RunConsole } from "./run-console";
import { NotificationsAlerts } from "./notifications-alerts";
import { AddSiteModal } from "./add-site-modal";
import { ScheduleModal } from "./schedule-modal";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import { usePolling } from "@/lib/hooks/useApi";
import { ScrapeStatus } from "@/lib/types";
import { useTriggerGitHubScrape } from "@/lib/hooks/useTriggerGitHubScrape";

export function ScraperControl() {
  // State management
  const [showAddSiteModal, setShowAddSiteModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [selectedSites, setSelectedSites] = useState<string[]>([]);
  const [maxPages, setMaxPages] = useState<number | undefined>(15);
  const [geocoding, setGeocoding] = useState<boolean | undefined>(true);
  const [scrapeLoading, setScrapeLoading] = useState(false);
  const [scrapeError, setScrapeError] = useState<string | null>(null);
  const [scrapeComplete, setScrapeComplete] = useState(false);
  const [refreshSites, setRefreshSites] = useState(0);
  const [githubRunId, setGithubRunId] = useState<number | undefined>(undefined);

  // GitHub Actions Hook
  const {
    triggerScrape,
    loading: ghLoading,
    error: ghError,
    result: ghResult,
  } = useTriggerGitHubScrape();

  // Poll scrape status
  const getScrapeStatus = useCallback(() => apiClient.getScrapeStatus(), []);
  const { data: scrapeStatus } = usePolling<ScrapeStatus>(
    getScrapeStatus,
    5000,
    true
  );

  const isRunning = scrapeStatus?.is_running || false;
  const currentRun = scrapeStatus?.current_run;
  const lastRun = scrapeStatus?.last_run;

  // Status helpers
  const getStatusString = () => {
    if (isRunning) return "running";
    if (lastRun?.success === true) return "completed";
    if (lastRun?.success === false) return "error";
    return "idle";
  };

  const statusString = getStatusString();

  // Track previous running state to detect completion
  const previousStatusRef = useRef<boolean | undefined>(undefined);
  useEffect(() => {
    if (previousStatusRef.current === true && !isRunning && lastRun) {
      const totalListings =
        lastRun.final_stats?.successful_sites ||
        lastRun.progress?.completed_sites ||
        0;
      toast.success("Scrape completed", {
        description: `Completed ${totalListings} site(s)`,
        duration: 4000,
      });
      setScrapeComplete(true);
    }
    previousStatusRef.current = isRunning;
  }, [isRunning, lastRun]);

  // Manual refresh handler
  const handleRefresh = async () => {
    try {
      window.location.reload();
      toast.success("Scraper data refreshed");
    } catch (error) {
      toast.error("Failed to refresh scraper data");
    }
  };

  // Poll for GitHub workflow runs to track current run
  const getLatestWorkflowRuns = useCallback(async () => {
    try {
      const runs = await apiClient.listWorkflowRuns(1);
      if (runs && runs.length > 0) {
        const latestRun = runs[0];

        // Show logs for active runs OR recently completed runs (within 2 hours)
        if (latestRun.status === "in_progress" || latestRun.status === "queued") {
          setGithubRunId(latestRun.id);
        } else if (latestRun.status === "completed") {
          // Check if run completed recently (within 2 hours)
          const completedAt = new Date(latestRun.updated_at);
          const now = new Date();
          const minutesAgo = (now.getTime() - completedAt.getTime()) / 1000 / 60;

          if (minutesAgo < 120) {
            // Show logs for recently completed runs (within 2 hours)
            setGithubRunId(latestRun.id);
          } else {
            // Run is too old, clear it
            setGithubRunId(undefined);
          }
        }
      }
    } catch (error) {
      console.error("Failed to fetch workflow runs:", error);
    }
  }, []);

  // Poll for workflow runs
  usePolling(getLatestWorkflowRuns, 15000, true);

  // GitHub Actions Scrape Trigger
  const handleTriggerGitHubScrape = async () => {
    try {
      const res = await triggerScrape({
        pageCap: maxPages,
        geocode: geocoding ? 1 : 0,
        sites: selectedSites,
      });

      // Fetch the latest workflow run to get its ID
      setTimeout(async () => {
        try {
          const runs = await apiClient.listWorkflowRuns(1);
          if (runs && runs.length > 0) {
            setGithubRunId(runs[0].id);
          }
        } catch (error) {
          console.error("Failed to fetch workflow run ID:", error);
        }
      }, 3000); // Wait 3s for GitHub to create the run

      toast.success("GitHub Actions scrape triggered!", {
        description: res.message || "Workflow started.",
        duration: 4000,
      });
    } catch (err: any) {
      toast.error("Failed to trigger GitHub Actions scrape", {
        description: err.message,
        duration: 4000,
      });
    }
  };

  // Direct API Scrape Control
  const handleRunScraper = async () => {
    setScrapeError(null);
    setScrapeComplete(false);
    setScrapeLoading(true);

    try {
      if (isRunning) {
        await apiClient.stopScrape();
        toast.success("Scraper stopped successfully");
        setScrapeLoading(false);
        setScrapeComplete(true);
      } else {
        const params: {
          sites?: string[];
          max_pages?: number;
          geocode?: boolean;
        } = {};
        if (selectedSites.length > 0) params.sites = selectedSites;
        if (maxPages !== undefined) params.max_pages = maxPages;
        if (geocoding !== undefined) params.geocode = geocoding;

        await apiClient.startScrape(params);
        toast.success("Scraper started successfully");

        // Poll for completion
        let pollCount = 0;
        let running = true;
        let finalStatus: any = null;

        while (running && pollCount < 60) {
          await new Promise((res) => setTimeout(res, 5000));
          const status: any = await apiClient.getScrapeStatus();
          finalStatus = status;
          running = status?.is_running || false;
          pollCount++;
        }

        setScrapeLoading(false);
        setScrapeComplete(true);

        if (finalStatus?.last_run) {
          const lastRun = finalStatus.last_run;
          const success = lastRun.success === true || lastRun.return_code === 0;

          if (success) {
            toast.success("✅ Scrape completed successfully!", {
              description: `Scraped ${lastRun.total_scraped || 0} properties`,
              duration: 5000,
            });
          } else {
            toast.error("❌ Scrape failed", {
              description: lastRun.error_message || "Check logs for details",
              duration: 5000,
            });
          }
        }
      }
    } catch (error) {
      setScrapeError(
        error instanceof Error ? error.message : "Failed to control scraper"
      );
      setScrapeLoading(false);
      toast.error(
        error instanceof Error ? error.message : "Failed to control scraper"
      );
    }
  };

  const handleScheduleRuns = () => {
    setShowScheduleModal(true);
  };

  const handleSiteAdded = () => {
    setRefreshSites((prev) => prev + 1);
    toast.success("Site list refreshed");
  };

  // Status badge component
  const StatusBadge = ({ status }: { status: string }) => {
    const config = {
      running: {
        color: "text-blue-400",
        bg: "bg-blue-500/20",
        border: "border-blue-500/30",
        icon: Activity,
        pulse: true,
      },
      completed: {
        color: "text-green-400",
        bg: "bg-green-500/20",
        border: "border-green-500/30",
        icon: CheckCircle2,
        pulse: false,
      },
      error: {
        color: "text-red-400",
        bg: "bg-red-500/20",
        border: "border-red-500/30",
        icon: XCircle,
        pulse: false,
      },
      idle: {
        color: "text-slate-400",
        bg: "bg-slate-500/20",
        border: "border-slate-500/30",
        icon: Clock,
        pulse: false,
      },
    };

    const statusConfig = config[status as keyof typeof config] || config.idle;
    const Icon = statusConfig.icon;

    return (
      <div
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${statusConfig.bg} ${statusConfig.border}`}
      >
        <Icon
          className={`w-4 h-4 ${statusConfig.color} ${
            statusConfig.pulse ? "animate-pulse" : ""
          }`}
        />
        <span className={`text-sm font-medium ${statusConfig.color}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
              Scraper Control
            </h1>
            <p className="text-slate-400 text-sm sm:text-base">
              Manage web scraping operations and site configurations. View
              results in{" "}
              <a
                href="/scrape-results"
                className="text-blue-400 hover:text-blue-300 underline"
              >
                Scrape Results
              </a>
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleRefresh}
              variant="outline"
              size="sm"
              className="bg-slate-600"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button
              onClick={handleScheduleRuns}
              variant="outline"
              size="sm"
              className="bg-slate-600"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Schedule
            </Button>
          </div>
        </div>

        {/* Admin Notice */}
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-yellow-400 font-medium">
                Admin Access Required
              </p>
              <p className="text-yellow-400/70 text-sm mt-1">
                Scraping operations affect all enabled sites and consume
                significant resources. Use with caution.
              </p>
            </div>
          </div>
        </div>

        {/* Status Banner */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <StatusBadge status={statusString} />
              </div>

              <div className="flex-1">
                <h3 className="text-white font-semibold mb-2">
                  Current Status
                </h3>
                <div className="space-y-2 text-sm">
                  {isRunning && currentRun ? (
                    <>
                      {currentRun.batch_info?.current_batch_sites && (
                        <div className="flex items-center gap-2 text-slate-300">
                          <Globe className="w-4 h-4" />
                          <span>
                            Sites:{" "}
                            {currentRun.batch_info.current_batch_sites.join(
                              ", "
                            )}
                          </span>
                        </div>
                      )}
                      {currentRun.progress && (
                        <div className="flex items-center gap-2 text-slate-300">
                          <TrendingUp className="w-4 h-4" />
                          <span>
                            Progress: {currentRun.progress.completed_sites} /{" "}
                            {currentRun.progress.total_sites} sites
                          </span>
                        </div>
                      )}
                      {currentRun.started_at && (
                        <div className="flex items-center gap-2 text-slate-300">
                          <Clock className="w-4 h-4" />
                          <span>
                            Started:{" "}
                            {new Date(currentRun.started_at).toLocaleString()}
                          </span>
                        </div>
                      )}
                      {currentRun.timing?.estimated_completion && (
                        <div className="flex items-center gap-2 text-blue-400">
                          <Clock className="w-4 h-4" />
                          <span>
                            ETA:{" "}
                            {new Date(
                              currentRun.timing.estimated_completion
                            ).toLocaleTimeString()}
                          </span>
                        </div>
                      )}
                    </>
                  ) : !isRunning && lastRun ? (
                    <>
                      <div className="flex items-center gap-2 text-slate-300">
                        <Clock className="w-4 h-4" />
                        <span>
                          Last Run:{" "}
                          {new Date(lastRun.completed_at).toLocaleString()}
                        </span>
                      </div>
                      {lastRun.final_stats && (
                        <>
                          <div className="flex items-center gap-2 text-slate-300">
                            <CheckCircle2 className="w-4 h-4" />
                            <span>
                              Sites: {lastRun.final_stats.successful_sites} /{" "}
                              {lastRun.final_stats.total_sites}
                            </span>
                          </div>
                          {lastRun.final_stats.failed_sites > 0 && (
                            <div className="flex items-center gap-2 text-red-400">
                              <XCircle className="w-4 h-4" />
                              <span>
                                Failed: {lastRun.final_stats.failed_sites} sites
                              </span>
                            </div>
                          )}
                        </>
                      )}
                      {lastRun.timing && (
                        <div className="flex items-center gap-2 text-slate-300">
                          <Clock className="w-4 h-4" />
                          <span>
                            Duration:{" "}
                            {Math.round(lastRun.timing.elapsed_seconds)} seconds
                          </span>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-slate-400">No recent activity</div>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex flex-col gap-2">
              <Button
                onClick={handleTriggerGitHubScrape}
                disabled={ghLoading || isRunning}
                className="bg-blue-600 hover:bg-blue-500 text-white"
              >
                {ghLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Start New Scrape
                  </>
                )}
              </Button>

              {isRunning && (
                <Button
                  onClick={handleRunScraper}
                  disabled={scrapeLoading}
                  variant="outline"
                  className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                >
                  <Square className="w-4 h-4 mr-2" />
                  Stop Scraper
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* GitHub Actions Result */}
        {ghResult && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-green-400 font-medium">{ghResult.message}</p>
                {ghResult.run_url && (
                  <div className="mt-2 space-y-2">
                    <a
                      href={ghResult.run_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm"
                    >
                      View Progress on GitHub
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    <p className="text-slate-400 text-sm">
                      When finished, check{" "}
                      <a
                        href="/scrape-results"
                        className="text-blue-400 hover:text-blue-300 underline"
                      >
                        Scrape Results
                      </a>{" "}
                      for new data
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* GitHub Actions Error */}
        {ghError && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-400 font-medium">
                  Failed to trigger scrape
                </p>
                <p className="text-red-400/70 text-sm mt-1">{ghError}</p>
              </div>
            </div>
          </div>
        )}

        {/* Direct API Scrape Feedback */}
        {(scrapeLoading || scrapeComplete || scrapeError) && (
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
            {scrapeLoading && (
              <div className="flex items-center gap-3 text-blue-400">
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Scraping in progress...</span>
              </div>
            )}
            {scrapeComplete && !scrapeError && (
              <div className="flex items-center gap-3 text-green-400">
                <CheckCircle2 className="w-5 h-5" />
                <span>Scraping complete!</span>
              </div>
            )}
            {scrapeError && (
              <div className="flex items-center gap-3 text-red-400">
                <XCircle className="w-5 h-5" />
                <span>Error: {scrapeError}</span>
              </div>
            )}
          </div>
        )}

        {/* Advanced Settings Toggle */}
        <button
          onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
          className="w-full bg-slate-800/50 border border-slate-700 hover:border-slate-600 rounded-xl p-4 transition-colors text-left"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Settings className="w-5 h-5 text-slate-400" />
              <span className="text-white font-medium">Advanced Settings</span>
            </div>
            <ChevronDown
              className={`w-5 h-5 text-slate-400 transition-transform ${
                showAdvancedSettings ? "rotate-180" : ""
              }`}
            />
          </div>
        </button>

        {/* Advanced Settings Content */}
        {showAdvancedSettings && (
          <div className="space-y-6">
            {/* Global Parameters */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Global Parameters
              </h3>
              <GlobalParameters
                maxPages={maxPages}
                geocoding={geocoding}
                onMaxPagesChange={setMaxPages}
                onGeocodingChange={setGeocoding}
              />
            </div>

            {/* Scrape Time Estimate */}
            <ScrapeTimeEstimate
              pageCap={maxPages ?? 1}
              geocode={geocoding ?? false}
              sites={selectedSites}
            />

            {/* Notifications & Alerts */}
            <NotificationsAlerts />
          </div>
        )}

        {/* Site Configuration */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Database className="w-5 h-5" />
              Site Configuration
            </h3>
            <Button
              onClick={() => setShowAddSiteModal(true)}
              size="sm"
              className="bg-blue-600 hover:bg-blue-500"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Site
            </Button>
          </div>
          <SiteConfiguration
            onAddSite={() => setShowAddSiteModal(true)}
            selectedSites={selectedSites}
            onSelectedSitesChange={setSelectedSites}
            refreshTrigger={refreshSites}
          />
        </div>

        {/* Panels Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Scrape History */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Scrape History
            </h3>
            <ScrapeHistoryPanel />
          </div>

          {/* Scheduled Runs */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Scheduled Runs
            </h3>
            <ScheduledRunsPanel />
          </div>
        </div>

        {/* Run Console */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Run Console</h3>
          <RunConsole isRunning={isRunning} githubRunId={githubRunId} />
        </div>

        {/* Error & Alert Center */}
        <ErrorAlertPanel />

        {/* Modals */}
        <AddSiteModal
          isOpen={showAddSiteModal}
          onClose={() => setShowAddSiteModal(false)}
          onSiteAdded={handleSiteAdded}
        />

        <ScheduleModal
          isOpen={showScheduleModal}
          onClose={() => setShowScheduleModal(false)}
        />
      </div>
    </div>
  );
}

// "use client";

// import { useState, useCallback, useEffect, useRef } from "react";
// import { Play, Square, Calendar } from "lucide-react";
// import { ScheduledRunsPanel } from "./scheduled-runs-panel";
// import { ErrorAlertPanel } from "./error-alert-panel";
// import { ScrapeHistoryPanel } from "./scrape-history-panel";
// import { Button } from "@/components/ui/button";
// import { SiteConfiguration } from "./site-configuration";
// import { GlobalParameters } from "./global-parameters";
// import { ScrapeTimeEstimate } from "./scrape-time-estimate";
// import { RunConsole } from "./run-console";
// import { NotificationsAlerts } from "./notifications-alerts";
// import { AddSiteModal } from "./add-site-modal";
// import { ScheduleModal } from "./schedule-modal";
// import { toast } from "sonner";
// import { apiClient } from "@/lib/api";
// import { usePolling } from "@/lib/hooks/useApi";
// import { ScrapeStatus } from "@/lib/types";
// import { useTriggerGitHubScrape } from "@/lib/hooks/useTriggerGitHubScrape";

// export function ScraperControl() {
//   // Manual refresh handler
//   const handleRefresh = async () => {
//     try {
//       // Refetch all relevant scraper data (status, history, scheduled runs)
//       window.location.reload(); // Simple reload for now; can be replaced with granular refetch logic
//       toast.success("Scraper data refreshed");
//     } catch (error) {
//       toast.error("Failed to refresh scraper data");
//     }
//   };
//   const [showAddSiteModal, setShowAddSiteModal] = useState(false);
//   const [showScheduleModal, setShowScheduleModal] = useState(false);
//   const [selectedSites, setSelectedSites] = useState<string[]>([]);
//   const [maxPages, setMaxPages] = useState<number | undefined>(15);
//   // GitHub Actions Scrape Trigger Hook
//   const {
//     triggerScrape,
//     loading: ghLoading,
//     error: ghError,
//     result: ghResult,
//   } = useTriggerGitHubScrape();

//   const handleTriggerGitHubScrape = async () => {
//     try {
//       const res = await triggerScrape({
//         pageCap: maxPages,
//         geocode: geocoding ? 1 : 0,
//         sites: selectedSites,
//       });
//       toast.success("GitHub Actions scrape triggered!", {
//         description: res.message || "Workflow started.",
//         duration: 4000,
//       });
//     } catch (err: any) {
//       toast.error("Failed to trigger GitHub Actions scrape", {
//         description: err.message,
//         duration: 4000,
//       });
//     }
//   };
//   const [geocoding, setGeocoding] = useState<boolean | undefined>(true);
//   const [scrapeLoading, setScrapeLoading] = useState(false);
//   const [scrapeError, setScrapeError] = useState<string | null>(null);
//   const [scrapeComplete, setScrapeComplete] = useState(false);
//   const [refreshSites, setRefreshSites] = useState(0); // Counter to trigger site list refresh

//   const getScrapeStatus = useCallback(() => apiClient.getScrapeStatus(), []);
//   const { data: scrapeStatus } = usePolling<ScrapeStatus>(
//     getScrapeStatus,
//     5000,
//     true
//   );

//   const isRunning = scrapeStatus?.is_running || false;
//   const currentRun = scrapeStatus?.current_run;
//   const lastRun = scrapeStatus?.last_run;

//   // Derive status string for display
//   const getStatusString = () => {
//     if (isRunning) return "running";
//     if (lastRun?.success === true) return "completed";
//     if (lastRun?.success === false) return "error";
//     return "idle";
//   };

//   const statusString = getStatusString();

//   // Track previous running state to detect completion
//   const previousStatusRef = useRef<boolean | undefined>(undefined);
//   useEffect(() => {
//     if (previousStatusRef.current === true && !isRunning && lastRun) {
//       const totalListings =
//         lastRun.final_stats?.successful_sites ||
//         lastRun.progress?.completed_sites ||
//         0;
//       toast.success("Scrape completed", {
//         description: `Completed ${totalListings} site(s)`,
//         duration: 4000,
//       });
//       setScrapeComplete(true);
//     }
//     previousStatusRef.current = isRunning;
//   }, [isRunning, lastRun]);

//   console.log("[ScraperControl] Component mounted/updated");
//   if (scrapeStatus) {
//     console.log(
//       "[ScraperControl] Scraper status:",
//       JSON.stringify(scrapeStatus, null, 2)
//     );
//   } else {
//     console.log("[ScraperControl] Scraper status: null");
//   }

//   const handleRunScraper = async () => {
//     console.log(
//       "[ScraperControl] handleRunScraper called, isRunning:",
//       isRunning
//     );
//     setScrapeError(null);
//     setScrapeComplete(false);
//     setScrapeLoading(true);
//     try {
//       if (isRunning) {
//         console.log("[ScraperControl] Stopping scraper...");
//         await apiClient.stopScrape();
//         toast.success("Scraper stopped successfully");
//         setScrapeLoading(false);
//         setScrapeComplete(true);
//       } else {
//         const params: {
//           sites?: string[];
//           max_pages?: number;
//           geocode?: boolean;
//         } = {};
//         if (selectedSites.length > 0) params.sites = selectedSites;
//         if (maxPages !== undefined) params.max_pages = maxPages;
//         if (geocoding !== undefined) params.geocode = geocoding;

//         console.log("[ScraperControl] Starting scraper with params:", params);
//         await apiClient.startScrape(params);
//         toast.success("Scraper started successfully");
//         // Poll for completion
//         let pollCount = 0;
//         let running = true;
//         let finalStatus: any = null;
//         while (running && pollCount < 60) {
//           // up to 5 min
//           await new Promise((res) => setTimeout(res, 5000));
//           const status: any = await apiClient.getScrapeStatus();
//           finalStatus = status;
//           running = status?.is_running || false;
//           pollCount++;
//         }
//         setScrapeLoading(false);
//         setScrapeComplete(true);

//         // Check final status and show appropriate toast
//         if (finalStatus?.last_run) {
//           const lastRun = finalStatus.last_run;
//           const success = lastRun.success === true || lastRun.return_code === 0;

//           if (success) {
//             toast.success("✅ Scrape completed successfully!", {
//               description: `Scraped ${lastRun.total_scraped || 0} properties`,
//               duration: 5000,
//             });
//           } else {
//             toast.error("❌ Scrape failed", {
//               description: lastRun.error_message || "Check logs for details",
//               duration: 5000,
//             });
//           }
//         } else if (!running) {
//           toast.info("⏱️ Scrape completed", {
//             description: "Check Scrape Results page for details",
//             duration: 5000,
//           });
//         } else {
//           toast.warning("⚠️ Scrape still running", {
//             description: "Taking longer than expected. Check status page.",
//             duration: 5000,
//           });
//         }
//       }
//     } catch (error) {
//       console.error("[ScraperControl] Failed to control scraper:", error);
//       setScrapeError(
//         error instanceof Error ? error.message : "Failed to control scraper"
//       );
//       setScrapeLoading(false);
//       toast.error(
//         error instanceof Error ? error.message : "Failed to control scraper"
//       );
//     }
//   };

//   const handleScheduleRuns = () => {
//     setShowScheduleModal(true);
//   };

//   const handleSiteAdded = () => {
//     // Trigger site list refresh
//     setRefreshSites((prev) => prev + 1);
//     toast.success("Site list refreshed");
//   };

//   return (
//     <div className="space-y-4 sm:space-y-6 p-4 sm:p-6">
//       {/* Page Header */}
//       <div className="flex flex-col space-y-2 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
//         <div>
//           <h1 className="text-2xl sm:text-3xl font-bold text-white">
//             Scraper Control
//           </h1>
//           <p className="text-slate-400 text-sm mt-1">
//             Start a new property data scrape. After completion, view results on
//             the{" "}
//             <a href="/scrape-results" className="underline text-blue-300">
//               Scrape Results page
//             </a>
//             .
//           </p>
//         </div>
//       </div>

//       {/* Scraper Status Banner */}
//       {scrapeStatus && (
//         <div
//           className={`border rounded-lg p-4 ${
//             isRunning
//               ? "bg-blue-500/10 border-blue-500/30"
//               : statusString === "completed"
//               ? "bg-green-500/10 border-green-500/30"
//               : statusString === "error"
//               ? "bg-red-500/10 border-red-500/30"
//               : "bg-slate-700/10 border-slate-700/30"
//           }`}
//         >
//           <div className="flex items-center gap-3">
//             <div className="flex-shrink-0">
//               <div
//                 className={`w-3 h-3 rounded-full ${
//                   isRunning
//                     ? "bg-blue-500 animate-pulse"
//                     : statusString === "completed"
//                     ? "bg-green-500"
//                     : statusString === "error"
//                     ? "bg-red-500"
//                     : "bg-slate-500"
//                 }`}
//               ></div>
//             </div>
//             <div className="flex-1">
//               <p
//                 className={`font-medium ${
//                   isRunning
//                     ? "text-blue-400"
//                     : statusString === "completed"
//                     ? "text-green-400"
//                     : statusString === "error"
//                     ? "text-red-400"
//                     : "text-slate-400"
//                 }`}
//               >
//                 Status:{" "}
//                 {statusString.charAt(0).toUpperCase() + statusString.slice(1)}
//               </p>
//               <div className="mt-2 space-y-1 text-sm text-slate-300">
//                 {/* Show current run info if running */}
//                 {isRunning && currentRun && (
//                   <>
//                     {currentRun.batch_info?.current_batch_sites &&
//                       currentRun.batch_info.current_batch_sites.length > 0 && (
//                         <p>
//                           Current Sites:{" "}
//                           {currentRun.batch_info.current_batch_sites.join(", ")}
//                         </p>
//                       )}
//                     {currentRun.progress && (
//                       <p>
//                         Progress: {currentRun.progress.completed_sites} /{" "}
//                         {currentRun.progress.total_sites} sites
//                       </p>
//                     )}
//                     {currentRun.started_at && (
//                       <p>
//                         Started:{" "}
//                         {new Date(currentRun.started_at).toLocaleString()}
//                       </p>
//                     )}
//                     {currentRun.timing?.estimated_completion && (
//                       <p>
//                         ETA:{" "}
//                         {new Date(
//                           currentRun.timing.estimated_completion
//                         ).toLocaleTimeString()}
//                       </p>
//                     )}
//                     {currentRun.batch_info && (
//                       <p>
//                         Batch: {currentRun.batch_info.current_batch} /{" "}
//                         {currentRun.batch_info.total_batches}
//                       </p>
//                     )}
//                   </>
//                 )}
//                 {/* Show last run info if not running */}
//                 {!isRunning && lastRun && (
//                   <>
//                     <p>
//                       Last Run:{" "}
//                       {new Date(lastRun.completed_at).toLocaleString()}
//                     </p>
//                     {lastRun.final_stats && (
//                       <>
//                         <p>
//                           Sites: {lastRun.final_stats.successful_sites} /{" "}
//                           {lastRun.final_stats.total_sites}
//                         </p>
//                         {lastRun.final_stats.failed_sites > 0 && (
//                           <p className="text-red-400">
//                             Failed: {lastRun.final_stats.failed_sites} sites
//                           </p>
//                         )}
//                       </>
//                     )}
//                     {lastRun.timing && (
//                       <p>
//                         Duration: {Math.round(lastRun.timing.elapsed_seconds)}{" "}
//                         seconds
//                       </p>
//                     )}
//                   </>
//                 )}
//               </div>
//             </div>
//           </div>
//         </div>
//       )}

//       {/* Scrape History Panel */}
//       {/* <ScrapeHistoryPanel /> */}

//       {/* Scheduled Runs Panel */}
//       {/* <ScheduledRunsPanel /> */}

//       {/* Error & Alert Center */}
//       {/* <ErrorAlertPanel /> */}

//       {/* Control Buttons & Scrape Status */}
//       <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
//         <Button
//           onClick={handleTriggerGitHubScrape}
//           disabled={ghLoading}
//           className="bg-blue-600 hover:bg-blue-700 w-full sm:w-auto text-white"
//         >
//           {ghLoading ? "Starting..." : "Start New Scrape"}
//         </Button>
//         {ghError && <div className="text-red-400 mt-2">Error: {ghError}</div>}
//         {ghResult && (
//           <div className="text-green-400 mt-2">
//             {ghResult.message}
//             {ghResult.run_url && (
//               <>
//                 <br />
//                 <a
//                   href={ghResult.run_url}
//                   target="_blank"
//                   rel="noopener noreferrer"
//                   className="underline text-blue-300"
//                 >
//                   View Scrape Progress on GitHub
//                 </a>
//                 <br />
//                 <span className="text-blue-200 text-xs">
//                   When finished,{" "}
//                   <b>
//                     visit the{" "}
//                     <a href="/scrape-results" className="underline">
//                       Scrape Results page
//                     </a>
//                   </b>{" "}
//                   to see new results.
//                 </span>
//               </>
//             )}
//           </div>
//         )}
//       </div>
//       {/* Scrape Status Feedback */}
//       {(scrapeLoading || scrapeComplete || scrapeError) && (
//         <div className="mt-2">
//           {scrapeLoading && (
//             <div className="text-blue-400 flex items-center gap-2">
//               <span className="animate-spin w-4 h-4 border-b-2 border-blue-400 rounded-full"></span>
//               <span>Scraping in progress...</span>
//             </div>
//           )}
//           {scrapeComplete && !scrapeError && (
//             <div className="text-green-400">Scraping complete!</div>
//           )}
//           {scrapeError && (
//             <div className="text-red-400">Error: {scrapeError}</div>
//           )}
//         </div>
//       )}

//       {/* Site Configuration (simple) */}
//       <div className="mt-6">
//         <SiteConfiguration
//           onAddSite={() => setShowAddSiteModal(true)}
//           selectedSites={selectedSites}
//           onSelectedSitesChange={setSelectedSites}
//           refreshTrigger={refreshSites}
//         />
//       </div>
//     </div>
//   );
// }
