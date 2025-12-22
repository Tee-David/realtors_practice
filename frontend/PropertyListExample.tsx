/**
 * Example React Component: Property Listing from Firestore
 * This shows how to use the Firestore hooks to fetch and display properties
 */

import React from 'react';
import { useFirestoreProperties, useFirestoreSearch, useFirestorePagination } from './useFirestore';

// ============================================================================
// Example 1: Simple Property List
// ============================================================================

export function PropertyList() {
  const { properties, count, isLoading, error } = useFirestoreProperties({
    limit: 20,
    sort_by: 'uploaded_at',
    sort_desc: true,
  });

  if (isLoading) return <div>Loading properties...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Properties ({count} total)</h1>
      <div className="property-grid">
        {properties.map((property, index) => (
          <PropertyCard key={index} property={property} />
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Example 2: Filtered Property List
// ============================================================================

export function LagosProperties() {
  const { properties, isLoading, error } = useFirestoreProperties({
    filters: {
      'location.state': 'Lagos',
      'property_details.bedrooms': 3,
    },
    limit: 50,
    sort_by: 'financial.price',
    sort_desc: false, // Ascending (cheapest first)
  });

  if (isLoading) return <div>Loading Lagos properties...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>3-Bedroom Properties in Lagos</h1>
      <p>Found {properties.length} properties</p>
      <div className="property-grid">
        {properties.map((property, index) => (
          <PropertyCard key={index} property={property} />
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Example 3: Search with Filters
// ============================================================================

export function PropertySearch() {
  const search = useFirestoreSearch();
  const [selectedState, setSelectedState] = React.useState('Lagos');
  const [minBedrooms, setMinBedrooms] = React.useState(2);

  React.useEffect(() => {
    search.byState(selectedState);
  }, [selectedState]);

  return (
    <div>
      <div className="search-filters">
        <select
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
        >
          <option value="Lagos">Lagos</option>
          <option value="Abuja">Abuja</option>
          <option value="Port Harcourt">Port Harcourt</option>
        </select>

        <input
          type="number"
          min="1"
          value={minBedrooms}
          onChange={(e) => {
            const value = parseInt(e.target.value);
            setMinBedrooms(value);
            search.byBedrooms(value);
          }}
          placeholder="Min bedrooms"
        />

        <button onClick={() => search.clearFilters()}>Clear Filters</button>
      </div>

      {search.isLoading && <div>Loading...</div>}

      <div>
        <h2>Results ({search.count})</h2>
        <div className="property-grid">
          {search.properties.map((property, index) => (
            <PropertyCard key={index} property={property} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Example 4: Infinite Scroll / Pagination
// ============================================================================

export function InfinitePropertyList() {
  const {
    properties,
    hasMore,
    loadMore,
    isLoading,
    totalCount,
  } = useFirestorePagination(
    {
      filters: { 'location.state': 'Lagos' },
      sort_by: 'uploaded_at',
      sort_desc: true,
    },
    20 // Page size
  );

  return (
    <div>
      <h1>All Properties ({totalCount} total)</h1>
      <div className="property-grid">
        {properties.map((property, index) => (
          <PropertyCard key={index} property={property} />
        ))}
      </div>

      {hasMore && (
        <button
          onClick={loadMore}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}

// ============================================================================
// Property Card Component
// ============================================================================

function PropertyCard({ property }: { property: any }) {
  const basicInfo = property.basic_info || {};
  const financial = property.financial || {};
  const propertyDetails = property.property_details || {};
  const location = property.location || {};
  const media = property.media || {};
  const metadata = property.metadata || {};

  const firstImage = media.images?.[0]?.url;
  const price = financial.price;
  const bedrooms = propertyDetails.bedrooms;
  const bathrooms = propertyDetails.bathrooms;
  const propertyType = propertyDetails.property_type;
  const locationText = location.location_text || location.state;
  const qualityScore = metadata.quality_score;

  return (
    <div className="property-card">
      {firstImage && (
        <img
          src={firstImage}
          alt={basicInfo.title || 'Property'}
          className="property-image"
        />
      )}

      <div className="property-details">
        <h3>{basicInfo.title || 'Property Listing'}</h3>

        {price && (
          <p className="price">
            ₦{price.toLocaleString()}
          </p>
        )}

        <div className="property-specs">
          {bedrooms && <span>{bedrooms} Beds</span>}
          {bathrooms && <span>{bathrooms} Baths</span>}
          {propertyType && <span>{propertyType}</span>}
        </div>

        <p className="location">{locationText}</p>

        {qualityScore && (
          <p className="quality-score">
            Quality Score: {qualityScore.toFixed(1)}%
          </p>
        )}

        {basicInfo.listing_url && (
          <a
            href={basicInfo.listing_url}
            target="_blank"
            rel="noopener noreferrer"
            className="view-link"
          >
            View Details
          </a>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Usage in Your App
// ============================================================================

/*
import { PropertyList, PropertySearch, InfinitePropertyList } from './PropertyListExample';

function App() {
  return (
    <div>
      <PropertyList />
      {/* or * /}
      <PropertySearch />
      {/* or * /}
      <InfinitePropertyList />
    </div>
  );
}
*/
