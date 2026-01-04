"use client";

import { useState, useCallback, useEffect } from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";
import { PropertyCard } from "@/components/shared/property-card";
import { PropertyDetailsModal } from "@/components/shared/property-details-modal";
import { SearchBar } from "@/components/shared/search-bar";
import { FilterPanel } from "@/components/shared/filter-panel";
import { Pagination } from "@/components/shared/pagination";
import { ExportButton } from "@/components/properties/export-button";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Grid,
  List,
  RefreshCw,
  Filter,
  X,
  Home,
  TrendingUp,
  MapPin,
  Sliders,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Grid3x3,
  Grid2x2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

/**
 * Data Explorer Page - Advanced Filtering & Search
 * Uses Firestore-optimized endpoints with legacy fallback
 */

interface Filters {
  location?: string;
  minPrice?: number;
  maxPrice?: number;
  bedrooms?: number;
  bathrooms?: number;
  propertyType?: string;
  listingType?: "For Sale" | "For Rent" | "Short Let";
  siteKey?: string;
  amenities?: string[];
}

type ListingTypeOption = {
  value: "For Sale" | "For Rent" | "Short Let" | undefined;
  label: string;
  icon: any;
  color: string;
  bgColor: string;
  borderColor: string;
};

type ViewMode = "list" | "grid-2" | "grid-3" | "grid-4" | "grid-5" | "grid-6";

export default function DataExplorerPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<Filters>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState<ViewMode>("grid-2");
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [desktopFiltersOpen, setDesktopFiltersOpen] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<any | null>(null);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  // Disable quality filter by default - let users see all properties
  const [hideIncompleteListing, setHideIncompleteListings] = useState(false);
  const [itemsPerPage, setItemsPerPage] = useState(20);

  // Listing type options
  const listingTypes: ListingTypeOption[] = [
    {
      value: undefined,
      label: "All Properties",
      icon: Home,
      color: "text-blue-400",
      bgColor: "bg-blue-500/20",
      borderColor: "border-blue-500/30",
    },
    {
      value: "For Sale",
      label: "For Sale",
      icon: TrendingUp,
      color: "text-green-400",
      bgColor: "bg-green-500/20",
      borderColor: "border-green-500/30",
    },
    {
      value: "For Rent",
      label: "For Rent",
      icon: Home,
      color: "text-purple-400",
      bgColor: "bg-purple-500/20",
      borderColor: "border-purple-500/30",
    },
    {
      value: "Short Let",
      label: "Short Let",
      icon: Sparkles,
      color: "text-orange-400",
      bgColor: "bg-orange-500/20",
      borderColor: "border-orange-500/30",
    },
  ];

  // Fetch properties using Firestore-optimized endpoints with fallback
  const getAllData = useCallback(async () => {
    const params: any = {
      limit: itemsPerPage,
      offset: (currentPage - 1) * itemsPerPage,
      // Filter out low-quality listings (quality_score < 40)
      min_quality_score: hideIncompleteListing ? 40 : 0,
    };

    try {
      // Check if we have any filters (excluding listingType which is handled separately)
      const hasFilters = searchQuery ||
        filters.location ||
        filters.minPrice ||
        filters.maxPrice ||
        filters.bedrooms ||
        filters.bathrooms ||
        filters.propertyType ||
        filters.siteKey ||
        (filters.amenities && filters.amenities.length > 0);

      // ALWAYS use searchFirestore when there are any filters - it handles all cases properly
      if (hasFilters || filters.listingType) {
        return await apiClient.searchFirestore({
          query: searchQuery || undefined,
          location: filters.location,
          property_type: filters.propertyType,
          min_price: filters.minPrice,
          max_price: filters.maxPrice,
          min_bedrooms: filters.bedrooms, // API expects min_bedrooms
          min_bathrooms: filters.bathrooms, // API expects min_bathrooms (not bathrooms)
          listing_type: filters.listingType,
          site_key: filters.siteKey,
          ...params,
        });
      }

      // Default to For Sale endpoint when no filters at all
      return await apiClient.getFirestoreForSale(params);
    } catch (error: any) {
      console.error('[DataExplorer] API Error:', error);
      // Return empty result with error message instead of throwing
      return {
        properties: [],
        total: 0,
        error: error.message || 'Failed to fetch properties'
      };
    }
  }, [currentPage, searchQuery, filters, hideIncompleteListing, itemsPerPage]);

  const { data, loading, error, refetch } = useApi<any>(getAllData);

  // Trigger refetch when search, filters, or quality filter changes
  useEffect(() => {
    refetch();
  }, [searchQuery, filters, currentPage, hideIncompleteListing, itemsPerPage, refetch]);

  const rawProperties = data?.properties || [];
  const totalCount = data?.total || 0;

  // Enterprise-grade quality filtering
  const isPropertyComplete = (property: any): boolean => {
    const normalized = property.basic_info || property;
    const title = normalized.basic_info?.title || normalized.title || '';
    const price = normalized.financial?.price || normalized.price || 0;
    const location = normalized.location?.area || normalized.location || '';

    // Consider a property complete if:
    // - Has a descriptive title (> 10 chars)
    // - Has a price > 0
    // - Has location info
    return title.length > 10 && price > 0 && location.length > 0;
  };

  // Apply client-side quality filter
  const properties = hideIncompleteListing
    ? rawProperties.filter(isPropertyComplete)
    : rawProperties;

  const filteredCount = hideIncompleteListing
    ? properties.length
    : totalCount;

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handleClearFilters = () => {
    setFilters({});
    setSearchQuery("");
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleItemsPerPageChange = (value: number) => {
    // Warn user if selecting large pagination (performance impact)
    if (value > 200 && (searchQuery || Object.keys(filters).length > 0)) {
      console.warn('[DataExplorer] Large pagination with filters may impact performance');
    }
    setItemsPerPage(value);
    setCurrentPage(1); // Reset to first page when changing items per page
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handlePropertyClick = (property: any) => {
    setSelectedProperty(property);
    setDetailsModalOpen(true);
  };

  const handleModalClose = () => {
    setDetailsModalOpen(false);
    setSelectedProperty(null);
  };

  const handleNavigate = (page: string) => {
    window.dispatchEvent(new CustomEvent("navigate", { detail: { page } }));
  };

  const activeFilterCount = Object.keys(filters).filter(
    (key) =>
      filters[key as keyof Filters] !== undefined &&
      filters[key as keyof Filters] !== ""
  ).length;

  const hasActiveFilters = activeFilterCount > 0 || searchQuery;

  // Get grid class based on view mode with mobile-first responsive design
  const getGridClass = () => {
    switch (viewMode) {
      case "list":
        return "grid grid-cols-1 gap-4";
      case "grid-2":
        return "grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6";
      case "grid-3":
        return "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6";
      case "grid-4":
        return "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5";
      case "grid-5":
        return "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 sm:gap-3";
      case "grid-6":
        return "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 sm:gap-3";
      default:
        return "grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6";
    }
  };

  // Get display label for view mode
  const getViewModeLabel = (mode: ViewMode) => {
    switch (mode) {
      case "list":
        return "List View";
      case "grid-2":
        return "2 Columns";
      case "grid-3":
        return "3 Columns";
      case "grid-4":
        return "4 Columns";
      case "grid-5":
        return "5 Columns";
      case "grid-6":
        return "6 Columns";
      default:
        return "Grid View";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Mobile Filter Overlay */}
      {mobileFiltersOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-black/80 backdrop-blur-sm"
            onClick={() => setMobileFiltersOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 w-full max-w-sm bg-slate-900 border-r border-slate-800 shadow-xl overflow-y-auto">
            <div className="sticky top-0 z-10 bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Sliders className="w-5 h-5" />
                Filters
                {activeFilterCount > 0 && (
                  <span className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
                    {activeFilterCount}
                  </span>
                )}
              </h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setMobileFiltersOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            <div className="p-4">
              <FilterPanel
                filters={filters}
                onFilterChange={handleFilterChange}
                onClear={handleClearFilters}
              />
            </div>
          </div>
        </div>
      )}

      <div className="flex">
        {/* Desktop Sidebar - Conditionally rendered */}
        {desktopFiltersOpen && (
          <aside className="hidden lg:block w-80 border-r border-slate-800 bg-slate-900/50 overflow-y-auto sticky top-0 h-screen">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Sliders className="w-5 h-5" />
                  Filters
                </h2>
                {activeFilterCount > 0 && (
                  <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                    {activeFilterCount}
                  </span>
                )}
              </div>
              <FilterPanel
                filters={filters}
                onFilterChange={handleFilterChange}
                onClear={handleClearFilters}
              />
            </div>
          </aside>
        )}

        {/* Main Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-[1400px] mx-auto space-y-6">
            {/* Header */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div>
                  <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
                    Data Explorer
                  </h1>
                  <p className="text-slate-400 text-sm sm:text-base">
                    Advanced filtering and search across all property listings
                  </p>
                </div>

                {/* Quick Stats */}
                {totalCount > 0 && (
                  <div className="flex gap-3">
                    <div className="bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2">
                      <div className="text-xs text-slate-400">
                        {hideIncompleteListing ? "Quality" : "Total"}
                      </div>
                      <div className="text-xl font-bold text-white">
                        {hideIncompleteListing ? filteredCount : totalCount}
                      </div>
                    </div>
                    <div className="bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2">
                      <div className="text-xs text-slate-400">Showing</div>
                      <div className="text-xl font-bold text-white">
                        {properties.length}
                      </div>
                    </div>
                    {hideIncompleteListing && filteredCount < totalCount && (
                      <div className="bg-green-500/10 border border-green-500/30 rounded-lg px-4 py-2">
                        <div className="text-xs text-green-400">Filtered Out</div>
                        <div className="text-xl font-bold text-green-400">
                          {totalCount - filteredCount}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Search Bar */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <SearchBar
                  onSearch={handleSearch}
                  placeholder="Search by location, property type, or features..."
                  defaultValue={searchQuery}
                />
              </div>

              {/* Quick Filters - Listing Types */}
              <div className="flex flex-wrap gap-3">
                {listingTypes.map((type) => {
                  const Icon = type.icon;
                  const isActive = filters.listingType === type.value;

                  return (
                    <button
                      key={type.label}
                      onClick={() =>
                        handleFilterChange({
                          ...filters,
                          listingType: type.value,
                        })
                      }
                      className={`
                        flex items-center gap-2 px-4 py-2 rounded-lg border transition-all
                        ${
                          isActive
                            ? `${type.bgColor} ${type.borderColor} ${type.color}`
                            : "bg-slate-800/50 border-slate-700 text-slate-300 hover:border-slate-600"
                        }
                      `}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{type.label}</span>
                      {isActive && <CheckCircle2 className="w-4 h-4" />}
                    </button>
                  );
                })}
              </div>

              {/* Active Filters Banner */}
              {hasActiveFilters && (
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Filter className="w-4 h-4 text-blue-400" />
                    <span className="text-blue-400 text-sm font-medium">
                      Active Filters:
                    </span>

                    {searchQuery && (
                      <span className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-xs border border-blue-500/30">
                        Search: "{searchQuery}"
                      </span>
                    )}

                    {filters.location && (
                      <span className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-xs border border-purple-500/30 flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {filters.location}
                      </span>
                    )}

                    {filters.propertyType && (
                      <span className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-xs border border-green-500/30">
                        Type: {filters.propertyType}
                      </span>
                    )}

                    {filters.bedrooms && (
                      <span className="bg-orange-500/20 text-orange-300 px-3 py-1 rounded-full text-xs border border-orange-500/30">
                        🛏️ {filters.bedrooms}+ beds
                      </span>
                    )}

                    {filters.bathrooms && (
                      <span className="bg-pink-500/20 text-pink-300 px-3 py-1 rounded-full text-xs border border-pink-500/30">
                        🚿 {filters.bathrooms}+ baths
                      </span>
                    )}

                    <button
                      onClick={handleClearFilters}
                      className="ml-auto text-blue-400 hover:text-blue-300 text-sm font-medium flex items-center gap-1"
                    >
                      <X className="w-4 h-4" />
                      Clear All
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Toolbar */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3 flex-wrap">
                  {/* Show/Hide Filters Button - Desktop */}
                  <Button
                    onClick={() => setDesktopFiltersOpen(!desktopFiltersOpen)}
                    size="sm"
                    variant="outline"
                    className="hidden lg:flex bg-slate-700 border-slate-600 hover:bg-slate-600 text-white text-xs sm:text-sm"
                  >
                    <Filter className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                    <span className="hidden sm:inline">{desktopFiltersOpen ? 'Hide' : 'Show'} Filters</span>
                    <span className="sm:hidden">Filters</span>
                    {desktopFiltersOpen ? <ChevronUp className="w-3 h-3 sm:w-4 sm:h-4 ml-1" /> : <ChevronDown className="w-3 h-3 sm:w-4 sm:h-4 ml-1" />}
                  </Button>

                  {/* Mobile Filter Button */}
                  <Button
                    onClick={() => setMobileFiltersOpen(true)}
                    className="lg:hidden bg-slate-700 hover:bg-slate-600 border border-slate-600 relative"
                  >
                    <Filter className="w-4 h-4 mr-2" />
                    Filters
                    {activeFilterCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-blue-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                        {activeFilterCount}
                      </span>
                    )}
                  </Button>

                  {/* Grid View Selector */}
                  <Select value={viewMode} onValueChange={(value) => setViewMode(value as ViewMode)}>
                    <SelectTrigger className="w-[140px] bg-slate-700 border-slate-600 text-white text-sm">
                      <SelectValue placeholder={getViewModeLabel(viewMode)}>
                        {getViewModeLabel(viewMode)}
                      </SelectValue>
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700 text-white z-50">
                      <SelectItem value="list" className="text-white cursor-pointer hover:bg-slate-700">
                        <span className="flex items-center gap-2">
                          <List className="w-4 h-4" />
                          List View
                        </span>
                      </SelectItem>
                      <SelectItem value="grid-2" className="text-white cursor-pointer hover:bg-slate-700">
                        <span className="flex items-center gap-2">
                          <Grid2x2 className="w-4 h-4" />
                          2 Columns
                        </span>
                      </SelectItem>
                      <SelectItem value="grid-3" className="text-white cursor-pointer hover:bg-slate-700">
                        <span className="flex items-center gap-2">
                          <Grid3x3 className="w-4 h-4" />
                          3 Columns
                        </span>
                      </SelectItem>
                      <SelectItem value="grid-4" className="text-white cursor-pointer hover:bg-slate-700">
                        4 Columns
                      </SelectItem>
                      <SelectItem value="grid-5" className="text-white cursor-pointer hover:bg-slate-700">
                        5 Columns
                      </SelectItem>
                      <SelectItem value="grid-6" className="text-white cursor-pointer hover:bg-slate-700">
                        6 Columns
                      </SelectItem>
                    </SelectContent>
                  </Select>

                  {/* Quality Filter Toggle */}
                  <button
                    onClick={() => setHideIncompleteListings(!hideIncompleteListing)}
                    className={`
                      flex items-center gap-2 px-3 py-2 rounded-lg border transition-all
                      ${
                        hideIncompleteListing
                          ? "bg-green-500/20 border-green-500/30 text-green-400"
                          : "bg-slate-900 border-slate-700 text-slate-400 hover:text-white"
                      }
                    `}
                    title="Hide properties with incomplete data"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span className="hidden md:inline text-sm">
                      {hideIncompleteListing ? "Quality Filter ON" : "Quality Filter"}
                    </span>
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  {/* Export Button */}
                  <ExportButton filters={filters} totalCount={totalCount} properties={properties} />

                  {/* Refresh */}
                  <Button
                    onClick={refetch}
                    disabled={loading}
                    className="bg-slate-700 hover:bg-slate-600 border border-slate-600"
                    size="sm"
                  >
                    <RefreshCw
                      className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
                    />
                  </Button>
                </div>
              </div>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="space-y-6">
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 text-center">
                  <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-3" />
                  <p className="text-white font-medium mb-1">
                    Loading properties...
                  </p>
                  <p className="text-sm text-slate-400">
                    First load may take 30-60 seconds while server wakes up
                  </p>
                </div>
                <div
                  className={
                    viewMode === "grid"
                      ? "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
                      : "space-y-4"
                  }
                >
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <Skeleton key={i} className="h-96 w-full bg-slate-800" />
                  ))}
                </div>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 text-center">
                <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-red-400 mb-2">
                  Failed to Load Properties
                </h3>
                <p className="text-red-400/70 text-sm mb-6">
                  {typeof error === "string"
                    ? error
                    : (error as any)?.message || "An error occurred"}
                </p>
                <div className="flex items-center justify-center gap-3">
                  <Button
                    onClick={refetch}
                    className="bg-blue-600 hover:bg-blue-500"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again
                  </Button>
                  <Button
                    onClick={handleClearFilters}
                    variant="outline"
                    className="border-slate-600 hover:bg-slate-700"
                  >
                    Clear Filters
                  </Button>
                </div>
                <p className="text-xs text-slate-500 mt-4">
                  If the issue persists, the API server may need time to wake up
                </p>
              </div>
            )}

            {/* Properties Grid/List */}
            {!loading && !error && properties.length > 0 && (
              <>
                <div className={getGridClass()}>
                  {properties.map((property: any) => (
                    <PropertyCard
                      key={
                        property.id ||
                        property.listing_id ||
                        property.metadata?.hash ||
                        property.basic_info?.listing_url ||
                        JSON.stringify(property).slice(0, 50)
                      }
                      property={property}
                      onClick={() => handlePropertyClick(property)}
                    />
                  ))}
                </div>

                <PropertyDetailsModal
                  open={detailsModalOpen}
                  onClose={handleModalClose}
                  property={selectedProperty}
                />

                {filteredCount > 0 && (
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8">
                    {/* Items Per Page Selector */}
                    <div className="flex items-center gap-3">
                      <label htmlFor="items-per-page" className="text-sm text-slate-400 whitespace-nowrap">
                        Items per page:
                      </label>
                      <select
                        id="items-per-page"
                        value={itemsPerPage}
                        onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
                        className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 hover:border-slate-600 transition-colors"
                      >
                        <option value={20}>20</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                        <option value={200}>200</option>
                        <option value={500}>500</option>
                        <option value={1000}>1000</option>
                      </select>
                    </div>

                    {/* Pagination */}
                    {filteredCount > itemsPerPage && (
                      <Pagination
                        currentPage={currentPage}
                        totalItems={filteredCount}
                        itemsPerPage={itemsPerPage}
                        onPageChange={handlePageChange}
                      />
                    )}
                  </div>
                )}
              </>
            )}

            {/* Empty State */}
            {!loading && !error && properties.length === 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-12 text-center">
                <Home className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  No Properties Found
                </h3>
                <p className="text-slate-400 mb-6 max-w-md mx-auto">
                  {hasActiveFilters
                    ? "Try adjusting your filters or search query to see more results."
                    : "Get started by running a scrape to fetch the latest property data."}
                </p>
                <div className="flex items-center justify-center gap-3">
                  {hasActiveFilters && (
                    <Button onClick={handleClearFilters} variant="outline">
                      Clear Filters
                    </Button>
                  )}
                  <Button
                    onClick={() => handleNavigate("scraper")}
                    className="bg-blue-600 hover:bg-blue-500"
                  >
                    Go to Scraper Control
                  </Button>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
