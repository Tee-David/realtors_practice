import {
  StatsResponse,
  SiteStat,
  TrendsPoint,
  ScrapeStatus,
  SiteListResponse,
  Site,
} from "@/lib/types";

// API service layer for backend integration
// Prefer build-time env, then runtime injected window.ENV, fallback to localhost
const API_BASE_URL: string =
  (process.env.NEXT_PUBLIC_API_URL as string) ||
  (typeof window !== "undefined" &&
    (window as unknown as { ENV?: { NEXT_PUBLIC_API_URL?: string } }).ENV
      ?.NEXT_PUBLIC_API_URL) ||
  "http://localhost:5000";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit & { timeoutMs?: number } = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const { timeoutMs = 15000, ...rest } = options as {
    timeoutMs?: number;
  } & RequestInit;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const config: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      ...rest.headers,
    },
    ...rest,
    signal: controller.signal,
  };

  console.log(`[API] ${rest.method || "GET"} ${url}`);

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = (await response
        .json()
        .catch(() => ({ error: "Unknown error" }))) as { error?: string };
      console.error(
        `[API] ${rest.method || "GET"} ${url} failed:`,
        response.status,
        errorData
      );
      throw new ApiError(
        response.status,
        errorData.error || `HTTP ${response.status}`
      );
    }
    const json = (await response.json()) as T;
    console.log(`[API] ${rest.method || "GET"} ${url} succeeded:`, json);
    return json;
  } catch (error) {
    if (timeoutId) clearTimeout(timeoutId);
    if (error instanceof ApiError) {
      throw error;
    }
    // Handle abort/timeout errors explicitly
    if ((error as { name?: string } | null)?.name === "AbortError") {
      console.error(
        `[API] ${rest.method || "GET"} ${url} timed out after ${timeoutMs}ms`
      );
      throw new ApiError(0, "Request timed out. Please try again.");
    }
    console.error(`[API] ${rest.method || "GET"} ${url} network error:`, error);
    throw new ApiError(
      0,
      error instanceof Error ? error.message : "Network error"
    );
  } finally {
    // Ensure the timeout is always cleared to avoid leaks
    if (timeoutId) clearTimeout(timeoutId);
  }
}

// Health Check
export const healthCheck = () => apiRequest("/api/health");

// Scraping Management
export const scrapeApi = {
  start: (params: {
    sites?: string[];
    max_pages?: number;
    geocoding?: boolean;
  }) =>
    apiRequest("/api/scrape/start", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  status: () => apiRequest<ScrapeStatus>("/api/scrape/status"),

  stop: () => apiRequest("/api/scrape/stop", { method: "POST" }),

  history: (limit = 20) => apiRequest(`/api/scrape/history?limit=${limit}`),
};

// Site Management
export const sitesApi = {
  list: async () => {
    // Normalize response shape in case backend returns { data: {...} }
    const resp = await apiRequest<
      SiteListResponse | { data?: SiteListResponse } | unknown
    >("/api/sites");
    const normalized =
      (resp as SiteListResponse)?.sites !== undefined
        ? (resp as SiteListResponse)
        : (resp as { data?: SiteListResponse })?.data;
    return (normalized || (resp as SiteListResponse)) as SiteListResponse;
  },

  get: (siteKey: string) =>
    apiRequest<Site | { site: Site }>(`/api/sites/${siteKey}`),

  create: (siteData: {
    site_key: string;
    name: string;
    url: string;
    enabled: boolean;
    parser?: string;
    selectors?: Record<string, unknown>;
  }) =>
    apiRequest("/api/sites", {
      method: "POST",
      body: JSON.stringify(siteData),
    }),

  update: (siteKey: string, updates: Record<string, unknown>) =>
    apiRequest(`/api/sites/${siteKey}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    }),

  delete: (siteKey: string) =>
    apiRequest(`/api/sites/${siteKey}`, {
      method: "DELETE",
    }),

  toggle: (siteKey: string) =>
    apiRequest(`/api/sites/${siteKey}/toggle`, {
      method: "PATCH",
    }),
};

// Data Management
export const dataApi = {
  listFiles: () => apiRequest("/api/data/sites"),
  getSiteData: (
    siteKey: string,
    options: {
      limit?: number;
      offset?: number;
      source?: "raw" | "cleaned";
    } = {}
  ) => {
    const params = new URLSearchParams();
    if (options.limit) params.append("limit", options.limit.toString());
    if (options.offset) params.append("offset", options.offset.toString());
    if (options.source) params.append("source", options.source);
    return apiRequest(`/api/data/sites/${siteKey}?${params.toString()}`);
  },
  getMasterData: (options: { limit?: number; site?: string } = {}) => {
    const params = new URLSearchParams();
    if (options.limit) params.append("limit", options.limit.toString());
    if (options.site) params.append("site", options.site);
    return apiRequest(`/api/data/master?${params.toString()}`);
  },
  search: (
    query: string,
    options: { fields?: string[]; limit?: number } = {}
  ) => {
    const params = new URLSearchParams();
    params.append("query", query);
    if (options.fields) params.append("fields", options.fields.join(","));
    if (options.limit) params.append("limit", options.limit.toString());
    return apiRequest(`/api/data/search?${params.toString()}`);
  },
};

// Logs
export const logsApi = {
  getLogs: (options: { limit?: number; level?: string } = {}) => {
    const params = new URLSearchParams();
    if (options.limit) params.append("limit", options.limit.toString());
    if (options.level) params.append("level", options.level);

    return apiRequest(`/api/logs?${params.toString()}`);
  },

  getErrors: (limit = 50) => apiRequest(`/api/logs/errors?limit=${limit}`),

  getSiteLogs: (siteKey: string, limit = 100) =>
    apiRequest(`/api/logs/site/${siteKey}?limit=${limit}`),
};

// Statistics
export const statsApi = {
  getOverview: () => apiRequest<StatsResponse>("/api/stats/overview"),
  getSiteStats: () =>
    apiRequest<SiteStat[] | { sites: SiteStat[] }>("/api/stats/sites"),
  getTrends: (days = 7) =>
    apiRequest<TrendsPoint[]>(`/api/stats/trends?days=${days}`),
};

export { ApiError };
