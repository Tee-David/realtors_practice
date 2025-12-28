/**
 * Custom React Hooks for Firestore Enterprise Endpoints (v3.1)
 * 40-300x faster than legacy endpoints
 *
 * These hooks provide convenient access to the 16 new Firestore endpoints
 * with automatic data fetching, error handling, caching, and loading states.
 */

import { useCallback } from 'react';
import { apiClient } from '@/lib/api';
import type {
  FirestoreProperty,
  FirestoreDashboardStats,
  FirestoreSearchRequest,
  FirestoreSiteStats,
  FirestoreListResponse,
  PropertyData,
} from '@/lib/types';
import { useApi, usePolling } from './useApi';

/**
 * Hook: Fetch Firestore Dashboard Statistics
 * GET /api/firestore/dashboard
 *
 * Replaces _Dashboard Excel sheet - 40-300x faster!
 * Returns: total_properties, price_range, type_breakdown, site_breakdown, quality_distribution
 *
 * @example
 * const { data: stats, loading, error } = useFirestoreDashboard();
 * if (loading) return <div>Loading...</div>;
 * return <div>Total: {stats?.total_properties} properties</div>;
 */
export function useFirestoreDashboard() {
  const fetchDashboard = useCallback(async () => {
    return await apiClient.getFirestoreDashboard();
  }, []);

  return useApi<FirestoreDashboardStats>(fetchDashboard);
}

/**
 * Hook: Fetch Top Deals (Cheapest Properties)
 * GET /api/firestore/top-deals
 *
 * Replaces _Top_100_Cheapest Excel sheet
 * Returns: Array of properties sorted by price (ascending)
 *
 * @example
 * const { data: deals, loading } = useFirestoreTopDeals({ limit: 50 });
 * return <div>{deals?.length} cheapest properties found</div>;
 */
export function useFirestoreTopDeals(params?: { limit?: number; min_quality?: number }) {
  const fetchTopDeals = useCallback(async () => {
    return await apiClient.getFirestoreTopDeals(params);
  }, [params]);

  return useApi<any>(fetchTopDeals);
}

/**
 * Hook: Fetch Newest Listings
 * GET /api/firestore/newest
 *
 * Replaces _Newest_Listings Excel sheet
 * Returns: Array of recently added properties
 *
 * @example
 * const { data: newest, refetch } = useFirestoreNewest({ limit: 20 });
 * return <div onClick={() => refetch()}>Refresh Recent Listings</div>;
 */
export function useFirestoreNewest(params?: { limit?: number; days_back?: number; site_key?: string }) {
  const fetchNewest = useCallback(async () => {
    return await apiClient.getFirestoreNewest(params);
  }, [params]);

  return useApi<any>(fetchNewest);
}

/**
 * Hook: Fetch For Sale Properties
 * GET /api/firestore/for-sale
 *
 * Replaces _For_Sale Excel sheet
 * Uses heuristics: listing_type === 'sale'
 *
 * @example
 * const { data: forSale } = useFirestoreForSale({ limit: 100 });
 */
export function useFirestoreForSale(params?: { limit?: number; price_max?: number }) {
  const fetchForSale = useCallback(async () => {
    return await apiClient.getFirestoreForSale(params);
  }, [params]);

  return useApi<any>(fetchForSale);
}

/**
 * Hook: Fetch For Rent Properties
 * GET /api/firestore/for-rent
 *
 * Replaces _For_Rent Excel sheet
 * Uses heuristics: listing_type === 'rent'
 *
 * @example
 * const { data: forRent } = useFirestoreForRent({ limit: 100 });
 */
export function useFirestoreForRent(params?: { limit?: number; price_max?: number }) {
  const fetchForRent = useCallback(async () => {
    return await apiClient.getFirestoreForRent(params);
  }, [params]);

  return useApi<any>(fetchForRent);
}

/**
 * Hook: Fetch Land Only Properties
 * GET /api/firestore/land
 *
 * Replaces _Land_Only Excel sheet
 * Filters: property_type === 'Land'
 *
 * @example
 * const { data: lands } = useFirestoreLand({ limit: 50 });
 */
export function useFirestoreLand(params?: { limit?: number; price_max?: number }) {
  const fetchLand = useCallback(async () => {
    return await apiClient.getFirestoreLand(params);
  }, [params]);

  return useApi<any>(fetchLand);
}

/**
 * Hook: Fetch Premium Properties
 * GET /api/firestore/premium
 *
 * Replaces _4BR_Plus Excel sheet
 * Filters: 4+ bedrooms OR price >= 100M with premium features
 *
 * @example
 * const { data: premium } = useFirestorePremium({ limit: 50 });
 */
export function useFirestorePremium(params?: { limit?: number; min_bedrooms?: number; price_max?: number }) {
  const fetchPremium = useCallback(async () => {
    return await apiClient.getFirestorePremium(params);
  }, [params]);

  return useApi<any>(fetchPremium);
}

/**
 * Hook: Fetch Verified Properties Only
 * GET /api/firestore/properties/verified
 *
 * NEW in v3.1 - Filter verified properties
 * Shows only properties with verification_status === 'verified'
 *
 * @example
 * const { data: verified } = useFirestoreVerified({ limit: 50 });
 */
export function useFirestoreVerified(params?: { limit?: number; offset?: number }) {
  const fetchVerified = useCallback(async () => {
    return await apiClient.getFirestoreVerified(params);
  }, [params]);

  return useApi<any>(fetchVerified);
}

/**
 * Hook: Fetch Furnished Properties
 * GET /api/firestore/properties/furnished
 *
 * NEW in v3.1 - Filter by furnishing status
 * Filters: furnishing in ['furnished', 'semi-furnished', 'unfurnished']
 *
 * @example
 * const { data: furnished } = useFirestoreFurnished({ limit: 50, furnishing_type: 'furnished' });
 */
export function useFirestoreFurnished(params?: {
  limit?: number;
  offset?: number;
  furnishing_type?: 'furnished' | 'semi-furnished' | 'unfurnished';
}) {
  const fetchFurnished = useCallback(async () => {
    return await apiClient.getFirestoreFurnished(params);
  }, [params]);

  return useApi<any>(fetchFurnished);
}

/**
 * Hook: Fetch Trending Properties
 * GET /api/firestore/properties/trending
 *
 * NEW in v3.1 - High view count properties
 * Properties automatically trending based on view_count
 *
 * @example
 * const { data: trending } = useFirestoreTrending({ limit: 20 });
 */
export function useFirestoreTrending(params?: { limit?: number; min_views?: number }) {
  const fetchTrending = useCallback(async () => {
    return await apiClient.getFirestoreTrending(params);
  }, [params]);

  return useApi<any>(fetchTrending);
}

/**
 * Hook: Fetch Hot Deal Properties
 * GET /api/firestore/properties/hot-deals
 *
 * NEW in v3.1 - Auto-tagged hot deals
 * Filters: tags.hot_deal === true (price per bedroom < 15M)
 *
 * @example
 * const { data: hotDeals } = useFirestoreHotDeals({ limit: 30 });
 */
export function useFirestoreHotDeals(params?: { limit?: number; offset?: number }) {
  const fetchHotDeals = useCallback(async () => {
    return await apiClient.getFirestoreHotDeals(params);
  }, [params]);

  return useApi<any>(fetchHotDeals);
}

/**
 * Hook: Fetch Properties by LGA (Local Government Area)
 * GET /api/firestore/properties/by-lga/<lga>
 *
 * NEW in v3.1 - Location-based filtering
 * Available LGAs: Eti-Osa, Lagos Island, Ikoyi, Surulere, Mushin, etc.
 *
 * @example
 * const { data: properties } = useFirestoreByLga('Eti-Osa', { limit: 50 });
 */
export function useFirestoreByLga(
  lga: string,
  params?: { limit?: number; offset?: number; sort_by?: string; sort_desc?: boolean }
) {
  const fetchByLga = useCallback(async () => {
    return await apiClient.getFirestoreByLga(lga, params);
  }, [lga, params]);

  return useApi<any>(fetchByLga);
}

/**
 * Hook: Fetch Properties by Area
 * GET /api/firestore/properties/by-area/<area>
 *
 * NEW in v3.1 - Neighborhood filtering
 * Examples: 'Lekki Phase 1', 'Victoria Island', 'Yaba'
 *
 * @example
 * const { data: lekki } = useFirestoreByArea('Lekki Phase 1', { limit: 50 });
 */
export function useFirestoreByArea(
  area: string,
  params?: { limit?: number; offset?: number; sort_by?: string; sort_desc?: boolean }
) {
  const fetchByArea = useCallback(async () => {
    return await apiClient.getFirestoreByArea(area, params);
  }, [area, params]);

  return useApi<any>(fetchByArea);
}

/**
 * Hook: Fetch New On Market Properties
 * GET /api/firestore/properties/new-on-market
 *
 * NEW in v3.1 - Recently listed properties
 * Shows properties recently added to market
 *
 * @example
 * const { data: newListings } = useFirestoreNewOnMarket({ limit: 50, days_back: 7 });
 */
export function useFirestoreNewOnMarket(params?: {
  limit?: number;
  offset?: number;
  days_back?: number;
}) {
  const fetchNewOnMarket = useCallback(async () => {
    return await apiClient.getFirestoreNewOnMarket(params);
  }, [params]);

  return useApi<any>(fetchNewOnMarket);
}

/**
 * Hook: Get Site Specific Properties
 * GET /api/firestore/site/<site_key>
 *
 * Get all properties from a specific site (npc, cwlagos, jiji, etc.)
 * Replaces per-site Excel sheets
 *
 * @example
 * const { data: npcProperties } = useFirestoreSiteProperties('npc', { limit: 50 });
 */
export function useFirestoreSiteProperties(
  siteKey: string,
  params?: { limit?: number; offset?: number }
) {
  const fetchSiteProperties = useCallback(async () => {
    return await apiClient.getFirestoreSiteProperties(siteKey, params);
  }, [siteKey, params]);

  return useApi<any>(fetchSiteProperties);
}

/**
 * Hook: Get Single Property Details
 * GET /api/firestore/property/<hash>
 *
 * Fetch complete details for a single property including all 9 categories
 *
 * @example
 * const { data: property } = useFirestoreProperty('abc123def456...');
 */
export function useFirestoreProperty(propertyHash: string) {
  const fetchProperty = useCallback(async () => {
    return await apiClient.getFirestoreProperty(propertyHash);
  }, [propertyHash]);

  return useApi<any>(fetchProperty);
}

/**
 * Hook: Get Site Statistics
 * GET /api/firestore/site-stats/<site_key>
 *
 * Get statistics for a specific site:
 * total_properties, price_range, type_breakdown, quality_distribution
 *
 * @example
 * const { data: stats } = useFirestoreSiteStats('npc');
 */
export function useFirestoreSiteStats(siteKey: string) {
  const fetchSiteStats = useCallback(async () => {
    return await apiClient.getFirestoreSiteStats(siteKey);
  }, [siteKey]);

  return useApi<FirestoreSiteStats>(fetchSiteStats);
}

/**
 * Hook: Advanced Search with Multiple Filters
 * POST /api/firestore/search
 *
 * Most powerful query - supports multi-criteria search with nested field filters
 * Supports filtering by: location, area, LGA, price range, bedrooms, bathrooms,
 * property_type, furnishing, condition, listing_type, quality score, amenities, etc.
 *
 * @example
 * const { data: results } = useFirestoreSearch({
 *   filters: {
 *     location: 'Lekki',
 *     furnishing: 'furnished',
 *     is_premium: true,
 *     quality_score_min: 0.8
 *   },
 *   sort_by: 'price',
 *   limit: 50
 * });
 */
export function useFirestoreSearch(request: FirestoreSearchRequest) {
  const fetchSearch = useCallback(async () => {
    return await apiClient.searchFirestoreAdvanced(request);
  }, [request]);

  return useApi<any>(fetchSearch);
}

/**
 * Hook: Poll Firestore Dashboard (Real-time Updates)
 * Automatically refetch dashboard stats at intervals
 *
 * @example
 * const { data: stats } = useFirestoreDashboardPolling({ interval: 30000 }); // 30 seconds
 */
export function useFirestoreDashboardPolling(options?: { interval?: number }) {
  const fetchDashboard = useCallback(async () => {
    return await apiClient.getFirestoreDashboard();
  }, []);

  return usePolling<FirestoreDashboardStats>(
    fetchDashboard,
    options?.interval || 60000 // Default 1 minute
  );
}

/**
 * Hook: Poll Firestore Newest Listings (Real-time Updates)
 * Automatically refetch newest listings at intervals
 *
 * @example
 * const { data: newest } = useFirestoreNewestPolling({ limit: 10, interval: 10000 }); // 10 seconds
 */
export function useFirestoreNewestPolling(
  params?: { limit?: number; days_back?: number },
  options?: { interval?: number }
) {
  const fetchNewest = useCallback(async () => {
    return await apiClient.getFirestoreNewest(params);
  }, [params]);

  return usePolling<any>(
    fetchNewest,
    options?.interval || 10000 // Default 10 seconds
  );
}

/**
 * Hook: Poll Hot Deals (Real-time Updates)
 * Automatically refetch hot deals at intervals
 *
 * @example
 * const { data: hotDeals } = useFirestoreHotDealsPolling({ interval: 30000 }); // 30 seconds
 */
export function useFirestoreHotDealsPolling(options?: { interval?: number }) {
  const fetchHotDeals = useCallback(async () => {
    return await apiClient.getFirestoreHotDeals();
  }, []);

  return usePolling<any>(
    fetchHotDeals,
    options?.interval || 30000 // Default 30 seconds
  );
}
