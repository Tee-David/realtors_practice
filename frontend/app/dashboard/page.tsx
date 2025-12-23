"use client";
// --- Type Definitions for Dashboard ---
import type { Property } from "@/lib/types";
type VariantType = "default" | "success" | "info" | "warning" | "danger";
type StatusType = "healthy" | "running" | "idle" | "error" | "warning";
interface StatusBadgeProps {
  status: StatusType;
  label: string;
}
interface PropertyCardProps {
  property: Property;
}
// "use client";

// import { useCallback, useEffect } from "react";
// import { apiClient } from "@/lib/api";
// import { useApi, usePolling } from "@/lib/hooks/useApi";
// import { ScrapeStatus, ScrapeHistory } from "@/lib/types";
// import { StatsCard } from "@/components/shared/stats-card";
// import { QuickActions } from "@/components/dashboard/quick-actions";
// import { RecentActivity } from "@/components/dashboard/recent-activity";
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import { Badge } from "@/components/ui/badge";
// import {
//   Home,
//   TrendingUp,
//   Search,
//   Activity,
//   AlertCircle,
//   CheckCircle,
//   XCircle,
//   Clock,
//   Database,
//   GitBranch,
// } from "lucide-react";
// import { Button } from "@/components/ui/button";
// import { RefreshCw } from "lucide-react";
// import { toast } from "sonner";
// import { ApiHealthCheck } from "@/components/diagnostics/api-health-check";
// import { ApiStatusBanner } from "@/components/ui/api-status-banner";

// /**
//  * Dashboard Page
//  * Uses NEW Firestore-optimized dashboard endpoint (40-300x faster!)
//  * Falls back to legacy endpoints if Firestore not available.
//  * Endpoints used:
//  * - GET /api/firestore/dashboard - All dashboard stats in one call (preferred)
//  * - GET /api/stats/overview - Legacy stats (fallback)
//  * - GET /api/health - API health check
//  * - GET /api/scrape/status - Scraping status
//  * - GET /api/firestore/newest - Recent properties (preferred)
//  * - GET /api/data - All properties (fallback)
//  * - GET /api/sites - Sites list
//  */

// export default function DashboardPage() {
//   // Fetch scrape history (last 5 runs) - must be inside the component!
//   const {
//     data: scrapeHistory,
//     loading: scrapeHistoryLoading,
//     error: scrapeHistoryError,
//     refetch: refetchScrapeHistory,
//   } = useApi<ScrapeHistory>(() => apiClient.getScrapeHistory(5));
//   // API calls with stable references
//   const getFirestoreDashboardStats = useCallback(async () => {
//     console.log("[Dashboard] Fetching Firestore dashboard stats...");
//     return await apiClient.getFirestoreDashboard();
//   }, []);

//   // Fetch active saved searches count
//   const getActiveSavedSearchesCount = useCallback(async () => {
//     const searches = await apiClient.listSavedSearches();
//     return Array.isArray(searches) ? searches.length : 0;
//   }, []);

//   const getLegacyDashboardStats = useCallback(async () => {
//     console.log("[Dashboard] 🔄 LEGACY STATS FETCH TRIGGERED");
//     return await apiClient.getOverviewStats();
//   }, []);

//   const getHealth = useCallback(async () => apiClient.healthCheck(), []);
//   const getScrapeStatus = useCallback(
//     async () => apiClient.getScrapeStatus(),
//     []
//   );

//   const getFirestoreRecentProperties = useCallback(async () => {
//     console.log("[Dashboard] Fetching Firestore recent properties...");
//     return await apiClient.getFirestoreNewest({ limit: 10 });
//   }, []);

//   const getLegacyRecentProperties = useCallback(async () => {
//     console.log("[Dashboard] 🔄 LEGACY PROPERTIES FETCH TRIGGERED");
//     const result = await apiClient.getAllData();
//     return result.properties?.slice(0, 10) || [];
//   }, []);

//   const getListSites = useCallback(async () => apiClient.listSites(), []);

//   // Try Firestore first for dashboard stats
//   const {
//     data: firestoreStats,
//     loading: firestoreStatsLoading,
//     error: firestoreStatsError,
//     refetch: refetchFirestoreStats,
//   } = useApi<any>(getFirestoreDashboardStats, {
//     onError: () => {
//       // Suppress error - fallback will handle it
//       console.log("[Dashboard] Firestore unavailable, using legacy endpoint");
//     },
//   });

//   // Fallback to legacy if Firestore fails
//   const {
//     data: legacyStats,
//     loading: legacyStatsLoading,
//     refetch: refetchLegacyStats,
//   } = useApi<any>(getLegacyDashboardStats, {
//     immediate: !!firestoreStatsError,
//   });

//   // Determine which stats to use
//   const dashboardStats = firestoreStatsError ? legacyStats : firestoreStats;
//   const dashboardLoading = firestoreStatsLoading || legacyStatsLoading;
//   const dashboardError =
//     firestoreStatsError && !legacyStats ? firestoreStatsError : null;

//   // Log fallback with detailed state
//   useEffect(() => {
//     if (firestoreStatsError) {
//       console.log("[Dashboard] Firestore FAILED - Error:", firestoreStatsError);
//       console.log(
//         "[Dashboard] Triggering legacy fallback... immediate:",
//         !!firestoreStatsError
//       );
//     }
//     if (legacyStats) {
//       console.log(
//         "[Dashboard] ✅ Legacy stats loaded successfully:",
//         legacyStats
//       );
//     }
//   }, [firestoreStatsError, legacyStats]);

//   // Fetch health status
//   const {
//     data: health,
//     loading: healthLoading,
//     error: healthError,
//   } = useApi<any>(getHealth);

//   // Poll scraper status every 10 seconds
//   const { data: scrapeStatus } = usePolling<any>(getScrapeStatus, 10000, true);

//   // Try Firestore first for recent properties
//   const {
//     data: firestoreProperties,
//     loading: firestorePropertiesLoading,
//     error: firestorePropertiesError,
//   } = useApi<any>(getFirestoreRecentProperties, {
//     onError: () => {
//       // Suppress error - fallback will handle it
//       console.log(
//         "[Dashboard] Firestore properties unavailable, using legacy endpoint"
//       );
//     },
//   });

//   // Fallback to legacy if Firestore fails
//   const { data: legacyProperties, loading: legacyPropertiesLoading } =
//     useApi<any>(getLegacyRecentProperties, {
//       immediate: !!firestorePropertiesError,
//     });

//   // Determine which properties to use
//   const recentProperties = firestorePropertiesError
//     ? legacyProperties
//     : firestoreProperties;
//   const propertiesLoading =
//     firestorePropertiesLoading || legacyPropertiesLoading;
//   const propertiesError =
//     firestorePropertiesError && !legacyProperties
//       ? firestorePropertiesError
//       : null;

//   // Log fallback with detailed state
//   useEffect(() => {
//     if (firestorePropertiesError) {
//       console.log(
//         "[Dashboard] Firestore properties FAILED - Error:",
//         firestorePropertiesError
//       );
//       console.log(
//         "[Dashboard] Triggering legacy properties fallback... immediate:",
//         !!firestorePropertiesError
//       );
//     }
//     if (legacyProperties) {
//       console.log(
//         "[Dashboard] ✅ Legacy properties loaded successfully:",
//         legacyProperties?.length,
//         "items"
//       );
//     }
//   }, [firestorePropertiesError, legacyProperties]);

//   // Fetch list of sites
//   const { data: sitesData } = useApi<any>(getListSites);

//   // Unified refetch that tries Firestore first
//   const refetchDashboard = useCallback(() => {
//     if (firestoreStatsError) {
//       refetchLegacyStats();
//     } else {
//       refetchFirestoreStats();
//     }
//   }, [firestoreStatsError, refetchFirestoreStats, refetchLegacyStats]);

//   // Refresh all data
//   const handleRefresh = () => {
//     refetchDashboard();
//     toast.success("Dashboard refreshed");
//   };

//   // Navigate to page
//   const handleNavigate = (page: string) => {
//     // This will be handled by the parent app routing
//     window.dispatchEvent(new CustomEvent("navigate", { detail: { page } }));
//   };

//   // Quick scrape action
//   const handleQuickScrape = async () => {
//     try {
//       await apiClient.startScrape({ sites: [], max_pages: 10 });
//       toast.success("Quick scrape started");
//     } catch (error) {
//       toast.error("Failed to start quick scrape");
//     }
//   };

//   // Derive stats from dashboard data (handles both Firestore and legacy formats)
//   // Firestore format: { total_properties, for_sale_count, for_rent_count, land_count, avg_price_for_sale }
//   // Legacy format: { total_properties, by_status, by_type, avg_price }
//   const totalProperties = dashboardStats?.total_properties || 0;
//   const forSaleCount =
//     dashboardStats?.for_sale_count || dashboardStats?.by_status?.for_sale || 0;
//   const forRentCount =
//     dashboardStats?.for_rent_count || dashboardStats?.by_status?.for_rent || 0;
//   const landCount =
//     dashboardStats?.land_count || dashboardStats?.by_type?.land || 0;
//   const avgPriceForSale =
//     dashboardStats?.avg_price_for_sale || dashboardStats?.avg_price || 0;
//   const addedToday = 0; // TODO: Calculate from newest_listing_date

//   // Fetch active saved searches count
//   const {
//     data: activeSavedSearches,
//     loading: activeSavedSearchesLoading,
//     error: activeSavedSearchesError,
//     refetch: refetchActiveSavedSearches,
//   } = useApi<number>(getActiveSavedSearchesCount);
//   const systemHealthStatus = health?.status || "unknown";
//   const isScraperRunning = scrapeStatus?.is_running || false;
//   const enabledSitesCount = sitesData?.enabled || 0;

//   // Check for critical errors
//   const hasError = dashboardError || healthError || propertiesError;
//   const errorMessage =
//     dashboardError ||
//     healthError ||
//     propertiesError ||
//     "Failed to load dashboard data";

//   return (
//     <div className="space-y-4 sm:space-y-6 p-4 sm:p-6">
//       {/* Scrape Status & History Section */}
//       <div className="mt-6">
//         <h2 className="text-lg font-semibold text-white mb-2">
//           Scrape Status & History
//         </h2>
//         {/* Current or Last Run Details */}
//         <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-4">
//           {scrapeStatus?.is_running && scrapeStatus.current_run ? (
//             <>
//               <div className="flex items-center gap-2 mb-2">
//                 <Activity className="w-5 h-5 text-blue-400 animate-pulse" />
//                 <span className="text-blue-300 font-medium">
//                   Scrape in progress
//                 </span>
//                 <span className="text-xs text-slate-400">
//                   Started:{" "}
//                   {new Date(
//                     scrapeStatus.current_run.started_at
//                   ).toLocaleString()}
//                 </span>
//               </div>
//               <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-slate-300 mb-2">
//                 <div>
//                   <span className="font-semibold">Sites:</span>{" "}
//                   {(scrapeStatus.current_run.sites &&
//                     scrapeStatus.current_run.sites.length) ||
//                     0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Completed:</span>{" "}
//                   {scrapeStatus.current_run.progress?.completed_sites ?? 0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">In Progress:</span>{" "}
//                   {scrapeStatus.current_run.progress?.in_progress_sites ?? 0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Failed:</span>{" "}
//                   {scrapeStatus.current_run.progress?.failed_sites ?? 0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Pending:</span>{" "}
//                   {scrapeStatus.current_run.progress?.pending_sites ?? 0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Batch:</span>{" "}
//                   {scrapeStatus.current_run.batch_info?.current_batch ?? 0} /{" "}
//                   {scrapeStatus.current_run.batch_info?.total_batches ?? 0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Elapsed:</span>{" "}
//                   {scrapeStatus.current_run.timing?.elapsed_seconds ?? 0}s
//                 </div>
//                 <div>
//                   <span className="font-semibold">Est. Remaining:</span>{" "}
//                   {scrapeStatus.current_run.timing
//                     ?.estimated_remaining_seconds ?? 0}
//                   s
//                 </div>
//               </div>
//               <div className="flex flex-wrap gap-4 text-xs text-slate-400">
//                 <span>
//                   CPU: {scrapeStatus.current_run.resources?.cpu_percent ?? 0}%
//                 </span>
//                 <span>
//                   Memory:{" "}
//                   {scrapeStatus.current_run.resources?.memory_percent ?? 0}%
//                 </span>
//                 <span>
//                   Est. Completion:{" "}
//                   {scrapeStatus.current_run.timing?.estimated_completion
//                     ? new Date(
//                         scrapeStatus.current_run.timing.estimated_completion
//                       ).toLocaleString()
//                     : "-"}
//                 </span>
//               </div>
//             </>
//           ) : scrapeStatus?.last_run ? (
//             <>
//               <div className="flex items-center gap-2 mb-2">
//                 {scrapeStatus.last_run.success ? (
//                   <CheckCircle className="w-5 h-5 text-green-400" />
//                 ) : (
//                   <XCircle className="w-5 h-5 text-red-400" />
//                 )}
//                 <span
//                   className={
//                     scrapeStatus.last_run.success
//                       ? "text-green-300 font-medium"
//                       : "text-red-300 font-medium"
//                   }
//                 >
//                   Last scrape{" "}
//                   {scrapeStatus.last_run.success ? "succeeded" : "failed"}
//                 </span>
//                 <span className="text-xs text-slate-400">
//                   Completed:{" "}
//                   {new Date(
//                     scrapeStatus.last_run.completed_at
//                   ).toLocaleString()}
//                 </span>
//               </div>
//               <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-slate-300 mb-2">
//                 <div>
//                   <span className="font-semibold">Sites:</span>{" "}
//                   {(scrapeStatus.last_run.sites &&
//                     scrapeStatus.last_run.sites.length) ||
//                     0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Completed:</span>{" "}
//                   {scrapeStatus.last_run.progress?.completed_sites ?? 0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Failed:</span>{" "}
//                   {scrapeStatus.last_run.progress?.failed_sites ?? 0}
//                 </div>
//                 <div>
//                   <span className="font-semibold">Duration:</span>{" "}
//                   {scrapeStatus.last_run.timing?.elapsed_seconds ?? 0}s
//                 </div>
//               </div>
//               <div className="flex flex-wrap gap-4 text-xs text-slate-400">
//                 <span>
//                   CPU: {scrapeStatus.last_run.resources?.cpu_percent ?? 0}%
//                 </span>
//                 <span>
//                   Memory: {scrapeStatus.last_run.resources?.memory_percent ?? 0}
//                   %
//                 </span>
//               </div>
//             </>
//           ) : (
//             <span className="text-slate-400 text-sm">
//               No scrape runs found.
//             </span>
//           )}
//         </div>
//         {/* Scrape History Table */}
//         <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
//           <h4 className="text-white text-sm font-semibold mb-2">
//             Recent Scrape History
//           </h4>
//           {scrapeHistoryLoading ? (
//             <span className="text-slate-400 text-xs">Loading history...</span>
//           ) : scrapeHistoryError ? (
//             <span className="text-red-400 text-xs">Failed to load history</span>
//           ) : scrapeHistory &&
//             Array.isArray(scrapeHistory.scrapes) &&
//             scrapeHistory.scrapes.length > 0 ? (
//             <table className="w-full text-xs text-slate-300">
//               <thead>
//                 <tr className="border-b border-slate-700">
//                   <th className="py-1 text-left">Start</th>
//                   <th className="py-1 text-left">End</th>
//                   <th className="py-1 text-left">Sites</th>
//                   <th className="py-1 text-left">Listings</th>
//                   <th className="py-1 text-left">Status</th>
//                   <th className="py-1 text-left">Duration</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {scrapeHistory.scrapes.map((item) => (
//                   <tr key={item.id} className="border-b border-slate-800">
//                     <td>{new Date(item.start_time).toLocaleString()}</td>
//                     <td>
//                       {item.end_time
//                         ? new Date(item.end_time).toLocaleString()
//                         : "-"}
//                     </td>
//                     <td>{item.sites?.join(", ")}</td>
//                     <td>{item.total_listings}</td>
//                     <td>
//                       <span
//                         className={
//                           item.status === "completed"
//                             ? "text-green-400"
//                             : item.status === "partial"
//                             ? "text-yellow-400"
//                             : "text-red-400"
//                         }
//                       >
//                         {item.status.charAt(0).toUpperCase() +
//                           item.status.slice(1)}
//                       </span>
//                     </td>
//                     <td>
//                       {item.duration_seconds
//                         ? `${item.duration_seconds}s`
//                         : "-"}
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           ) : (
//             <span className="text-slate-400 text-xs">
//               No scrape history found.
//             </span>
//           )}
//         </div>
//       </div>
//       {/* Onboarding & Guidance */}
//       <div className="mb-4">
//         <h1 className="text-2xl sm:text-3xl font-bold text-white">Dashboard</h1>
//         <p className="text-sm sm:text-base text-slate-400 mt-1 max-w-2xl">
//           Welcome to your Real Estate Scrapper dashboard! Here you can monitor
//           property data, system health, and scraping activity at a glance.
//           <br />
//           <span className="text-slate-300">New here?</span> Start by exploring
//           the <b>Scraper Control</b> page to run a new scrape, or use the{" "}
//           <b>Search</b> page to find properties. For advanced data, try the{" "}
//           <b>Data Explorer</b>.<br />
//           <span className="text-slate-300">Tip:</span> If you just triggered a
//           scrape (e.g. via GitHub Actions), results will appear here and in the{" "}
//           <b>Scrape Results</b> page once complete.
//         </p>
//       </div>

//       {/* API Health Check */}
//       <ApiHealthCheck />

//       {/* Error Banner */}
//       {hasError && (
//         <ApiStatusBanner
//           message={errorMessage}
//           onRetry={handleRefresh}
//           type="error"
//         />
//       )}

//       {/* Empty State for No Data */}
//       {!dashboardLoading && !hasError && totalProperties === 0 && (
//         <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-6 flex flex-col items-center text-center mb-6">
//           <AlertCircle className="w-8 h-8 text-yellow-400 mb-2" />
//           <h2 className="text-lg font-semibold text-white mb-1">
//             No property data yet
//           </h2>
//           <p className="text-slate-400 mb-3 max-w-md">
//             It looks like you haven't scraped any property data yet. To get
//             started:
//           </p>
//           <ul className="text-slate-300 text-sm mb-4 list-disc list-inside">
//             <li>
//               Go to <b>Scraper Control</b> and run a new scrape.
//             </li>
//             <li>Or, trigger a scrape via GitHub Actions (see project docs).</li>
//             <li>
//               Once complete, return here or visit <b>Scrape Results</b> to view
//               new data.
//             </li>
//           </ul>
//           <div className="flex gap-2">
//             <Button onClick={() => handleNavigate("scraper")}>
//               Go to Scraper Control
//             </Button>
//             <Button
//               variant="outline"
//               onClick={() => handleNavigate("scrape-results")}
//             >
//               View Scrape Results
//             </Button>
//           </div>
//         </div>
//       )}

//       {/* Header Actions */}
//       <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
//         <div>{/* ...existing code... */}</div>
//         <Button
//           onClick={handleRefresh}
//           variant="outline"
//           size="sm"
//           className="border-slate-600 hover:bg-slate-700 w-full sm:w-auto"
//         >
//           <RefreshCw className="w-4 h-4 mr-2" />
//           Refresh
//         </Button>
//       </div>

//       {/* Stats Cards Grid and Main Content */}
//       {totalProperties > 0 && (
//         <>
//           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//             <StatsCard
//               title="Total Properties"
//               value={totalProperties.toLocaleString()}
//               icon={Home}
//               loading={dashboardLoading}
//               variant="info"
//               description="Available in database"
//             />
//             <StatsCard
//               title="For Sale"
//               value={forSaleCount.toLocaleString()}
//               icon={Home}
//               loading={dashboardLoading}
//               variant="success"
//               description={`Avg: ₦${(avgPriceForSale / 1000000).toFixed(1)}M`}
//             />
//             <StatsCard
//               title="For Rent"
//               value={forRentCount.toLocaleString()}
//               icon={TrendingUp}
//               loading={dashboardLoading}
//               variant="default"
//               description="Rental properties"
//             />
//             <StatsCard
//               title="Active Saved Searches"
//               value={activeSavedSearches ?? 0}
//               icon={Search}
//               loading={activeSavedSearchesLoading}
//               variant="default"
//               description="Your alerts"
//             />
//             <StatsCard
//               title="System Health"
//               value={systemHealthStatus}
//               icon={Activity}
//               loading={healthLoading}
//               variant={
//                 systemHealthStatus === "healthy"
//                   ? "success"
//                   : systemHealthStatus === "degraded"
//                   ? "warning"
//                   : "danger"
//               }
//             />
//           </div>

//           {/* Quick Actions */}
//           <QuickActions
//             isAdmin={true}
//             isScraperRunning={isScraperRunning}
//             onNavigate={handleNavigate}
//             onQuickScrape={handleQuickScrape}
//           />

//           {/* Two Column Layout: Recent Activity + System Health */}
//           <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
//             {/* Recent Activity */}
//             <RecentActivity scrapeStatus={scrapeStatus} />

//             {/* System Health & Status */}
//             <Card className="bg-slate-800 border-slate-700">
//               <CardHeader>
//                 <CardTitle className="text-white">System Status</CardTitle>
//               </CardHeader>
//               <CardContent className="space-y-4">
//                 {/* API Health */}
//                 <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
//                   <div className="flex items-center gap-3">
//                     {health?.status === "healthy" ? (
//                       <CheckCircle className="w-5 h-5 text-green-400" />
//                     ) : (
//                       <XCircle className="w-5 h-5 text-red-400" />
//                     )}
//                     <div>
//                       <p className="text-sm font-medium text-white">
//                         API Server
//                       </p>
//                       <p className="text-xs text-slate-400">
//                         {health?.status || "Unknown"}
//                       </p>
//                     </div>
//                   </div>
//                   <Badge
//                     variant="outline"
//                     className={
//                       health?.status === "healthy"
//                         ? "bg-green-500/10 text-green-400 border-green-500/20"
//                         : "bg-red-500/10 text-red-400 border-red-500/20"
//                     }
//                   >
//                     {health?.status || "Unknown"}
//                   </Badge>
//                 </div>

//                 {/* Scraper Status */}
//                 <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
//                   <div className="flex items-center gap-3">
//                     {isScraperRunning ? (
//                       <Activity className="w-5 h-5 text-blue-400 animate-pulse" />
//                     ) : (
//                       <Clock className="w-5 h-5 text-slate-400" />
//                     )}
//                     <div>
//                       <p className="text-sm font-medium text-white">Scraper</p>
//                       <p className="text-xs text-slate-400">
//                         {isScraperRunning ? "Running" : "Idle"}
//                       </p>
//                     </div>
//                   </div>
//                   <Badge
//                     variant="outline"
//                     className={
//                       isScraperRunning
//                         ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
//                         : "bg-slate-500/10 text-slate-400 border-slate-500/20"
//                     }
//                   >
//                     {isScraperRunning ? "Active" : "Idle"}
//                   </Badge>
//                 </div>

//                 {/* Enabled Sites */}
//                 <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
//                   <div className="flex items-center gap-3">
//                     <Database className="w-5 h-5 text-purple-400" />
//                     <div>
//                       <p className="text-sm font-medium text-white">
//                         Enabled Sites
//                       </p>
//                       <p className="text-xs text-slate-400">
//                         Active data sources
//                       </p>
//                     </div>
//                   </div>
//                   <Badge
//                     variant="outline"
//                     className="bg-purple-500/10 text-purple-400 border-purple-500/20"
//                   >
//                     {enabledSitesCount}
//                   </Badge>
//                 </div>

//                 {/* GitHub Actions (if available) */}
//                 <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
//                   <div className="flex items-center gap-3">
//                     <GitBranch className="w-5 h-5 text-orange-400" />
//                     <div>
//                       <p className="text-sm font-medium text-white">
//                         GitHub Actions
//                       </p>
//                       <p className="text-xs text-slate-400">
//                         Automated workflows
//                       </p>
//                     </div>
//                   </div>
//                   <Badge
//                     variant="outline"
//                     className="bg-slate-500/10 text-slate-400 border-slate-500/20"
//                   >
//                     Not configured
//                   </Badge>
//                 </div>
//               </CardContent>
//             </Card>
//           </div>

//           {/* Admin Quick Panel (conditional) */}
//           {isScraperRunning && (
//             <Card className="bg-blue-500/10 border-blue-500/20">
//               <CardContent className="p-4">
//                 <div className="flex items-center gap-3">
//                   <Activity className="w-5 h-5 text-blue-400 animate-pulse" />
//                   <div className="flex-1">
//                     <p className="text-sm font-medium text-blue-300">
//                       Scraper is currently running
//                     </p>
//                     <p className="text-xs text-blue-400/70">
//                       Check Scraper Control page for detailed progress
//                     </p>
//                   </div>
//                   <Button
//                     variant="outline"
//                     size="sm"
//                     onClick={() => handleNavigate("scraper")}
//                     className="border-blue-500/30 hover:bg-blue-500/20"
//                   >
//                     View Details
//                   </Button>
//                 </div>
//               </CardContent>
//             </Card>
//           )}

//           {/* Recent Properties Section */}
//           <div className="mt-8">
//             <h2 className="text-xl font-semibold text-white mb-2">
//               Recent Properties
//             </h2>
//             {propertiesLoading ? (
//               <p className="text-slate-400">Loading recent properties...</p>
//             ) : Array.isArray(recentProperties) &&
//               recentProperties.length > 0 ? (
//               <ul className="divide-y divide-slate-700 bg-slate-900/60 rounded-lg">
//                 {recentProperties.map((prop: any, idx: number) => (
//                   <li
//                     key={prop.id || idx}
//                     className="p-4 flex flex-col sm:flex-row sm:items-center justify-between"
//                   >
//                     <div>
//                       <span className="font-medium text-white">
//                         {prop.title || prop.address || "Untitled Property"}
//                       </span>
//                       <span className="ml-2 text-xs text-slate-400">
//                         {prop.status || prop.type || "-"}
//                       </span>
//                     </div>
//                     <span className="text-xs text-slate-500 mt-1 sm:mt-0">
//                       {prop.site || "Unknown site"}
//                     </span>
//                   </li>
//                 ))}
//               </ul>
//             ) : (
//               <div className="bg-slate-800/80 border border-slate-700 rounded-lg p-6 flex flex-col items-center text-center">
//                 <AlertCircle className="w-7 h-7 text-yellow-400 mb-2" />
//                 <p className="text-slate-300 mb-2">
//                   No recent properties found.
//                 </p>
//                 <p className="text-slate-400 text-sm mb-3">
//                   Try running a new scrape or check back later.
//                 </p>
//                 <Button onClick={() => handleNavigate("scraper")}>
//                   Run Scraper
//                 </Button>
//               </div>
//             )}
//           </div>
//         </>
//       )}
//     </div>

import { useCallback, useEffect, useState } from "react";
import {
  Home,
  TrendingUp,
  Search,
  Activity,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Database,
  GitBranch,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  TrendingDown,
  MapPin,
  Calendar,
  DollarSign,
} from "lucide-react";

import { apiClient } from "@/lib/api";
import { useApi, usePolling } from "@/lib/hooks/useApi";
import { toast } from "sonner";

// Stats Card Component
interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  loading?: boolean;
  variant?: VariantType;
  description?: string;
  trend?: number;
}
const StatsCard = ({
  title,
  value,
  icon: Icon,
  loading,
  variant = "default",
  description,
  trend,
}: StatsCardProps) => {
  const variants: Record<VariantType, string> = {
    default: "from-slate-700 to-slate-800 border-slate-600",
    success: "from-green-900/40 to-green-800/40 border-green-700/50",
    info: "from-blue-900/40 to-blue-800/40 border-blue-700/50",
    warning: "from-yellow-900/40 to-yellow-800/40 border-yellow-700/50",
    danger: "from-red-900/40 to-red-800/40 border-red-700/50",
  };

  const iconColors: Record<VariantType, string> = {
    default: "text-slate-400",
    success: "text-green-400",
    info: "text-blue-400",
    warning: "text-yellow-400",
    danger: "text-red-400",
  };

  return (
    <div
      className={`relative overflow-hidden rounded-xl border bg-gradient-to-br ${variants[variant]} p-5 transition-all hover:shadow-lg hover:scale-[1.02]`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-400 mb-1">{title}</p>
          {loading ? (
            <div className="h-8 w-24 bg-slate-700 animate-pulse rounded" />
          ) : (
            <p className="text-3xl font-bold text-white mb-1">{value}</p>
          )}
          {description && (
            <p className="text-xs text-slate-400 flex items-center gap-1">
              {trend && (
                <span className={trend > 0 ? "text-green-400" : "text-red-400"}>
                  {trend > 0 ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                </span>
              )}
              {description}
            </p>
          )}
        </div>
        <div
          className={`p-3 rounded-lg bg-slate-900/50 ${iconColors[variant]}`}
        >
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};

// Status Badge Component
const StatusBadge = ({ status, label }: StatusBadgeProps) => {
  const variants: Record<StatusType, string> = {
    healthy: "bg-green-500/20 text-green-300 border-green-500/30",
    running: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    idle: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    error: "bg-red-500/20 text-red-300 border-red-500/30",
    warning: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
        variants[status] || variants.idle
      }`}
    >
      {label}
    </span>
  );
};

// Property Card Component
const PropertyCard = ({ property }: PropertyCardProps) => {
  // Accept price as string or number
  const formatPrice = (price: string | number | undefined) => {
    if (price === undefined || price === null || price === "") return "N/A";
    const num = typeof price === "string" ? parseFloat(price) : price;
    if (isNaN(num)) return "N/A";
    if (num >= 1000000) return `₦${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `₦${(num / 1000).toFixed(0)}K`;
    return `₦${num}`;
  };

  return (
    <div className="group bg-slate-800/50 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 rounded-lg p-4 transition-all cursor-pointer">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="text-white font-medium mb-1 group-hover:text-blue-400 transition-colors line-clamp-1">
            {property.title || "Untitled Property"}
          </h4>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <MapPin className="w-3 h-3" />
            <span>{property.location || "Location not specified"}</span>
          </div>
        </div>
        <StatusBadge
          status={property.type === "for_sale" ? "healthy" : "idle"}
          label={property.type?.replace("_", " ").toUpperCase() || "N/A"}
        />
      </div>
      <div className="flex items-center justify-between pt-3 border-t border-slate-700">
        <span className="text-lg font-bold text-white flex items-center gap-1">
          <DollarSign className="w-4 h-4" />
          {formatPrice(property.price)}
        </span>
        <span className="text-xs text-slate-500">
          {property.site_key || ""}
        </span>
      </div>
    </div>
  );
};

// Main Dashboard Component
export default function DashboardPage() {
  const [showHistory, setShowHistory] = useState(false);

  // API calls with stable references
  const getFirestoreDashboardStats = useCallback(async () => {
    console.log("[Dashboard] Fetching Firestore dashboard stats...");
    return await apiClient.getFirestoreDashboard();
  }, []);

  const getActiveSavedSearchesCount = useCallback(async () => {
    const searches = await apiClient.listSavedSearches();
    return Array.isArray(searches) ? searches.length : 0;
  }, []);

  const getLegacyDashboardStats = useCallback(async () => {
    console.log("[Dashboard] 🔄 LEGACY STATS FETCH TRIGGERED");
    return await apiClient.getOverviewStats();
  }, []);

  const getHealth = useCallback(async () => apiClient.healthCheck(), []);
  const getScrapeStatus = useCallback(
    async () => apiClient.getScrapeStatus(),
    []
  );

  const getFirestoreRecentProperties = useCallback(async () => {
    console.log("[Dashboard] Fetching Firestore recent properties...");
    return await apiClient.getFirestoreNewest({ limit: 10 });
  }, []);

  const getLegacyRecentProperties = useCallback(async () => {
    console.log("[Dashboard] 🔄 LEGACY PROPERTIES FETCH TRIGGERED");
    const result = await apiClient.getAllData();
    return result.properties?.slice(0, 10) || [];
  }, []);

  const getListSites = useCallback(async () => apiClient.listSites(), []);

  // Try Firestore first for dashboard stats
  const {
    data: firestoreStats,
    loading: firestoreStatsLoading,
    error: firestoreStatsError,
    refetch: refetchFirestoreStats,
  } = useApi(getFirestoreDashboardStats, {
    onError: () => {
      console.log("[Dashboard] Firestore unavailable, using legacy endpoint");
    },
  });

  // Fallback to legacy if Firestore fails
  const {
    data: legacyStats,
    loading: legacyStatsLoading,
    refetch: refetchLegacyStats,
  } = useApi(getLegacyDashboardStats, {
    immediate: !!firestoreStatsError,
  });

  // Determine which stats to use
  const stats = firestoreStatsError ? legacyStats : firestoreStats;
  const dashboardLoading = firestoreStatsLoading || legacyStatsLoading;

  // Fetch health status
  const { data: health, loading: healthLoading } = useApi(getHealth);

  // Poll scraper status every 10 seconds
  const { data: scrapeStatus } = usePolling(getScrapeStatus, 10000, true);

  // Fetch scrape history (last 5 runs)
  const { data: scrapeHistory, loading: scrapeHistoryLoading } = useApi(() =>
    apiClient.getScrapeHistory(5)
  );

  // Try Firestore first for recent properties
  const {
    data: firestoreProperties,
    loading: firestorePropertiesLoading,
    error: firestorePropertiesError,
  } = useApi(getFirestoreRecentProperties, {
    onError: () => {
      console.log(
        "[Dashboard] Firestore properties unavailable, using legacy endpoint"
      );
    },
  });

  // Fallback to legacy if Firestore fails
  const { data: legacyProperties, loading: legacyPropertiesLoading } = useApi(
    getLegacyRecentProperties,
    { immediate: !!firestorePropertiesError }
  );

  // Determine which properties to use
  const recentProperties = firestorePropertiesError
    ? legacyProperties
    : firestoreProperties;
  const propertiesLoading =
    firestorePropertiesLoading || legacyPropertiesLoading;

  // Fetch list of sites
  const { data: sitesData } = useApi(getListSites);

  // Fetch active saved searches count
  const { data: savedSearchesCount, loading: savedSearchesLoading } = useApi(
    getActiveSavedSearchesCount
  );

  // Unified refetch that tries Firestore first
  const handleRefresh = useCallback(() => {
    if (firestoreStatsError) {
      refetchLegacyStats();
    } else {
      refetchFirestoreStats();
    }
    toast.success("Dashboard refreshed");
  }, [firestoreStatsError, refetchFirestoreStats, refetchLegacyStats]);

  const totalProperties = stats?.total_properties || 0;
  const forSaleCount = stats?.for_sale_count || stats?.by_status?.for_sale || 0;
  const forRentCount = stats?.for_rent_count || stats?.by_status?.for_rent || 0;
  const avgPriceForSale = stats?.avg_price_for_sale || stats?.avg_price || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
              Dashboard
            </h1>
            <p className="text-slate-400 text-sm sm:text-base max-w-2xl">
              Monitor your real estate data, system health, and scraping
              activity in real-time.
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-white transition-colors disabled:opacity-50"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Properties"
            value={totalProperties.toLocaleString()}
            icon={Home}
            loading={dashboardLoading}
            variant="info"
            description="In database"
          />
          <StatsCard
            title="For Sale"
            value={forSaleCount.toLocaleString()}
            icon={TrendingUp}
            loading={dashboardLoading}
            variant="success"
            description={`Avg: ₦${(avgPriceForSale / 1000000).toFixed(1)}M`}
          />
          <StatsCard
            title="For Rent"
            value={forRentCount.toLocaleString()}
            icon={Home}
            loading={dashboardLoading}
            variant="default"
            description="Rental listings"
          />
          <StatsCard
            title="Saved Searches"
            value={savedSearchesCount ?? 0}
            icon={Search}
            loading={savedSearchesLoading || dashboardLoading}
            variant="default"
            description="Active alerts"
          />
        </div>

        {/* System Status Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* API Health */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                {health?.status === "healthy" ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-400" />
                )}
                <div>
                  <p className="text-sm font-semibold text-white">API Server</p>
                  <p className="text-xs text-slate-400">Backend service</p>
                </div>
              </div>
              <StatusBadge
                status={health?.status === "healthy" ? "healthy" : "error"}
                label={health?.status || "Unknown"}
              />
            </div>
          </div>

          {/* Scraper Status */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                {scrapeStatus?.is_running ? (
                  <Activity className="w-5 h-5 text-blue-400 animate-pulse" />
                ) : (
                  <Clock className="w-5 h-5 text-slate-400" />
                )}
                <div>
                  <p className="text-sm font-semibold text-white">Scraper</p>
                  <p className="text-xs text-slate-400">
                    {scrapeStatus?.is_running
                      ? "Currently running"
                      : "Ready to scrape"}
                  </p>
                </div>
              </div>
              <StatusBadge
                status={scrapeStatus?.is_running ? "running" : "idle"}
                label={scrapeStatus?.is_running ? "Active" : "Idle"}
              />
            </div>
          </div>

          {/* Data Sources */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <Database className="w-5 h-5 text-purple-400" />
                <div>
                  <p className="text-sm font-semibold text-white">
                    Data Sources
                  </p>
                  <p className="text-xs text-slate-400">Enabled sites</p>
                </div>
              </div>
              <StatusBadge
                status="healthy"
                label={`${sitesData?.enabled || 0} Active`}
              />
            </div>
          </div>
        </div>

        {/* Scrape Status & History */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
          <div className="p-5 border-b border-slate-700">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Scrape Activity
              </h2>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="text-sm text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
              >
                {showHistory ? (
                  <>
                    Hide History <ChevronUp className="w-4 h-4" />
                  </>
                ) : (
                  <>
                    Show History <ChevronDown className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Current/Last Run */}
          <div className="p-5">
            {scrapeStatus?.last_run && (
              <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {scrapeStatus.last_run.success ? (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-400" />
                    )}
                    <div>
                      <p
                        className={`font-medium ${
                          scrapeStatus.last_run.success
                            ? "text-green-300"
                            : "text-red-300"
                        }`}
                      >
                        Last scrape{" "}
                        {scrapeStatus.last_run.success
                          ? "completed successfully"
                          : "failed"}
                      </p>
                      <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(
                          scrapeStatus.last_run.completed_at
                        ).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-slate-400 text-xs">Sites</p>
                    <p className="text-white font-semibold">
                      {scrapeStatus.last_run.sites?.length || 0}
                    </p>
                  </div>
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-slate-400 text-xs">Completed</p>
                    <p className="text-white font-semibold">
                      {scrapeStatus.last_run.progress?.completed_sites || 0}
                    </p>
                  </div>
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-slate-400 text-xs">Duration</p>
                    <p className="text-white font-semibold">
                      {scrapeStatus.last_run.timing?.elapsed_seconds || 0}s
                    </p>
                  </div>
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-slate-400 text-xs">CPU Usage</p>
                    <p className="text-white font-semibold">
                      {scrapeStatus.last_run.resources?.cpu_percent || 0}%
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* History Table */}
            {showHistory && scrapeHistory?.scrapes && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-slate-400 border-b border-slate-700">
                      <th className="pb-3 font-medium">Start Time</th>
                      <th className="pb-3 font-medium hidden sm:table-cell">
                        Sites
                      </th>
                      <th className="pb-3 font-medium">Listings</th>
                      <th className="pb-3 font-medium">Status</th>
                      <th className="pb-3 font-medium hidden md:table-cell">
                        Duration
                      </th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-300">
                    {scrapeHistory.scrapes.map((item) => (
                      <tr key={item.id} className="border-b border-slate-800">
                        <td className="py-3">
                          {new Date(item.start_time).toLocaleString()}
                        </td>
                        <td className="py-3 hidden sm:table-cell">
                          {item.sites?.join(", ")}
                        </td>
                        <td className="py-3">{item.total_listings}</td>
                        <td className="py-3">
                          <StatusBadge
                            status={
                              item.status === "completed"
                                ? "healthy"
                                : item.status === "partial"
                                ? "warning"
                                : "error"
                            }
                            label={item.status}
                          />
                        </td>
                        <td className="py-3 hidden md:table-cell">
                          {item.duration_seconds}s
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Recent Properties */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <Home className="w-5 h-5" />
            Recent Properties
          </h2>
          {propertiesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 animate-pulse"
                >
                  <div className="h-6 bg-slate-700 rounded mb-2" />
                  <div className="h-4 bg-slate-700 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : Array.isArray(recentProperties) && recentProperties.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentProperties.map((property: Property, idx: number) => (
                <PropertyCard key={property.id ?? idx} property={property} />
              ))}
            </div>
          ) : (
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 text-center">
              <AlertCircle className="w-12 h-12 text-yellow-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-2">
                No Properties Yet
              </h3>
              <p className="text-slate-400 mb-4">
                Start by running a scrape to collect property data.
              </p>
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors">
                Start Scraping
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
