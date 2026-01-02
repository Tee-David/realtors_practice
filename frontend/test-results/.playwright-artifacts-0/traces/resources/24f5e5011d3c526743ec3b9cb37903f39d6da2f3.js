(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/lib/utils.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "cn",
    ()=>cn,
    "debounce",
    ()=>debounce,
    "formatCurrency",
    ()=>formatCurrency,
    "formatDate",
    ()=>formatDate,
    "formatDateTime",
    ()=>formatDateTime,
    "formatNumber",
    ()=>formatNumber,
    "generateId",
    ()=>generateId,
    "getPageTitle",
    ()=>getPageTitle,
    "getRoleColor",
    ()=>getRoleColor,
    "getStatusColor",
    ()=>getStatusColor
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/clsx/dist/clsx.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/tailwind-merge/dist/bundle-mjs.mjs [app-client] (ecmascript)");
;
;
function cn(...inputs) {
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$tailwind$2d$merge$2f$dist$2f$bundle$2d$mjs$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["twMerge"])((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$clsx$2f$dist$2f$clsx$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["clsx"])(inputs));
}
function formatCurrency(amount) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}
function formatDate(date) {
    return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
    }).format(new Date(date));
}
function formatDateTime(date) {
    return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
    }).format(new Date(date));
}
function formatNumber(num) {
    return new Intl.NumberFormat("en-US").format(num);
}
function getStatusColor(status) {
    switch(status.toLowerCase()){
        case "active":
        case "completed":
        case "success":
            return "bg-green-500/20 text-green-400 border border-green-500/30";
        case "inactive":
        case "failed":
            return "bg-red-500/20 text-red-400 border border-red-500/30";
        case "running":
            return "bg-blue-500/20 text-blue-400 border border-blue-500/30";
        default:
            return "bg-gray-500/20 text-gray-400 border border-gray-500/30";
    }
}
function getRoleColor(role) {
    switch(role.toLowerCase()){
        case "admin":
            return "bg-purple-500/20 text-purple-400 border border-purple-500/30";
        case "editor":
            return "bg-blue-500/20 text-blue-400 border border-blue-500/30";
        case "viewer":
            return "bg-slate-500/20 text-slate-400 border border-slate-500/30";
        default:
            return "bg-gray-500/20 text-gray-400 border border-gray-500/30";
    }
}
const getPageTitle = (tab)=>{
    switch(tab){
        case "dashboard":
            return "Dashboard";
        case "data":
            return "Data Explorer";
        case "scraper":
            return "Scraper Control";
        case "users":
            return "User Management";
        default:
            return "Dashboard";
    }
};
function generateId() {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
}
function debounce(func, wait) {
    let timeout;
    return (...args)=>{
        clearTimeout(timeout);
        timeout = setTimeout(()=>func(...args), wait);
    };
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/hooks/useApi.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useApi",
    ()=>useApi,
    "useApiMutation",
    ()=>useApiMutation,
    "usePolling",
    ()=>usePolling
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature(), _s2 = __turbopack_context__.k.signature();
"use client";
;
function useApi(apiCall, options = {}) {
    _s();
    const [state, setState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        data: null,
        loading: false,
        error: null
    });
    const isMountedRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(true);
    // Store options in ref to avoid recreating execute on every options change
    const optionsRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(options);
    optionsRef.current = options;
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useApi.useEffect": ()=>{
            isMountedRef.current = true;
            return ({
                "useApi.useEffect": ()=>{
                    isMountedRef.current = false;
                }
            })["useApi.useEffect"];
        }
    }["useApi.useEffect"], []);
    // Store the latest apiCall in a ref to avoid dependency issues
    const apiCallRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(apiCall);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useApi.useEffect": ()=>{
            apiCallRef.current = apiCall;
        }
    }["useApi.useEffect"], [
        apiCall
    ]);
    const execute = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useApi.useCallback[execute]": async ()=>{
            if (!isMountedRef.current) return;
            // Only log in development
            if ("TURBOPACK compile-time truthy", 1) {
                console.log("[useApi] Starting request...");
            }
            setState({
                "useApi.useCallback[execute]": (prev)=>({
                        ...prev,
                        loading: true,
                        error: null
                    })
            }["useApi.useCallback[execute]"]);
            // Create abort controller for request cancellation
            const controller = new AbortController();
            let timeoutId = null;
            // Add timeout to prevent infinite loading (120 second timeout for cold starts)
            timeoutId = setTimeout({
                "useApi.useCallback[execute]": ()=>{
                    if (isMountedRef.current) {
                        controller.abort();
                        console.error("[useApi] Request timeout after 120 seconds");
                        setState({
                            "useApi.useCallback[execute]": (prev)=>({
                                    ...prev,
                                    loading: false,
                                    error: "API timeout: The server is taking longer than expected. Please wait and refresh the page."
                                })
                        }["useApi.useCallback[execute]"]);
                    }
                }
            }["useApi.useCallback[execute]"], 120000); // 120 second timeout
            try {
                // Use apiCallRef to get the latest apiCall without causing re-renders
                const data = await apiCallRef.current();
                if (timeoutId) clearTimeout(timeoutId);
                if (isMountedRef.current) {
                    if ("TURBOPACK compile-time truthy", 1) {
                        console.log("[useApi] Request succeeded:", data);
                    }
                    setState({
                        data,
                        loading: false,
                        error: null
                    });
                }
            } catch (error) {
                if (timeoutId) clearTimeout(timeoutId);
                if (!isMountedRef.current) return;
                // Skip timeout errors that we already handled
                if (error instanceof Error && error.name === "AbortError") {
                    return;
                }
                let errorMessage = "An error occurred";
                if (error && typeof error === "object" && "message" in error) {
                    errorMessage = error.message || errorMessage;
                } else if (typeof error === "string") {
                    errorMessage = error;
                }
                // Only log error if no custom error handler is provided
                if (!optionsRef.current.onError) {
                    console.error("[useApi] Request failed:", errorMessage, error);
                }
                setState({
                    "useApi.useCallback[execute]": (prev)=>({
                            ...prev,
                            loading: false,
                            error: errorMessage
                        })
                }["useApi.useCallback[execute]"]);
                if (optionsRef.current.onError) {
                    optionsRef.current.onError(error);
                }
            }
        }
    }["useApi.useCallback[execute]"], []); // Empty deps - use refs to avoid infinite loops
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useApi.useEffect": ()=>{
            // Execute on mount if immediate is not false
            if (optionsRef.current.immediate !== false) {
                execute();
            }
        // eslint-disable-next-line react-hooks/exhaustive-deps
        }
    }["useApi.useEffect"], []); // Only run on mount
    return {
        ...state,
        refetch: execute
    };
}
_s(useApi, "zwtYzR5zWD0BxgcoiHkWY96elYk=");
function useApiMutation(apiCall) {
    _s1();
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const mutate = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useApiMutation.useCallback[mutate]": async (params)=>{
            if ("TURBOPACK compile-time truthy", 1) {
                console.log("[useApiMutation] Starting mutation with params:", params);
            }
            setLoading(true);
            setError(null);
            try {
                const result = await apiCall(params);
                if ("TURBOPACK compile-time truthy", 1) {
                    console.log("[useApiMutation] Mutation succeeded:", result);
                }
                setLoading(false);
                return result;
            } catch (err) {
                let errorMessage = "An error occurred";
                if (err && typeof err === "object" && "message" in err) {
                    errorMessage = err.message || errorMessage;
                }
                console.error("[useApiMutation] Mutation failed:", errorMessage, err);
                setError(errorMessage);
                setLoading(false);
                throw err;
            }
        }
    }["useApiMutation.useCallback[mutate]"], [
        apiCall
    ]);
    return {
        mutate,
        loading,
        error
    };
}
_s1(useApiMutation, "IBQZTU9ar8ZGD5syh54afoGaHvA=");
function usePolling(apiCall, interval = 5000, enabled = true) {
    _s2();
    const [state, setState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        data: null,
        loading: false,
        error: null
    });
    const isMountedRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(true);
    const intervalRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(interval);
    const enabledRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(enabled);
    const pollCountRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(0);
    const apiCallRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(apiCall);
    // Update refs with latest values
    intervalRef.current = interval;
    enabledRef.current = enabled;
    // Update apiCallRef when apiCall changes
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "usePolling.useEffect": ()=>{
            apiCallRef.current = apiCall;
        }
    }["usePolling.useEffect"], [
        apiCall
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "usePolling.useEffect": ()=>{
            isMountedRef.current = true;
            return ({
                "usePolling.useEffect": ()=>{
                    isMountedRef.current = false;
                }
            })["usePolling.useEffect"];
        }
    }["usePolling.useEffect"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "usePolling.useEffect": ()=>{
            if (!enabled) return;
            let timeoutId;
            pollCountRef.current = 0;
            let consecutiveErrors = 0;
            const poll = {
                "usePolling.useEffect.poll": async ()=>{
                    if (!isMountedRef.current || !enabledRef.current) return;
                    pollCountRef.current++;
                    const currentPoll = pollCountRef.current;
                    if ("TURBOPACK compile-time truthy", 1) {
                        console.log(`[usePolling] Poll #${currentPoll} starting (interval: ${intervalRef.current}ms)`);
                    }
                    try {
                        setState({
                            "usePolling.useEffect.poll": (prev)=>({
                                    ...prev,
                                    loading: true,
                                    error: null
                                })
                        }["usePolling.useEffect.poll"]);
                        // Use apiCallRef to avoid dependency issues
                        const data = await apiCallRef.current();
                        if (isMountedRef.current) {
                            if ("TURBOPACK compile-time truthy", 1) {
                                console.log(`[usePolling] Poll #${currentPoll} succeeded:`, data);
                            }
                            setState({
                                data,
                                loading: false,
                                error: null
                            });
                            // Reset consecutive error count on success
                            consecutiveErrors = 0;
                        }
                    } catch (error) {
                        if (!isMountedRef.current) return;
                        consecutiveErrors++;
                        let errorMessage = "An error occurred";
                        if (error && typeof error === "object" && "message" in error) {
                            errorMessage = error.message || errorMessage;
                        }
                        if ("TURBOPACK compile-time truthy", 1) {
                            console.warn(`[usePolling] Poll #${currentPoll} failed (attempt #${consecutiveErrors}):`, errorMessage);
                        }
                        setState({
                            "usePolling.useEffect.poll": (prev)=>({
                                    ...prev,
                                    loading: false,
                                    error: consecutiveErrors > 3 ? errorMessage : null
                                })
                        }["usePolling.useEffect.poll"]);
                    }
                    // Schedule next poll only if still enabled and mounted
                    if (enabledRef.current && isMountedRef.current) {
                        // Exponential backoff: if there have been errors, increase interval
                        const backoffMultiplier = Math.min(2 ** (consecutiveErrors - 1), 4);
                        const nextInterval = intervalRef.current * backoffMultiplier;
                        timeoutId = setTimeout(poll, nextInterval);
                    }
                }
            }["usePolling.useEffect.poll"];
            // Start polling immediately
            if ("TURBOPACK compile-time truthy", 1) {
                console.log(`[usePolling] Starting polling (interval: ${intervalRef.current}ms, enabled: ${enabled})`);
            }
            poll();
            return ({
                "usePolling.useEffect": ()=>{
                    if ("TURBOPACK compile-time truthy", 1) {
                        console.log(`[usePolling] Stopping polling (total polls: ${pollCountRef.current})`);
                    }
                    if (timeoutId) {
                        clearTimeout(timeoutId);
                    }
                }
            })["usePolling.useEffect"];
        // eslint-disable-next-line react-hooks/exhaustive-deps
        }
    }["usePolling.useEffect"], [
        enabled
    ]); // Only depend on enabled - apiCall is handled by ref
    return state;
}
_s2(usePolling, "hxsb6PI6N8/XnjI7EYYHfRsfxhQ=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/api.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * TypeScript API Client for Nigerian Real Estate API
 * Complete typed client for all 90 endpoints (68 legacy + 16 Firestore + 6 other)
 */ __turbopack_context__.s([
    "RealEstateApiClient",
    ()=>RealEstateApiClient,
    "apiClient",
    ()=>apiClient,
    "default",
    ()=>__TURBOPACK__default__export__
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
class RealEstateApiClient {
    baseUrl;
    apiKey;
    timeout;
    headers;
    constructor(config = {}){
        this.baseUrl = config.baseUrl || ("TURBOPACK compile-time value", "https://realtors-practice-api.onrender.com/api") || "https://realtors-practice-api.onrender.com/api";
        this.apiKey = config.apiKey;
        this.timeout = config.timeout || 120000; // 120 seconds for cold starts from Render
        this.headers = {
            "Content-Type": "application/json",
            ...config.headers
        };
        if (this.apiKey) {
            this.headers["X-API-Key"] = this.apiKey;
        }
    }
    /**
   * Generic request method
   */ async request(method, endpoint, data, queryParams) {
        let url = `${this.baseUrl}${endpoint}`;
        // Add query parameters
        if (queryParams) {
            const params = new URLSearchParams();
            Object.entries(queryParams).forEach(([key, value])=>{
                if (value !== undefined && value !== null) {
                    params.append(key, String(value));
                }
            });
            const queryString = params.toString();
            if (queryString) {
                url += `?${queryString}`;
            }
        }
        const options = {
            method,
            headers: this.headers,
            signal: AbortSignal.timeout(this.timeout)
        };
        if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
            options.body = JSON.stringify(data);
        }
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json().catch(()=>({}));
                const errorMessage = errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
                throw new Error(errorMessage);
            }
            const contentType = response.headers.get("content-type");
            if (contentType?.includes("application/json")) {
                return await response.json();
            }
            // For file downloads or non-JSON responses
            return response;
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
    async healthCheck() {
        return this.request("GET", "/health");
    }
    async overallHealth() {
        return this.request("GET", "/health/overall");
    }
    async siteHealth(siteKey) {
        return this.request("GET", `/health/sites/${siteKey}`);
    }
    async healthAlerts() {
        return this.request("GET", "/health/alerts");
    }
    async topPerformers() {
        return this.request("GET", "/health/top-performers");
    }
    // ============================================================================
    // Scraping Operations
    // ============================================================================
    async startScrape(request = {}) {
        return this.request("POST", "/scrape/start", request);
    }
    async getScrapeStatus() {
        return this.request("GET", "/scrape/status");
    }
    async stopScrape() {
        return this.request("POST", "/scrape/stop");
    }
    async getScrapeHistory(limit) {
        return this.request("GET", "/scrape/history", undefined, {
            limit
        });
    }
    // ============================================================================
    // Sites Management
    // ============================================================================
    async listSites() {
        return this.request("GET", "/sites");
    }
    async getSite(siteKey) {
        return this.request("GET", `/sites/${siteKey}`);
    }
    async createSite(site) {
        return this.request("POST", "/sites", site);
    }
    async updateSite(siteKey, updates) {
        return this.request("PUT", `/sites/${siteKey}`, updates);
    }
    async deleteSite(siteKey) {
        return this.request("DELETE", `/sites/${siteKey}`);
    }
    async toggleSite(siteKey) {
        return this.request("PATCH", `/sites/${siteKey}/toggle`);
    }
    // ============================================================================
    // Data Access
    // ============================================================================
    async getAvailableData() {
        return this.request("GET", "/data/sites");
    }
    async getAllData(params) {
        return this.request("GET", "/data/sites", undefined, params);
    }
    async getSiteData(siteKey, params) {
        return this.request("GET", `/data/sites/${siteKey}`, undefined, params);
    }
    async getMasterData(params) {
        return this.request("GET", "/data/master", undefined, params);
    }
    async searchData(searchParams) {
        return this.request("GET", "/data/search", undefined, searchParams);
    }
    // ============================================================================
    // Statistics
    // ============================================================================
    async getOverviewStats() {
        return this.request("GET", "/stats/overview");
    }
    async getSiteStats() {
        return this.request("GET", "/stats/sites");
    }
    async getTrendStats(days) {
        return this.request("GET", "/stats/trends", undefined, {
            days
        });
    }
    // ============================================================================
    // Logs
    // ============================================================================
    async getLogs(params) {
        return this.request("GET", "/logs", undefined, params);
    }
    async getErrorLogs(limit) {
        return this.request("GET", "/logs/errors", undefined, {
            limit
        });
    }
    async getSiteLogs(siteKey, limit) {
        return this.request("GET", `/logs/site/${siteKey}`, undefined, {
            limit
        });
    }
    // ============================================================================
    // URL Validation
    // ============================================================================
    async validateUrl(url) {
        return this.request("POST", "/validate/url", {
            url
        });
    }
    async validateUrls(urls) {
        return this.request("POST", "/validate/urls", {
            urls
        });
    }
    // ============================================================================
    // Location Filter
    // ============================================================================
    async filterByLocation(listings) {
        return this.request("POST", "/filter/location", {
            listings
        });
    }
    async getLocationStats() {
        return this.request("GET", "/filter/stats");
    }
    async getLocationConfig() {
        return this.request("GET", "/config/locations");
    }
    async updateLocationConfig(config) {
        return this.request("PUT", "/config/locations", config);
    }
    // ============================================================================
    // Property Query Engine
    // ============================================================================
    async queryProperties(query) {
        return this.request("POST", "/query", query);
    }
    async getQuerySummary(query) {
        return this.request("POST", "/query/summary", query);
    }
    // ============================================================================
    // Rate Limiting
    // ============================================================================
    async getRateLimitStatus() {
        return this.request("GET", "/rate-limit/status");
    }
    async checkRateLimit(action) {
        return this.request("POST", "/rate-limit/check", {
            action
        });
    }
    // ============================================================================
    // Price Intelligence
    // ============================================================================
    async getPriceHistory(propertyId) {
        return this.request("GET", `/price-history/${propertyId}`);
    }
    async getPriceDrops(params) {
        return this.request("GET", "/price-drops", undefined, params);
    }
    async getStaleListings(days) {
        return this.request("GET", "/stale-listings", undefined, {
            days
        });
    }
    async getMarketTrends() {
        return this.request("GET", "/market-trends");
    }
    // ============================================================================
    // Natural Language Search
    // ============================================================================
    async naturalLanguageSearch(query) {
        return this.request("POST", "/search/natural", {
            query
        });
    }
    async getSearchSuggestions(partial) {
        return this.request("GET", "/search/suggestions", undefined, {
            q: partial
        });
    }
    // ============================================================================
    // Saved Searches
    // ============================================================================
    async listSavedSearches() {
        const response = await this.request("GET", "/searches");
        // Transform backend 'criteria' to frontend 'query'
        return response.searches.map((search)=>({
                ...search,
                query: search.criteria || search.query
            }));
    }
    async createSavedSearch(search) {
        // Transform request to match backend expectations
        const requestBody = {
            user_id: "default-user",
            name: search.name,
            criteria: search.query,
            alert_frequency: search.alert_frequency || "daily"
        };
        return this.request("POST", "/searches", requestBody);
    }
    async getSavedSearch(searchId) {
        const search = await this.request("GET", `/searches/${searchId}`);
        // Transform backend 'criteria' to frontend 'query'
        return {
            ...search,
            query: search.criteria || search.query
        };
    }
    async updateSavedSearch(searchId, updates) {
        // Transform request to match backend expectations
        const requestBody = {
            ...updates
        };
        if (updates.query) {
            requestBody.criteria = updates.query; // Backend expects 'criteria' not 'query'
            delete requestBody.query;
        }
        return this.request("PUT", `/searches/${searchId}`, requestBody);
    }
    async deleteSavedSearch(searchId) {
        return this.request("DELETE", `/searches/${searchId}`);
    }
    async getSavedSearchStats(searchId) {
        return this.request("GET", `/searches/${searchId}/stats`);
    }
    // ============================================================================
    // Duplicate Detection & Quality
    // ============================================================================
    async detectDuplicates(listings) {
        return this.request("POST", "/duplicates/detect", {
            listings
        });
    }
    async scoreQuality(listing) {
        return this.request("POST", "/quality/score", {
            listing
        });
    }
    // ============================================================================
    // Firestore Integration
    // ============================================================================
    async queryFirestore(query) {
        return this.request("POST", "/firestore/query", query);
    }
    async queryFirestoreArchive(query) {
        return this.request("POST", "/firestore/query-archive", query);
    }
    async exportToFirestore(listings) {
        return this.request("POST", "/firestore/export", {
            listings
        });
    }
    // ============================================================================
    // Export Management
    // ============================================================================
    async generateExport(request) {
        return this.request("POST", "/export/generate", request);
    }
    async downloadExport(filename) {
        return this.request("GET", `/export/download/${filename}`);
    }
    async getExportFormats() {
        return this.request("GET", "/export/formats");
    }
    // ============================================================================
    // GitHub Actions
    // ============================================================================
    async triggerGitHubScrape(sites) {
        return this.request("POST", "/github/trigger-scrape", {
            sites
        });
    }
    async estimateScrapeTime(sites) {
        return this.request("POST", "/github/estimate-scrape-time", {
            sites
        });
    }
    async subscribeToWorkflow(email, runId) {
        return this.request("POST", "/notifications/subscribe", {
            email,
            run_id: runId
        });
    }
    async getWorkflowStatus(runId) {
        return this.request("GET", `/notifications/workflow-status/${runId}`);
    }
    async listWorkflowRuns(limit) {
        const response = await this.request("GET", "/github/workflow-runs", undefined, {
            limit
        });
        // Extract the workflow_runs array from the response object
        return response.workflow_runs || [];
    }
    async listArtifacts(runId) {
        return this.request("GET", "/github/artifacts", undefined, {
            run_id: runId
        });
    }
    async downloadArtifact(artifactId) {
        return this.request("GET", `/github/artifact/${artifactId}/download`);
    }
    async getWorkflowLogs(runId, options) {
        return this.request("GET", `/github/workflow-runs/${runId}/logs`, undefined, {
            job_id: options?.jobId,
            tail: options?.tail || 100
        });
    }
    // ============================================================================
    // Scheduling
    // ============================================================================
    async scheduleScrape(scheduleTime, params) {
        return this.request("POST", "/schedule/scrape", {
            scheduled_time: scheduleTime,
            ...params || {}
        });
    }
    async listScheduledJobs() {
        return this.request("GET", "/schedule/jobs");
    }
    async getScheduledJob(jobId) {
        return this.request("GET", `/schedule/jobs/${jobId}`);
    }
    async cancelScheduledJob(jobId) {
        return this.request("POST", `/schedule/jobs/${jobId}/cancel`);
    }
    // ============================================================================
    // Email Notifications
    // ============================================================================
    async configureEmail(config) {
        return this.request("POST", "/email/configure", config);
    }
    async testEmailConnection(config) {
        return this.request("POST", "/email/test-connection", config);
    }
    async getEmailConfig() {
        return this.request("GET", "/email/config");
    }
    async listEmailRecipients() {
        return this.request("GET", "/email/recipients");
    }
    async addEmailRecipient(recipient) {
        return this.request("POST", "/email/recipients", recipient);
    }
    async removeEmailRecipient(email) {
        return this.request("DELETE", `/email/recipients/${email}`);
    }
    async sendTestEmail(to) {
        return this.request("POST", "/email/send-test", {
            to
        });
    }
    // ============================================================================
    // NEW: Firestore-Optimized Endpoints (40-300x faster!)
    // ============================================================================
    /**
   * Get dashboard statistics (replaces _Dashboard Excel sheet)
   * 40-300x faster than legacy endpoints
   */ async getFirestoreDashboard() {
        return this.request("GET", "/firestore/dashboard");
    }
    /**
   * Get top 100 cheapest properties (replaces _Top_100_Cheapest)
   */ async getFirestoreTopDeals(params) {
        return this.request("GET", "/firestore/top-deals", undefined, params);
    }
    /**
   * Get newest listings (replaces _Newest_Listings)
   */ async getFirestoreNewest(params) {
        return this.request("GET", "/firestore/newest", undefined, params);
    }
    /**
   * Get for sale properties (replaces _For_Sale sheet)
   */ async getFirestoreForSale(params) {
        return this.request("GET", "/firestore/for-sale", undefined, params);
    }
    /**
   * Get for rent properties (replaces _For_Rent sheet)
   */ async getFirestoreForRent(params) {
        return this.request("GET", "/firestore/for-rent", undefined, params);
    }
    /**
   * Get land-only properties (replaces _Land_Only sheet)
   */ async getFirestoreLand(params) {
        return this.request("GET", "/firestore/land", undefined, params);
    }
    /**
   * Get premium 4+ bedroom properties (replaces _4BR_Plus sheet)
   */ async getFirestorePremium(params) {
        return this.request("GET", "/firestore/premium", undefined, params);
    }
    /**
   * Advanced cross-site search with filters
   * MUCH faster than legacy search
   */ async searchFirestore(params) {
        return this.request("POST", "/firestore/search", params);
    }
    /**
   * Get site-specific properties (replaces per-site Excel sheets)
   */ async getFirestoreSiteProperties(siteKey, params) {
        return this.request("GET", `/firestore/site/${siteKey}`, undefined, params);
    }
    /**
   * Get individual property by hash
   */ async getFirestoreProperty(hash) {
        return this.request("GET", `/firestore/property/${hash}`);
    }
    /**
   * Get site statistics
   */ async getFirestoreSiteStats(siteKey) {
        return this.request("GET", `/firestore/site-stats/${siteKey}`);
    }
    // ============================================================================
    // Additional Saved Searches Endpoints
    // ============================================================================
    /**
   * Get properties matching a saved search
   */ async getSavedSearchMatches(searchId, params) {
        return this.request("GET", `/searches/${searchId}/matches`, undefined, params);
    }
    /**
   * Get new matches since last check
   */ async getNewSavedSearchMatches(searchId) {
        return this.request("GET", `/searches/${searchId}/matches/new`);
    }
    /**
   * Send email notification for saved search
   */ async notifySavedSearch(searchId) {
        return this.request("POST", `/searches/${searchId}/notify`);
    }
    /**
   * Update saved search settings
   */ async updateSavedSearchSettings(searchId, settings) {
        return this.request("PUT", `/searches/${searchId}/settings`, settings);
    }
    // ============================================================================
    // NEW: 7 Enterprise Firestore Endpoints (v3.1)
    // ============================================================================
    /**
   * Get verified properties only
   * Uses auto-verified flag in metadata
   */ async getFirestoreVerified(params) {
        return this.request("GET", "/firestore/properties/verified", undefined, params);
    }
    /**
   * Get furnished/semi-furnished properties
   * Filters by furnishing status in property_details
   */ async getFirestoreFurnished(params) {
        return this.request("GET", "/firestore/properties/furnished", undefined, params);
    }
    /**
   * Get trending properties (high view count)
   * Automatically trending based on view_count in metadata
   */ async getFirestoreTrending(params) {
        return this.request("GET", "/firestore/properties/trending", undefined, params);
    }
    /**
   * Get hot deal properties
   * Auto-tagged properties with price_per_bedroom < 15M
   */ async getFirestoreHotDeals(params) {
        return this.request("GET", "/firestore/properties/hot-deals", undefined, params);
    }
    /**
   * Get properties by Local Government Area (LGA)
   * Filter Lagos properties by LGA (Eti-Osa, Lagos Island, etc.)
   */ async getFirestoreByLga(lga, params) {
        return this.request("GET", `/firestore/properties/by-lga/${lga}`, undefined, params);
    }
    /**
   * Get properties by area/neighborhood
   * Filter by specific area (Lekki Phase 1, Yaba, etc.)
   */ async getFirestoreByArea(area, params) {
        return this.request("GET", `/firestore/properties/by-area/${area}`, undefined, params);
    }
    /**
   * Get newly listed properties on market
   * Properties recently added (within specified days)
   */ async getFirestoreNewOnMarket(params) {
        return this.request("GET", "/firestore/properties/new-on-market", undefined, params);
    }
    // ============================================================================
    // Advanced Firestore Search with Full Nested Schema
    // ============================================================================
    /**
   * Advanced search using full enterprise schema filters
   * Supports multi-criteria queries with nested field filtering
   */ async searchFirestoreAdvanced(request) {
        return this.request("POST", "/firestore/search", request);
    }
    // ============================================================================
    // Configuration Management Endpoints
    // ============================================================================
    /**
   * Get all editable environment variables
   */ async getEnvVariables() {
        return this.request("GET", "/config/env");
    }
    /**
   * Get environment variables grouped by category
   */ async getEnvCategories() {
        return this.request("GET", "/config/env/categories");
    }
    /**
   * Update environment variables
   */ async updateEnvVariables(variables) {
        return this.request("POST", "/config/env", {
            variables
        });
    }
    /**
   * Test if environment variable changes took effect
   */ async testEnvChange(key) {
        return this.request("POST", "/config/env/test", {
            key
        });
    }
}
const apiClient = new RealEstateApiClient();
const __TURBOPACK__default__export__ = RealEstateApiClient;
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/hooks/useTriggerGitHubScrape.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useTriggerGitHubScrape",
    ()=>useTriggerGitHubScrape
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
;
;
function useTriggerGitHubScrape() {
    _s();
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [result, setResult] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const triggerScrape = async ({ pageCap = 20, geocode = 1, sites = [] })=>{
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            // The backend expects page_cap, geocode, sites
            const res = await __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].triggerGitHubScrape(sites);
            setResult(res);
            setLoading(false);
            return res;
        } catch (err) {
            setError(err.message || "Failed to trigger GitHub Actions scrape");
            setLoading(false);
            throw err;
        }
    };
    return {
        triggerScrape,
        loading,
        error,
        result
    };
}
_s(useTriggerGitHubScrape, "0rJtg/E9+fiowe8eKNooMN/xlkg=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/hooks/useKeepAlive.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useKeepAlive",
    ()=>useKeepAlive
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
"use client";
;
;
function useKeepAlive(options = {}) {
    _s();
    const { interval = 12 * 60 * 1000, enabled = ("TURBOPACK compile-time value", "development") === "production", pingFn = ()=>__TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClient"].healthCheck() } = options;
    const pingCountRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(0);
    const isMountedRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(true);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useKeepAlive.useEffect": ()=>{
            isMountedRef.current = true;
            if (!enabled) {
                console.log("[KeepAlive] Disabled - not pinging backend");
                return;
            }
            console.log(`[KeepAlive] Starting keep-alive pings (interval: ${interval / 60000} minutes)`);
            let timeoutId = null;
            const ping = {
                "useKeepAlive.useEffect.ping": async ()=>{
                    if (!isMountedRef.current || !enabled) return;
                    pingCountRef.current++;
                    const currentPing = pingCountRef.current;
                    try {
                        console.log(`[KeepAlive] Ping #${currentPing} at ${new Date().toLocaleTimeString()}`);
                        // Emit event for UI indicator
                        if ("TURBOPACK compile-time truthy", 1) {
                            window.dispatchEvent(new CustomEvent("keep-alive-ping", {
                                detail: {
                                    ping: currentPing,
                                    timestamp: new Date()
                                }
                            }));
                        }
                        await pingFn();
                        console.log(`[KeepAlive] Ping #${currentPing} successful - backend is awake`);
                    } catch (error) {
                        console.warn(`[KeepAlive] Ping #${currentPing} failed - backend may be waking up:`, error instanceof Error ? error.message : error);
                    }
                    // Schedule next ping
                    if (isMountedRef.current && enabled) {
                        timeoutId = setTimeout(ping, interval);
                    }
                }
            }["useKeepAlive.useEffect.ping"]; // Start pinging after initial delay (1 minute)
            // This gives the app time to load before starting keep-alive
            const initialDelay = 60 * 1000; // 1 minute
            console.log("[KeepAlive] Initial ping in 1 minute...");
            timeoutId = setTimeout({
                "useKeepAlive.useEffect": ()=>{
                    ping();
                }
            }["useKeepAlive.useEffect"], initialDelay);
            return ({
                "useKeepAlive.useEffect": ()=>{
                    isMountedRef.current = false;
                    if (timeoutId) {
                        clearTimeout(timeoutId);
                    }
                    console.log(`[KeepAlive] Stopped (total pings: ${pingCountRef.current})`);
                }
            })["useKeepAlive.useEffect"];
        }
    }["useKeepAlive.useEffect"], [
        enabled,
        interval,
        pingFn
    ]);
}
_s(useKeepAlive, "ErqyjOABEwO+ix415RFnWhCmYxk=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/api-axios.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "RealEstateApiClientAxios",
    ()=>RealEstateApiClientAxios,
    "apiClientAxios",
    ()=>apiClientAxios
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/axios/lib/axios.js [app-client] (ecmascript)");
;
class RealEstateApiClientAxios {
    axios;
    constructor(config = {}){
        this.axios = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$axios$2f$lib$2f$axios$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].create({
            baseURL: config.baseUrl || ("TURBOPACK compile-time value", "https://realtors-practice-api.onrender.com/api") || "https://realtors-practice-api.onrender.com/api",
            timeout: config.timeout || 120000,
            headers: {
                "Content-Type": "application/json",
                ...config.headers
            }
        });
        if (config.apiKey) {
            this.axios.defaults.headers.common["X-API-Key"] = config.apiKey;
        }
    }
    async request(method, endpoint, data, params) {
        const response = await this.axios.request({
            url: endpoint,
            method,
            data,
            params
        });
        return response.data;
    }
    // Example endpoint
    async getProperties(params) {
        return this.request("GET", "/data/master", undefined, params);
    }
}
const apiClientAxios = new RealEstateApiClientAxios();
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/hooks/useSWRProperties.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useSWRProperties",
    ()=>useSWRProperties
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$swr$2f$dist$2f$index$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/swr/dist/index/index.mjs [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2d$axios$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api-axios.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
;
;
function useSWRProperties(params = {}, refreshInterval = 0) {
    _s();
    const { data, error, isLoading, mutate } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$swr$2f$dist$2f$index$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["default"])([
        "properties",
        params
    ], {
        "useSWRProperties.useSWR": async (key)=>{
            return __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2d$axios$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["apiClientAxios"].getProperties(key[1]);
        }
    }["useSWRProperties.useSWR"], {
        refreshInterval
    });
    return {
        properties: data?.properties || [],
        total: data?.total || 0,
        loading: isLoading,
        error,
        mutate
    };
}
_s(useSWRProperties, "VRI3YSxoWYZ/jyoKeeIu/AvyMKw=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$swr$2f$dist$2f$index$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["default"]
    ];
});
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/hooks/useAuthAPI.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/**
 * Authentication API Hooks
 *
 * Provides hooks for interacting with the backend authentication API
 */ __turbopack_context__.s([
    "useAuthAPI",
    ()=>useAuthAPI
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/contexts/AuthContext.tsx [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
'use client';
;
;
const API_BASE_URL = ("TURBOPACK compile-time value", "https://realtors-practice-api.onrender.com/api") || 'http://localhost:5000';
function useAuthAPI() {
    _s();
    const { getIdToken } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAuth"])();
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    /**
   * Make an authenticated API request
   */ const makeAuthRequest = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[makeAuthRequest]": async (endpoint, options = {})=>{
            setLoading(true);
            setError(null);
            try {
                // Get Firebase ID token
                const token = await getIdToken();
                if (!token) {
                    throw new Error('No authentication token available');
                }
                // Make request with Authorization header
                const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        ...options.headers
                    }
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.message || data.error || 'Request failed');
                }
                setLoading(false);
                return {
                    success: true,
                    data
                };
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'An error occurred';
                setError(errorMessage);
                setLoading(false);
                return {
                    success: false,
                    error: errorMessage
                };
            }
        }
    }["useAuthAPI.useCallback[makeAuthRequest]"], [
        getIdToken
    ]);
    /**
   * Verify token with backend
   */ const verifyToken = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[verifyToken]": async (idToken)=>{
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/auth/verify-token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        idToken
                    })
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Token verification failed');
                }
                setLoading(false);
                return {
                    success: true,
                    data
                };
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Verification failed';
                setError(errorMessage);
                setLoading(false);
                return {
                    success: false,
                    error: errorMessage
                };
            }
        }
    }["useAuthAPI.useCallback[verifyToken]"], []);
    /**
   * Get current user from backend
   */ const getCurrentUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[getCurrentUser]": async ()=>{
            return makeAuthRequest('/api/auth/user/me');
        }
    }["useAuthAPI.useCallback[getCurrentUser]"], [
        makeAuthRequest
    ]);
    /**
   * Update current user profile
   */ const updateUserProfile = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[updateUserProfile]": async (updates)=>{
            return makeAuthRequest('/api/auth/user/me', {
                method: 'PUT',
                body: JSON.stringify(updates)
            });
        }
    }["useAuthAPI.useCallback[updateUserProfile]"], [
        makeAuthRequest
    ]);
    /**
   * Get user by ID (admin or self)
   */ const getUserById = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[getUserById]": async (uid)=>{
            return makeAuthRequest(`/api/auth/user/${uid}`);
        }
    }["useAuthAPI.useCallback[getUserById]"], [
        makeAuthRequest
    ]);
    /**
   * List all users (admin only)
   */ const listUsers = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[listUsers]": async (limit = 100)=>{
            return makeAuthRequest(`/api/auth/users?limit=${limit}`);
        }
    }["useAuthAPI.useCallback[listUsers]"], [
        makeAuthRequest
    ]);
    /**
   * Delete user (admin or self)
   */ const deleteUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[deleteUser]": async (uid)=>{
            return makeAuthRequest(`/api/auth/user/${uid}`, {
                method: 'DELETE'
            });
        }
    }["useAuthAPI.useCallback[deleteUser]"], [
        makeAuthRequest
    ]);
    /**
   * Update user role (admin only)
   */ const updateUserRole = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[updateUserRole]": async (uid, role)=>{
            return makeAuthRequest(`/api/auth/user/${uid}/role`, {
                method: 'PUT',
                body: JSON.stringify({
                    role
                })
            });
        }
    }["useAuthAPI.useCallback[updateUserRole]"], [
        makeAuthRequest
    ]);
    /**
   * Request password reset
   */ const requestPasswordReset = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[requestPasswordReset]": async (email)=>{
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/auth/password-reset`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email
                    })
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Password reset request failed');
                }
                setLoading(false);
                return {
                    success: true,
                    data
                };
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Request failed';
                setError(errorMessage);
                setLoading(false);
                return {
                    success: false,
                    error: errorMessage
                };
            }
        }
    }["useAuthAPI.useCallback[requestPasswordReset]"], []);
    /**
   * Logout from backend (revoke tokens)
   */ const logoutFromBackend = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[logoutFromBackend]": async ()=>{
            return makeAuthRequest('/api/auth/logout', {
                method: 'POST'
            });
        }
    }["useAuthAPI.useCallback[logoutFromBackend]"], [
        makeAuthRequest
    ]);
    /**
   * Check auth service health
   */ const checkAuthHealth = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuthAPI.useCallback[checkAuthHealth]": async ()=>{
            try {
                const response = await fetch(`${API_BASE_URL}/api/auth/health`);
                const data = await response.json();
                return {
                    success: true,
                    data
                };
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Health check failed';
                return {
                    success: false,
                    error: errorMessage
                };
            }
        }
    }["useAuthAPI.useCallback[checkAuthHealth]"], []);
    return {
        loading,
        error,
        verifyToken,
        getCurrentUser,
        updateUserProfile,
        getUserById,
        listUsers,
        deleteUser,
        updateUserRole,
        requestPasswordReset,
        logoutFromBackend,
        checkAuthHealth,
        makeAuthRequest
    };
}
_s(useAuthAPI, "O8LmjE1o22A1dmt7NdmHwLzia+o=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$contexts$2f$AuthContext$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAuth"]
    ];
});
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_e1302f8b._.js.map