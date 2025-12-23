/**
 * TypeScript API Client for Nigerian Real Estate API
 * Complete typed client for all 67 endpoints
 */

import type {
  ApiResponse,
  Property,
  Site,
  SiteStats,
  ScrapeRequest,
  ScrapeStatus,
  ScrapeHistory,
  OverviewStats,
  TrendStats,
  SearchParams,
  PropertyQuery,
  QueryResult,
  SavedSearch,
  SavedSearchStats,
  PriceHistory,
  PriceDrop,
  MarketTrends,
  LocationFilter,
  LocationStats,
  HealthCheck,
  SiteHealth,
  HealthAlert,
  ExportRequest,
  ExportJob,
  GitHubWorkflowRun,
  GitHubArtifact,
  ScheduleJob,
  EmailConfig,
  EmailRecipient,
  URLValidation,
  DuplicateDetection,
  QualityScore,
  LogResponse,
} from './types';

/**
 * API Client Configuration
 */
export interface ApiClientConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
  headers?: Record<string, string>;
}

/**
 * Main API Client Class
 */
export class RealEstateApiClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;
  private headers: Record<string, string>;

  constructor(config: ApiClientConfig = {}) {
    this.baseUrl = config.baseUrl || 'http://localhost:5000/api';
    this.apiKey = config.apiKey;
    this.timeout = config.timeout || 30000;
    this.headers = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    if (this.apiKey) {
      this.headers['X-API-Key'] = this.apiKey;
    }
  }

  /**
   * Generic request method
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: any,
    queryParams?: Record<string, any>
  ): Promise<T> {
    let url = `${this.baseUrl}${endpoint}`;

    // Add query parameters
    if (queryParams) {
      const params = new URLSearchParams();
      Object.entries(queryParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    const options: RequestInit = {
      method,
      headers: this.headers,
      signal: AbortSignal.timeout(this.timeout),
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      }

      // For file downloads or non-JSON responses
      return response as any;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unknown error occurred');
    }
  }

  // ============================================================================
  // Health & Monitoring
  // ============================================================================

  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>('GET', '/health');
  }

  async overallHealth(): Promise<any> {
    return this.request('GET', '/health/overall');
  }

  async siteHealth(siteKey: string): Promise<SiteHealth> {
    return this.request<SiteHealth>('GET', `/health/sites/${siteKey}`);
  }

  async healthAlerts(): Promise<HealthAlert[]> {
    return this.request<HealthAlert[]>('GET', '/health/alerts');
  }

  async topPerformers(): Promise<SiteStats[]> {
    return this.request<SiteStats[]>('GET', '/health/top-performers');
  }

  // ============================================================================
  // Scraping Operations
  // ============================================================================

  async startScrape(request: ScrapeRequest = {}): Promise<{ message: string; job_id?: string }> {
    return this.request('POST', '/scrape/start', request);
  }

  async getScrapeStatus(): Promise<ScrapeStatus> {
    return this.request<ScrapeStatus>('GET', '/scrape/status');
  }

  async stopScrape(): Promise<{ message: string }> {
    return this.request('POST', '/scrape/stop');
  }

  async getScrapeHistory(limit?: number): Promise<ScrapeHistory> {
    return this.request<ScrapeHistory>('GET', '/scrape/history', undefined, { limit });
  }

  // ============================================================================
  // Sites Management
  // ============================================================================

  async listSites(): Promise<{ sites: Site[]; total: number; enabled: number; disabled: number }> {
    return this.request('GET', '/sites');
  }

  async getSite(siteKey: string): Promise<Site> {
    return this.request<Site>('GET', `/sites/${siteKey}`);
  }

  async createSite(site: Partial<Site>): Promise<{ message: string; site_key: string }> {
    return this.request('POST', '/sites', site);
  }

  async updateSite(siteKey: string, updates: Partial<Site>): Promise<{ message: string }> {
    return this.request('PUT', `/sites/${siteKey}`, updates);
  }

  async deleteSite(siteKey: string): Promise<{ message: string }> {
    return this.request('DELETE', `/sites/${siteKey}`);
  }

  async toggleSite(siteKey: string, enabled: boolean): Promise<{ message: string; enabled: boolean }> {
    return this.request('PATCH', `/sites/${siteKey}/toggle`, { enabled });
  }

  // ============================================================================
  // Data Access
  // ============================================================================

  async getAllData(params?: { limit?: number; offset?: number }): Promise<QueryResult> {
    return this.request<QueryResult>('GET', '/data/sites', undefined, params);
  }

  async getSiteData(siteKey: string, params?: { limit?: number; offset?: number }): Promise<QueryResult> {
    return this.request<QueryResult>('GET', `/data/sites/${siteKey}`, undefined, params);
  }

  async getMasterData(params?: { limit?: number; offset?: number }): Promise<QueryResult> {
    return this.request<QueryResult>('GET', '/data/master', undefined, params);
  }

  async searchData(searchParams: SearchParams): Promise<QueryResult> {
    return this.request<QueryResult>('GET', '/data/search', undefined, searchParams);
  }

  // ============================================================================
  // Statistics
  // ============================================================================

  async getOverviewStats(): Promise<OverviewStats> {
    return this.request<OverviewStats>('GET', '/stats/overview');
  }

  async getSiteStats(): Promise<SiteStats[]> {
    return this.request<SiteStats[]>('GET', '/stats/sites');
  }

  async getTrendStats(days?: number): Promise<TrendStats> {
    return this.request<TrendStats>('GET', '/stats/trends', undefined, { days });
  }

  // ============================================================================
  // Logs
  // ============================================================================

  async getLogs(params?: { limit?: number; level?: string }): Promise<LogResponse> {
    return this.request<LogResponse>('GET', '/logs', undefined, params);
  }

  async getErrorLogs(limit?: number): Promise<LogResponse> {
    return this.request<LogResponse>('GET', '/logs/errors', undefined, { limit });
  }

  async getSiteLogs(siteKey: string, limit?: number): Promise<LogResponse> {
    return this.request<LogResponse>('GET', `/logs/site/${siteKey}`, undefined, { limit });
  }

  // ============================================================================
  // URL Validation
  // ============================================================================

  async validateUrl(url: string): Promise<URLValidation> {
    return this.request<URLValidation>('POST', '/validate/url', { url });
  }

  async validateUrls(urls: string[]): Promise<URLValidation[]> {
    return this.request<URLValidation[]>('POST', '/validate/urls', { urls });
  }

  // ============================================================================
  // Location Filter
  // ============================================================================

  async filterByLocation(listings: Property[]): Promise<Property[]> {
    return this.request<Property[]>('POST', '/filter/location', { listings });
  }

  async getLocationStats(): Promise<LocationStats> {
    return this.request<LocationStats>('GET', '/filter/stats');
  }

  async getLocationConfig(): Promise<LocationFilter> {
    return this.request<LocationFilter>('GET', '/config/locations');
  }

  async updateLocationConfig(config: LocationFilter): Promise<{ message: string }> {
    return this.request('PUT', '/config/locations', config);
  }

  // ============================================================================
  // Property Query Engine
  // ============================================================================

  async queryProperties(query: PropertyQuery): Promise<QueryResult> {
    return this.request<QueryResult>('POST', '/query', query);
  }

  async getQuerySummary(query: PropertyQuery): Promise<any> {
    return this.request('POST', '/query/summary', query);
  }

  // ============================================================================
  // Rate Limiting
  // ============================================================================

  async getRateLimitStatus(): Promise<any> {
    return this.request('GET', '/rate-limit/status');
  }

  async checkRateLimit(action: string): Promise<{ allowed: boolean; retry_after?: number }> {
    return this.request('POST', '/rate-limit/check', { action });
  }

  // ============================================================================
  // Price Intelligence
  // ============================================================================

  async getPriceHistory(propertyId: string): Promise<PriceHistory> {
    return this.request<PriceHistory>('GET', `/price-history/${propertyId}`);
  }

  async getPriceDrops(params?: { min_drop_percentage?: number; days?: number }): Promise<PriceDrop[]> {
    return this.request<PriceDrop[]>('GET', '/price-drops', undefined, params);
  }

  async getStaleListings(days?: number): Promise<Property[]> {
    return this.request<Property[]>('GET', '/stale-listings', undefined, { days });
  }

  async getMarketTrends(): Promise<MarketTrends> {
    return this.request<MarketTrends>('GET', '/market-trends');
  }

  // ============================================================================
  // Natural Language Search
  // ============================================================================

  async naturalLanguageSearch(query: string): Promise<QueryResult> {
    return this.request<QueryResult>('POST', '/search/natural', { query });
  }

  async getSearchSuggestions(partial: string): Promise<string[]> {
    return this.request<string[]>('GET', '/search/suggestions', undefined, { q: partial });
  }

  // ============================================================================
  // Saved Searches
  // ============================================================================

  async listSavedSearches(): Promise<SavedSearch[]> {
    return this.request<SavedSearch[]>('GET', '/searches');
  }

  async createSavedSearch(search: Omit<SavedSearch, 'id' | 'created_at'>): Promise<{ id: string; message: string }> {
    return this.request('POST', '/searches', search);
  }

  async getSavedSearch(searchId: string): Promise<SavedSearch> {
    return this.request<SavedSearch>('GET', `/searches/${searchId}`);
  }

  async updateSavedSearch(searchId: string, updates: Partial<SavedSearch>): Promise<{ message: string }> {
    return this.request('PUT', `/searches/${searchId}`, updates);
  }

  async deleteSavedSearch(searchId: string): Promise<{ message: string }> {
    return this.request('DELETE', `/searches/${searchId}`);
  }

  async getSavedSearchStats(searchId: string): Promise<SavedSearchStats> {
    return this.request<SavedSearchStats>('GET', `/searches/${searchId}/stats`);
  }

  // ============================================================================
  // Duplicate Detection & Quality
  // ============================================================================

  async detectDuplicates(listings: Property[]): Promise<DuplicateDetection> {
    return this.request<DuplicateDetection>('POST', '/duplicates/detect', { listings });
  }

  async scoreQuality(listing: Property): Promise<QualityScore> {
    return this.request<QualityScore>('POST', '/quality/score', { listing });
  }

  // ============================================================================
  // Firestore Integration
  // ============================================================================

  async queryFirestore(query: any): Promise<Property[]> {
    return this.request<Property[]>('POST', '/firestore/query', query);
  }

  async queryFirestoreArchive(query: any): Promise<Property[]> {
    return this.request<Property[]>('POST', '/firestore/query-archive', query);
  }

  async exportToFirestore(listings: Property[]): Promise<{ message: string; exported: number }> {
    return this.request('POST', '/firestore/export', { listings });
  }

  // ============================================================================
  // Export Management
  // ============================================================================

  async generateExport(request: ExportRequest): Promise<ExportJob> {
    return this.request<ExportJob>('POST', '/export/generate', request);
  }

  async downloadExport(filename: string): Promise<Response> {
    return this.request<Response>('GET', `/export/download/${filename}`);
  }

  async getExportFormats(): Promise<string[]> {
    return this.request<string[]>('GET', '/export/formats');
  }

  // ============================================================================
  // GitHub Actions
  // ============================================================================

  async triggerGitHubScrape(sites?: string[]): Promise<{ message: string; run_id?: number }> {
    return this.request('POST', '/github/trigger-scrape', { sites });
  }

  async estimateScrapeTime(sites?: string[]): Promise<{ estimated_minutes: number }> {
    return this.request('POST', '/github/estimate-scrape-time', { sites });
  }

  async subscribeToWorkflow(email: string, runId: number): Promise<{ message: string }> {
    return this.request('POST', '/notifications/subscribe', { email, run_id: runId });
  }

  async getWorkflowStatus(runId: number): Promise<GitHubWorkflowRun> {
    return this.request<GitHubWorkflowRun>('GET', `/notifications/workflow-status/${runId}`);
  }

  async listWorkflowRuns(limit?: number): Promise<GitHubWorkflowRun[]> {
    return this.request<GitHubWorkflowRun[]>('GET', '/github/workflow-runs', undefined, { limit });
  }

  async listArtifacts(runId?: number): Promise<GitHubArtifact[]> {
    return this.request<GitHubArtifact[]>('GET', '/github/artifacts', undefined, { run_id: runId });
  }

  async downloadArtifact(artifactId: number): Promise<Response> {
    return this.request<Response>('GET', `/github/artifact/${artifactId}/download`);
  }

  // ============================================================================
  // Scheduling
  // ============================================================================

  async scheduleScrape(scheduleTime: string, sites?: string[], maxPages?: number): Promise<{ job_id: number }> {
    return this.request('POST', '/schedule/scrape', { schedule_time: scheduleTime, sites, max_pages: maxPages });
  }

  async listScheduledJobs(): Promise<ScheduleJob[]> {
    return this.request<ScheduleJob[]>('GET', '/schedule/jobs');
  }

  async getScheduledJob(jobId: number): Promise<ScheduleJob> {
    return this.request<ScheduleJob>('GET', `/schedule/jobs/${jobId}`);
  }

  async cancelScheduledJob(jobId: number): Promise<{ message: string }> {
    return this.request('POST', `/schedule/jobs/${jobId}/cancel`);
  }

  // ============================================================================
  // Email Notifications
  // ============================================================================

  async configureEmail(config: EmailConfig): Promise<{ message: string }> {
    return this.request('POST', '/email/configure', config);
  }

  async testEmailConnection(config: EmailConfig): Promise<{ success: boolean; error?: string }> {
    return this.request('POST', '/email/test-connection', config);
  }

  async getEmailConfig(): Promise<EmailConfig> {
    return this.request<EmailConfig>('GET', '/email/config');
  }

  async listEmailRecipients(): Promise<EmailRecipient[]> {
    return this.request<EmailRecipient[]>('GET', '/email/recipients');
  }

  async addEmailRecipient(recipient: EmailRecipient): Promise<{ message: string }> {
    return this.request('POST', '/email/recipients', recipient);
  }

  async removeEmailRecipient(email: string): Promise<{ message: string }> {
    return this.request('DELETE', `/email/recipients/${email}`);
  }

  async sendTestEmail(to: string): Promise<{ success: boolean; error?: string }> {
    return this.request('POST', '/email/send-test', { to });
  }
}

/**
 * Create a singleton instance for convenience
 */
export const apiClient = new RealEstateApiClient();

/**
 * Export default for easy importing
 */
export default RealEstateApiClient;
