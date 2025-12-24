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
    };
  }

  // Flat schema - return as-is
  return property;
}

export function PropertyCard({ property, onClick }: PropertyCardProps) {
  const normalized = normalizeProperty(property);

  return (
    <Card
      className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
      onClick={onClick}
    >
      {/* Property Image */}
      <div className="relative h-48 w-full bg-slate-900">
        {normalized.image_url ? (
          <Image
            src={normalized.image_url}
            alt={normalized.title}
            fill
            className="object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <Home className="w-16 h-16 text-slate-600" />
          </div>
        )}
        {normalized.site_key && (
          <Badge className="absolute top-2 right-2 bg-blue-500/80 text-white border-none">
            {normalized.site_key}
          </Badge>
        )}
      </div>

      <CardContent className="p-4 space-y-3">
        {/* Price */}
        {normalized.price && normalized.price > 0 && (
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-xl font-bold text-green-400">
              ₦{normalized.price.toLocaleString()}
            </span>
          </div>
        )}

        {/* Title */}
        <h3 className="text-white font-semibold text-lg line-clamp-2">
          {normalized.title}
        </h3>

        {/* Location */}
        {normalized.location && (
          <div className="flex items-center gap-2 text-slate-400">
            <MapPin className="w-4 h-4" />
            <span className="text-sm truncate">{normalized.location}</span>
          </div>
        )}

        {/* Property Details */}
        <div className="flex items-center gap-4 text-slate-400 text-sm">
          {normalized.bedrooms !== undefined && normalized.bedrooms !== null && (
            <div className="flex items-center gap-1">
              <Bed className="w-4 h-4" />
              <span>{normalized.bedrooms} beds</span>
            </div>
          )}
          {normalized.bathrooms !== undefined && normalized.bathrooms !== null && (
            <div className="flex items-center gap-1">
              <Bath className="w-4 h-4" />
              <span>{normalized.bathrooms} baths</span>
            </div>
          )}
        </div>

        {/* Property Type */}
        {normalized.property_type && (
          <Badge
            variant="outline"
            className="bg-slate-700/50 text-slate-300 border-slate-600"
          >
            {normalized.property_type}
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
