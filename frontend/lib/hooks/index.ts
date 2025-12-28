/**
 * Custom Hooks for Real Estate Scraper UI
 *
 * This file exports all custom hooks for easy importing
 */

export { useApi, useApiMutation } from "./useApi";
export { usePolling } from "./useApi";
export { useProperties } from "./useProperties";
export { useSavedSearches } from "./useSavedSearches";
export { useSites } from "./useSites";
export { useFilters } from "./useFilters";
export { usePagination } from "./usePagination";

// NEW: Firestore Enterprise Hooks (v3.1)
export {
  useFirestoreDashboard,
  useFirestoreTopDeals,
  useFirestoreNewest,
  useFirestoreForSale,
  useFirestoreForRent,
  useFirestoreLand,
  useFirestorePremium,
  useFirestoreVerified,
  useFirestoreFurnished,
  useFirestoreTrending,
  useFirestoreHotDeals,
  useFirestoreByLga,
  useFirestoreByArea,
  useFirestoreNewOnMarket,
  useFirestoreSiteProperties,
  useFirestoreProperty,
  useFirestoreSiteStats,
  useFirestoreSearch,
  useFirestoreDashboardPolling,
  useFirestoreNewestPolling,
  useFirestoreHotDealsPolling,
} from "./useFirestore";

// Re-export types
export type { PropertyFilters, UsePaginationOptions } from "./useProperties";
export type { FilterState } from "./useFilters";
export type { UsePaginationOptions as PaginationOptions } from "./usePagination";
