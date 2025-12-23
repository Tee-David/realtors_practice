"use client";

import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";
import { SavedSearchCard } from "@/components/shared/saved-search-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiStatusBanner } from "@/components/ui/api-status-banner";
import {
  Plus,
  RefreshCw,
  Search,
  MapPin,
  Home,
  DollarSign,
  Bed,
} from "lucide-react";
import { toast } from "sonner";
import { PropertyQuery } from "@/lib/types";

/**
 * Saved Searches Page
 * Consolidates 10 API endpoints:
 * - POST /api/saved-searches/create
 * - GET /api/saved-searches
 * - PUT /api/saved-searches/{id}/update
 * - DELETE /api/saved-searches/{id}
 * - GET /api/saved-searches/{id}
 * - GET /api/saved-searches/matches
 * - GET /api/saved-searches/matches/new
 * - POST /api/saved-searches/{id}/notify
 * - PUT /api/saved-searches/{id}/settings
 * - POST /api/email/test
 */

export default function SavedSearchesPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newSearchName, setNewSearchName] = useState("");
  const [newSearchQuery, setNewSearchQuery] = useState<any>({});
  const [isCreating, setIsCreating] = useState(false);
  const [viewMatchesOpen, setViewMatchesOpen] = useState(false);
  const [matches, setMatches] = useState<any[]>([]);
  const [matchesLoading, setMatchesLoading] = useState(false);
  const [matchesError, setMatchesError] = useState<string | null>(null);
  const [activeSearch, setActiveSearch] = useState<any | null>(null);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editSearchName, setEditSearchName] = useState("");
  const [editSearchQuery, setEditSearchQuery] = useState<any>({});
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  // Fetch saved searches
  const listSavedSearches = useCallback(
    async () => apiClient.listSavedSearches(),
    []
  );
  const {
    data: searches,
    loading,
    error,
    refetch,
  } = useApi<any>(listSavedSearches);

  // Reset form
  const resetForm = () => {
    setNewSearchName("");
    setNewSearchQuery({});
    setShowCreateForm(false);
  };

  // Handle create new search
  const handleCreateSearch = async () => {
    if (!newSearchName.trim()) {
      toast.error("Please enter a search name");
      return;
    }

    // Validate at least one criteria
    const hasCriteria = Object.keys(newSearchQuery).some(
      (key) => newSearchQuery[key] !== undefined && newSearchQuery[key] !== ""
    );

    if (!hasCriteria) {
      toast.error("Please add at least one search criteria");
      return;
    }

    setIsCreating(true);
    try {
      const result = await apiClient.createSavedSearch({
        name: newSearchName,
        query: newSearchQuery,
        email_alerts: false,
      });
      toast.success("Saved search created!", {
        description: `You can now receive alerts for "${newSearchName}"`,
      });
      resetForm();
      refetch();
    } catch (error: any) {
      console.error("Failed to create saved search:", error);
      toast.error("Failed to create saved search", {
        description: error.message || "Please try again",
      });
    } finally {
      setIsCreating(false);
    }
  };

  // Handle view matches
  const handleViewMatches = async (search: any) => {
    setActiveSearch(search);
    setMatchesLoading(true);
    setMatchesError(null);
    setViewMatchesOpen(true);
    try {
      const result = await apiClient.getSavedSearchMatches(search.id, {
        limit: 100,
      });
      setMatches(result);
    } catch (error: any) {
      setMatchesError(error.message || "Failed to load matches");
      setMatches([]);
    } finally {
      setMatchesLoading(false);
    }
  };

  // Handle check new matches
  const handleCheckNewMatches = async (search: any) => {
    const loadingToast = toast.loading("Checking for new matches...");
    try {
      const newMatches = await apiClient.getNewSavedSearchMatches(search.id);
      toast.dismiss(loadingToast);
      if (newMatches.length > 0) {
        toast.success(`${newMatches.length} new properties found!`, {
          description: `New listings since last check`,
          duration: 5000,
        });
      } else {
        toast.info("No new matches since last check", {
          description: "We'll notify you when new properties are listed",
        });
      }
      refetch(); // Refresh to update counts
    } catch (error: any) {
      toast.dismiss(loadingToast);
      console.error("Failed to check new matches:", error);
      toast.error("Failed to check new matches", {
        description: error.message || "Please try again",
      });
    }
  };

  // Handle send notification
  const handleNotify = async (search: any) => {
    const loadingToast = toast.loading("Sending email notification...");
    try {
      await apiClient.notifySavedSearch(search.id);
      toast.dismiss(loadingToast);
      toast.success("Email notification sent!", {
        description: `Check your inbox for "${search.name}" matches`,
      });
    } catch (error: any) {
      toast.dismiss(loadingToast);
      console.error("Failed to send notification:", error);
      toast.error("Failed to send notification", {
        description: error.message || "Please check your email settings",
      });
    }
  };

  // Handle edit search
  const handleEditSearch = (search: any) => {
    setActiveSearch(search);
    setEditSearchName(search.name);
    setEditSearchQuery(search.query || {});
    setEditError(null);
    setEditModalOpen(true);
  };

  const handleEditSave = async () => {
    if (!editSearchName.trim()) {
      setEditError("Please enter a search name");
      return;
    }
    const hasCriteria = Object.keys(editSearchQuery).some(
      (key) => editSearchQuery[key] !== undefined && editSearchQuery[key] !== ""
    );
    if (!hasCriteria) {
      setEditError("Please add at least one search criteria");
      return;
    }
    setEditLoading(true);
    setEditError(null);
    try {
      await apiClient.updateSavedSearch(activeSearch.id, {
        name: editSearchName,
        query: editSearchQuery,
      });
      toast.success("Saved search updated", {
        description: `Search "${editSearchName}" updated successfully`,
      });
      setEditModalOpen(false);
      refetch();
    } catch (error: any) {
      setEditError(error.message || "Failed to update search");
    } finally {
      setEditLoading(false);
    }
  };

  // Handle delete search
  const handleDeleteSearch = async (searchId: string, searchName: string) => {
    // Confirm deletion
    if (!confirm(`Are you sure you want to delete "${searchName}"?`)) {
      return;
    }

    const loadingToast = toast.loading("Deleting search...");
    try {
      await apiClient.deleteSavedSearch(searchId);
      toast.dismiss(loadingToast);
      toast.success("Saved search deleted", {
        description: `"${searchName}" has been removed`,
      });
      refetch();
    } catch (error: any) {
      toast.dismiss(loadingToast);
      console.error("Failed to delete saved search:", error);
      toast.error("Failed to delete saved search", {
        description: error.message || "Please try again",
      });
    }
  };

  // Handle toggle email
  const handleToggleEmail = async (searchId: string, enabled: boolean) => {
    try {
      await apiClient.updateSavedSearch(searchId, { email_alerts: enabled });
      toast.success(
        enabled ? "Email alerts enabled ✅" : "Email alerts disabled",
        {
          description: enabled
            ? "You'll be notified when new properties match this search"
            : "You won't receive email notifications for this search",
        }
      );
      refetch();
    } catch (error: any) {
      console.error("Failed to update email settings:", error);
      toast.error("Failed to update email settings", {
        description: error.message || "Please try again",
      });
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white">
            Saved Searches
          </h1>
          <p className="text-sm sm:text-base text-slate-400 mt-1">
            Manage your saved property searches and email alerts
          </p>
        </div>
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={refetch}
            className="border-slate-600 hover:bg-slate-700 flex-1 sm:flex-none"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-blue-600 hover:bg-blue-700 flex-1 sm:flex-none"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Search
          </Button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <ApiStatusBanner message={error} onRetry={refetch} type="error" />
      )}

      {/* Create New Search Form */}
      {showCreateForm && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Search className="w-5 h-5" />
              Create New Saved Search
            </CardTitle>
            <p className="text-sm text-slate-400 mt-2">
              Set up criteria to automatically track properties matching your
              preferences
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Search Name */}
            <div className="space-y-2">
              <Label
                htmlFor="searchName"
                className="text-slate-300 font-medium"
              >
                Search Name *
              </Label>
              <Input
                id="searchName"
                placeholder="e.g. 3BR Apartments in Lekki under ₦50M"
                value={newSearchName}
                onChange={(e) => setNewSearchName(e.target.value)}
                className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                disabled={isCreating}
              />
            </div>

            {/* Search Criteria */}
            <div className="space-y-4 p-4 bg-slate-900/50 rounded-lg border border-slate-700">
              <h4 className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Home className="w-4 h-4" />
                Search Criteria
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Location */}
                <div className="space-y-2">
                  <Label
                    htmlFor="location"
                    className="text-slate-400 text-sm flex items-center gap-1"
                  >
                    <MapPin className="w-3 h-3" />
                    Location
                  </Label>
                  <Input
                    id="location"
                    placeholder="e.g. Lekki, Victoria Island"
                    value={newSearchQuery.location || ""}
                    onChange={(e) =>
                      setNewSearchQuery({
                        ...newSearchQuery,
                        location: e.target.value,
                      })
                    }
                    className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                    disabled={isCreating}
                  />
                </div>

                {/* Property Type */}
                <div className="space-y-2">
                  <Label
                    htmlFor="propertyType"
                    className="text-slate-400 text-sm"
                  >
                    Property Type
                  </Label>
                  <Select
                    value={newSearchQuery.property_type || "all"}
                    onValueChange={(value) =>
                      setNewSearchQuery({
                        ...newSearchQuery,
                        property_type: value === "all" ? undefined : value,
                      })
                    }
                    disabled={isCreating}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                      <SelectValue placeholder="Any type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any Type</SelectItem>
                      <SelectItem value="house">House</SelectItem>
                      <SelectItem value="apartment">Apartment</SelectItem>
                      <SelectItem value="land">Land</SelectItem>
                      <SelectItem value="commercial">Commercial</SelectItem>
                      <SelectItem value="duplex">Duplex</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Min Price */}
                <div className="space-y-2">
                  <Label
                    htmlFor="minPrice"
                    className="text-slate-400 text-sm flex items-center gap-1"
                  >
                    <DollarSign className="w-3 h-3" />
                    Min Price (₦)
                  </Label>
                  <Input
                    id="minPrice"
                    type="number"
                    placeholder="e.g. 5000000"
                    value={newSearchQuery.min_price || ""}
                    onChange={(e) =>
                      setNewSearchQuery({
                        ...newSearchQuery,
                        min_price: e.target.value
                          ? Number(e.target.value)
                          : undefined,
                      })
                    }
                    className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                    disabled={isCreating}
                  />
                </div>

                {/* Max Price */}
                <div className="space-y-2">
                  <Label htmlFor="maxPrice" className="text-slate-400 text-sm">
                    Max Price (₦)
                  </Label>
                  <Input
                    id="maxPrice"
                    type="number"
                    placeholder="e.g. 50000000"
                    value={newSearchQuery.max_price || ""}
                    onChange={(e) =>
                      setNewSearchQuery({
                        ...newSearchQuery,
                        max_price: e.target.value
                          ? Number(e.target.value)
                          : undefined,
                      })
                    }
                    className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                    disabled={isCreating}
                  />
                </div>

                {/* Bedrooms */}
                <div className="space-y-2">
                  <Label
                    htmlFor="bedrooms"
                    className="text-slate-400 text-sm flex items-center gap-1"
                  >
                    <Bed className="w-3 h-3" />
                    Min Bedrooms
                  </Label>
                  <Select
                    value={newSearchQuery.bedrooms?.toString() || "any"}
                    onValueChange={(value) =>
                      setNewSearchQuery({
                        ...newSearchQuery,
                        bedrooms: value === "any" ? undefined : Number(value),
                      })
                    }
                    disabled={isCreating}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any</SelectItem>
                      <SelectItem value="1">1+</SelectItem>
                      <SelectItem value="2">2+</SelectItem>
                      <SelectItem value="3">3+</SelectItem>
                      <SelectItem value="4">4+</SelectItem>
                      <SelectItem value="5">5+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Listing Type */}
                <div className="space-y-2">
                  <Label
                    htmlFor="listingType"
                    className="text-slate-400 text-sm"
                  >
                    Listing Type
                  </Label>
                  <Select
                    value={newSearchQuery.listing_type || "all"}
                    onValueChange={(value) =>
                      setNewSearchQuery({
                        ...newSearchQuery,
                        listing_type: value === "all" ? undefined : value,
                      })
                    }
                    disabled={isCreating}
                  >
                    <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any</SelectItem>
                      <SelectItem value="For Sale">For Sale</SelectItem>
                      <SelectItem value="For Rent">For Rent</SelectItem>
                      <SelectItem value="Short Let">Short Let</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 pt-2">
              <Button
                onClick={handleCreateSearch}
                disabled={isCreating}
                className="bg-blue-600 hover:bg-blue-700 flex-1 sm:flex-none"
              >
                {isCreating ? (
                  <>
                    <span className="animate-spin mr-2 w-4 h-4 border-b-2 border-white rounded-full inline-block"></span>
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Search
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={resetForm}
                disabled={isCreating}
                className="border-slate-600 hover:bg-slate-700"
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-64 w-full" />
          ))}
        </div>
      )}

      {/* Saved Searches List */}
      {!loading && searches && searches.length > 0 && (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              <span className="font-medium text-white">{searches.length}</span>{" "}
              saved {searches.length === 1 ? "search" : "searches"}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {searches.map((search: any) => (
              <SavedSearchCard
                key={search.id}
                search={search}
                onView={() => handleViewMatches(search)}
                onCheckNew={() => handleCheckNewMatches(search)}
                onNotify={() => handleNotify(search)}
                onEdit={() => handleEditSearch(search)}
                onDelete={() => handleDeleteSearch(search.id, search.name)}
                onToggleEmail={(enabled) =>
                  handleToggleEmail(search.id, enabled)
                }
              />
            ))}
          </div>

          {/* View Matches Modal */}
          {viewMatchesOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
              <div className="bg-slate-900 border border-slate-700 rounded-lg shadow-lg max-w-2xl w-full p-6 relative">
                <button
                  className="absolute top-3 right-3 text-slate-400 hover:text-white"
                  onClick={() => setViewMatchesOpen(false)}
                  aria-label="Close"
                >
                  ×
                </button>
                <h2 className="text-xl font-bold text-white mb-4">
                  Matches for "{activeSearch?.name}"
                </h2>
                {matchesLoading ? (
                  <div className="text-center py-8">
                    <span className="animate-spin inline-block w-6 h-6 border-b-2 border-white rounded-full mr-2"></span>
                    <span className="text-slate-300">
                      Loading properties...
                    </span>
                  </div>
                ) : matchesError ? (
                  <div className="text-center py-8 text-red-400">
                    {matchesError}
                  </div>
                ) : matches.length === 0 ? (
                  <div className="text-center py-8 text-slate-400">
                    No properties match this search yet.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-4">
                    {matches.map((property: any) => (
                      <div
                        key={property.id || property.listing_id}
                        className="bg-slate-800 border border-slate-700 rounded-lg p-4"
                      >
                        <div className="flex items-center gap-3">
                          <span className="font-bold text-white text-lg">
                            {property.title || property.location}
                          </span>
                          {property.price && (
                            <span className="text-green-400 font-semibold ml-2">
                              ₦{property.price.toLocaleString()}
                            </span>
                          )}
                        </div>
                        <div className="text-slate-400 text-sm mt-1">
                          {property.location}
                        </div>
                        <div className="flex gap-4 text-xs text-slate-500 mt-2">
                          {property.bedrooms !== undefined && (
                            <span>{property.bedrooms} beds</span>
                          )}
                          {property.bathrooms !== undefined && (
                            <span>{property.bathrooms} baths</span>
                          )}
                          {property.property_type && (
                            <span>{property.property_type}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Edit Saved Search Modal */}
          {editModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
              <div className="bg-slate-900 border border-slate-700 rounded-lg shadow-lg max-w-lg w-full p-6 relative">
                <button
                  className="absolute top-3 right-3 text-slate-400 hover:text-white"
                  onClick={() => setEditModalOpen(false)}
                  aria-label="Close"
                >
                  ×
                </button>
                <h2 className="text-xl font-bold text-white mb-4">
                  Edit Saved Search
                </h2>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label
                      htmlFor="editSearchName"
                      className="text-slate-300 font-medium"
                    >
                      Search Name *
                    </Label>
                    <Input
                      id="editSearchName"
                      value={editSearchName}
                      onChange={(e) => setEditSearchName(e.target.value)}
                      className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                      disabled={editLoading}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Location */}
                    <div className="space-y-2">
                      <Label
                        htmlFor="editLocation"
                        className="text-slate-400 text-sm flex items-center gap-1"
                      >
                        <MapPin className="w-3 h-3" />
                        Location
                      </Label>
                      <Input
                        id="editLocation"
                        value={editSearchQuery.location || ""}
                        onChange={(e) =>
                          setEditSearchQuery({
                            ...editSearchQuery,
                            location: e.target.value,
                          })
                        }
                        className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                        disabled={editLoading}
                      />
                    </div>
                    {/* Property Type */}
                    <div className="space-y-2">
                      <Label
                        htmlFor="editPropertyType"
                        className="text-slate-400 text-sm"
                      >
                        Property Type
                      </Label>
                      <Select
                        value={editSearchQuery.property_type || "all"}
                        onValueChange={(value) =>
                          setEditSearchQuery({
                            ...editSearchQuery,
                            property_type: value === "all" ? undefined : value,
                          })
                        }
                        disabled={editLoading}
                      >
                        <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                          <SelectValue placeholder="Any type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Any Type</SelectItem>
                          <SelectItem value="house">House</SelectItem>
                          <SelectItem value="apartment">Apartment</SelectItem>
                          <SelectItem value="land">Land</SelectItem>
                          <SelectItem value="commercial">Commercial</SelectItem>
                          <SelectItem value="duplex">Duplex</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    {/* Min Price */}
                    <div className="space-y-2">
                      <Label
                        htmlFor="editMinPrice"
                        className="text-slate-400 text-sm flex items-center gap-1"
                      >
                        <DollarSign className="w-3 h-3" />
                        Min Price (₦)
                      </Label>
                      <Input
                        id="editMinPrice"
                        type="number"
                        value={editSearchQuery.min_price || ""}
                        onChange={(e) =>
                          setEditSearchQuery({
                            ...editSearchQuery,
                            min_price: e.target.value
                              ? Number(e.target.value)
                              : undefined,
                          })
                        }
                        className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                        disabled={editLoading}
                      />
                    </div>
                    {/* Max Price */}
                    <div className="space-y-2">
                      <Label
                        htmlFor="editMaxPrice"
                        className="text-slate-400 text-sm"
                      >
                        Max Price (₦)
                      </Label>
                      <Input
                        id="editMaxPrice"
                        type="number"
                        value={editSearchQuery.max_price || ""}
                        onChange={(e) =>
                          setEditSearchQuery({
                            ...editSearchQuery,
                            max_price: e.target.value
                              ? Number(e.target.value)
                              : undefined,
                          })
                        }
                        className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                        disabled={editLoading}
                      />
                    </div>
                    {/* Bedrooms */}
                    <div className="space-y-2">
                      <Label
                        htmlFor="editBedrooms"
                        className="text-slate-400 text-sm flex items-center gap-1"
                      >
                        <Bed className="w-3 h-3" />
                        Min Bedrooms
                      </Label>
                      <Select
                        value={editSearchQuery.bedrooms?.toString() || "any"}
                        onValueChange={(value) =>
                          setEditSearchQuery({
                            ...editSearchQuery,
                            bedrooms:
                              value === "any" ? undefined : Number(value),
                          })
                        }
                        disabled={editLoading}
                      >
                        <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                          <SelectValue placeholder="Any" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="any">Any</SelectItem>
                          <SelectItem value="1">1+</SelectItem>
                          <SelectItem value="2">2+</SelectItem>
                          <SelectItem value="3">3+</SelectItem>
                          <SelectItem value="4">4+</SelectItem>
                          <SelectItem value="5">5+</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    {/* Listing Type */}
                    <div className="space-y-2">
                      <Label
                        htmlFor="editListingType"
                        className="text-slate-400 text-sm"
                      >
                        Listing Type
                      </Label>
                      <Select
                        value={editSearchQuery.listing_type || "all"}
                        onValueChange={(value) =>
                          setEditSearchQuery({
                            ...editSearchQuery,
                            listing_type: value === "all" ? undefined : value,
                          })
                        }
                        disabled={editLoading}
                      >
                        <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                          <SelectValue placeholder="Any" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Any</SelectItem>
                          <SelectItem value="For Sale">For Sale</SelectItem>
                          <SelectItem value="For Rent">For Rent</SelectItem>
                          <SelectItem value="Short Let">Short Let</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  {editError && (
                    <div className="text-red-400 text-sm mt-2">{editError}</div>
                  )}
                  <div className="flex items-center gap-3 pt-2">
                    <Button
                      onClick={handleEditSave}
                      disabled={editLoading}
                      className="bg-blue-600 hover:bg-blue-700 flex-1 sm:flex-none"
                    >
                      {editLoading ? (
                        <>
                          <span className="animate-spin mr-2 w-4 h-4 border-b-2 border-white rounded-full inline-block"></span>
                          Saving...
                        </>
                      ) : (
                        <>Save Changes</>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setEditModalOpen(false)}
                      disabled={editLoading}
                      className="border-slate-600 hover:bg-slate-700"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Empty State */}
      {!loading && (!searches || searches.length === 0) && (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="py-12 text-center">
            <Search className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No Saved Searches Yet
            </h3>
            <p className="text-slate-400 mb-6">
              Create your first saved search to get email alerts when new
              properties match your criteria
            </p>
            <Button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Search
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
