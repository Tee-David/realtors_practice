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

export const PropertyDetailsModal: React.FC<PropertyDetailsModalProps> = ({
  open,
  onClose,
  property,
}) => {
  if (!property) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg w-full bg-slate-900 border-slate-700 text-white p-0">
        <DialogHeader className="flex items-center justify-between p-4 border-b border-slate-700">
          <DialogTitle className="text-xl font-bold">
            {property.title || "Untitled Property"}
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
        <div className="p-4 space-y-3">
          {property.price && (
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-xl font-bold text-green-400">
                ₦{property.price.toLocaleString()}
              </span>
            </div>
          )}
          <div className="flex items-center gap-2 text-slate-400">
            <MapPin className="w-4 h-4" />
            <span className="text-sm truncate">{property.location}</span>
          </div>
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
          {property.property_type && (
            <Badge
              variant="outline"
              className="bg-slate-700/50 text-slate-300 border-slate-600"
            >
              {property.property_type}
            </Badge>
          )}
          {property.amenities && property.amenities.length > 0 && (
            <div className="mt-2">
              <span className="font-semibold text-slate-300">Amenities:</span>
              <span className="ml-2 text-slate-400 text-sm">
                {property.amenities.join(", ")}
              </span>
            </div>
          )}
          {property.created_at && (
            <div className="text-xs text-slate-500 mt-2">
              Listed: {new Date(property.created_at).toLocaleDateString()}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
