"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { FilterState } from "@/lib/types";

interface FilterSidebarProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onClose?: () => void;
}

export default function FilterSidebar({
  filters,
  onFiltersChange,
  onClose,
}: FilterSidebarProps) {
  const [expandedSections, setExpandedSections] = useState({
    search: true,
    location: true,
    price: true,
    rooms: true,
    type: true,
    promo: true,
    dates: false,
    source: false,
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const updateFilter = <K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const handleBedroomChange = (bedroom: number, checked: boolean) => {
    const newBedrooms = checked
      ? [...filters.bedrooms, bedroom]
      : filters.bedrooms.filter((b) => b !== bedroom);
    updateFilter("bedrooms", newBedrooms);
  };

  const handleBathroomChange = (bathroom: number, checked: boolean) => {
    const newBathrooms = checked
      ? [...filters.bathrooms, bathroom]
      : filters.bathrooms.filter((b) => b !== bathroom);
    updateFilter("bathrooms", newBathrooms);
  };

  const handlePromoTagChange = (tag: string, checked: boolean) => {
    const newTags = checked
      ? [...filters.promoTags, tag]
      : filters.promoTags.filter((t) => t !== tag);
    updateFilter("promoTags", newTags);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      keyword: "",
      location: "",
      priceRange: [0, 1000000],
      bedrooms: [],
      bathrooms: [],
      propertyType: "",
      promoTags: [],
      startDate: "",
      endDate: "",
      sourceSite: "",
    });
    if (onClose) onClose();
  };

  const FilterSection = ({
    title,
    section,
    children,
  }: {
    title: string;
    section: keyof typeof expandedSections;
    children: React.ReactNode;
  }) => (
    <div className="border-b border-slate-700 pb-4 last:border-b-0">
      <button
        onClick={() => toggleSection(section)}
        className="flex items-center justify-between w-full text-left text-white font-medium mb-3 hover:text-blue-400 transition-colors py-2"
      >
        <span className="text-sm lg:text-base">{title}</span>
        {expandedSections[section] ? (
          <ChevronUp className="w-4 h-4 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-4 h-4 flex-shrink-0" />
        )}
      </button>
      {expandedSections[section] && <div className="space-y-3">{children}</div>}
    </div>
  );

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-4 lg:p-6 max-h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-4 lg:mb-6">
        <h3 className="text-lg font-semibold text-white">Search & Filters</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={clearAllFilters}
          className="text-slate-400 hover:text-white text-xs"
        >
          Clear All
        </Button>
      </div>

      <div className="space-y-4 lg:space-y-6">
        <FilterSection title="Keyword Search" section="search">
          <Input
            type="text"
            placeholder="Search keywords..."
            value={filters.keyword}
            onChange={(e) => updateFilter("keyword", e.target.value)}
            className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-500 text-sm"
          />
        </FilterSection>

        <FilterSection title="Location" section="location">
          <Select
            value={filters.location}
            onValueChange={(value) =>
              updateFilter("location", value === "all" ? "" : value)
            }
          >
            <SelectTrigger className="bg-slate-700 border-slate-600 text-white text-sm">
              <SelectValue placeholder="All Locations" />
            </SelectTrigger>
            <SelectContent className="bg-slate-700 border-slate-600">
              <SelectItem value="all">All Locations</SelectItem>
              <SelectItem value="city center">City Center</SelectItem>
              <SelectItem value="greenfield">Greenfield Estates</SelectItem>
              <SelectItem value="coastal">Coastal Heights</SelectItem>
              <SelectItem value="old town">Old Town</SelectItem>
              <SelectItem value="hip district">Hip District</SelectItem>
            </SelectContent>
          </Select>
        </FilterSection>

        <FilterSection title="Price Range" section="price">
          <div className="space-y-4">
            <Slider
              value={filters.priceRange as [number, number]}
              onValueChange={(value: [number, number]) =>
                updateFilter("priceRange", value)
              }
              max={1000000}
              min={0}
              step={10000}
              className="w-full"
            />
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>${filters.priceRange[0].toLocaleString()}</span>
              <span>${filters.priceRange[1].toLocaleString()}</span>
            </div>
            <div className="text-center text-white text-sm font-medium">
              ${filters.priceRange[0].toLocaleString()} - $
              {filters.priceRange[1].toLocaleString()}
            </div>
          </div>
        </FilterSection>

        <FilterSection title="Bedrooms & Bathrooms" section="rooms">
          <div className="space-y-4">
            <div>
              <p className="text-slate-300 text-sm mb-3">Bedrooms</p>
              <div className="grid grid-cols-3 lg:grid-cols-5 gap-2">
                {[1, 2, 3, 4, 5].map((bedroom) => (
                  <label
                    key={bedroom}
                    className="flex items-center space-x-2 text-sm"
                  >
                    <Checkbox
                      checked={filters.bedrooms.includes(bedroom)}
                      onCheckedChange={(checked) =>
                        handleBedroomChange(bedroom, checked as boolean)
                      }
                    />
                    <span className="text-slate-300">{bedroom}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <p className="text-slate-300 text-sm mb-3">Bathrooms</p>
              <div className="grid grid-cols-3 lg:grid-cols-4 gap-2">
                {[1, 2, 3, 4].map((bathroom) => (
                  <label
                    key={bathroom}
                    className="flex items-center space-x-2 text-sm"
                  >
                    <Checkbox
                      checked={filters.bathrooms.includes(bathroom)}
                      onCheckedChange={(checked) =>
                        handleBathroomChange(bathroom, checked as boolean)
                      }
                    />
                    <span className="text-slate-300">{bathroom}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </FilterSection>

        <FilterSection title="Property Type" section="type">
          <Select
            value={filters.propertyType}
            onValueChange={(value) =>
              updateFilter("propertyType", value === "all" ? "" : value)
            }
          >
            <SelectTrigger className="bg-slate-700 border-slate-600 text-white text-sm">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent className="bg-slate-700 border-slate-600">
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="apartment">Apartment</SelectItem>
              <SelectItem value="house">House</SelectItem>
              <SelectItem value="condo">Condo</SelectItem>
              <SelectItem value="townhouse">Townhouse</SelectItem>
              <SelectItem value="studio">Studio</SelectItem>
            </SelectContent>
          </Select>
        </FilterSection>

        <FilterSection title="Promo Tags" section="promo">
          <div className="space-y-3">
            {["Featured", "New Listing", "Open House"].map((tag) => (
              <label key={tag} className="flex items-center space-x-2 text-sm">
                <Checkbox
                  checked={filters.promoTags.includes(tag)}
                  onCheckedChange={(checked) =>
                    handlePromoTagChange(tag, checked as boolean)
                  }
                />
                <span className="text-slate-300">{tag}</span>
              </label>
            ))}
          </div>
        </FilterSection>

        <FilterSection title="Date Range" section="dates">
          <div className="space-y-3">
            <Input
              type="date"
              placeholder="Start Date"
              value={filters.startDate}
              onChange={(e) => updateFilter("startDate", e.target.value)}
              className="bg-slate-700 border-slate-600 text-white text-sm"
            />
            <Input
              type="date"
              placeholder="End Date"
              value={filters.endDate}
              onChange={(e) => updateFilter("endDate", e.target.value)}
              className="bg-slate-700 border-slate-600 text-white text-sm"
            />
          </div>
        </FilterSection>

        <FilterSection title="Source Site" section="source">
          <Select
            value={filters.sourceSite}
            onValueChange={(value) =>
              updateFilter("sourceSite", value === "all" ? "" : value)
            }
          >
            <SelectTrigger className="bg-slate-700 border-slate-600 text-white text-sm">
              <SelectValue placeholder="All Sources" />
            </SelectTrigger>
            <SelectContent className="bg-slate-700 border-slate-600">
              <SelectItem value="all">All Sources</SelectItem>
              <SelectItem value="realestate.com">RealEstate.com</SelectItem>
              <SelectItem value="zillow.com">Zillow.com</SelectItem>
              <SelectItem value="realtor.com">Realtor.com</SelectItem>
            </SelectContent>
          </Select>
        </FilterSection>
      </div>

      {onClose && (
        <div className="mt-6 pt-4 border-t border-slate-700 lg:hidden">
          <Button
            onClick={onClose}
            className="w-full bg-blue-500 hover:bg-blue-600"
          >
            Apply Filters
          </Button>
        </div>
      )}
    </div>
  );
}
