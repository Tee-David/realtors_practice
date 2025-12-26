"use client";

import { useState, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PropertyCard } from "@/components/shared/property-card";
import { SearchBar } from "@/components/shared/search-bar";
import { Pagination } from "@/components/shared/pagination";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RefreshCw, Download, Home } from "lucide-react";

export default function DataExplorer() {
  const [properties, setProperties] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);

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
    const headers = ["Title", "Price", "Location", "Bedrooms", "Bathrooms", "URL"];
    const rows = filteredProperties.map((p) => [
      p.basic_info?.title || "",
      p.financial?.price || 0,
      p.location?.area || "",
      p.property_details?.bedrooms || "",
      p.property_details?.bathrooms || "",
      p.basic_info?.listing_url || "",
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `properties-export-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
            <Home className="w-8 h-8" />
            Properties
          </h1>
          <p className="text-slate-400">
            Browse and export property listings
          </p>
        </div>

        <Card className="bg-slate-800/50 border-slate-700 mb-6">
          <CardHeader>
            <CardTitle className="text-white flex items-center justify-between">
              <span>Search & Export</span>
              <div className="flex gap-2">
                <Button
                  onClick={loadData}
                  disabled={loading}
                  size="sm"
                  variant="outline"
                  className="text-white"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
                <Button
                  onClick={exportToCSV}
                  disabled={filteredProperties.length === 0}
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SearchBar
              onSearch={setSearchQuery}
              placeholder="Search by title or location..."
              defaultValue={searchQuery}
            />
            <p className="text-sm text-slate-400 mt-2">
              Showing {filteredProperties.length} of {totalCount} properties
            </p>
          </CardContent>
        </Card>

        {loading ? (
          <div className="text-center text-white py-12">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
            Loading properties...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
        {!loading && totalCount > itemsPerPage && (
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
                  setItemsPerPage(Number(e.target.value));
                  setCurrentPage(1); // Reset to first page
                  window.scrollTo({ top: 0, behavior: "smooth" });
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
            <Pagination
              currentPage={currentPage}
              totalItems={totalCount}
              itemsPerPage={itemsPerPage}
              onPageChange={setCurrentPage}
            />
          </div>
        )}
      </div>
    </div>
  );
}
