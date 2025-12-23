"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Bed, Bath, Home, TrendingUp } from "lucide-react";
import Image from "next/image";

interface PropertyCardProps {
  property: {
    id: string;
    title: string;
    price?: number;
    location?: string;
    bedrooms?: number;
    bathrooms?: number;
    property_type?: string;
    image_url?: string;
    site_key?: string;
    created_at?: string;
  };
  onClick?: () => void;
}

export function PropertyCard({ property, onClick }: PropertyCardProps) {
  return (
    <Card
      className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-all hover:scale-[1.02] cursor-pointer overflow-hidden"
      onClick={onClick}
    >
      {/* Property Image */}
      <div className="relative h-48 w-full bg-slate-900">
        {property.image_url ? (
          <Image
            src={property.image_url}
            alt={property.title}
            fill
            className="object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <Home className="w-16 h-16 text-slate-600" />
          </div>
        )}
        {property.site_key && (
          <Badge className="absolute top-2 right-2 bg-blue-500/80 text-white border-none">
            {property.site_key}
          </Badge>
        )}
      </div>

      <CardContent className="p-4 space-y-3">
        {/* Price */}
        {property.price && (
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-xl font-bold text-green-400">
              ₦{property.price.toLocaleString()}
            </span>
          </div>
        )}

        {/* Title */}
        <h3 className="text-white font-semibold text-lg line-clamp-2">
          {property.title}
        </h3>

        {/* Location */}
        {property.location && (
          <div className="flex items-center gap-2 text-slate-400">
            <MapPin className="w-4 h-4" />
            <span className="text-sm truncate">{property.location}</span>
          </div>
        )}

        {/* Property Details */}
        <div className="flex items-center gap-4 text-slate-400 text-sm">
          {property.bedrooms !== undefined && (
            <div className="flex items-center gap-1">
              <Bed className="w-4 h-4" />
              <span>{property.bedrooms} beds</span>
            </div>
          )}
          {property.bathrooms !== undefined && (
            <div className="flex items-center gap-1">
              <Bath className="w-4 h-4" />
              <span>{property.bathrooms} baths</span>
            </div>
          )}
        </div>

        {/* Property Type */}
        {property.property_type && (
          <Badge
            variant="outline"
            className="bg-slate-700/50 text-slate-300 border-slate-600"
          >
            {property.property_type}
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
