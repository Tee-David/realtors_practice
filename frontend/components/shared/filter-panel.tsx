"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X } from "lucide-react";

interface FilterPanelProps {
  filters: {
    location?: string;
    minPrice?: number;
    maxPrice?: number;
    bedrooms?: number;
    bathrooms?: number;
    propertyType?: string;
    listingType?: "For Sale" | "For Rent" | "Short Let";
    siteKey?: string;
    amenities?: string[];
  };
  onFilterChange: (filters: any) => void;
  onClear: () => void;
}

export function FilterPanel({
  filters,
  onFilterChange,
  onClear,
}: FilterPanelProps) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <CardTitle className="text-white">Filters</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            className="text-white"
            aria-label="Clear all filters"
          >
            <X className="w-4 h-4 mr-1" />
            Clear
          </Button>
        </div>
        {/* Onboarding/Help Section */}
        <div className="text-xs text-slate-400 mt-1 mb-2 leading-relaxed">
          <span className="font-semibold text-slate-300">How to use:</span>{" "}
          Select filters below to narrow your property search by location,
          price, type, and more.
          <br />
          <span className="text-slate-300">Tip:</span> You can combine multiple
          filters for more precise results. Click <b>Clear</b> to reset all
          filters.
          <br />
          Not seeing results? Try fewer filters, or run a new scrape from the{" "}
          <b>Scraper Control</b> page.
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Location */}
        <div className="space-y-2">
          <Label htmlFor="location" className="text-slate-300">
            Location
          </Label>
          <Input
            id="location"
            placeholder="e.g. Lekki, Victoria Island"
            value={filters.location || ""}
            onChange={(e) =>
              onFilterChange({ ...filters, location: e.target.value })
            }
            className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-400"
          />
        </div>

        {/* Price Range */}
        <div className="space-y-2">
          <Label className="text-slate-300">Price Range</Label>
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="number"
              placeholder="Min"
              value={filters.minPrice || ""}
              onChange={(e) =>
                onFilterChange({
                  ...filters,
                  minPrice: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-400"
            />
            <Input
              type="number"
              placeholder="Max"
              value={filters.maxPrice || ""}
              onChange={(e) =>
                onFilterChange({
                  ...filters,
                  maxPrice: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Bedrooms */}
        <div className="space-y-2">
          <Label htmlFor="bedrooms" className="text-slate-300">
            Bedrooms
          </Label>
          <Select
            value={filters.bedrooms?.toString() || "any"}
            onValueChange={(value) =>
              onFilterChange({
                ...filters,
                bedrooms: value === "any" ? undefined : Number(value),
              })
            }
          >
            <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Any</SelectItem>
              <SelectItem value="1">1+</SelectItem>
              <SelectItem value="2">2+</SelectItem>
              <SelectItem value="3">3+</SelectItem>
              <SelectItem value="4">4+</SelectItem>
              <SelectItem value="5">5+</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Bathrooms */}
        <div className="space-y-2">
          <Label htmlFor="bathrooms" className="text-slate-300">
            Bathrooms
          </Label>
          <Select
            value={filters.bathrooms?.toString() || "any"}
            onValueChange={(value) =>
              onFilterChange({
                ...filters,
                bathrooms: value === "any" ? undefined : Number(value),
              })
            }
          >
            <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Any</SelectItem>
              <SelectItem value="1">1+</SelectItem>
              <SelectItem value="2">2+</SelectItem>
              <SelectItem value="3">3+</SelectItem>
              <SelectItem value="4">4+</SelectItem>
              <SelectItem value="5">5+</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Property Type */}
        <div className="space-y-2">
          <Label htmlFor="propertyType" className="text-slate-300">
            Property Type
          </Label>
          <Select
            value={filters.propertyType || "all"}
            onValueChange={(value) =>
              onFilterChange({
                ...filters,
                propertyType: value === "all" ? undefined : value,
              })
            }
          >
            <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="house">House</SelectItem>
              <SelectItem value="apartment">Apartment</SelectItem>
              <SelectItem value="land">Land</SelectItem>
              <SelectItem value="commercial">Commercial</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Listing Type */}
        <div className="space-y-2">
          <Label htmlFor="listingType" className="text-slate-300">
            Listing Type
          </Label>
          <Select
            value={filters.listingType || "all"}
            onValueChange={(value) =>
              onFilterChange({
                ...filters,
                listingType: value === "all" ? undefined : value,
              })
            }
          >
            <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
              <SelectValue placeholder="All" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="For Sale">For Sale</SelectItem>
              <SelectItem value="For Rent">For Rent</SelectItem>
              <SelectItem value="Short Let">Short Let</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Site Key */}
        <div className="space-y-2">
          <Label htmlFor="siteKey" className="text-slate-300">
            Site
          </Label>
          <Input
            id="siteKey"
            placeholder="e.g. npc, jiji, propertypro, etc.."
            value={filters.siteKey || ""}
            onChange={(e) =>
              onFilterChange({ ...filters, siteKey: e.target.value })
            }
            className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-400"
          />
        </div>

        {/* Amenities (comma separated) */}
        <div className="space-y-2">
          <Label htmlFor="amenities" className="text-slate-300">
            Amenities
          </Label>
          <Input
            id="amenities"
            placeholder="e.g. pool, gym, parking"
            value={filters.amenities?.join(", ") || ""}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                amenities: e.target.value
                  ? e.target.value.split(",").map((a) => a.trim())
                  : [],
              })
            }
            className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-400"
          />
        </div>

        {/* Show Results Button for Mobile */}
        <div className="block lg:hidden pt-2">
          <Button
            variant="default"
            size="lg"
            className="w-full text-white"
            onClick={() => onFilterChange(filters)}
            aria-label="Show Results"
          >
            Show Results
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
