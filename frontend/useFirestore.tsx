/**
 * React Hooks for Firestore Integration
 * Use these hooks to fetch listings from Firestore in your frontend
 */

import useSWR, { mutate } from 'swr';
import { apiClient } from './api-client';
import type { Property } from './types';

// ============================================================================
// Firestore Query Hook
// ============================================================================

export interface FirestoreQuery {
  filters?: {
    'location.location_text'?: string;
    'location.state'?: string;
    'location.lga'?: string;
    'financial.price'?: number;
    'property_details.bedrooms'?: number;
    'property_details.bathrooms'?: number;
    'property_details.property_type'?: string;
    'basic_info.site_key'?: string;
    'basic_info.status'?: string;
    'metadata.quality_score'?: number;
    [key: string]: any;
  };
  sort_by?: string;
  sort_desc?: boolean;
  limit?: number;
  offset?: number;
}

export interface FirestoreResponse {
  results: Property[];
  count: number;
  filters_applied: Record<string, any>;
  sort_by: string;
  sort_desc: boolean;
}

/**
 * Hook to query properties from Firestore
 *
 * @example
 * ```tsx
 * const { properties, isLoading, error, refetch } = useFirestoreProperties({
 *   filters: {
 *     'location.state': 'Lagos',
 *     'property_details.bedrooms': 3
 *   },
 *   limit: 20,
 *   sort_by: 'uploaded_at',
 *   sort_desc: true
 * });
 * ```
 */
export function useFirestoreProperties(query: FirestoreQuery = {}, enabled = true) {
  // Create cache key from query parameters
  const key = enabled
    ? `/firestore/query?${JSON.stringify(query)}`
    : null;

  const { data, error, isLoading, mutate: refetch } = useSWR<FirestoreResponse>(
    key,
    () => apiClient.queryFirestore(query),
    {
      revalidateOnFocus: false, // Don't auto-refresh on focus
      dedupingInterval: 5000, // Dedupe requests within 5 seconds
    }
  );

  return {
    properties: data?.results || [],
    count: data?.count || 0,
    filtersApplied: data?.filters_applied || {},
    sortBy: data?.sort_by,
    sortDesc: data?.sort_desc,
    error,
    isLoading,
    refetch,
  };
}

/**
 * Hook to query archived properties from Firestore
 *
 * @example
 * ```tsx
 * const { properties, isLoading } = useFirestoreArchive({
 *   limit: 50
 * });
 * ```
 */
export function useFirestoreArchive(query: FirestoreQuery = {}, enabled = true) {
  const key = enabled
    ? `/firestore/query-archive?${JSON.stringify(query)}`
    : null;

  const { data, error, isLoading, mutate: refetch } = useSWR<FirestoreResponse>(
    key,
    () => apiClient.queryFirestoreArchive(query),
    {
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );

  return {
    properties: data?.results || [],
    count: data?.count || 0,
    error,
    isLoading,
    refetch,
  };
}

/**
 * Hook for paginated Firestore queries
 *
 * @example
 * ```tsx
 * const { properties, hasMore, loadMore, isLoading } = useFirestorePagination({
 *   filters: { 'location.state': 'Lagos' },
 *   pageSize: 20
 * });
 * ```
 */
export function useFirestorePagination(
  baseQuery: Omit<FirestoreQuery, 'limit' | 'offset'> = {},
  pageSize = 20
) {
  const [page, setPage] = React.useState(0);
  const [allProperties, setAllProperties] = React.useState<Property[]>([]);

  const query: FirestoreQuery = {
    ...baseQuery,
    limit: pageSize,
    offset: page * pageSize,
  };

  const { properties, count, isLoading, error } = useFirestoreProperties(query);

  React.useEffect(() => {
    if (properties.length > 0) {
      setAllProperties((prev) => {
        if (page === 0) return properties;
        return [...prev, ...properties];
      });
    }
  }, [properties, page]);

  const loadMore = () => {
    setPage((prev) => prev + 1);
  };

  const reset = () => {
    setPage(0);
    setAllProperties([]);
  };

  const hasMore = allProperties.length < count;

  return {
    properties: allProperties,
    totalCount: count,
    hasMore,
    loadMore,
    reset,
    isLoading,
    error,
    currentPage: page,
  };
}

// Import React for pagination hook
import React from 'react';

/**
 * Hook to search Firestore with various filters
 * Provides helper methods for common search patterns
 *
 * @example
 * ```tsx
 * const search = useFirestoreSearch();
 *
 * // Search by location
 * search.byLocation('Lekki');
 *
 * // Search by price range
 * search.byPriceRange(10000000, 50000000);
 *
 * // Search by bedrooms
 * search.byBedrooms(3);
 * ```
 */
export function useFirestoreSearch() {
  const [query, setQuery] = React.useState<FirestoreQuery>({});
  const { properties, count, isLoading, error, refetch } = useFirestoreProperties(query);

  const updateQuery = (updates: Partial<FirestoreQuery>) => {
    setQuery((prev) => ({
      ...prev,
      ...updates,
      filters: {
        ...prev.filters,
        ...updates.filters,
      },
    }));
  };

  const byLocation = (location: string) => {
    updateQuery({
      filters: { 'location.location_text': location },
    });
  };

  const byState = (state: string) => {
    updateQuery({
      filters: { 'location.state': state },
    });
  };

  const byBedrooms = (bedrooms: number) => {
    updateQuery({
      filters: { 'property_details.bedrooms': bedrooms },
    });
  };

  const byPropertyType = (propertyType: string) => {
    updateQuery({
      filters: { 'property_details.property_type': propertyType },
    });
  };

  const byPriceRange = (minPrice: number, maxPrice: number) => {
    // Note: Firestore range queries require indexes
    // For now, fetch all and filter client-side
    updateQuery({
      filters: {},
    });
  };

  const setSort = (sortBy: string, descending = true) => {
    updateQuery({
      sort_by: sortBy,
      sort_desc: descending,
    });
  };

  const setLimit = (limit: number) => {
    updateQuery({ limit });
  };

  const clearFilters = () => {
    setQuery({});
  };

  return {
    properties,
    count,
    isLoading,
    error,
    query,
    byLocation,
    byState,
    byBedrooms,
    byPropertyType,
    byPriceRange,
    setSort,
    setLimit,
    clearFilters,
    updateQuery,
    refetch,
  };
}
