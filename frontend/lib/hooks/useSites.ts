import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "./useApi";

/**
 * Custom hook for managing site configuration
 */
export function useSites() {
  const [togglingSite, setTogglingSite] = useState<string | null>(null);
  const [testingSite, setTestingSite] = useState<string | null>(null);

  // Fetch all sites
  const fetchSites = useCallback(async () => apiClient.listSites(), []);

  const { data, loading, error, refetch } = useApi(fetchSites);

  const sites = data?.sites || [];
  const totalSites = data?.total || 0;
  const enabledCount = data?.enabled || 0;
  const disabledCount = data?.disabled || 0;

  // Toggle site enabled/disabled
  const toggleSite = useCallback(
    async (siteKey: string) => {
      setTogglingSite(siteKey);
      try {
        const result = await apiClient.toggleSite(siteKey);
        await refetch();
        return {
          success: true,
          message: result.message,
          enabled: result.enabled,
        };
      } catch (error) {
        return { success: false, error };
      } finally {
        setTogglingSite(null);
      }
    },
    [refetch]
  );

  // Test site health
  const testSite = useCallback(async (siteKey: string) => {
    setTestingSite(siteKey);
    try {
      const result = await apiClient.siteHealth(siteKey);
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error };
    } finally {
      setTestingSite(null);
    }
  }, []);

  // Get site details
  const getSiteDetails = useCallback(async (siteKey: string) => {
    try {
      return await apiClient.getSite(siteKey);
    } catch (error) {
      throw error;
    }
  }, []);

  // Update site configuration
  const updateSite = useCallback(
    async (siteKey: string, updates: any) => {
      try {
        await apiClient.updateSite(siteKey, updates);
        await refetch();
        return { success: true };
      } catch (error) {
        return { success: false, error };
      }
    },
    [refetch]
  );

  // Get site statistics
  const getSiteStats = useCallback(async () => {
    try {
      return await apiClient.getSiteStats();
    } catch (error) {
      throw error;
    }
  }, []);

  return {
    // Data
    sites,
    totalSites,
    enabledCount,
    disabledCount,
    loading,
    error,

    // Actions
    toggleSite,
    testSite,
    getSiteDetails,
    updateSite,
    getSiteStats,
    refetch,

    // Loading states
    togglingSite,
    testingSite,
  };
}
