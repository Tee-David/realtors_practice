import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "./useApi";

/**
 * Custom hook for managing saved searches
 */
export function useSavedSearches() {
  const [creatingSearch, setCreatingSearch] = useState(false);
  const [updatingSearch, setUpdatingSearch] = useState<string | null>(null);
  const [deletingSearch, setDeletingSearch] = useState<string | null>(null);

  // Fetch all saved searches
  const fetchSavedSearches = useCallback(
    async () => apiClient.listSavedSearches(),
    []
  );

  const {
    data: searches,
    loading,
    error,
    refetch,
  } = useApi(fetchSavedSearches);

  // Create a new saved search
  const createSearch = useCallback(
    async (searchData: {
      name: string;
      query: any;
      email_alerts?: boolean;
    }) => {
      setCreatingSearch(true);
      try {
        await apiClient.createSavedSearch(searchData);
        await refetch();
        return { success: true };
      } catch (error) {
        return { success: false, error };
      } finally {
        setCreatingSearch(false);
      }
    },
    [refetch]
  );

  // Update a saved search
  const updateSearch = useCallback(
    async (searchId: string, updates: any) => {
      setUpdatingSearch(searchId);
      try {
        await apiClient.updateSavedSearch(searchId, updates);
        await refetch();
        return { success: true };
      } catch (error) {
        return { success: false, error };
      } finally {
        setUpdatingSearch(null);
      }
    },
    [refetch]
  );

  // Delete a saved search
  const deleteSearch = useCallback(
    async (searchId: string) => {
      setDeletingSearch(searchId);
      try {
        await apiClient.deleteSavedSearch(searchId);
        await refetch();
        return { success: true };
      } catch (error) {
        return { success: false, error };
      } finally {
        setDeletingSearch(null);
      }
    },
    [refetch]
  );

  // Toggle email alerts for a search
  const toggleEmailAlerts = useCallback(
    async (searchId: string, enabled: boolean) => {
      return updateSearch(searchId, { email_alerts: enabled });
    },
    [updateSearch]
  );

  // Get matches for a specific search
  const getSearchMatches = useCallback(async (searchId: string) => {
    try {
      const search = await apiClient.getSavedSearch(searchId);
      // Use the search query to fetch matching properties
      return apiClient.getAllData();
    } catch (error) {
      throw error;
    }
  }, []);

  return {
    // Data
    searches: searches || [],
    loading,
    error,

    // Actions
    createSearch,
    updateSearch,
    deleteSearch,
    toggleEmailAlerts,
    getSearchMatches,
    refetch,

    // Loading states
    creatingSearch,
    updatingSearch,
    deletingSearch,
  };
}
