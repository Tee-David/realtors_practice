"use client";

import { useState, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PropertyCard } from "@/components/shared/property-card";
import { SearchBar } from "@/components/shared/search-bar";
import { Pagination } from "@/components/shared/pagination";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RefreshCw, Download, Home, Grid3x3, List, Grid2x2, Filter, ChevronDown, ChevronUp } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

type ViewMode = "list" | "grid-2" | "grid-3" | "grid-4" | "grid-5" | "grid-6";

export default function DataExplorer() {
  const [properties, setProperties] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [showLargePageWarning, setShowLargePageWarning] = useState(false);
  const [pendingPageSize, setPendingPageSize] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("grid-3");
  const [showFilters, setShowFilters] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.getFirestoreForSale({
        limit: itemsPerPage,
        offset: (currentPage - 1) * itemsPerPage,
      });
      setProperties(response.properties || []);
      setTotalCount(response.total || 0);
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  }, [itemsPerPage, currentPage]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const filteredProperties = searchQuery
    ? properties.filter(
        (p) =>
          p.basic_info?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.location?.area?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : properties;

  const exportToCSV = () => {
    try {
      if (filteredProperties.length === 0) {
        toast.error("No properties to export");
        return;
      }

      // Helper function to escape CSV values
      const escapeCsvValue = (value: any): string => {
        if (value === null || value === undefined) return "";
        const str = String(value);
        // If value contains comma, quote, or newline, wrap in quotes and escape internal quotes
        if (str.includes(",") || str.includes('"') || str.includes("\n")) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      };

      // Extract data with fallback for both nested and flat schemas
      const headers = [
        "Title",
        "Price (NGN)",
        "Location",
        "Bedrooms",
        "Bathrooms",
        "Property Type",
        "Size (sqm)",
        "Furnishing",
        "Status",
        "Source",
        "URL"
      ];

      const rows = filteredProperties.map((p) => {
        // Support both nested (Firestore enterprise) and flat schemas
        const title = p.basic_info?.title || p.title || "";
        const price = p.financial?.price || p.price || 0;
        const location =
          p.location?.area ||
          p.location?.full_address ||
          p.location?.lga ||
          (typeof p.location === 'string' ? p.location : "") ||
          "";
        const bedrooms = p.property_details?.bedrooms || p.bedrooms || "";
        const bathrooms = p.property_details?.bathrooms || p.bathrooms || "";
        const propertyType = p.property_details?.property_type || p.property_type || "";
        const size = p.property_details?.size || p.size || "";
        const furnishing = p.property_details?.furnishing || p.furnishing || "";
        const status = p.basic_info?.status || p.status || "";
        const source = p.basic_info?.source || p.basic_info?.site_key || p.source || p.site_key || "";
        const url = p.basic_info?.listing_url || p.listing_url || p.url || "";

        return [
          title,
          price,
          location,
          bedrooms,
          bathrooms,
          propertyType,
          size,
          furnishing,
          status,
          source,
          url
        ].map(escapeCsvValue);
      });

      // Create CSV content
      const csvContent = [
        headers.join(","),
        ...rows.map(row => row.join(","))
      ].join("\n");

      // Create and download file
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `properties-export-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success(`Successfully exported ${filteredProperties.length} properties to CSV`);
    } catch (error) {
      console.error("Export error:", error);
      toast.error("Failed to export properties. Please try again.");
    }
  };

  // Get grid class based on view mode
  const getGridClass = () => {
    switch (viewMode) {
      case "list":
        return "grid grid-cols-1 gap-4";
      case "grid-2":
        return "grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6";
      case "grid-3":
        return "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6";
      case "grid-4":
        return "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4";
      case "grid-5":
        return "grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3";
      case "grid-6":
        return "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-3";
      default:
        return "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6";
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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-2 sm:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-4 sm:mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2 flex items-center gap-2">
            <Home className="w-6 h-6 sm:w-8 sm:h-8" />
            Properties
          </h1>
          <p className="text-sm sm:text-base text-slate-400">
            Browse and export property listings
          </p>
        </div>

        {/* Sticky Filter Card */}
        <Card className="bg-slate-800/50 border-slate-700 mb-4 sm:mb-6 sticky top-0 sm:top-2 z-10 shadow-lg">
          <CardHeader className="pb-3 sm:pb-6">
            <CardTitle className="text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2 sm:gap-3">
                {/* Show Filters Button */}
                <Button
                  onClick={() => setShowFilters(!showFilters)}
                  size="sm"
                  variant="outline"
                  className="bg-slate-700 border-slate-600 hover:bg-slate-600 text-white text-xs sm:text-sm"
                >
                  <Filter className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">{showFilters ? 'Hide' : 'Show'} Filters</span>
                  <span className="sm:hidden">Filters</span>
                  {showFilters ? <ChevronUp className="w-3 h-3 sm:w-4 sm:h-4 ml-1" /> : <ChevronDown className="w-3 h-3 sm:w-4 sm:h-4 ml-1" />}
                </Button>
                <span className="text-base sm:text-lg">Search & Export</span>
              </div>
              <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                {/* View Mode Selector */}
                <Select value={viewMode} onValueChange={(value) => setViewMode(value as ViewMode)}>
                  <SelectTrigger className="w-[140px] bg-slate-700 border-slate-600 text-white text-sm">
                    <SelectValue placeholder={getViewModeLabel(viewMode)}>
                      {getViewModeLabel(viewMode)}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700 text-white">
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

                <Button
                  onClick={loadData}
                  disabled={loading}
                  size="sm"
                  variant="outline"
                  className="text-white text-xs sm:text-sm"
                >
                  <RefreshCw className={`w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2 ${loading ? 'animate-spin' : ''}`} />
                  <span className="hidden sm:inline">Refresh</span>
                </Button>
                <Button
                  onClick={exportToCSV}
                  disabled={filteredProperties.length === 0}
                  size="sm"
                  className="bg-green-600 hover:bg-green-700 text-xs sm:text-sm"
                >
                  <Download className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">Export CSV</span>
                  <span className="sm:hidden">Export</span>
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          {showFilters && (
            <CardContent className="pt-0">
              <SearchBar
                onSearch={setSearchQuery}
                placeholder="Search by title or location..."
                defaultValue={searchQuery}
              />
              <p className="text-xs sm:text-sm text-slate-400 mt-2">
                Showing {filteredProperties.length} of {totalCount} properties
              </p>
            </CardContent>
          )}
        </Card>

        {loading ? (
          <div className="text-center text-white py-12">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
            Loading properties...
          </div>
        ) : (
          <div className={getGridClass()}>
            {filteredProperties.map((property, index) => (
              <PropertyCard key={property.metadata?.hash || index} property={property} />
            ))}
          </div>
        )}

        {!loading && filteredProperties.length === 0 && (
          <Card className="bg-slate-800/50 border-slate-700 text-center py-12">
            <CardContent>
              <p className="text-slate-400">No properties found</p>
            </CardContent>
          </Card>
        )}

        {/* Pagination Controls */}
        {!loading && totalCount > 0 && (
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8">
            {/* Items Per Page Selector */}
            <div className="flex items-center gap-3">
              <label htmlFor="items-per-page" className="text-sm text-slate-400 whitespace-nowrap">
                Items per page:
              </label>
              <select
                id="items-per-page"
                value={itemsPerPage}
                onChange={(e) => {
                  const newValue = Number(e.target.value);
                  // Show warning for page sizes >= 200
                  if (newValue >= 200) {
                    setPendingPageSize(newValue);
                    setShowLargePageWarning(true);
                  } else {
                    setItemsPerPage(newValue);
                    setCurrentPage(1);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }
                }}
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

            {/* Pagination Component */}
            {totalCount > itemsPerPage && (
              <Pagination
                currentPage={currentPage}
                totalItems={totalCount}
                itemsPerPage={itemsPerPage}
                onPageChange={setCurrentPage}
              />
            )}
          </div>
        )}

        {/* Large Page Size Warning Dialog */}
        {showLargePageWarning && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
            <Card className="bg-slate-800 border-slate-700 max-w-md w-full">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <svg className="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Performance Warning
                </CardTitle>
              </CardHeader>
              <CardContent className="text-slate-300">
                <p className="mb-4">
                  Loading {pendingPageSize} items at once may cause performance issues or browser crashes on some devices.
                </p>
                <p className="mb-6 text-sm text-slate-400">
                  Consider using the Export CSV feature instead for large datasets.
                </p>
                <div className="flex gap-3 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowLargePageWarning(false);
                      setPendingPageSize(null);
                    }}
                    className="border-slate-600 hover:bg-slate-700"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => {
                      if (pendingPageSize) {
                        setItemsPerPage(pendingPageSize);
                        setCurrentPage(1);
                        window.scrollTo({ top: 0, behavior: "smooth" });
                      }
                      setShowLargePageWarning(false);
                      setPendingPageSize(null);
                    }}
                    className="bg-yellow-600 hover:bg-yellow-700"
                  >
                    Continue Anyway
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
