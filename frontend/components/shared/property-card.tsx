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
}

// Helper to normalize property data from both flat and nested schemas
function normalizeProperty(property: any) {
  // Check if it's nested Firestore enterprise schema - check for object structure, not just values
  const isNested = property.basic_info || property.financial || (typeof property.location === 'object' && property.location !== null);

  if (isNested) {
    return {
      id: property.id || property.metadata?.hash,
      title: property.basic_info?.title || property.title,
      price: property.financial?.price,
      price_per_sqm: property.financial?.price_per_sqm,
      listing_type: property.basic_info?.listing_type,
      status: property.basic_info?.status,
      location: property.location?.area || property.location?.full_address || property.location?.location_text || property.location?.lga || property.location?.state || undefined,
      lga: property.location?.lga,
      state: property.location?.state,
      bedrooms: property.property_details?.bedrooms,
      bathrooms: property.property_details?.bathrooms,
      toilets: property.property_details?.toilets,
      property_type: property.property_details?.property_type,
      furnishing: property.property_details?.furnishing,
      land_size: property.property_details?.land_size,
      built_area: property.property_details?.built_area,
      year_built: property.property_details?.year_built,
      parking_spaces: property.property_details?.parking_spaces,
      image_url: property.media?.images?.[0]?.url || property.image_url,
      image_count: property.media?.images?.length || 0,
      site_key: property.basic_info?.site_key || property.site_key,
      quality_score: property.metadata?.quality_score,
      scrape_timestamp: property.metadata?.scrape_timestamp,
      agent_name: property.agent_info?.name,
      agency: property.agent_info?.agency,
      contact: property.agent_info?.contact,
      description: property.basic_info?.description,
      features: property.amenities?.features || [],
      security: property.amenities?.security || [],
      utilities: property.amenities?.utilities || [],
      is_premium: property.tags?.premium,
      is_hot_deal: property.tags?.hot_deal,
    };
  }

  // Flat schema - explicitly extract only the fields we need to avoid nested objects
  const flatLocation = typeof property.location === 'object'
    ? (property.location?.area || property.location?.full_address || property.location?.location_text || property.location?.lga || property.location?.state || undefined)
    : property.location;

  return {
    id: property.id,
    title: property.title,
    price: property.price,
    price_per_sqm: property.price_per_sqm,
    listing_type: property.listing_type,
    status: property.status,
    location: flatLocation,
    lga: property.lga,
    state: property.state,
    bedrooms: property.bedrooms,
    bathrooms: property.bathrooms,
    toilets: property.toilets,
    property_type: property.property_type,
    furnishing: property.furnishing,
    land_size: property.land_size,
    built_area: property.built_area,
    year_built: property.year_built,
    parking_spaces: property.parking_spaces,
    image_url: property.image_url,
    image_count: property.image_count || 0,
    site_key: property.site_key,
    quality_score: property.quality_score || property.metadata?.quality_score,
    scrape_timestamp: property.scrape_timestamp || property.metadata?.scrape_timestamp,
    agent_name: property.agent_name,
    agency: property.agency,
    contact: property.contact,
    description: property.description,
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

export function PropertyCard({ property, onClick }: PropertyCardProps) {
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

  return (
    <>
      <Card
        className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all hover:scale-[1.01] cursor-pointer group flex flex-col h-[600px] max-h-[600px] overflow-hidden"
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

        {/* Scrollable Content */}
        <CardContent className="p-4 flex-1 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
          {/* Price Section */}
          {priceInfo && (
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <TrendingUp className={`w-5 h-5 ${priceInfo.color}`} />
                <span className={`text-2xl font-bold ${priceInfo.color}`}>
                  {priceInfo.display}
                </span>
              </div>
              {normalized.price_per_sqm && (
                <div className="text-xs text-slate-400">
                  ₦{normalized.price_per_sqm.toLocaleString()}/sqm
                </div>
              )}
            </div>
          )}

          {/* Title */}
          <h3 className="text-white font-semibold text-lg leading-tight">
            {displayTitle}
          </h3>

          {/* Status & Listing Type */}
          <div className="flex flex-wrap gap-2">
            {normalized.listing_type && (
              <Badge variant="outline" className="bg-blue-500/20 text-blue-300 border-blue-500/50 capitalize text-xs">
                <Tag className="w-3 h-3 mr-1" />
                {normalized.listing_type}
              </Badge>
            )}
            {normalized.furnishing && (
              <Badge variant="outline" className="bg-purple-500/20 text-purple-300 border-purple-500/50 capitalize text-xs">
                {normalized.furnishing}
              </Badge>
            )}
          </div>

          {/* Location */}
          <div className="space-y-1">
            {safeLocation && (
              <div className="flex items-start gap-2 text-slate-300">
                <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span className="text-sm">{safeLocation}</span>
              </div>
            )}
            {(normalized.lga || normalized.state) && (
              <div className="flex items-center gap-2 text-slate-400 text-xs ml-6">
                <MapPinned className="w-3 h-3" />
                {[normalized.lga, normalized.state].filter(Boolean).join(', ')}
              </div>
            )}
          </div>

          {/* Property Specs Grid */}
          <div className="grid grid-cols-2 gap-2 py-2 border-y border-slate-700">
            {normalized.bedrooms !== undefined && normalized.bedrooms > 0 && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Bed className="w-4 h-4 text-blue-400" />
                <span>{normalized.bedrooms} Beds</span>
              </div>
            )}
            {normalized.bathrooms !== undefined && normalized.bathrooms > 0 && normalized.bathrooms <= 10 && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Bath className="w-4 h-4 text-blue-400" />
                <span>{normalized.bathrooms} Baths</span>
              </div>
            )}
            {normalized.toilets !== undefined && normalized.toilets > 0 && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Droplet className="w-4 h-4 text-blue-400" />
                <span>{normalized.toilets} Toilets</span>
              </div>
            )}
            {normalized.parking_spaces !== undefined && normalized.parking_spaces > 0 && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Car className="w-4 h-4 text-green-400" />
                <span>{normalized.parking_spaces} Parking</span>
              </div>
            )}
            {normalized.land_size && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Square className="w-4 h-4 text-yellow-400" />
                <span>{normalized.land_size.toLocaleString()} sqm</span>
              </div>
            )}
            {normalized.built_area && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Maximize2 className="w-4 h-4 text-yellow-400" />
                <span>{normalized.built_area.toLocaleString()} sqm</span>
              </div>
            )}
            {normalized.year_built && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Calendar className="w-4 h-4 text-purple-400" />
                <span>Built {normalized.year_built}</span>
              </div>
            )}
            {normalized.property_type && (
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <Building2 className="w-4 h-4 text-indigo-400" />
                <span className="capitalize">{normalized.property_type}</span>
              </div>
            )}
          </div>

          {/* Description Preview */}
          {normalized.description && (
            <div className="space-y-1">
              <div className="text-xs font-semibold text-slate-400 uppercase">Description</div>
              <p className="text-sm text-slate-300 line-clamp-3">
                {normalized.description}
              </p>
            </div>
          )}

          {/* Amenities & Features */}
          {(normalized.features.length > 0 || normalized.security.length > 0 || normalized.utilities.length > 0) && (
            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase">Amenities</div>
              <div className="flex flex-wrap gap-1">
                {normalized.features.slice(0, 6).map((feature: string, idx: number) => (
                  <Badge key={idx} variant="outline" className="bg-green-500/10 text-green-300 border-green-500/30 text-xs">
                    {feature}
                  </Badge>
                ))}
                {normalized.security.slice(0, 3).map((item: string, idx: number) => (
                  <Badge key={`sec-${idx}`} variant="outline" className="bg-red-500/10 text-red-300 border-red-500/30 text-xs flex items-center gap-1">
                    <Shield className="w-3 h-3" />
                    {item}
                  </Badge>
                ))}
                {normalized.utilities.slice(0, 3).map((item: string, idx: number) => (
                  <Badge key={`util-${idx}`} variant="outline" className="bg-blue-500/10 text-blue-300 border-blue-500/30 text-xs flex items-center gap-1">
                    <Zap className="w-3 h-3" />
                    {item}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Agent/Agency Info */}
          {(normalized.agent_name || normalized.agency) && (
            <div className="space-y-1 pt-2 border-t border-slate-700">
              <div className="text-xs font-semibold text-slate-400 uppercase">Listed By</div>
              {normalized.agent_name && (
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <User className="w-4 h-4 text-blue-400" />
                  <span>{normalized.agent_name}</span>
                </div>
              )}
              {normalized.agency && (
                <div className="flex items-center gap-2 text-sm text-slate-300">
                  <Building2 className="w-4 h-4 text-indigo-400" />
                  <span>{normalized.agency}</span>
                </div>
              )}
              {normalized.contact && (
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Phone className="w-3 h-3" />
                  <span>Contact available</span>
                </div>
              )}
            </div>
          )}

          {/* Listing Date */}
          {normalized.scrape_timestamp && (
            <div className="flex items-center gap-2 text-xs text-slate-400 pt-2 border-t border-slate-700">
              <Clock className="w-3 h-3" />
              <span>
                Listed {new Date(normalized.scrape_timestamp).toLocaleDateString()}
              </span>
            </div>
          )}

          {/* Click to view more */}
          <div className="text-center text-xs text-blue-400 font-medium py-2">
            Click to view full details →
          </div>
        </CardContent>
      </Card>

      {/* Property Detail Modal */}
      <PropertyDetailModal
        property={property}
        open={showDetailModal}
        onOpenChange={setShowDetailModal}
      />
    </>
  );
}
