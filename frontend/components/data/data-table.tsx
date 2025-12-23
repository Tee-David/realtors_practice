"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Star, Home, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Property } from "@/lib/types";
import { formatCurrency, formatDateTime } from "@/lib/utils";

interface DataTableProps {
  properties: Property[];
}

export default function DataTable({ properties }: DataTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const totalPages = Math.ceil(properties.length / itemsPerPage);

  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentProperties = properties.slice(startIndex, endIndex);

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const getVisiblePages = () => {
    const pages = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const start = Math.max(1, currentPage - 2);
      const end = Math.min(totalPages, start + maxVisible - 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
    }

    return pages;
  };

  if (properties.length === 0) {
    return (
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center">
        <div className="text-slate-400 space-y-3">
          <Home className="h-12 w-12 mx-auto opacity-50" />
          <p className="text-lg font-medium">No properties found</p>
          <p className="text-sm max-w-md mx-auto">
            No data is available yet. Start by running a scraper to collect
            property listings from configured sites.
          </p>
          <p className="text-xs text-slate-500 mt-4">
            Go to &quot;Scraper Control&quot; to start collecting data
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
      {/* Desktop Table */}
      <div className="hidden lg:block">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-900/50">
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  TITLE
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  PRICE
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  PRICE/SQM
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  LOCATION
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  BED
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  BATH
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  TYPE
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  SOURCE
                </th>
                <th className="text-left p-4 text-sm font-medium text-slate-400 whitespace-nowrap">
                  TIMESTAMP
                </th>
              </tr>
            </thead>
            <tbody>
              {currentProperties.map((property) => (
                <tr
                  key={property.id}
                  className="border-b border-slate-700 hover:bg-slate-700/30 transition-colors"
                >
                  <td className="p-4 text-white font-medium max-w-xs">
                    <div className="flex items-start space-x-2">
                      <div className="min-w-0 flex-1">
                        <div className="truncate">{property.title}</div>
                        <div className="flex items-center space-x-2 mt-1">
                          {property.featured && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400">
                              <Star className="w-3 h-3 mr-1" />
                              Featured
                            </span>
                          )}
                          {property.newListing && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-green-500/20 text-green-400">
                              New
                            </span>
                          )}
                          {property.openHouse && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400">
                              Open House
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4 text-slate-300 whitespace-nowrap font-semibold">
                    {formatCurrency(
                      typeof property.price === "number"
                        ? property.price
                        : parseFloat(property.price) || 0
                    )}
                  </td>
                  <td className="p-4 text-slate-300 whitespace-nowrap">
                    {property.price_per_sqm
                      ? formatCurrency(property.price_per_sqm)
                      : "N/A"}
                  </td>
                  <td className="p-4 text-slate-300 max-w-xs truncate">
                    {property.location}
                  </td>
                  <td className="p-4 text-slate-300 text-center">
                    {property.bedrooms}
                  </td>
                  <td className="p-4 text-slate-300 text-center">
                    {property.bathrooms}
                  </td>
                  <td className="p-4 text-slate-300">
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">
                      {property.type}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300 max-w-xs truncate">
                    {property.source}
                  </td>
                  <td className="p-4 text-slate-300 text-sm whitespace-nowrap">
                    {property.timestamp
                      ? formatDateTime(property.timestamp)
                      : "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile Cards */}
      <div className="lg:hidden">
        <div className="divide-y divide-slate-700">
          {currentProperties.map((property) => (
            <div
              key={property.id}
              className="p-4 hover:bg-slate-700/30 transition-colors"
            >
              <div className="space-y-3">
                {/* Header */}
                <div className="flex justify-between items-start">
                  <div className="min-w-0 flex-1 pr-3">
                    <h3 className="text-white font-medium text-base leading-tight">
                      {property.title}
                    </h3>
                    <p className="text-slate-400 text-sm mt-1">
                      {property.location}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-green-400 font-bold text-lg">
                      {formatCurrency(
                        typeof property.price === "number"
                          ? property.price
                          : parseFloat(property.price) || 0
                      )}
                    </div>
                    <div className="text-slate-400 text-sm">
                      {property.price_per_sqm
                        ? formatCurrency(property.price_per_sqm)
                        : "N/A"}
                      /sqm
                    </div>
                  </div>
                </div>

                {/* Property Details */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-400">Bedrooms:</span>
                    <span className="text-white font-medium">
                      {property.bedrooms}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-400">Bathrooms:</span>
                    <span className="text-white font-medium">
                      {property.bathrooms}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-400">Type:</span>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-slate-700 text-slate-300">
                      {property.type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-400">Source:</span>
                    <span className="text-slate-300 truncate">
                      {property.source}
                    </span>
                  </div>
                </div>

                {/* Tags */}
                {(property.featured ||
                  property.newListing ||
                  property.openHouse) && (
                  <div className="flex flex-wrap gap-2">
                    {property.featured && (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-yellow-500/20 text-yellow-400">
                        <Star className="w-3 h-3 mr-1" />
                        Featured
                      </span>
                    )}
                    {property.newListing && (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-500/20 text-green-400">
                        New Listing
                      </span>
                    )}
                    {property.openHouse && (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-500/20 text-blue-400">
                        Open House
                      </span>
                    )}
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-700">
                  <div className="flex items-center space-x-1 text-slate-400 text-xs">
                    <Calendar className="w-3 h-3" />
                    <span>
                      {property.timestamp
                        ? formatDateTime(property.timestamp)
                        : "N/A"}
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-blue-400 hover:text-blue-300 text-xs h-6"
                  >
                    View Details
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="border-t border-slate-700 p-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            {/* Results Info */}
            <div className="text-sm text-slate-400 text-center sm:text-left">
              Showing {startIndex + 1}-{Math.min(endIndex, properties.length)}{" "}
              of {properties.length} results
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-center space-x-1">
              <Button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
                variant="outline"
                size="sm"
                className="border-slate-600 text-slate-300 hover:bg-slate-700 disabled:opacity-50"
              >
                <ChevronLeft className="w-4 h-4" />
                <span className="hidden sm:inline ml-1">Previous</span>
              </Button>

              <div className="flex items-center space-x-1">
                {getVisiblePages().map((page) => (
                  <Button
                    key={page}
                    onClick={() => goToPage(page)}
                    variant={currentPage === page ? "default" : "outline"}
                    size="sm"
                    className={
                      currentPage === page
                        ? "bg-blue-500 hover:bg-blue-600 text-white min-w-[32px]"
                        : "border-slate-600 text-slate-300 hover:bg-slate-700 min-w-[32px]"
                    }
                  >
                    {page}
                  </Button>
                ))}
              </div>

              <Button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                variant="outline"
                size="sm"
                className="border-slate-600 text-slate-300 hover:bg-slate-700 disabled:opacity-50"
              >
                <span className="hidden sm:inline mr-1">Next</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
