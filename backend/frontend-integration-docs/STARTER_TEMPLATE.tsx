/**
 * Nigerian Real Estate Frontend - Starter Template
 *
 * This file contains ready-to-use components and pages.
 * Copy and modify as needed for your application.
 *
 * Dependencies required:
 * - npm install swr axios
 *
 * Files required:
 * - lib/api/types.ts (from frontend/types.ts)
 * - lib/api/client.ts (from frontend/api-client.ts)
 * - lib/api/hooks.tsx (from frontend/hooks.tsx)
 */

import { useState } from 'react';
import { useProperties, usePropertySearch, useDashboard, useScraperStatus } from '@/lib/api/hooks';
import { Property } from '@/lib/api/types';
import Image from 'next/image';

// ============================================================================
// PROPERTY CARD COMPONENT
// ============================================================================

interface PropertyCardProps {
  property: Property;
  onClick?: () => void;
}

export function PropertyCard({ property, onClick }: PropertyCardProps) {
  const { basic_info, property_details, financial, location, media, tags } = property;

  return (
    <div
      onClick={onClick}
      className="border rounded-lg overflow-hidden hover:shadow-lg transition cursor-pointer bg-white"
    >
      {/* Property Image */}
      {media.images?.[0] && (
        <div className="relative h-48 bg-gray-200">
          <Image
            src={media.images[0].url}
            alt={basic_info.title}
            fill
            className="object-cover"
          />

          {/* Tags */}
          <div className="absolute top-2 right-2 space-y-1">
            {tags.premium && (
              <span className="block bg-yellow-500 text-white px-2 py-1 text-xs rounded font-semibold">
                PREMIUM
              </span>
            )}
            {tags.hot_deal && (
              <span className="block bg-red-500 text-white px-2 py-1 text-xs rounded font-semibold">
                HOT DEAL
              </span>
            )}
            {tags.featured && (
              <span className="block bg-blue-500 text-white px-2 py-1 text-xs rounded font-semibold">
                FEATURED
              </span>
            )}
          </div>

          {/* Status Badge */}
          <span className="absolute top-2 left-2 bg-black bg-opacity-70 text-white px-2 py-1 text-xs rounded">
            {basic_info.status === 'for_sale' ? 'FOR SALE' : 'FOR RENT'}
          </span>
        </div>
      )}

      {/* Property Info */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-bold text-lg mb-2 line-clamp-2 text-gray-900">
          {basic_info.title}
        </h3>

        {/* Price */}
        <p className="text-2xl font-bold text-blue-600 mb-2">
          {financial.currency} {financial.price.toLocaleString()}
          {basic_info.listing_type === 'rent' && <span className="text-sm font-normal">/year</span>}
        </p>

        {/* Location */}
        <p className="text-gray-600 text-sm mb-3 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
          </svg>
          {location.area}, {location.lga}
        </p>

        {/* Property Details */}
        <div className="flex gap-4 text-sm text-gray-600 border-t pt-3">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
            </svg>
            {property_details.bedrooms} beds
          </span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
            </svg>
            {property_details.bathrooms} baths
          </span>
          <span className="truncate">{property_details.property_type}</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// PROPERTY GRID COMPONENT
// ============================================================================

interface PropertyGridProps {
  properties: Property[];
  onPropertyClick?: (property: Property) => void;
}

export function PropertyGrid({ properties, onPropertyClick }: PropertyGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {properties.map((property) => (
        <PropertyCard
          key={property.hash}
          property={property}
          onClick={() => onPropertyClick?.(property)}
        />
      ))}
    </div>
  );
}

// ============================================================================
// SEARCH BAR COMPONENT
// ============================================================================

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export function SearchBar({ onSearch, placeholder = "Search properties in Lagos..." }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <button
        type="submit"
        className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded transition"
      >
        Search
      </button>
    </form>
  );
}

// ============================================================================
// DASHBOARD STATS COMPONENT
// ============================================================================

export function DashboardStats() {
  const { stats, isLoading } = useDashboard();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  const statsCards = [
    { title: 'Total Properties', value: stats.total_properties, color: 'blue' },
    { title: 'For Sale', value: stats.for_sale_count, color: 'green' },
    { title: 'For Rent', value: stats.for_rent_count, color: 'purple' },
    { title: 'Premium', value: stats.premium_count, color: 'yellow' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {statsCards.map((card) => (
        <div key={card.title} className="bg-white p-6 rounded-lg shadow">
          <p className="text-gray-600 text-sm font-medium mb-2">{card.title}</p>
          <p className={`text-3xl font-bold text-${card.color}-600`}>
            {card.value?.toLocaleString() ?? 0}
          </p>
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// SCRAPER STATUS COMPONENT
// ============================================================================

export function ScraperStatus() {
  const { status, isRunning, progress, timing } = useScraperStatus();

  if (!isRunning) {
    return (
      <div className="bg-gray-100 p-4 rounded-lg">
        <p className="text-gray-600">No scraping in progress</p>
      </div>
    );
  }

  const percentage = progress.total_sites > 0
    ? Math.round((progress.completed_sites / progress.total_sites) * 100)
    : 0;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="font-bold text-lg mb-4">Scraping in Progress</h3>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress: {progress.completed_sites}/{progress.total_sites} sites</span>
          <span>{percentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <p className="text-gray-600">Completed</p>
          <p className="font-bold text-green-600">{progress.completed_sites}</p>
        </div>
        <div>
          <p className="text-gray-600">In Progress</p>
          <p className="font-bold text-blue-600">{progress.in_progress_sites}</p>
        </div>
        <div>
          <p className="text-gray-600">Failed</p>
          <p className="font-bold text-red-600">{progress.failed_sites}</p>
        </div>
      </div>

      {/* ETA */}
      {timing.estimated_remaining_seconds && (
        <div className="mt-4 pt-4 border-t">
          <p className="text-sm text-gray-600">
            Estimated time remaining: {Math.round(timing.estimated_remaining_seconds / 60)} minutes
          </p>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// FULL PAGE EXAMPLES
// ============================================================================

// Example 1: Properties Listing Page
export function PropertiesListingPage() {
  const [page, setPage] = useState(1);
  const limit = 20;

  const { properties, total, isLoading, error } = useProperties({
    limit,
    offset: (page - 1) * limit
  });

  const totalPages = Math.ceil(total / limit);

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error loading properties: {error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          Properties in Lagos
        </h1>
        <p className="text-gray-600">
          {total.toLocaleString()} properties available
        </p>
      </div>

      {/* Properties Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading properties...</p>
        </div>
      ) : (
        <>
          <PropertyGrid
            properties={properties}
            onPropertyClick={(property) => {
              // Navigate to property detail page
              window.location.href = `/properties/${property.hash}`;
            }}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-8 flex justify-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Previous
              </button>

              <span className="px-4 py-2">
                Page {page} of {totalPages}
              </span>

              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// Example 2: Search Page
export function SearchPage() {
  const [query, setQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const { properties, isLoading } = usePropertySearch(activeQuery);

  const handleSearch = (searchQuery: string) => {
    setActiveQuery(searchQuery);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">Search Properties</h1>
        <SearchBar onSearch={handleSearch} />
      </div>

      {/* Results */}
      {activeQuery && (
        <div className="mb-4">
          <p className="text-gray-600">
            {isLoading ? 'Searching...' : `Found ${properties.length} properties for "${activeQuery}"`}
          </p>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <PropertyGrid properties={properties} />
      )}
    </div>
  );
}

// Example 3: Admin Dashboard
export function AdminDashboard() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

      {/* Stats */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Overview</h2>
        <DashboardStats />
      </div>

      {/* Scraper Status */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">Scraper Status</h2>
        <ScraperStatus />
      </div>

      {/* Recent Properties */}
      <div>
        <h2 className="text-xl font-bold mb-4">Recent Properties</h2>
        <RecentPropertiesWidget />
      </div>
    </div>
  );
}

// Helper component for recent properties
function RecentPropertiesWidget() {
  const { properties, isLoading } = useProperties({ limit: 6 });

  if (isLoading) return <div>Loading...</div>;

  return (
    <PropertyGrid properties={properties.slice(0, 6)} />
  );
}

// ============================================================================
// EXPORT ALL
// ============================================================================

export {
  // Components
  PropertyCard,
  PropertyGrid,
  SearchBar,
  DashboardStats,
  ScraperStatus,

  // Pages
  PropertiesListingPage,
  SearchPage,
  AdminDashboard,
};
