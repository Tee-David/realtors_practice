"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  MapPin, Bed, Bath, Home, TrendingUp,
  Square, Calendar, Phone, User,
  Maximize2, Tag, Clock, Camera,
  Wifi, Car, Dumbbell, Shield, Droplet,
  Zap, Building2, MapPinned
} from "lucide-react";
import Image from "next/image";
import { PropertyDetailModal } from "./property-detail-modal";

interface PropertyCardProps {
  property: any; // Support both flat and nested Firestore enterprise schema
  onClick?: () => void;
  viewMode?: 'grid' | 'list'; // Add view mode support
}

// Data sanitization helpers
function sanitizeNumber(value: any): number | undefined {
  if (value === null || value === undefined) return undefined;

  // If it's already a valid number, return it
  if (typeof value === 'number' && !isNaN(value) && isFinite(value)) {
    return value > 0 ? value : undefined;
  }

  // If it's a string, try to parse it
  if (typeof value === 'string') {
    // Reject very long strings (likely HTML dumps)
    if (value.length > 50) return undefined;

    // Try to extract number from string
    const parsed = parseFloat(value.replace(/[^0-9.]/g, ''));
    if (!isNaN(parsed) && isFinite(parsed) && parsed > 0) {
      return parsed;
    }
  }

  return undefined;
}

function sanitizeText(value: any, maxLength: number = 200): string | undefined {
  if (value === null || value === undefined) return undefined;
  if (typeof value !== 'string') return undefined;

  // Trim and check length
  const trimmed = value.trim();
  if (trimmed.length === 0 || trimmed.length > maxLength) return undefined;

  return trimmed;
}

// Helper to normalize property data from both flat and nested schemas
function normalizeProperty(property: any) {
  // Check if it's nested Firestore enterprise schema - check for object structure, not just values
  const isNested = property.basic_info || property.financial || (typeof property.location === 'object' && property.location !== null);

  if (isNested) {
    return {
      id: property.id || property.metadata?.hash,
      title: sanitizeText(property.basic_info?.title || property.title, 150),
      price: sanitizeNumber(property.financial?.price),
      price_per_sqm: sanitizeNumber(property.financial?.price_per_sqm),
      listing_type: sanitizeText(property.basic_info?.listing_type, 50),
      status: sanitizeText(property.basic_info?.status, 50),
      location: sanitizeText(property.location?.area || property.location?.full_address || property.location?.location_text || property.location?.lga || property.location?.state, 100),
      lga: sanitizeText(property.location?.lga, 50),
      state: sanitizeText(property.location?.state, 50),
      bedrooms: sanitizeNumber(property.property_details?.bedrooms),
      bathrooms: sanitizeNumber(property.property_details?.bathrooms),
      toilets: sanitizeNumber(property.property_details?.toilets),
      property_type: sanitizeText(property.property_details?.property_type, 50),
      furnishing: sanitizeText(property.property_details?.furnishing, 50),
      land_size: sanitizeNumber(property.property_details?.land_size),
      built_area: sanitizeNumber(property.property_details?.built_area),
      year_built: sanitizeNumber(property.property_details?.year_built),
      parking_spaces: sanitizeNumber(property.property_details?.parking_spaces),
      image_url: property.media?.images?.[0]?.url || property.image_url,
      image_count: property.media?.images?.length || 0,
      site_key: sanitizeText(property.basic_info?.site_key || property.site_key, 50),
      quality_score: sanitizeNumber(property.metadata?.quality_score),
      scrape_timestamp: property.metadata?.scrape_timestamp,
      agent_name: sanitizeText(property.agent_info?.name, 100),
      agency: sanitizeText(property.agent_info?.agency, 100),
      contact: sanitizeText(property.agent_info?.contact, 50),
      description: sanitizeText(property.basic_info?.description, 500),
      features: property.amenities?.features || [],
      security: property.amenities?.security || [],
      utilities: property.amenities?.utilities || [],
      is_premium: property.tags?.premium,
      is_hot_deal: property.tags?.hot_deal,
    };
  }

  // Flat schema - explicitly extract only the fields we need to avoid nested objects
  const flatLocation = typeof property.location === 'object'
    ? sanitizeText(property.location?.area || property.location?.full_address || property.location?.location_text || property.location?.lga || property.location?.state, 100)
    : sanitizeText(property.location, 100);

  return {
    id: property.id,
    title: sanitizeText(property.title, 150),
    price: sanitizeNumber(property.price),
    price_per_sqm: sanitizeNumber(property.price_per_sqm),
    listing_type: sanitizeText(property.listing_type, 50),
    status: sanitizeText(property.status, 50),
    location: flatLocation,
    lga: sanitizeText(property.lga, 50),
    state: sanitizeText(property.state, 50),
    bedrooms: sanitizeNumber(property.bedrooms),
    bathrooms: sanitizeNumber(property.bathrooms),
    toilets: sanitizeNumber(property.toilets),
    property_type: sanitizeText(property.property_type, 50),
    furnishing: sanitizeText(property.furnishing, 50),
    land_size: sanitizeNumber(property.land_size),
    built_area: sanitizeNumber(property.built_area),
    year_built: sanitizeNumber(property.year_built),
    parking_spaces: sanitizeNumber(property.parking_spaces),
    image_url: property.image_url,
    image_count: property.image_count || 0,
    site_key: sanitizeText(property.site_key, 50),
    quality_score: sanitizeNumber(property.quality_score || property.metadata?.quality_score),
    scrape_timestamp: property.scrape_timestamp || property.metadata?.scrape_timestamp,
    agent_name: sanitizeText(property.agent_name, 100),
    agency: sanitizeText(property.agency, 100),
    contact: sanitizeText(property.contact, 50),
    description: sanitizeText(property.description, 500),
    features: property.features || [],
    security: property.security || [],
    utilities: property.utilities || [],
    is_premium: property.is_premium || property.tags?.premium,
    is_hot_deal: property.is_hot_deal || property.tags?.hot_deal,
  };
}

// Enterprise-grade data quality helpers
function normalizeImageUrl(url: string | undefined): string | undefined {
  if (!url) return undefined;

  // Reject relative paths (../../, ../, ./)
  if (url.startsWith('../') || url.startsWith('./')) return undefined;

  // Convert protocol-relative URLs to HTTPS
  if (url.startsWith('//')) {
    return `https:${url}`;
  }

  // Accept absolute URLs (http://, https://) or absolute paths (/)
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/')) {
    return url;
  }

  return undefined;
}

function getDisplayTitle(title: string | undefined, location: string | undefined, propertyType: string | undefined): string {
  // If title is missing or too short (generic location names like "Chevron", "Ikate")
  if (!title || title.length < 10) {
    // Generate a descriptive title from available data
    const parts = [];
    if (propertyType) parts.push(propertyType);
    if (location) parts.push(`in ${location}`);

    return parts.length > 0 ? parts.join(' ') : 'Property Details Available';
  }

  return title;
}

function getDisplayPrice(price: number | undefined): { display: string; color: string } | null {
  if (!price || price === 0) {
    return { display: 'Price on Request', color: 'text-slate-400' };
  }

  // Format large numbers nicely
  if (price >= 1_000_000_000) {
    return { display: `₦${(price / 1_000_000_000).toFixed(2)}B`, color: 'text-green-400' };
  } else if (price >= 1_000_000) {
    return { display: `₦${(price / 1_000_000).toFixed(2)}M`, color: 'text-green-400' };
  } else if (price >= 1_000) {
    return { display: `₦${(price / 1_000).toFixed(0)}K`, color: 'text-green-400' };
  }

  return { display: `₦${price.toLocaleString()}`, color: 'text-green-400' };
}

export function PropertyCard({ property, onClick, viewMode = 'grid' }: PropertyCardProps) {
  const [showDetailModal, setShowDetailModal] = useState(false);
  const normalized = normalizeProperty(property);

  // CRITICAL: Force location to be a string or undefined to prevent React errors
  const safeLocation = typeof normalized.location === 'string' ? normalized.location : undefined;

  // Enterprise-grade data processing
  const displayTitle = getDisplayTitle(normalized.title, safeLocation, normalized.property_type);
  const priceInfo = getDisplayPrice(normalized.price);
  const hasLowQuality = normalized.quality_score !== undefined && normalized.quality_score < 50;
  const safeImageUrl = normalizeImageUrl(normalized.image_url);

  // Check if image URL has query string (needs unoptimized mode)
  const hasQueryString = safeImageUrl?.includes('?') ?? false;

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      setShowDetailModal(true);
    }
  };

  // List View Layout - Horizontal
  if (viewMode === 'list') {
    return (
      <>
        <Card
          className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all cursor-pointer group"
          onClick={handleClick}
        >
          <div className="flex flex-col sm:flex-row gap-4 p-3 sm:p-4">
            {/* Property Image - Left side on desktop, top on mobile */}
            <div className="relative w-full sm:w-48 h-48 sm:h-32 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden flex-shrink-0 rounded-lg">
              {safeImageUrl ? (
                <Image
                  src={safeImageUrl}
                  alt={displayTitle}
                  fill
                  className="object-cover transition-transform group-hover:scale-105"
                  unoptimized={hasQueryString}
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                  }}
                />
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-slate-600">
                  <Home className="w-12 h-12 mb-1" />
                  <span className="text-xs text-slate-500">No Image</span>
                </div>
              )}

              {/* Badges */}
              <div className="absolute top-2 left-2 right-2 flex justify-between items-start gap-2">
                <div className="flex flex-wrap gap-1">
                  {normalized.is_premium && (
                    <Badge className="bg-yellow-500 text-black border-none text-xs font-bold">
                      PREMIUM
                    </Badge>
                  )}
                  {normalized.is_hot_deal && (
                    <Badge className="bg-red-500 text-white border-none text-xs font-bold">
                      HOT DEAL
                    </Badge>
                  )}
                  {hasLowQuality && (
                    <Badge className="bg-yellow-500/80 backdrop-blur-sm text-black border-none text-xs">
                      Limited Info
                    </Badge>
                  )}
                </div>
                {normalized.site_key && (
                  <Badge className="bg-blue-500/80 backdrop-blur-sm text-white border-none text-xs">
                    {normalized.site_key}
                  </Badge>
                )}
              </div>

              {normalized.image_count > 1 && (
                <Badge className="absolute bottom-2 right-2 bg-black/60 backdrop-blur-sm text-white border-none text-xs flex items-center gap-1">
                  <Camera className="w-3 h-3" />
                  {normalized.image_count}
                </Badge>
              )}
            </div>

            {/* Property Details - Right side on desktop, bottom on mobile */}
            <div className="flex-1 min-w-0 space-y-2">
              {/* Price and Title Row */}
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-white font-semibold text-base sm:text-lg line-clamp-2 flex-1">
                  {displayTitle}
                </h3>
                {priceInfo && (
                  <div className="flex flex-col items-end flex-shrink-0">
                    <span className={`text-lg sm:text-xl font-bold ${priceInfo.color} whitespace-nowrap`}>
                      {priceInfo.display}
                    </span>
                    {normalized.price_per_sqm && (
                      <span className="text-xs text-slate-400 whitespace-nowrap">
                        ₦{(normalized.price_per_sqm / 1000).toFixed(0)}K/sqm
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Location */}
              {safeLocation && (
                <div className="flex items-center gap-2 text-slate-400 min-w-0">
                  <MapPin className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs sm:text-sm truncate">{safeLocation}</span>
                </div>
              )}

              {/* Property Details and Badges */}
              <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                {normalized.bedrooms !== undefined && normalized.bedrooms !== null && normalized.bedrooms > 0 && normalized.bedrooms <= 20 && (
                  <div className="flex items-center gap-1 text-slate-400 text-xs sm:text-sm">
                    <Bed className="w-4 h-4" />
                    <span>{normalized.bedrooms} bed{normalized.bedrooms !== 1 ? 's' : ''}</span>
                  </div>
                )}
                {normalized.bathrooms !== undefined && normalized.bathrooms !== null && normalized.bathrooms > 0 && normalized.bathrooms <= 10 && (
                  <div className="flex items-center gap-1 text-slate-400 text-xs sm:text-sm">
                    <Bath className="w-4 h-4" />
                    <span>{normalized.bathrooms} bath{normalized.bathrooms !== 1 ? 's' : ''}</span>
                  </div>
                )}
                {normalized.land_size && normalized.land_size < 1000000 && (
                  <div className="flex items-center gap-1 text-slate-400 text-xs sm:text-sm">
                    <Square className="w-4 h-4" />
                    <span>{normalized.land_size.toLocaleString()} sqm</span>
                  </div>
                )}

                {/* Type Badges */}
                {normalized.property_type && (
                  <Badge variant="outline" className="bg-slate-700/50 text-slate-300 border-slate-600 capitalize text-xs">
                    {normalized.property_type}
                  </Badge>
                )}
                {normalized.listing_type && (
                  <Badge variant="outline" className="bg-blue-500/20 text-blue-300 border-blue-500/50 capitalize text-xs">
                    {normalized.listing_type}
                  </Badge>
                )}
                {normalized.furnishing && (
                  <Badge variant="outline" className="bg-purple-500/20 text-purple-300 border-purple-500/50 capitalize text-xs">
                    {normalized.furnishing}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </Card>

        <PropertyDetailModal
          property={property}
          open={showDetailModal}
          onOpenChange={setShowDetailModal}
        />
      </>
    );
  }

  // Grid View Layout - Vertical Card (default)
  return (
    <>
      <Card
        className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all hover:scale-[1.02] cursor-pointer group flex flex-col h-full"
        onClick={handleClick}
      >
        {/* Property Image */}
        <div className="relative h-48 sm:h-56 w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden flex-shrink-0">
          {safeImageUrl ? (
            <Image
              src={safeImageUrl}
              alt={displayTitle}
              fill
              className="object-cover transition-transform group-hover:scale-105"
              unoptimized={hasQueryString}
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-600">
              <Home className="w-16 h-16 mb-2" />
              <span className="text-xs text-slate-500">No Image Available</span>
            </div>
          )}

          {/* Top Badges Row */}
          <div className="absolute top-2 left-2 right-2 flex justify-between items-start gap-2">
            <div className="flex flex-wrap gap-1">
              {normalized.is_premium && (
                <Badge className="bg-yellow-500 text-black border-none text-xs font-bold">
                  PREMIUM
                </Badge>
              )}
              {normalized.is_hot_deal && (
                <Badge className="bg-red-500 text-white border-none text-xs font-bold">
                  HOT DEAL
                </Badge>
              )}
              {hasLowQuality && (
                <Badge className="bg-yellow-500/80 backdrop-blur-sm text-black border-none text-xs">
                  Limited Info
                </Badge>
              )}
            </div>
            {normalized.site_key && (
              <Badge className="bg-blue-500/80 backdrop-blur-sm text-white border-none text-xs">
                {normalized.site_key}
              </Badge>
            )}
          </div>

          {/* Image Count Badge */}
          {normalized.image_count > 1 && (
            <Badge className="absolute bottom-2 right-2 bg-black/60 backdrop-blur-sm text-white border-none text-xs flex items-center gap-1">
              <Camera className="w-3 h-3" />
              {normalized.image_count}
            </Badge>
          )}
        </div>

        <CardContent className="p-3 sm:p-4 space-y-2 sm:space-y-3 flex-1 flex flex-col min-h-0">
          {/* Price - Always show, with graceful handling of missing price */}
          {priceInfo && (
            <div className="flex items-center justify-between gap-2 flex-shrink-0">
              <div className="flex items-center gap-2">
                <TrendingUp className={`w-4 h-4 ${priceInfo.color} flex-shrink-0`} />
                <span className={`text-lg sm:text-xl font-bold ${priceInfo.color} truncate`}>
                  {priceInfo.display}
                </span>
              </div>
              {normalized.price_per_sqm && (
                <span className="text-xs text-slate-400 whitespace-nowrap">
                  ₦{(normalized.price_per_sqm / 1000).toFixed(0)}K/sqm
                </span>
              )}
            </div>
          )}

          {/* Title - Enhanced with fallback */}
          <h3 className="text-white font-semibold text-base sm:text-lg line-clamp-2 min-h-[2.5rem] sm:min-h-[3.5rem] flex-shrink-0">
            {displayTitle}
          </h3>

          {/* Location */}
          {safeLocation && (
            <div className="flex items-center gap-2 text-slate-400 min-w-0 flex-shrink-0">
              <MapPin className="w-4 h-4 flex-shrink-0" />
              <span className="text-xs sm:text-sm truncate">{safeLocation}</span>
            </div>
          )}

          {/* Property Details */}
          <div className="flex items-center gap-3 sm:gap-4 text-slate-400 text-xs sm:text-sm flex-shrink-0 flex-wrap">
            {normalized.bedrooms !== undefined && normalized.bedrooms !== null && normalized.bedrooms > 0 && (
              <div className="flex items-center gap-1 flex-shrink-0">
                <Bed className="w-4 h-4 flex-shrink-0" />
                <span>{normalized.bedrooms} bed{normalized.bedrooms !== 1 ? 's' : ''}</span>
              </div>
            )}
            {normalized.bathrooms !== undefined && normalized.bathrooms !== null && normalized.bathrooms > 0 && normalized.bathrooms <= 10 && (
              <div className="flex items-center gap-1 flex-shrink-0">
                <Bath className="w-4 h-4 flex-shrink-0" />
                <span>{normalized.bathrooms} bath{normalized.bathrooms !== 1 ? 's' : ''}</span>
              </div>
            )}
            {normalized.land_size && (
              <div className="flex items-center gap-1 flex-shrink-0">
                <Square className="w-4 h-4 flex-shrink-0" />
                <span>{normalized.land_size.toLocaleString()} sqm</span>
              </div>
            )}
          </div>

          {/* Badges Row */}
          <div className="flex flex-wrap gap-2 flex-shrink-0">
            {normalized.property_type && (
              <Badge
                variant="outline"
                className="bg-slate-700/50 text-slate-300 border-slate-600 capitalize text-xs"
              >
                {normalized.property_type}
              </Badge>
            )}
            {normalized.listing_type && (
              <Badge variant="outline" className="bg-blue-500/20 text-blue-300 border-blue-500/50 capitalize text-xs">
                {normalized.listing_type}
              </Badge>
            )}
            {normalized.furnishing && (
              <Badge variant="outline" className="bg-purple-500/20 text-purple-300 border-purple-500/50 capitalize text-xs">
                {normalized.furnishing}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Property Detail Modal - All comprehensive details shown here */}
      <PropertyDetailModal
        property={property}
        open={showDetailModal}
        onOpenChange={setShowDetailModal}
      />
    </>
  );
}
