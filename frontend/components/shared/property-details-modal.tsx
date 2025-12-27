"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { MapPin, Bed, Bath, Home, TrendingUp, X } from "lucide-react";
import Image from "next/image";
import { Button } from "@/components/ui/button";

interface PropertyDetailsModalProps {
  open: boolean;
  onClose: () => void;
  property: any; // Use FirestoreProperty type if available
}

// Helper to normalize property data from both flat and nested schemas
function normalizeProperty(property: any) {
  if (!property) return null;

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
      amenities: property.amenities?.features || property.amenities,
      created_at: property.uploaded_at || property.created_at,
    };
  }

  // Flat schema - return as-is
  return property;
}

export const PropertyDetailsModal: React.FC<PropertyDetailsModalProps> = ({
  open,
  onClose,
  property,
}) => {
  const normalized = normalizeProperty(property);

  if (!normalized) return null;

  // Check if image URL has query string (needs unoptimized mode)
  const hasQueryString = normalized.image_url?.includes('?') ?? false;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg w-full bg-slate-900 border-slate-700 text-white p-0">
        <DialogHeader className="flex items-center justify-between p-4 border-b border-slate-700">
          <DialogTitle className="text-xl font-bold">
            {normalized.title || "Untitled Property"}
          </DialogTitle>
          <DialogClose asChild>
            <Button
              variant="ghost"
              size="sm"
              aria-label="Close details"
              className="text-white"
            >
              <X className="w-5 h-5" />
            </Button>
          </DialogClose>
        </DialogHeader>
        <div className="relative h-56 w-full bg-slate-800">
          {normalized.image_url ? (
            <Image
              src={normalized.image_url}
              alt={normalized.title}
              fill
              className="object-cover"
              unoptimized={hasQueryString}
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
        <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
          {/* Price */}
          {normalized.price && normalized.price > 0 && (
            <div className="flex items-center gap-2 bg-green-500/10 p-3 rounded-lg border border-green-500/20">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <div>
                <div className="text-sm text-green-300/70">Price</div>
                <div className="text-2xl font-bold text-green-400">
                  ₦{normalized.price.toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {/* Location */}
          {normalized.location && (
            <div className="flex items-start gap-2 text-slate-300">
              <MapPin className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-xs text-slate-400">Location</div>
                <div className="font-medium">{normalized.location}</div>
              </div>
            </div>
          )}

          {/* Property Details */}
          <div className="grid grid-cols-2 gap-3">
            {normalized.bedrooms !== undefined && normalized.bedrooms !== null && normalized.bedrooms > 0 && (
              <div className="flex items-center gap-2 bg-slate-800/50 p-3 rounded-lg">
                <Bed className="w-4 h-4 text-blue-400" />
                <div>
                  <div className="text-xs text-slate-400">Bedrooms</div>
                  <div className="font-semibold text-white">{normalized.bedrooms}</div>
                </div>
              </div>
            )}
            {normalized.bathrooms !== undefined && normalized.bathrooms !== null && normalized.bathrooms > 0 && (
              <div className="flex items-center gap-2 bg-slate-800/50 p-3 rounded-lg">
                <Bath className="w-4 h-4 text-cyan-400" />
                <div>
                  <div className="text-xs text-slate-400">Bathrooms</div>
                  <div className="font-semibold text-white">{normalized.bathrooms}</div>
                </div>
              </div>
            )}
          </div>

          {/* Property Type */}
          {normalized.property_type && (
            <div>
              <div className="text-xs text-slate-400 mb-1">Property Type</div>
              <Badge
                variant="outline"
                className="bg-slate-700/50 text-slate-300 border-slate-600"
              >
                {normalized.property_type}
              </Badge>
            </div>
          )}

          {/* Amenities */}
          {normalized.amenities && normalized.amenities.length > 0 && (
            <div>
              <div className="text-xs text-slate-400 mb-2">Amenities</div>
              <div className="flex flex-wrap gap-2">
                {normalized.amenities.slice(0, 10).map((amenity: string, i: number) => (
                  <Badge
                    key={i}
                    variant="outline"
                    className="bg-blue-500/10 text-blue-300 border-blue-500/20 text-xs"
                  >
                    {amenity}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Listing Date */}
          {normalized.created_at && (
            <div className="pt-3 border-t border-slate-700">
              <div className="text-xs text-slate-500">
                Listed: {new Date(normalized.created_at).toLocaleDateString()}
              </div>
            </div>
          )}

          {/* View Property Link */}
          {property.basic_info?.listing_url || property.listing_url && (
            <a
              href={property.basic_info?.listing_url || property.listing_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center bg-blue-600 hover:bg-blue-500 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              View Full Listing
            </a>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
