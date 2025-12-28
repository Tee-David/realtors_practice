import { useState, useCallback, useEffect } from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "./useApi";

export interface PropertyFilters {
  location?: string;
  minPrice?: number;
  maxPrice?: number;
  bedrooms?: number;
  propertyType?: string;
  searchQuery?: string;
}

export interface UsePaginationOptions {
  initialPage?: number;
  itemsPerPage?: number;
}

/**
 * Custom hook for managing property data with filters and pagination
 */
export function useProperties(
  filters: PropertyFilters = {},
  paginationOptions: UsePaginationOptions = {}
) {
  const { initialPage = 1, itemsPerPage = 20 } = paginationOptions;

  const [currentPage, setCurrentPage] = useState(initialPage);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  // Calculate pagination params
  const offset = (currentPage - 1) * itemsPerPage;

  // Build query params
  const getQueryParams = useCallback(() => {
    const params: any = {
      limit: itemsPerPage,
      offset,
    };

    if (filters.location) params.location = filters.location;
    if (filters.minPrice) params.min_price = filters.minPrice;
    if (filters.maxPrice) params.max_price = filters.maxPrice;
    if (filters.bedrooms) params.bedrooms = filters.bedrooms;
    if (filters.propertyType) params.property_type = filters.propertyType;

    return params;
  }, [filters, itemsPerPage, offset]);

  // Fetch properties based on filters
  const fetchProperties = useCallback(async () => {
    if (filters.searchQuery) {
      // Use natural language search
      return apiClient.naturalLanguageSearch(filters.searchQuery);
    } else {
      // Use regular data fetch
      return apiClient.getAllData(getQueryParams());
    }
  }, [filters.searchQuery, getQueryParams]);

  const { data, loading, error, refetch } = useApi(fetchProperties);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [
    filters.location,
    filters.minPrice,
    filters.maxPrice,
    filters.bedrooms,
    filters.propertyType,
    filters.searchQuery,
  ]);

  // Pagination helpers
  const totalPages = data?.total ? Math.ceil(data.total / itemsPerPage) : 1;

  const goToPage = useCallback(
    (page: number) => {
      setCurrentPage(Math.max(1, Math.min(page, totalPages)));
    },
    [totalPages]
  );

  const nextPage = useCallback(() => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  }, [currentPage, totalPages]);

  const prevPage = useCallback(() => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  }, [currentPage]);

  // Export functionality
  const exportData = useCallback(
    async (format: "csv" | "xlsx" | "json") => {
      try {
        const result = await apiClient.generateExport({
          format,
          ...getQueryParams(),
        });
        return result;
      } catch (error) {
        throw error;
      }
    },
    [getQueryParams]
  );

  return {
    // Data
    properties: data?.properties || [],
    total: data?.total || 0,
    loading,
    error,

    // Pagination
    currentPage,
    totalPages,
    itemsPerPage,
    goToPage,
    nextPage,
    prevPage,

    // View mode
    viewMode,
    setViewMode,

    // Actions
    refetch,
    exportData,
  };
}
