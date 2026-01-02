"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  MapPin,
  Bed,
  Bath,
  Home,
  TrendingUp,
  Calendar,
  ExternalLink,
  Share2,
  Heart,
  Ruler,
  CheckCircle,
  Phone,
  Mail,
  Building,
  Shield,
  Zap,
  Wifi,
  Car,
  Wind,
  Droplet,
  Grid,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import Image from "next/image";
import { toast } from "sonner";

interface PropertyDetailModalProps {
  property: any;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PropertyDetailModal({ property, open, onOpenChange }: PropertyDetailModalProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);

  // Extract all data from property schema
  const basicInfo = property.basic_info || {};
  const propertyDetails = property.property_details || {};
  const financial = property.financial || {};
  const location = property.location || {};
  const amenities = property.amenities || {};
  const media = property.media || {};
  const agentInfo = property.agent_info || {};
  const metadata = property.metadata || {};
  const tags = property.tags || {};

  // Image gallery handling
  const images = media.images || [];
  const videos = media.videos || [];
  const currentImage = images[currentImageIndex]?.url || property.image_url;

  const nextImage = () => {
    if (images.length > 0) {
      setCurrentImageIndex((prev) => (prev + 1) % images.length);
    }
  };

  const prevImage = () => {
    if (images.length > 0) {
      setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
    }
  };

  // Format price
  const formatPrice = (price: number) => {
    if (!price) return "Price on Request";
    if (price >= 1_000_000_000) return `₦${(price / 1_000_000_000).toFixed(2)}B`;
    if (price >= 1_000_000) return `₦${(price / 1_000_000).toFixed(2)}M`;
    if (price >= 1_000) return `₦${(price / 1_000).toFixed(0)}K`;
    return `₦${price.toLocaleString()}`;
  };

  // Format date
  const formatDate = (timestamp: string) => {
    if (!timestamp) return null;
    try {
      return new Date(timestamp).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch {
      return null;
    }
  };

  const handleShare = () => {
    const url = basicInfo.listing_url || window.location.href;
    navigator.clipboard.writeText(url);
    toast.success("Link copied to clipboard!");
  };

  const handleFavorite = () => {
    setIsFavorite(!isFavorite);
    toast.success(isFavorite ? "Removed from favorites" : "Added to favorites");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] p-0 bg-slate-900 border-slate-700 overflow-auto">
        <div className="max-h-[90vh]">
          {/* Image Gallery */}
          <div className="relative h-[400px] bg-slate-800">
            {currentImage ? (
              <>
                <Image
                  src={currentImage}
                  alt={basicInfo.title || "Property"}
                  fill
                  className="object-cover"
                  unoptimized
                />
                {images.length > 1 && (
                  <>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                      onClick={prevImage}
                    >
                      <ChevronLeft className="w-6 h-6" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white"
                      onClick={nextImage}
                    >
                      <ChevronRight className="w-6 h-6" />
                    </Button>
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/50 backdrop-blur-sm px-3 py-1 rounded-full text-white text-sm">
                      {currentImageIndex + 1} / {images.length}
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-600">
                <Home className="w-24 h-24" />
              </div>
            )}

            {/* Action Buttons */}
            <div className="absolute top-4 right-4 flex gap-2">
              <Button
                variant="ghost"
                size="icon"
                className="bg-black/50 hover:bg-black/70 text-white"
                onClick={handleShare}
              >
                <Share2 className="w-5 h-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className={`bg-black/50 hover:bg-black/70 ${
                  isFavorite ? "text-red-500" : "text-white"
                }`}
                onClick={handleFavorite}
              >
                <Heart className={`w-5 h-5 ${isFavorite ? "fill-current" : ""}`} />
              </Button>
            </div>

            {/* Badges */}
            <div className="absolute top-4 left-4 flex flex-wrap gap-2">
              {tags.premium && (
                <Badge className="bg-yellow-500 text-black border-none">Premium</Badge>
              )}
              {tags.hot_deal && (
                <Badge className="bg-red-500 text-white border-none">Hot Deal</Badge>
              )}
              {basicInfo.status && (
                <Badge className="bg-blue-500/80 backdrop-blur-sm text-white border-none">
                  {basicInfo.status}
                </Badge>
              )}
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Header Section */}
            <div>
              <DialogHeader>
                <DialogTitle className="text-2xl sm:text-3xl text-white font-bold">
                  {basicInfo.title || "Property Details"}
                </DialogTitle>
              </DialogHeader>

              {/* Location */}
              {(location.area || location.lga || location.state) && (
                <div className="flex items-center gap-2 text-slate-400 mt-2">
                  <MapPin className="w-5 h-5" />
                  <span className="text-lg">
                    {[location.area, location.lga, location.state].filter(Boolean).join(", ")}
                  </span>
                </div>
              )}

              {/* Price */}
              <div className="flex items-center gap-3 mt-4">
                <TrendingUp className="w-6 h-6 text-green-400" />
                <span className="text-3xl font-bold text-green-400">
                  {formatPrice(financial.price)}
                </span>
                {financial.price_per_sqm && (
                  <span className="text-slate-400">
                    (₦{financial.price_per_sqm.toLocaleString()}/sqm)
                  </span>
                )}
              </div>

              {/* Quick Stats */}
              <div className="flex flex-wrap gap-4 mt-4">
                {propertyDetails.bedrooms > 0 && (
                  <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg">
                    <Bed className="w-5 h-5 text-blue-400" />
                    <span className="text-white font-semibold">{propertyDetails.bedrooms}</span>
                    <span className="text-slate-400 text-sm">Bedrooms</span>
                  </div>
                )}
                {propertyDetails.bathrooms > 0 && (
                  <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg">
                    <Bath className="w-5 h-5 text-blue-400" />
                    <span className="text-white font-semibold">{propertyDetails.bathrooms}</span>
                    <span className="text-slate-400 text-sm">Bathrooms</span>
                  </div>
                )}
                {propertyDetails.property_type && (
                  <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg">
                    <Home className="w-5 h-5 text-blue-400" />
                    <span className="text-white font-semibold capitalize">
                      {propertyDetails.property_type}
                    </span>
                  </div>
                )}
                {propertyDetails.size && (
                  <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg">
                    <Ruler className="w-5 h-5 text-blue-400" />
                    <span className="text-white font-semibold">{propertyDetails.size}</span>
                    <span className="text-slate-400 text-sm">sqm</span>
                  </div>
                )}
              </div>
            </div>

            <div className="h-px bg-slate-700 my-4" />

            {/* Property Details Section */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="space-y-6">
                {/* Overview */}
                {(basicInfo.listing_type || propertyDetails.furnishing || basicInfo.status) && (
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                      <Grid className="w-5 h-5 text-blue-400" />
                      Overview
                    </h3>
                    <div className="space-y-2 bg-slate-800/50 p-4 rounded-lg">
                      {basicInfo.listing_type && (
                        <div className="flex justify-between">
                          <span className="text-slate-400">Type</span>
                          <span className="text-white capitalize">{basicInfo.listing_type}</span>
                        </div>
                      )}
                      {propertyDetails.furnishing && (
                        <div className="flex justify-between">
                          <span className="text-slate-400">Furnishing</span>
                          <span className="text-white capitalize">{propertyDetails.furnishing}</span>
                        </div>
                      )}
                      {basicInfo.status && (
                        <div className="flex justify-between">
                          <span className="text-slate-400">Status</span>
                          <span className="text-white capitalize">{basicInfo.status}</span>
                        </div>
                      )}
                      {metadata.quality_score && (
                        <div className="flex justify-between">
                          <span className="text-slate-400">Quality Score</span>
                          <span className="text-white">{metadata.quality_score}%</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Amenities */}
                {(amenities.features?.length > 0 || amenities.security?.length > 0 || amenities.utilities?.length > 0) && (
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                      Amenities & Features
                    </h3>
                    <div className="space-y-3">
                      {amenities.features?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-slate-400 mb-2">Features</h4>
                          <div className="grid grid-cols-1 gap-2">
                            {amenities.features.map((feature: string, idx: number) => (
                              <div key={idx} className="flex items-center gap-2 text-slate-300 text-sm">
                                <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                                <span>{feature}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {amenities.security?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-slate-400 mb-2 flex items-center gap-1">
                            <Shield className="w-4 h-4" />
                            Security
                          </h4>
                          <div className="grid grid-cols-1 gap-2">
                            {amenities.security.map((item: string, idx: number) => (
                              <div key={idx} className="flex items-center gap-2 text-slate-300 text-sm">
                                <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                                <span>{item}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {amenities.utilities?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-slate-400 mb-2 flex items-center gap-1">
                            <Zap className="w-4 h-4" />
                            Utilities
                          </h4>
                          <div className="grid grid-cols-1 gap-2">
                            {amenities.utilities.map((utility: string, idx: number) => (
                              <div key={idx} className="flex items-center gap-2 text-slate-300 text-sm">
                                <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                                <span>{utility}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column */}
              <div className="space-y-6">
                {/* Agent Information */}
                {(agentInfo.name || agentInfo.contact || agentInfo.agency) && (
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                      <Building className="w-5 h-5 text-blue-400" />
                      Agent Information
                    </h3>
                    <div className="bg-slate-800/50 p-4 rounded-lg space-y-3">
                      {agentInfo.agency && (
                        <div>
                          <span className="text-slate-400 text-sm">Agency</span>
                          <p className="text-white font-medium">{agentInfo.agency}</p>
                        </div>
                      )}
                      {agentInfo.name && (
                        <div>
                          <span className="text-slate-400 text-sm">Agent</span>
                          <p className="text-white font-medium">{agentInfo.name}</p>
                        </div>
                      )}
                      {agentInfo.contact && (
                        <div className="flex flex-col gap-2">
                          <Button className="w-full bg-blue-600 hover:bg-blue-700" asChild>
                            <a href={`tel:${agentInfo.contact}`}>
                              <Phone className="w-4 h-4 mr-2" />
                              Call Agent
                            </a>
                          </Button>
                          {agentInfo.email && (
                            <Button variant="outline" className="w-full border-slate-600" asChild>
                              <a href={`mailto:${agentInfo.email}`}>
                                <Mail className="w-4 h-4 mr-2" />
                                Email Agent
                              </a>
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Location Details */}
                {location.coordinates && (
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-red-400" />
                      Location
                    </h3>
                    <div className="bg-slate-800/50 p-4 rounded-lg space-y-2">
                      {location.area && (
                        <div className="flex justify-between">
                          <span className="text-slate-400">Area</span>
                          <span className="text-white">{location.area}</span>
                        </div>
                      )}
                      {location.lga && (
                        <div className="flex justify-between">
                          <span className="text-slate-400">LGA</span>
                          <span className="text-white">{location.lga}</span>
                        </div>
                      )}
                      {location.state && (
                        <div className="flex justify-between">
                          <span className="text-slate-400">State</span>
                          <span className="text-white">{location.state}</span>
                        </div>
                      )}
                      {location.coordinates && (
                        <Button variant="outline" className="w-full mt-2 border-slate-600" asChild>
                          <a
                            href={`https://www.google.com/maps?q=${location.coordinates.latitude},${location.coordinates.longitude}`}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <MapPin className="w-4 h-4 mr-2" />
                            View on Map
                          </a>
                        </Button>
                      )}
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div>
                  <h3 className="text-xl font-semibold text-white mb-3 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-purple-400" />
                    Listing Details
                  </h3>
                  <div className="bg-slate-800/50 p-4 rounded-lg space-y-2">
                    {basicInfo.source && (
                      <div className="flex justify-between">
                        <span className="text-slate-400">Source</span>
                        <Badge className="bg-blue-500 text-white">{basicInfo.source}</Badge>
                      </div>
                    )}
                    {metadata.scrape_timestamp && formatDate(metadata.scrape_timestamp) && (
                      <div className="flex justify-between">
                        <span className="text-slate-400">Listed</span>
                        <span className="text-white text-sm">
                          {formatDate(metadata.scrape_timestamp)}
                        </span>
                      </div>
                    )}
                    {basicInfo.listing_url && (
                      <Button
                        variant="outline"
                        className="w-full mt-2 border-slate-600"
                        asChild
                      >
                        <a
                          href={basicInfo.listing_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="w-4 h-4 mr-2" />
                          View Original Listing
                        </a>
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Video Gallery */}
            {videos.length > 0 && (
              <>
                <div className="h-px bg-slate-700 my-4" />
                <div>
                  <h3 className="text-xl font-semibold text-white mb-3">Video Tour</h3>
                  <div className="grid grid-cols-1 gap-4">
                    {videos.map((videoUrl: string, idx: number) => (
                      <div key={idx} className="aspect-video bg-slate-800 rounded-lg overflow-hidden">
                        <iframe
                          src={videoUrl}
                          className="w-full h-full"
                          allowFullScreen
                          title={`Property video ${idx + 1}`}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
