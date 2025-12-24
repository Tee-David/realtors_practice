"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Bed, Bath, Home, TrendingUp } from "lucide-react";
import Image from "next/image";

interface PropertyCardProps {
  property: any; // Support both flat and nested Firestore enterprise schema
  onClick?: () => void;
}

// Helper to normalize property data from both flat and nested schemas
function normalizeProperty(property: any) {
  // Check if it's nested Firestore enterprise schema
  const isNested = property.basic_info || property.financial || property.location?.area;

  if (isNested) {
    return {
      id: property.id || property.metadata?.hash,
      title: property.basic_info?.title || property.title,
      price: property.financial?.price,
      location: property.location?.area || property.location?.full_address || property.location?.location_text,
      bedrooms: property.property_details?.bedrooms,
      bathrooms: property.property_details?.bathrooms,
      property_type: property.property_details?.property_type,
      image_url: property.media?.images?.[0]?.url || property.image_url,
      site_key: property.basic_info?.site_key || property.site_key,
      quality_score: property.metadata?.quality_score,
    };
  }

  // Flat schema - return as-is with quality score if available
  return {
    ...property,
    quality_score: property.quality_score || property.metadata?.quality_score,
  };
}

// Enterprise-grade data quality helpers
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
  const normalized = normalizeProperty(property);

  // Enterprise-grade data processing
  const displayTitle = getDisplayTitle(normalized.title, normalized.location, normalized.property_type);
  const priceInfo = getDisplayPrice(normalized.price);
  const hasLowQuality = normalized.quality_score !== undefined && normalized.quality_score < 50;

  return (
    <Card
      className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden group"
      onClick={onClick}
    >
      {/* Property Image */}
      <div className="relative h-48 w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {normalized.image_url ? (
          <Image
            src={normalized.image_url}
            alt={displayTitle}
            fill
            className="object-cover transition-transform group-hover:scale-105"
            onError={(e) => {
              // Fallback if image fails to load
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

        {/* Source Badge */}
        {normalized.site_key && (
          <Badge className="absolute top-2 right-2 bg-blue-500/80 backdrop-blur-sm text-white border-none text-xs">
            {normalized.site_key}
          </Badge>
        )}

        {/* Quality Indicator (for low quality properties) */}
        {hasLowQuality && (
          <Badge className="absolute top-2 left-2 bg-yellow-500/80 backdrop-blur-sm text-black border-none text-xs">
            Limited Info
          </Badge>
        )}
      </div>

      <CardContent className="p-4 space-y-3">
        {/* Price - Always show, with graceful handling of missing price */}
        {priceInfo && (
          <div className="flex items-center gap-2">
            <TrendingUp className={`w-4 h-4 ${priceInfo.color}`} />
            <span className={`text-xl font-bold ${priceInfo.color}`}>
              {priceInfo.display}
            </span>
          </div>
        )}

        {/* Title - Enhanced with fallback */}
        <h3 className="text-white font-semibold text-lg line-clamp-2 min-h-[3.5rem]">
          {displayTitle}
        </h3>

        {/* Location */}
        {normalized.location && (
          <div className="flex items-center gap-2 text-slate-400">
            <MapPin className="w-4 h-4 flex-shrink-0" />
            <span className="text-sm truncate">{normalized.location}</span>
          </div>
        )}

        {/* Property Details */}
        <div className="flex items-center gap-4 text-slate-400 text-sm">
          {normalized.bedrooms !== undefined && normalized.bedrooms !== null && normalized.bedrooms > 0 && (
            <div className="flex items-center gap-1">
              <Bed className="w-4 h-4" />
              <span>{normalized.bedrooms} bed{normalized.bedrooms !== 1 ? 's' : ''}</span>
            </div>
          )}
          {normalized.bathrooms !== undefined && normalized.bathrooms !== null && normalized.bathrooms > 0 && normalized.bathrooms <= 10 && (
            <div className="flex items-center gap-1">
              <Bath className="w-4 h-4" />
              <span>{normalized.bathrooms} bath{normalized.bathrooms !== 1 ? 's' : ''}</span>
            </div>
          )}
        </div>

        {/* Property Type */}
        {normalized.property_type && (
          <Badge
            variant="outline"
            className="bg-slate-700/50 text-slate-300 border-slate-600 capitalize"
          >
            {normalized.property_type}
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
