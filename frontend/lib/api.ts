/**
 * TypeScript API Client for Nigerian Real Estate API
 * Complete typed client for all 90 endpoints (68 legacy + 16 Firestore + 6 other)
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
  GitHubWorkflowLogsResponse,
  ScheduleJob,
  EmailConfig,
  EmailRecipient,
  URLValidation,
  DuplicateDetection,
  QualityScore,
  LogResponse,
  // NEW: Firestore Enterprise Types (v3.1)
  FirestoreProperty,
  FirestoreResponse,
  FirestoreDashboardStats,
  FirestoreListResponse,
  FirestoreSearchRequest,
  FirestoreSiteStats,
  PropertyData,
} from "./types";

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
    this.baseUrl =
      config.baseUrl ||
      process.env.NEXT_PUBLIC_API_URL ||
      "https://realtors-practice-api.onrender.com/api";
    this.apiKey = config.apiKey;
    this.timeout = config.timeout || 120000; // 120 seconds for cold starts from Render
    this.headers = {
      "Content-Type": "application/json",
      ...config.headers,
    };

    if (this.apiKey) {
      this.headers["X-API-Key"] = this.apiKey;
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

    if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage =
          errorData.error ||
          errorData.message ||
          `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
      }

      const contentType = response.headers.get("content-type");
      if (contentType?.includes("application/json")) {
        return await response.json();
      }

      // For file downloads or non-JSON responses
      return response as any;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("An unknown error occurred");
    }
  }

  // ============================================================================
  // Health & Monitoring
  // ============================================================================

  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>("GET", "/health");
  }

  async overallHealth(): Promise<any> {
    return this.request("GET", "/health/overall");
  }

  async siteHealth(siteKey: string): Promise<SiteHealth> {
    return this.request<SiteHealth>("GET", `/health/sites/${siteKey}`);
  }

  async healthAlerts(): Promise<HealthAlert[]> {
    return this.request<HealthAlert[]>("GET", "/health/alerts");
  }

  async topPerformers(): Promise<SiteStats[]> {
    return this.request<SiteStats[]>("GET", "/health/top-performers");
  }

  // ============================================================================
  // Scraping Operations
  // ============================================================================

  async startScrape(
    request: ScrapeRequest = {}
  ): Promise<{ message: string; job_id?: string }> {
    return this.request("POST", "/scrape/start", request);
  }

  async getScrapeStatus(): Promise<ScrapeStatus> {
    return this.request<ScrapeStatus>("GET", "/scrape/status");
  }

  async stopScrape(): Promise<{ message: string }> {
    return this.request("POST", "/scrape/stop");
  }

  async getScrapeHistory(limit?: number): Promise<ScrapeHistory> {
    return this.request<ScrapeHistory>("GET", "/scrape/history", undefined, {
      limit,
    });
  }

  // ============================================================================
  // Sites Management
  // ============================================================================

  async listSites(): Promise<{
    sites: Site[];
    total: number;
    enabled: number;
    disabled: number;
  }> {
    return this.request("GET", "/sites");
  }

  async getSite(siteKey: string): Promise<Site> {
    return this.request<Site>("GET", `/sites/${siteKey}`);
  }

  async createSite(
    site: Partial<Site>
  ): Promise<{ message: string; site_key: string }> {
    return this.request("POST", "/sites", site);
  }

  async updateSite(
    siteKey: string,
    updates: Partial<Site>
  ): Promise<{ message: string }> {
    return this.request("PUT", `/sites/${siteKey}`, updates);
  }

  async deleteSite(siteKey: string): Promise<{ message: string }> {
    return this.request("DELETE", `/sites/${siteKey}`);
  }

  async toggleSite(siteKey: string): Promise<{
    success: boolean;
    site_key: string;
    enabled: boolean;
    message: string;
  }> {
    return this.request("PATCH", `/sites/${siteKey}/toggle`);
  }

  // ============================================================================
  // Data Access
  // ============================================================================

  async getAvailableData(): Promise<any> {
    return this.request("GET", "/data/sites");
  }

  async getAllData(params?: {
    limit?: number;
    offset?: number;
  }): Promise<QueryResult> {
    return this.request<QueryResult>("GET", "/data/sites", undefined, params);
  }

  async getSiteData(
    siteKey: string,
    params?: { limit?: number; offset?: number }
  ): Promise<QueryResult> {
    return this.request<QueryResult>(
      "GET",
      `/data/sites/${siteKey}`,
      undefined,
      params
    );
  }

  async getMasterData(params?: {
    limit?: number;
    offset?: number;
  }): Promise<QueryResult> {
    return this.request<QueryResult>("GET", "/data/master", undefined, params);
  }

  async searchData(searchParams: SearchParams): Promise<QueryResult> {
    return this.request<QueryResult>(
      "GET",
      "/data/search",
      undefined,
      searchParams
    );
  }

  // ============================================================================
  // Statistics
  // ============================================================================

  async getOverviewStats(): Promise<OverviewStats> {
    return this.request<OverviewStats>("GET", "/stats/overview");
  }

  async getSiteStats(): Promise<SiteStats[]> {
    return this.request<SiteStats[]>("GET", "/stats/sites");
  }

  async getTrendStats(days?: number): Promise<TrendStats> {
    return this.request<TrendStats>("GET", "/stats/trends", undefined, {
      days,
    });
  }

  // ============================================================================
  // Logs
  // ============================================================================

  async getLogs(params?: {
    limit?: number;
    level?: string;
  }): Promise<LogResponse> {
    return this.request<LogResponse>("GET", "/logs", undefined, params);
  }

  async getErrorLogs(limit?: number): Promise<LogResponse> {
    return this.request<LogResponse>("GET", "/logs/errors", undefined, {
      limit,
    });
  }

  async getSiteLogs(siteKey: string, limit?: number): Promise<LogResponse> {
    return this.request<LogResponse>(
      "GET",
      `/logs/site/${siteKey}`,
      undefined,
      { limit }
    );
  }

  // ============================================================================
  // URL Validation
  // ============================================================================

  async validateUrl(url: string): Promise<URLValidation> {
    return this.request<URLValidation>("POST", "/validate/url", { url });
  }

  async validateUrls(urls: string[]): Promise<URLValidation[]> {
    return this.request<URLValidation[]>("POST", "/validate/urls", { urls });
  }

  // ============================================================================
  // Location Filter
  // ============================================================================

  async filterByLocation(listings: Property[]): Promise<Property[]> {
    return this.request<Property[]>("POST", "/filter/location", { listings });
  }

  async getLocationStats(): Promise<LocationStats> {
    return this.request<LocationStats>("GET", "/filter/stats");
  }

  async getLocationConfig(): Promise<LocationFilter> {
    return this.request<LocationFilter>("GET", "/config/locations");
  }

  async updateLocationConfig(
    config: LocationFilter
  ): Promise<{ message: string }> {
    return this.request("PUT", "/config/locations", config);
  }

  // ============================================================================
  // Property Query Engine
  // ============================================================================

  async queryProperties(query: PropertyQuery): Promise<QueryResult> {
    return this.request<QueryResult>("POST", "/query", query);
  }

  async getQuerySummary(query: PropertyQuery): Promise<any> {
    return this.request("POST", "/query/summary", query);
  }

  // ============================================================================
  // Rate Limiting
  // ============================================================================

  async getRateLimitStatus(): Promise<any> {
    return this.request("GET", "/rate-limit/status");
  }

  async checkRateLimit(
    action: string
  ): Promise<{ allowed: boolean; retry_after?: number }> {
    return this.request("POST", "/rate-limit/check", { action });
  }

  // ============================================================================
  // Price Intelligence
  // ============================================================================

  async getPriceHistory(propertyId: string): Promise<PriceHistory> {
    return this.request<PriceHistory>("GET", `/price-history/${propertyId}`);
  }

  async getPriceDrops(params?: {
    min_drop_percentage?: number;
    days?: number;
  }): Promise<PriceDrop[]> {
    return this.request<PriceDrop[]>("GET", "/price-drops", undefined, params);
  }

  async getStaleListings(days?: number): Promise<Property[]> {
    return this.request<Property[]>("GET", "/stale-listings", undefined, {
      days,
    });
  }

  async getMarketTrends(): Promise<MarketTrends> {
    return this.request<MarketTrends>("GET", "/market-trends");
  }

  // ============================================================================
  // Natural Language Search
  // ============================================================================

  async naturalLanguageSearch(query: string): Promise<QueryResult> {
    return this.request<QueryResult>("POST", "/search/natural", { query });
  }

  async getSearchSuggestions(partial: string): Promise<string[]> {
    return this.request<string[]>("GET", "/search/suggestions", undefined, {
      q: partial,
    });
  }

  // ============================================================================
  // Saved Searches
  // ============================================================================

  async listSavedSearches(): Promise<SavedSearch[]> {
    const response = await this.request<{searches: SavedSearch[], total: number}>("GET", "/searches");
    return response.searches;
  }

  async createSavedSearch(
    search: Omit<SavedSearch, "id" | "created_at">
  ): Promise<{ id: string; message: string }> {
    return this.request("POST", "/searches", search);
  }

  async getSavedSearch(searchId: string): Promise<SavedSearch> {
    return this.request<SavedSearch>("GET", `/searches/${searchId}`);
  }

  async updateSavedSearch(
    searchId: string,
    updates: Partial<SavedSearch>
  ): Promise<{ message: string }> {
    return this.request("PUT", `/searches/${searchId}`, updates);
  }

  async deleteSavedSearch(searchId: string): Promise<{ message: string }> {
    return this.request("DELETE", `/searches/${searchId}`);
  }

  async getSavedSearchStats(searchId: string): Promise<SavedSearchStats> {
    return this.request<SavedSearchStats>("GET", `/searches/${searchId}/stats`);
  }

  // ============================================================================
  // Duplicate Detection & Quality
  // ============================================================================

  async detectDuplicates(listings: Property[]): Promise<DuplicateDetection> {
    return this.request<DuplicateDetection>("POST", "/duplicates/detect", {
      listings,
    });
  }

  async scoreQuality(listing: Property): Promise<QualityScore> {
    return this.request<QualityScore>("POST", "/quality/score", { listing });
  }

  // ============================================================================
  // Firestore Integration
  // ============================================================================

  async queryFirestore(
    query: any
  ): Promise<
    | {
        results: Property[];
        count: number;
        filters_applied?: any;
        sort_by?: string;
        sort_desc?: boolean;
      }
    | Property[]
  > {
    return this.request<any>("POST", "/firestore/query", query);
  }

  async queryFirestoreArchive(query: any): Promise<Property[]> {
    return this.request<Property[]>("POST", "/firestore/query-archive", query);
  }

  async exportToFirestore(
    listings: Property[]
  ): Promise<{ message: string; exported: number }> {
    return this.request("POST", "/firestore/export", { listings });
  }

  // ============================================================================
  // Export Management
  // ============================================================================

  async generateExport(request: ExportRequest): Promise<ExportJob> {
    return this.request<ExportJob>("POST", "/export/generate", request);
  }

  async downloadExport(filename: string): Promise<Response> {
    return this.request<Response>("GET", `/export/download/${filename}`);
  }

  async getExportFormats(): Promise<string[]> {
    return this.request<string[]>("GET", "/export/formats");
  }

  // ============================================================================
  // GitHub Actions
  // ============================================================================

  async triggerGitHubScrape(
    sites?: string[]
  ): Promise<{ message: string; run_id?: number }> {
    return this.request("POST", "/github/trigger-scrape", { sites });
  }

  async estimateScrapeTime(
    sites?: string[]
  ): Promise<{ estimated_minutes: number }> {
    return this.request("POST", "/github/estimate-scrape-time", { sites });
  }

  async subscribeToWorkflow(
    email: string,
    runId: number
  ): Promise<{ message: string }> {
    return this.request("POST", "/notifications/subscribe", {
      email,
      run_id: runId,
    });
  }

  async getWorkflowStatus(runId: number): Promise<GitHubWorkflowRun> {
    return this.request<GitHubWorkflowRun>(
      "GET",
      `/notifications/workflow-status/${runId}`
    );
  }

  async listWorkflowRuns(limit?: number): Promise<GitHubWorkflowRun[]> {
    const response = await this.request<{ workflow_runs: GitHubWorkflowRun[]; total_count: number }>(
      "GET",
      "/github/workflow-runs",
      undefined,
      { limit }
    );
    // Extract the workflow_runs array from the response object
    return response.workflow_runs || [];
  }

  async listArtifacts(runId?: number): Promise<GitHubArtifact[]> {
    return this.request<GitHubArtifact[]>(
      "GET",
      "/github/artifacts",
      undefined,
      { run_id: runId }
    );
  }

  async downloadArtifact(artifactId: number): Promise<Response> {
    return this.request<Response>(
      "GET",
      `/github/artifact/${artifactId}/download`
    );
  }

  async getWorkflowLogs(
    runId: number,
    options?: { jobId?: number; tail?: number }
  ): Promise<GitHubWorkflowLogsResponse> {
    return this.request<GitHubWorkflowLogsResponse>(
      "GET",
      `/github/workflow-runs/${runId}/logs`,
      undefined,
      {
        job_id: options?.jobId,
        tail: options?.tail || 100,
      }
    );
  }

  // ============================================================================
  // Scheduling
  // ============================================================================

  async scheduleScrape(
    scheduleTime: string,
    params?: {
      sites?: string[];
      max_pages?: number;
      geocode?: boolean;
    }
  ): Promise<{ job_id: number }> {
    return this.request("POST", "/schedule/scrape", {
      scheduled_time: scheduleTime,
      ...(params || {}),
    });
  }

  async listScheduledJobs(): Promise<ScheduleJob[]> {
    return this.request<ScheduleJob[]>("GET", "/schedule/jobs");
  }

  async getScheduledJob(jobId: number): Promise<ScheduleJob> {
    return this.request<ScheduleJob>("GET", `/schedule/jobs/${jobId}`);
  }

  async cancelScheduledJob(jobId: number): Promise<{ message: string }> {
    return this.request("POST", `/schedule/jobs/${jobId}/cancel`);
  }

  // ============================================================================
  // Email Notifications
  // ============================================================================

  async configureEmail(config: EmailConfig): Promise<{ message: string }> {
    return this.request("POST", "/email/configure", config);
  }

  async testEmailConnection(
    config: EmailConfig
  ): Promise<{ success: boolean; error?: string }> {
    return this.request("POST", "/email/test-connection", config);
  }

  async getEmailConfig(): Promise<EmailConfig> {
    return this.request<EmailConfig>("GET", "/email/config");
  }

  async listEmailRecipients(): Promise<EmailRecipient[]> {
    return this.request<EmailRecipient[]>("GET", "/email/recipients");
  }

  async addEmailRecipient(
    recipient: EmailRecipient
  ): Promise<{ message: string }> {
    return this.request("POST", "/email/recipients", recipient);
  }

  async removeEmailRecipient(email: string): Promise<{ message: string }> {
    return this.request("DELETE", `/email/recipients/${email}`);
  }

  async sendTestEmail(
    to: string
  ): Promise<{ success: boolean; error?: string }> {
    return this.request("POST", "/email/send-test", { to });
  }

  // ============================================================================
  // NEW: Firestore-Optimized Endpoints (40-300x faster!)
  // ============================================================================

  /**
   * Get dashboard statistics (replaces _Dashboard Excel sheet)
   * 40-300x faster than legacy endpoints
   */
  async getFirestoreDashboard(): Promise<any> {
    return this.request("GET", "/firestore/dashboard");
  }

  /**
   * Get top 100 cheapest properties (replaces _Top_100_Cheapest)
   */
  async getFirestoreTopDeals(params?: { limit?: number }): Promise<Property[]> {
    return this.request<Property[]>(
      "GET",
      "/firestore/top-deals",
      undefined,
      params
    );
  }

  /**
   * Get newest listings (replaces _Newest_Listings)
   */
  async getFirestoreNewest(params?: { limit?: number }): Promise<Property[]> {
    return this.request<Property[]>(
      "GET",
      "/firestore/newest",
      undefined,
      params
    );
  }

  /**
   * Get for sale properties (replaces _For_Sale sheet)
   */
  async getFirestoreForSale(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{ properties: Property[]; total: number }> {
    return this.request("GET", "/firestore/for-sale", undefined, params);
  }

  /**
   * Get for rent properties (replaces _For_Rent sheet)
   */
  async getFirestoreForRent(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{ properties: Property[]; total: number }> {
    return this.request("GET", "/firestore/for-rent", undefined, params);
  }

  /**
   * Get land-only properties (replaces _Land_Only sheet)
   */
  async getFirestoreLand(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{ properties: Property[]; total: number }> {
    return this.request("GET", "/firestore/land", undefined, params);
  }

  /**
   * Get premium 4+ bedroom properties (replaces _4BR_Plus sheet)
   */
  async getFirestorePremium(params?: {
    limit?: number;
    offset?: number;
  }): Promise<{ properties: Property[]; total: number }> {
    return this.request("GET", "/firestore/premium", undefined, params);
  }

  /**
   * Advanced cross-site search with filters
   * MUCH faster than legacy search
   */
  async searchFirestore(params: {
    query?: string;
    location?: string;
    property_type?: string;
    min_price?: number;
    max_price?: number;
    min_bedrooms?: number;
    max_bedrooms?: number;
    min_bathrooms?: number;
    listing_type?: string;
    site_key?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ properties: Property[]; total: number }> {
    return this.request("POST", "/firestore/search", params);
  }

  /**
   * Get site-specific properties (replaces per-site Excel sheets)
   */
  async getFirestoreSiteProperties(
    siteKey: string,
    params?: { limit?: number; offset?: number }
  ): Promise<{ properties: Property[]; total: number }> {
    return this.request("GET", `/firestore/site/${siteKey}`, undefined, params);
  }

  /**
   * Get individual property by hash
   */
  async getFirestoreProperty(hash: string): Promise<Property> {
    return this.request<Property>("GET", `/firestore/property/${hash}`);
  }

  /**
   * Get site statistics
   */
  async getFirestoreSiteStats(siteKey: string): Promise<any> {
    return this.request("GET", `/firestore/site-stats/${siteKey}`);
  }

  // ============================================================================
  // Additional Saved Searches Endpoints
  // ============================================================================

  /**
   * Get properties matching a saved search
   */
  async getSavedSearchMatches(
    searchId: string,
    params?: { limit?: number }
  ): Promise<Property[]> {
    return this.request<Property[]>(
      "GET",
      `/searches/${searchId}/matches`,
      undefined,
      params
    );
  }

  /**
   * Get new matches since last check
   */
  async getNewSavedSearchMatches(searchId: string): Promise<Property[]> {
    return this.request<Property[]>("GET", `/searches/${searchId}/matches/new`);
  }

  /**
   * Send email notification for saved search
   */
  async notifySavedSearch(searchId: string): Promise<{ message: string }> {
    return this.request("POST", `/searches/${searchId}/notify`);
  }

  /**
   * Update saved search settings
   */
  async updateSavedSearchSettings(
    searchId: string,
    settings: any
  ): Promise<{ message: string }> {
    return this.request("PUT", `/searches/${searchId}/settings`, settings);
  }

  // ============================================================================
  // NEW: 7 Enterprise Firestore Endpoints (v3.1)
  // ============================================================================

  /**
   * Get verified properties only
   * Uses auto-verified flag in metadata
   */
  async getFirestoreVerified(params?: {
    limit?: number;
    offset?: number;
  }): Promise<any> {
    return this.request(
      "GET",
      "/firestore/properties/verified",
      undefined,
      params
    );
  }

  /**
   * Get furnished/semi-furnished properties
   * Filters by furnishing status in property_details
   */
  async getFirestoreFurnished(params?: {
    limit?: number;
    offset?: number;
    furnishing_type?: string; // furnished, semi-furnished, unfurnished
  }): Promise<any> {
    return this.request(
      "GET",
      "/firestore/properties/furnished",
      undefined,
      params
    );
  }

  /**
   * Get trending properties (high view count)
   * Automatically trending based on view_count in metadata
   */
  async getFirestoreTrending(params?: {
    limit?: number;
    min_views?: number;
  }): Promise<any> {
    return this.request(
      "GET",
      "/firestore/properties/trending",
      undefined,
      params
    );
  }

  /**
   * Get hot deal properties
   * Auto-tagged properties with price_per_bedroom < 15M
   */
  async getFirestoreHotDeals(params?: {
    limit?: number;
    offset?: number;
  }): Promise<any> {
    return this.request(
      "GET",
      "/firestore/properties/hot-deals",
      undefined,
      params
    );
  }

  /**
   * Get properties by Local Government Area (LGA)
   * Filter Lagos properties by LGA (Eti-Osa, Lagos Island, etc.)
   */
  async getFirestoreByLga(
    lga: string,
    params?: {
      limit?: number;
      offset?: number;
      sort_by?: string;
      sort_desc?: boolean;
    }
  ): Promise<any> {
    return this.request(
      "GET",
      `/firestore/properties/by-lga/${lga}`,
      undefined,
      params
    );
  }

  /**
   * Get properties by area/neighborhood
   * Filter by specific area (Lekki Phase 1, Yaba, etc.)
   */
  async getFirestoreByArea(
    area: string,
    params?: {
      limit?: number;
      offset?: number;
      sort_by?: string;
      sort_desc?: boolean;
    }
  ): Promise<any> {
    return this.request(
      "GET",
      `/firestore/properties/by-area/${area}`,
      undefined,
      params
    );
  }

  /**
   * Get newly listed properties on market
   * Properties recently added (within specified days)
   */
  async getFirestoreNewOnMarket(params?: {
    limit?: number;
    offset?: number;
    days_back?: number;
  }): Promise<any> {
    return this.request(
      "GET",
      "/firestore/properties/new-on-market",
      undefined,
      params
    );
  }

  // ============================================================================
  // Advanced Firestore Search with Full Nested Schema
  // ============================================================================

  /**
   * Advanced search using full enterprise schema filters
   * Supports multi-criteria queries with nested field filtering
   */
  async searchFirestoreAdvanced(request: any): Promise<any> {
    return this.request("POST", "/firestore/search", request);
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
