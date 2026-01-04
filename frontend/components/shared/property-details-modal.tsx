"use client";

import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  MapPin,
  Bed,
  Bath,
  Home,
  TrendingUp,
  X,
  Car,
  Calendar,
  Shield,
  Lightbulb,
  User,
  Phone,
  Building2,
  Award,
  Clock,
  DollarSign,
  Maximize2,
  Toilet,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
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
      // Basic Info
      id: property.id || property.metadata?.hash,
      title: property.basic_info?.title || property.title,
      status: property.basic_info?.status,
      listing_type: property.basic_info?.listing_type,
      site_key: property.basic_info?.site_key || property.site_key,
      listing_url: property.basic_info?.listing_url,

      // Financial
      price: property.financial?.price,
      currency: property.financial?.currency,
      price_per_sqm: property.financial?.price_per_sqm,

      // Property Details
      property_type: property.property_details?.property_type,
      bedrooms: property.property_details?.bedrooms,
      bathrooms: property.property_details?.bathrooms,
      toilets: property.property_details?.toilets,
      furnishing: property.property_details?.furnishing,
      land_size: property.property_details?.land_size,
      built_area: property.property_details?.built_area,
      year_built: property.property_details?.year_built,
      parking_spaces: property.property_details?.parking_spaces,

      // Location
      location: property.location?.area || property.location?.full_address || property.location?.location_text,
      full_address: property.location?.full_address,
      area: property.location?.area,
      lga: property.location?.lga,
      state: property.location?.state,
      coordinates: property.location?.coordinates,

      // Amenities
      amenities: property.amenities?.features || property.amenities || [],
      security: property.amenities?.security || [],
      utilities: property.amenities?.utilities || [],

      // Media
      images: property.media?.images || [],
      videos: property.media?.videos || [],
      image_url: property.media?.images?.[0]?.url || property.image_url,

      // Agent Info
      agent_name: property.agent_info?.name,
      agent_contact: property.agent_info?.contact,
      agent_agency: property.agent_info?.agency,

      // Metadata
      quality_score: property.metadata?.quality_score,
      scrape_timestamp: property.metadata?.scrape_timestamp,
      hash: property.metadata?.hash,

      // Tags
      premium: property.tags?.premium,
      hot_deal: property.tags?.hot_deal,

      created_at: property.uploaded_at || property.created_at,
    };
  }

  // Flat schema - normalize to same structure
  return {
    id: property.id,
    title: property.title,
    status: property.status,
    listing_type: property.listing_type,
    site_key: property.site_key || property.source,
    listing_url: property.listing_url,
    price: property.price,
    currency: property.currency,
    price_per_sqm: property.price_per_sqm,
    property_type: property.property_type,
    bedrooms: property.bedrooms,
    bathrooms: property.bathrooms,
    toilets: property.toilets,
    furnishing: property.furnishing,
    land_size: property.land_size,
    built_area: property.built_area,
    year_built: property.year_built,
    parking_spaces: property.parking_spaces,
    location: property.location,
    full_address: property.full_address,
    area: property.area,
    lga: property.lga,
    state: property.state,
    coordinates: property.coordinates,
    amenities: Array.isArray(property.amenities) ? property.amenities : [],
    security: Array.isArray(property.security) ? property.security : [],
    utilities: Array.isArray(property.utilities) ? property.utilities : [],
    images: Array.isArray(property.images) ? property.images : [],
    videos: Array.isArray(property.videos) ? property.videos : [],
    image_url: property.image_url,
    agent_name: property.agent_name,
    agent_contact: property.agent_contact,
    agent_agency: property.agent_agency,
    quality_score: property.quality_score,
    scrape_timestamp: property.scrape_timestamp,
    hash: property.hash,
    premium: property.premium,
    hot_deal: property.hot_deal,
    created_at: property.created_at,
  };
}

export const PropertyDetailsModal: React.FC<PropertyDetailsModalProps> = ({
  open,
  onClose,
  property,
}) => {
  const normalized = normalizeProperty(property);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  if (!normalized) return null;

  // Get all images
  const allImages = normalized.images && normalized.images.length > 0
    ? normalized.images
    : normalized.image_url
      ? [{ url: normalized.image_url, order: 0 }]
      : [];

  // Check if image URL has query string (needs unoptimized mode)
  const currentImage = allImages[currentImageIndex];
  const hasQueryString = currentImage?.url?.includes('?') ?? false;

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % allImages.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + allImages.length) % allImages.length);
  };

  // Helper to format currency
  const formatPrice = (price: number | undefined, currency?: string) => {
    if (!price || price === 0) return 'Price on Request';
    const currencySymbol = currency === 'USD' || currency === '$' ? '$' : '₦';
    return `${currencySymbol}${price.toLocaleString()}`;
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl w-full bg-slate-900 border-slate-700 text-white p-0 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <DialogHeader className="flex flex-row items-start justify-between p-4 sm:p-6 border-b border-slate-700 space-y-0">
          <div className="flex-1 pr-4">
            <div className="flex flex-wrap gap-2 mb-2">
              {normalized.premium && (
                <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                  <Award className="w-3 h-3 mr-1" />
                  PREMIUM
                </Badge>
              )}
              {normalized.hot_deal && (
                <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  HOT DEAL
                </Badge>
              )}
              {normalized.status && (
                <Badge variant="outline" className="bg-slate-700/50 text-slate-300 border-slate-600 capitalize">
                  {normalized.status}
                </Badge>
              )}
              {normalized.listing_type && (
                <Badge variant="outline" className="bg-blue-500/10 text-blue-300 border-blue-500/30 capitalize">
                  {normalized.listing_type}
                </Badge>
              )}
            </div>
            <DialogTitle className="text-xl sm:text-2xl font-bold pr-8">
              {normalized.title || "Untitled Property"}
            </DialogTitle>
            {normalized.site_key && (
              <div className="text-sm text-slate-400 mt-1">
                Source: <span className="text-blue-400">{normalized.site_key}</span>
              </div>
            )}
          </div>
          <DialogClose asChild>
            <Button
              variant="ghost"
              size="sm"
              aria-label="Close details"
              className="text-white hover:bg-slate-800 flex-shrink-0"
            >
              <X className="w-5 h-5" />
            </Button>
          </DialogClose>
        </DialogHeader>

        {/* Scrollable Content */}
        <div className="overflow-y-auto flex-1">
          {/* Image Gallery */}
          {allImages.length > 0 && (
            <div className="relative h-64 sm:h-80 w-full bg-slate-800">
              <Image
                src={currentImage.url}
                alt={normalized.title || "Property"}
                fill
                className="object-cover"
                unoptimized={hasQueryString}
              />
              {allImages.length > 1 && (
                <>
                  <Button
                    onClick={prevImage}
                    variant="ghost"
                    size="sm"
                    className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </Button>
                  <Button
                    onClick={nextImage}
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </Button>
                  <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-black/50 px-3 py-1 rounded-full text-xs text-white">
                    {currentImageIndex + 1} / {allImages.length}
                  </div>
                </>
              )}
            </div>
          )}

          <div className="p-4 sm:p-6 space-y-6">
            {/* Price & Financial Details */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-green-400" />
                Financial Details
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {normalized.price && normalized.price > 0 && (
                  <div className="bg-green-500/10 p-4 rounded-lg border border-green-500/20">
                    <div className="text-sm text-green-300/70 mb-1">Price</div>
                    <div className="text-2xl font-bold text-green-400">
                      {formatPrice(normalized.price, normalized.currency)}
                    </div>
                  </div>
                )}
                {normalized.price_per_sqm && normalized.price_per_sqm > 0 && (
                  <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                    <div className="text-sm text-slate-400 mb-1">Price per sqm</div>
                    <div className="text-xl font-semibold text-white">
                      {formatPrice(normalized.price_per_sqm, normalized.currency)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Property Specifications */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Home className="w-5 h-5 text-blue-400" />
                Property Specifications
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {normalized.property_type && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <div className="text-xs text-slate-400 mb-1">Type</div>
                    <div className="font-semibold text-white text-sm">{normalized.property_type}</div>
                  </div>
                )}
                {normalized.bedrooms !== undefined && normalized.bedrooms !== null && normalized.bedrooms > 0 && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <Bed className="w-4 h-4 text-blue-400 mb-1" />
                    <div className="text-xs text-slate-400 mb-1">Bedrooms</div>
                    <div className="font-semibold text-white text-sm">{normalized.bedrooms}</div>
                  </div>
                )}
                {normalized.bathrooms !== undefined && normalized.bathrooms !== null && normalized.bathrooms > 0 && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <Bath className="w-4 h-4 text-cyan-400 mb-1" />
                    <div className="text-xs text-slate-400 mb-1">Bathrooms</div>
                    <div className="font-semibold text-white text-sm">{normalized.bathrooms}</div>
                  </div>
                )}
                {normalized.toilets !== undefined && normalized.toilets !== null && normalized.toilets > 0 && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <Toilet className="w-4 h-4 text-purple-400 mb-1" />
                    <div className="text-xs text-slate-400 mb-1">Toilets</div>
                    <div className="font-semibold text-white text-sm">{normalized.toilets}</div>
                  </div>
                )}
                {normalized.parking_spaces !== undefined && normalized.parking_spaces !== null && normalized.parking_spaces > 0 && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <Car className="w-4 h-4 text-orange-400 mb-1" />
                    <div className="text-xs text-slate-400 mb-1">Parking</div>
                    <div className="font-semibold text-white text-sm">{normalized.parking_spaces}</div>
                  </div>
                )}
                {normalized.land_size && normalized.land_size > 0 && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <Maximize2 className="w-4 h-4 text-green-400 mb-1" />
                    <div className="text-xs text-slate-400 mb-1">Land Size</div>
                    <div className="font-semibold text-white text-sm">{normalized.land_size.toLocaleString()} sqm</div>
                  </div>
                )}
                {normalized.built_area && normalized.built_area > 0 && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <Building2 className="w-4 h-4 text-indigo-400 mb-1" />
                    <div className="text-xs text-slate-400 mb-1">Built Area</div>
                    <div className="font-semibold text-white text-sm">{normalized.built_area.toLocaleString()} sqm</div>
                  </div>
                )}
                {normalized.year_built && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <Calendar className="w-4 h-4 text-yellow-400 mb-1" />
                    <div className="text-xs text-slate-400 mb-1">Year Built</div>
                    <div className="font-semibold text-white text-sm">{normalized.year_built}</div>
                  </div>
                )}
                {normalized.furnishing && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <div className="text-xs text-slate-400 mb-1">Furnishing</div>
                    <div className="font-semibold text-white text-sm capitalize">{normalized.furnishing}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Location Details */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <MapPin className="w-5 h-5 text-red-400" />
                Location
              </h3>
              <div className="space-y-2">
                {normalized.full_address && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <div className="text-xs text-slate-400 mb-1">Full Address</div>
                    <div className="text-white">{normalized.full_address}</div>
                  </div>
                )}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {normalized.area && (
                    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                      <div className="text-xs text-slate-400 mb-1">Area</div>
                      <div className="text-white text-sm">{normalized.area}</div>
                    </div>
                  )}
                  {normalized.lga && (
                    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                      <div className="text-xs text-slate-400 mb-1">LGA</div>
                      <div className="text-white text-sm">{normalized.lga}</div>
                    </div>
                  )}
                  {normalized.state && (
                    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                      <div className="text-xs text-slate-400 mb-1">State</div>
                      <div className="text-white text-sm">{normalized.state}</div>
                    </div>
                  )}
                </div>
                {normalized.coordinates && (normalized.coordinates._latitude || normalized.coordinates.latitude) && (
                  <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <div className="text-xs text-slate-400 mb-1">Coordinates</div>
                    <div className="text-white text-sm font-mono">
                      {normalized.coordinates._latitude || normalized.coordinates.latitude}, {normalized.coordinates._longitude || normalized.coordinates.longitude}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Amenities & Features */}
            {(normalized.amenities?.length > 0 || normalized.security?.length > 0 || normalized.utilities?.length > 0) && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  Amenities & Features
                </h3>
                <div className="space-y-3">
                  {normalized.amenities && normalized.amenities.length > 0 && (
                    <div>
                      <div className="text-sm text-slate-400 mb-2">General Features</div>
                      <div className="flex flex-wrap gap-2">
                        {normalized.amenities.map((amenity: string, i: number) => (
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
                  {normalized.security && normalized.security.length > 0 && (
                    <div>
                      <div className="text-sm text-slate-400 mb-2 flex items-center gap-1">
                        <Shield className="w-4 h-4" />
                        Security
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {normalized.security.map((item: string, i: number) => (
                          <Badge
                            key={i}
                            variant="outline"
                            className="bg-green-500/10 text-green-300 border-green-500/20 text-xs"
                          >
                            {item}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {normalized.utilities && normalized.utilities.length > 0 && (
                    <div>
                      <div className="text-sm text-slate-400 mb-2">Utilities</div>
                      <div className="flex flex-wrap gap-2">
                        {normalized.utilities.map((utility: string, i: number) => (
                          <Badge
                            key={i}
                            variant="outline"
                            className="bg-purple-500/10 text-purple-300 border-purple-500/20 text-xs"
                          >
                            {utility}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Agent Information */}
            {(normalized.agent_name || normalized.agent_contact || normalized.agent_agency) && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <User className="w-5 h-5 text-indigo-400" />
                  Agent Information
                </h3>
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700 space-y-2">
                  {normalized.agent_name && (
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-slate-400" />
                      <div>
                        <div className="text-xs text-slate-400">Name</div>
                        <div className="text-white">{normalized.agent_name}</div>
                      </div>
                    </div>
                  )}
                  {normalized.agent_contact && (
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-slate-400" />
                      <div>
                        <div className="text-xs text-slate-400">Contact</div>
                        <div className="text-white">{normalized.agent_contact}</div>
                      </div>
                    </div>
                  )}
                  {normalized.agent_agency && (
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-slate-400" />
                      <div>
                        <div className="text-xs text-slate-400">Agency</div>
                        <div className="text-white">{normalized.agent_agency}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="space-y-2 pt-3 border-t border-slate-700">
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
                {normalized.quality_score !== undefined && normalized.quality_score !== null && (
                  <div className="flex items-center gap-1">
                    <Award className="w-3 h-3" />
                    Quality: {normalized.quality_score}%
                  </div>
                )}
                {normalized.created_at && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Listed: {new Date(normalized.created_at).toLocaleDateString()}
                  </div>
                )}
                {normalized.scrape_timestamp && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Scraped: {new Date(normalized.scrape_timestamp).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-slate-700 p-4 sm:p-6 space-y-3">
          {normalized.listing_url && (
            <a
              href={normalized.listing_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              View Full Listing on {normalized.site_key || 'Website'}
            </a>
          )}
          <Button
            onClick={onClose}
            variant="outline"
            className="w-full border-slate-600 hover:bg-slate-800 text-white"
          >
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
