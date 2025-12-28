import { useState, useCallback } from "react";

export interface FilterState {
  location?: string;
  minPrice?: number;
  maxPrice?: number;
  bedrooms?: number;
  propertyType?: string;
  searchQuery?: string;
}

/**
 * Custom hook for managing filter state
 */
export function useFilters(initialFilters: FilterState = {}) {
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const [hasActiveFilters, setHasActiveFilters] = useState(false);

  // Update a single filter
  const updateFilter = useCallback((key: keyof FilterState, value: any) => {
    setFilters((prev) => {
      const newFilters = { ...prev, [key]: value };

      // Check if any filters are active
      const isActive = Object.values(newFilters).some(
        (val) => val !== undefined && val !== "" && val !== null
      );
      setHasActiveFilters(isActive);

      return newFilters;
    });
  }, []);

  // Update multiple filters at once
  const updateFilters = useCallback((newFilters: Partial<FilterState>) => {
    setFilters((prev) => {
      const merged = { ...prev, ...newFilters };

      // Check if any filters are active
      const isActive = Object.values(merged).some(
        (val) => val !== undefined && val !== "" && val !== null
      );
      setHasActiveFilters(isActive);

      return merged;
    });
  }, []);

  // Clear all filters
  const clearFilters = useCallback(() => {
    setFilters({});
    setHasActiveFilters(false);
  }, []);

  // Clear a specific filter
  const clearFilter = useCallback((key: keyof FilterState) => {
    setFilters((prev) => {
      const newFilters = { ...prev };
      delete newFilters[key];

      // Check if any filters are active
      const isActive = Object.values(newFilters).some(
        (val) => val !== undefined && val !== "" && val !== null
      );
      setHasActiveFilters(isActive);

      return newFilters;
    });
  }, []);

  // Reset to initial filters
  const resetFilters = useCallback(() => {
    setFilters(initialFilters);

    const isActive = Object.values(initialFilters).some(
      (val) => val !== undefined && val !== "" && val !== null
    );
    setHasActiveFilters(isActive);
  }, [initialFilters]);

  // Get filter count
  const activeFilterCount = Object.values(filters).filter(
    (val) => val !== undefined && val !== "" && val !== null
  ).length;

  return {
    filters,
    hasActiveFilters,
    activeFilterCount,
    updateFilter,
    updateFilters,
    clearFilters,
    clearFilter,
    resetFilters,
  };
}
