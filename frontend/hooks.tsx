/**
 * React Hooks for Nigerian Real Estate API
 * Ready-to-use hooks with SWR for data fetching, caching, and revalidation
 */

import useSWR, { mutate } from 'swr';
import { apiClient, RealEstateApiClient } from './api-client';
import type {
  Property,
  Site,
  SiteStats,
  ScrapeStatus,
  ScrapeHistory,
  OverviewStats,
  TrendStats,
  QueryResult,
  SavedSearch,
  HealthCheck,
  LogResponse,
  MarketTrends,
  ScrapeRequest,
} from './types';

/**
 * Configuration hook
 */
export function useApiClient(config?: ConstructorParameters<typeof RealEstateApiClient>[0]) {
  return config ? new RealEstateApiClient(config) : apiClient;
}

// ============================================================================
// Health & Status Hooks
// ============================================================================

export function useHealth() {
  const { data, error, isLoading } = useSWR('/health', () => apiClient.healthCheck());

  return {
    health: data,
    isHealthy: data?.status === 'healthy',
    error,
    isLoading,
  };
}

export function useOverviewStats() {
  const { data, error, isLoading } = useSWR<OverviewStats>(
    '/stats/overview',
    () => apiClient.getOverviewStats(),
    { refreshInterval: 60000 } // Refresh every minute
  );

  return {
    stats: data,
    error,
    isLoading,
  };
}

// ============================================================================
// Scraping Hooks
// ============================================================================

export function useScrapeStatus() {
  const { data, error, isLoading } = useSWR<ScrapeStatus>(
    '/scrape/status',
    () => apiClient.getScrapeStatus(),
    {
      refreshInterval: 2000, // Poll every 2 seconds during scraping
      revalidateOnFocus: true,
    }
  );

  const startScrape = async (request: ScrapeRequest = {}) => {
    const result = await apiClient.startScrape(request);
    mutate('/scrape/status'); // Revalidate status
    return result;
  };

  const stopScrape = async () => {
    const result = await apiClient.stopScrape();
    mutate('/scrape/status'); // Revalidate status
    return result;
  };

  return {
    status: data,
    isRunning: data?.status === 'running',
    progress: data?.progress_percentage || 0,
    error,
    isLoading,
    startScrape,
    stopScrape,
  };
}

export function useScrapeHistory(limit = 10) {
  const { data, error, isLoading } = useSWR<ScrapeHistory>(
    `/scrape/history?limit=${limit}`,
    () => apiClient.getScrapeHistory(limit)
  );

  return {
    history: data,
    scrapes: data?.scrapes || [],
    error,
    isLoading,
  };
}

// ============================================================================
// Sites Management Hooks
// ============================================================================

export function useSites() {
  const { data, error, isLoading } = useSWR(
    '/sites',
    () => apiClient.listSites(),
    { revalidateOnFocus: true }
  );

  const toggleSite = async (siteKey: string, enabled: boolean) => {
    await apiClient.toggleSite(siteKey, enabled);
    mutate('/sites'); // Revalidate sites list
  };

  const updateSite = async (siteKey: string, updates: Partial<Site>) => {
    await apiClient.updateSite(siteKey, updates);
    mutate('/sites');
    mutate(`/sites/${siteKey}`);
  };

  const deleteSite = async (siteKey: string) => {
    await apiClient.deleteSite(siteKey);
    mutate('/sites');
  };

  return {
    sites: data?.sites || [],
    total: data?.total || 0,
    enabled: data?.enabled || 0,
    disabled: data?.disabled || 0,
    error,
    isLoading,
    toggleSite,
    updateSite,
    deleteSite,
  };
}

export function useSite(siteKey: string) {
  const { data, error, isLoading } = useSWR<Site>(
    siteKey ? `/sites/${siteKey}` : null,
    () => apiClient.getSite(siteKey)
  );

  return {
    site: data,
    error,
    isLoading,
  };
}

export function useSiteStats() {
  const { data, error, isLoading } = useSWR<SiteStats[]>(
    '/stats/sites',
    () => apiClient.getSiteStats(),
    { refreshInterval: 300000 } // Refresh every 5 minutes
  );

  return {
    stats: data || [],
    error,
    isLoading,
  };
}

// ============================================================================
// Data & Search Hooks
// ============================================================================

export function useProperties(siteKey?: string, params?: { limit?: number; offset?: number }) {
  const key = siteKey
    ? `/data/sites/${siteKey}${params ? '?' + new URLSearchParams(params as any).toString() : ''}`
    : `/data/sites${params ? '?' + new URLSearchParams(params as any).toString() : ''}`;

  const { data, error, isLoading } = useSWR<QueryResult>(
    key,
    () => siteKey ? apiClient.getSiteData(siteKey, params) : apiClient.getAllData(params)
  );

  return {
    properties: data?.properties || [],
    total: data?.total || 0,
    hasMore: data?.has_more || false,
    error,
    isLoading,
  };
}

export function useSearch(query: string, enabled = true) {
  const { data, error, isLoading } = useSWR<QueryResult>(
    enabled && query ? `/data/search?query=${encodeURIComponent(query)}` : null,
    () => apiClient.searchData({ query })
  );

  return {
    results: data?.properties || [],
    total: data?.total || 0,
    error,
    isLoading,
  };
}

export function useNaturalLanguageSearch(query: string, enabled = true) {
  const { data, error, isLoading } = useSWR<QueryResult>(
    enabled && query ? `/search/natural?q=${encodeURIComponent(query)}` : null,
    () => apiClient.naturalLanguageSearch(query),
    { revalidateOnFocus: false } // Don't auto-refresh search results
  );

  return {
    results: data?.properties || [],
    total: data?.total || 0,
    error,
    isLoading,
  };
}

// ============================================================================
// Saved Searches Hooks
// ============================================================================

export function useSavedSearches() {
  const { data, error, isLoading } = useSWR<SavedSearch[]>(
    '/searches',
    () => apiClient.listSavedSearches()
  );

  const createSearch = async (search: Omit<SavedSearch, 'id' | 'created_at'>) => {
    const result = await apiClient.createSavedSearch(search);
    mutate('/searches');
    return result;
  };

  const deleteSearch = async (searchId: string) => {
    await apiClient.deleteSavedSearch(searchId);
    mutate('/searches');
  };

  return {
    searches: data || [],
    error,
    isLoading,
    createSearch,
    deleteSearch,
  };
}

export function useSavedSearch(searchId: string) {
  const { data, error, isLoading } = useSWR<SavedSearch>(
    searchId ? `/searches/${searchId}` : null,
    () => apiClient.getSavedSearch(searchId)
  );

  const updateSearch = async (updates: Partial<SavedSearch>) => {
    await apiClient.updateSavedSearch(searchId, updates);
    mutate(`/searches/${searchId}`);
    mutate('/searches');
  };

  return {
    search: data,
    error,
    isLoading,
    updateSearch,
  };
}

// ============================================================================
// Price Intelligence Hooks
// ============================================================================

export function useMarketTrends() {
  const { data, error, isLoading } = useSWR<MarketTrends>(
    '/market-trends',
    () => apiClient.getMarketTrends(),
    { refreshInterval: 3600000 } // Refresh every hour
  );

  return {
    trends: data,
    error,
    isLoading,
  };
}

export function usePriceDrops(minDropPercentage = 10, days = 30) {
  const { data, error, isLoading } = useSWR(
    `/price-drops?min_drop_percentage=${minDropPercentage}&days=${days}`,
    () => apiClient.getPriceDrops({ min_drop_percentage: minDropPercentage, days }),
    { refreshInterval: 3600000 }
  );

  return {
    priceDrops: data || [],
    error,
    isLoading,
  };
}

export function usePriceHistory(propertyId: string) {
  const { data, error, isLoading } = useSWR(
    propertyId ? `/price-history/${propertyId}` : null,
    () => apiClient.getPriceHistory(propertyId)
  );

  return {
    history: data,
    error,
    isLoading,
  };
}

// ============================================================================
// Statistics & Trends Hooks
// ============================================================================

export function useTrendStats(days = 30) {
  const { data, error, isLoading } = useSWR<TrendStats>(
    `/stats/trends?days=${days}`,
    () => apiClient.getTrendStats(days),
    { refreshInterval: 300000 }
  );

  return {
    trends: data,
    error,
    isLoading,
  };
}

// ============================================================================
// Logs Hooks
// ============================================================================

export function useLogs(params?: { limit?: number; level?: string }) {
  const key = `/logs${params ? '?' + new URLSearchParams(params as any).toString() : ''}`;
  const { data, error, isLoading } = useSWR<LogResponse>(
    key,
    () => apiClient.getLogs(params),
    { refreshInterval: 10000 } // Refresh every 10 seconds
  );

  return {
    logs: data?.logs || [],
    total: data?.total || 0,
    error,
    isLoading,
  };
}

export function useErrorLogs(limit = 50) {
  const { data, error, isLoading } = useSWR<LogResponse>(
    `/logs/errors?limit=${limit}`,
    () => apiClient.getErrorLogs(limit),
    { refreshInterval: 10000 }
  );

  return {
    logs: data?.logs || [],
    total: data?.total || 0,
    error,
    isLoading,
  };
}

// ============================================================================
// Email Configuration Hooks
// ============================================================================

export function useEmailRecipients() {
  const { data, error, isLoading } = useSWR(
    '/email/recipients',
    () => apiClient.listEmailRecipients()
  );

  const addRecipient = async (recipient: any) => {
    await apiClient.addEmailRecipient(recipient);
    mutate('/email/recipients');
  };

  const removeRecipient = async (email: string) => {
    await apiClient.removeEmailRecipient(email);
    mutate('/email/recipients');
  };

  return {
    recipients: data || [],
    error,
    isLoading,
    addRecipient,
    removeRecipient,
  };
}

// ============================================================================
// GitHub Actions Hooks
// ============================================================================

export function useWorkflowRuns(limit = 10) {
  const { data, error, isLoading } = useSWR(
    `/github/workflow-runs?limit=${limit}`,
    () => apiClient.listWorkflowRuns(limit),
    { refreshInterval: 30000 } // Refresh every 30 seconds
  );

  const triggerScrape = async (sites?: string[]) => {
    const result = await apiClient.triggerGitHubScrape(sites);
    mutate(`/github/workflow-runs?limit=${limit}`);
    return result;
  };

  return {
    runs: data || [],
    error,
    isLoading,
    triggerScrape,
  };
}

// ============================================================================
// Scheduling Hooks
// ============================================================================

export function useScheduledJobs() {
  const { data, error, isLoading } = useSWR(
    '/schedule/jobs',
    () => apiClient.listScheduledJobs(),
    { refreshInterval: 30000 }
  );

  const scheduleJob = async (scheduleTime: string, sites?: string[], maxPages?: number) => {
    const result = await apiClient.scheduleScrape(scheduleTime, sites, maxPages);
    mutate('/schedule/jobs');
    return result;
  };

  const cancelJob = async (jobId: number) => {
    await apiClient.cancelScheduledJob(jobId);
    mutate('/schedule/jobs');
  };

  return {
    jobs: data || [],
    error,
    isLoading,
    scheduleJob,
    cancelJob,
  };
}

// ============================================================================
// Export Hooks
// ============================================================================

export function useExportFormats() {
  const { data, error, isLoading } = useSWR(
    '/export/formats',
    () => apiClient.getExportFormats()
  );

  const generateExport = async (request: any) => {
    return await apiClient.generateExport(request);
  };

  return {
    formats: data || [],
    error,
    isLoading,
    generateExport,
  };
}
