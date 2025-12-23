// "use client";

// import { useState, useEffect, useCallback } from "react";
// import {
//   Download,
//   FileText,
//   Table,
//   Search,
//   Filter,
//   X,
//   RefreshCw,
// } from "lucide-react";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import { Property, FilterState, QueryResult } from "@/lib/types";
// import { toast } from "sonner";
// import { apiClient } from "@/lib/api";
// // import { useSWRProperties } from "@/lib/hooks/useSWRProperties";
// import { exportToCSV, exportToXLSX, exportToPDF } from "@/lib/export-utils";
// import DataTable from "./data-table";
// import FilterSidebar from "./filter-sidebar";

// export default function DataExplorer() {
//   console.log("[DataExplorer] Component mounted/updated");

//   const [searchTerm, setSearchTerm] = useState("");
//   const [showMobileFilters, setShowMobileFilters] = useState(false);
//   const [currentSite] = useState<string>("");
//   const [dataSource, setDataSource] = useState<
//     "firestore" | "firestore-archive" | "site" | "search"
//   >("firestore");

//   const [properties, setProperties] = useState<Property[]>([]);
//   const [totalRecords, setTotalRecords] = useState(0);
//   const [loading, setLoading] = useState(false);

//   const [filters, setFilters] = useState<FilterState>({
//     keyword: "",
//     location: "",
//     priceRange: [0, 1000000],
//     bedrooms: [],
//     bathrooms: [],
//     propertyType: "",
//     promoTags: [],
//     startDate: "",
//     endDate: "",
//     sourceSite: "",
//   });

//   // Get available data files - keeping for future use
//   // Use stable function reference to avoid re-mounting issues
//   // Removed getDataFiles, not implemented in API client
//   // eslint-disable-next-line @typescript-eslint/no-unused-vars
//   // Removed getDataFiles and related useApi usage

//   console.log("[DataExplorer] State:", {
//     dataSource,
//     currentSite,
//     searchTerm,
//     propertiesCount: properties.length,
//     totalRecords,
//     loading,
//   });

//   // Load data based on current source with debouncing
//   // SWR-based data loading for master data
//   const loadData = useCallback(async () => {
//     setLoading(true);
//     try {
//       if (dataSource === "firestore" || dataSource === "firestore-archive") {
//         // Query Firestore for properties (current or archive)
//         const query: any = {
//           filters: {},
//           limit: 100,
//         };
//         // Optionally add filters from UI
//         if (filters.location) query.filters.location = filters.location;
//         if (filters.priceRange) {
//           query.filters.price_min = filters.priceRange[0];
//           query.filters.price_max = filters.priceRange[1];
//         }
//         if (filters.bedrooms.length > 0)
//           query.filters.bedrooms_min = Math.min(...filters.bedrooms);
//         if (filters.bathrooms.length > 0)
//           query.filters.bathrooms_min = Math.min(...filters.bathrooms);
//         if (filters.propertyType)
//           query.filters.property_type = filters.propertyType;
//         // Add more filters as needed
//         let firestoreResponse;
//         if (dataSource === "firestore-archive") {
//           firestoreResponse = await apiClient.queryFirestoreArchive(query);
//         } else {
//           firestoreResponse = await apiClient.queryFirestore(query);
//         }
//         let results: Property[] = [];
//         if (Array.isArray(firestoreResponse)) {
//           results = firestoreResponse;
//         } else if (
//           firestoreResponse &&
//           Array.isArray((firestoreResponse as any).results)
//         ) {
//           results = (firestoreResponse as any).results;
//         }
//         setProperties(results);
//         setTotalRecords(results.length);
//       } else if (dataSource === "search" && searchTerm) {
//         const searchResults = await apiClient.searchData({
//           query: searchTerm,
//           limit: 100,
//         });
//         const typedSearchResults = searchResults as QueryResult;
//         setProperties(typedSearchResults.properties || []);
//         setTotalRecords(typedSearchResults.total || 0);
//       } else if (dataSource === "site" && currentSite) {
//         const siteData = await apiClient.getSiteData(currentSite, {
//           limit: 100,
//         });
//         const typedSiteData = siteData as {
//           data?: Property[];
//           total_records?: number;
//           message?: string;
//         };
//         setProperties(typedSiteData.data || []);
//         setTotalRecords(typedSiteData.total_records || 0);
//         if (typedSiteData.message && typedSiteData.data?.length === 0) {
//           toast.info(typedSiteData.message);
//         }
//       }
//     } catch (error) {
//       toast.error("Failed to load data");
//       setProperties([]);
//       setTotalRecords(0);
//     } finally {
//       setLoading(false);
//     }
//   }, [dataSource, currentSite, searchTerm, filters]);

//   // Debounced effect to prevent excessive API calls
//   useEffect(() => {
//     const timeoutId = setTimeout(() => {
//       loadData();
//     }, 500); // 500ms debounce

//     return () => clearTimeout(timeoutId);
//   }, [loadData]);

//   const filteredProperties = properties.filter((property) => {
//     const matchesSearch =
//       property.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
//       property.location.toLowerCase().includes(searchTerm.toLowerCase());

//     const matchesKeyword =
//       !filters.keyword ||
//       property.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
//       property.location.toLowerCase().includes(filters.keyword.toLowerCase());

//     const matchesLocation =
//       !filters.location ||
//       property.location.toLowerCase().includes(filters.location.toLowerCase());

//     const price =
//       typeof property.price === "number"
//         ? property.price
//         : typeof property.price === "string"
//         ? parseFloat(property.price.replace(/[^\d.]/g, "")) || 0
//         : 0;

//     const matchesPrice =
//       price >= filters.priceRange[0] && price <= filters.priceRange[1];

//     const bedrooms =
//       typeof property.bedrooms === "number"
//         ? property.bedrooms
//         : typeof property.bedrooms === "string"
//         ? parseInt(property.bedrooms) || 0
//         : 0;

//     const matchesBedrooms =
//       filters.bedrooms.length === 0 || filters.bedrooms.includes(bedrooms);

//     const bathrooms =
//       typeof property.bathrooms === "number"
//         ? property.bathrooms
//         : typeof property.bathrooms === "string"
//         ? parseInt(property.bathrooms) || 0
//         : 0;

//     const matchesBathrooms =
//       filters.bathrooms.length === 0 || filters.bathrooms.includes(bathrooms);

//     const matchesType =
//       !filters.propertyType ||
//       (property.type &&
//         property.type.toLowerCase() === filters.propertyType.toLowerCase());

//     const matchesPromoTags =
//       filters.promoTags.length === 0 ||
//       filters.promoTags.some((tag) => {
//         switch (tag) {
//           case "Featured":
//             return property.featured;
//           case "New Listing":
//             return property.newListing;
//           case "Open House":
//             return property.openHouse;
//           default:
//             return false;
//         }
//       });

//     return (
//       matchesSearch &&
//       matchesKeyword &&
//       matchesLocation &&
//       matchesPrice &&
//       matchesBedrooms &&
//       matchesBathrooms &&
//       matchesType &&
//       matchesPromoTags
//     );
//   });

//   const handleExport = async (format: "csv" | "xlsx" | "pdf") => {
//     try {
//       switch (format) {
//         case "csv":
//           exportToCSV(filteredProperties, "property-data");
//           break;
//         case "xlsx":
//           exportToXLSX(filteredProperties, "property-data");
//           break;
//         case "pdf":
//           exportToPDF(filteredProperties, "property-data");
//           break;
//       }
//       toast.success(`Data exported to ${format.toUpperCase()} successfully`);
//     } catch {
//       toast.error(`Failed to export to ${format.toUpperCase()}`);
//     }
//   };

//   // Empty state if no data
//   const isEmpty = !properties || properties.length === 0;

//   return (
//     <div className="relative">
//       {/* Mobile Filter Overlay */}
//       {showMobileFilters && (
//         <div className="fixed inset-0 z-50 lg:hidden">
//           <div
//             className="fixed inset-0 bg-black/50"
//             onClick={() => setShowMobileFilters(false)}
//           />
//           <div className="fixed inset-y-0 left-0 w-full max-w-sm bg-slate-900 p-4 overflow-y-auto">
//             <div className="flex items-center justify-between mb-4">
//               <h3 className="text-lg font-semibold text-white">Filters</h3>
//               <Button
//                 variant="ghost"
//                 size="icon"
//                 onClick={() => setShowMobileFilters(false)}
//                 className="text-slate-400 hover:text-white"
//               >
//                 <X className="h-5 w-5" />
//               </Button>
//             </div>
//             <FilterSidebar
//               filters={filters}
//               onFiltersChange={setFilters}
//               onClose={() => setShowMobileFilters(false)}
//             />
//           </div>
//         </div>
//       )}

//       {/* Header */}
//       <div className="space-y-4 mb-6">
//         <div className="flex flex-col space-y-2">
//           <h2 className="text-2xl font-bold text-white">Data Explorer</h2>
//           <p className="text-slate-400">
//             Browse, filter, and export your property data. Use the filters to
//             narrow results, or export to CSV/XLSX/PDF for further analysis.
//           </p>
//         </div>

//         {/* Data Source Selector (hidden by default, show with toggle) */}
//         <details className="mb-2">
//           <summary className="cursor-pointer text-slate-400 text-sm mb-2">
//             Advanced: Change Data Source
//           </summary>
//           <div className="flex flex-wrap gap-2 mt-2">
//             <Button
//               onClick={() => setDataSource("firestore")}
//               variant={dataSource === "firestore" ? "default" : "outline"}
//               size="sm"
//               className="text-xs"
//             >
//               Firestore Data
//             </Button>
//             <Button
//               onClick={() => setDataSource("firestore-archive")}
//               variant={
//                 dataSource === "firestore-archive" ? "default" : "outline"
//               }
//               size="sm"
//               className="text-xs"
//             >
//               Archived Data
//             </Button>
//             <Button
//               onClick={() => setDataSource("site")}
//               variant={dataSource === "site" ? "default" : "outline"}
//               size="sm"
//               className="text-xs"
//             >
//               Site Data
//             </Button>
//             <Button
//               onClick={() => setDataSource("search")}
//               variant={dataSource === "search" ? "default" : "outline"}
//               size="sm"
//               className="text-xs"
//             >
//               Search
//             </Button>
//             <Button
//               onClick={loadData}
//               variant="outline"
//               size="sm"
//               className="text-xs"
//               disabled={loading}
//             >
//               <RefreshCw
//                 className={`w-3 h-3 mr-1 ${loading ? "animate-spin" : ""}`}
//               />
//               Refresh
//             </Button>
//           </div>
//           <p className="text-xs text-slate-500 mt-2">
//             Most users should use <b>Firestore Data</b>. "Archived Data" shows
//             historical/archived listings. Site and Search are for advanced use.
//           </p>
//         </details>

//         {/* Mobile Export Buttons */}
//         <div className="flex flex-wrap gap-2 lg:hidden">
//           <Button
//             onClick={() => handleExport("csv")}
//             size="sm"
//             className="bg-blue-500 hover:bg-blue-600 flex items-center space-x-1 text-xs"
//           >
//             <Download className="w-3 h-3" />
//             <span>CSV</span>
//           </Button>
//           <Button
//             onClick={() => handleExport("xlsx")}
//             size="sm"
//             className="bg-green-500 hover:bg-green-600 flex items-center space-x-1 text-xs"
//           >
//             <Table className="w-3 h-3" />
//             <span>XLSX</span>
//           </Button>
//           <Button
//             onClick={() => handleExport("pdf")}
//             size="sm"
//             className="bg-red-500 hover:bg-red-600 flex items-center space-x-1 text-xs"
//           >
//             <FileText className="w-3 h-3" />
//             <span>PDF</span>
//           </Button>
//         </div>

//         {/* Desktop Export Buttons */}
//         <div className="hidden lg:flex lg:items-center lg:justify-end lg:space-x-3">
//           <Button
//             onClick={() => handleExport("csv")}
//             className="bg-blue-500 hover:bg-blue-600 flex items-center space-x-2"
//             style={{ display: "flex" }}
//           >
//             <Download className="w-4 h-4" />
//             <span style={{ display: "inline" }}>Export to CSV</span>
//           </Button>
//           <Button
//             onClick={() => handleExport("xlsx")}
//             className="bg-green-500 hover:bg-green-600 flex items-center space-x-2"
//             style={{ display: "flex" }}
//           >
//             <Table className="w-4 h-4" />
//             <span style={{ display: "inline" }}>Export to XLSX</span>
//           </Button>
//           <Button
//             onClick={() => handleExport("pdf")}
//             className="bg-red-500 hover:bg-red-600 flex items-center space-x-2"
//             style={{ display: "flex" }}
//           >
//             <FileText className="w-4 h-4" />
//             <span style={{ display: "inline" }}>Export to PDF</span>
//           </Button>
//         </div>
//       </div>

//       <div className="flex flex-col lg:flex-row gap-6">
//         {/* Desktop Filters Sidebar */}
//         <div className="hidden lg:block lg:w-80 lg:flex-shrink-0">
//           <FilterSidebar filters={filters} onFiltersChange={setFilters} />
//         </div>

//         {/* Main Content */}
//         <div className="flex-1 min-w-0 space-y-4">
//           {/* Search and Mobile Filter Button */}
//           <div className="flex gap-3">
//             <div className="relative flex-1">
//               <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
//               <Input
//                 type="text"
//                 placeholder="Search properties..."
//                 value={searchTerm}
//                 onChange={(e) => setSearchTerm(e.target.value)}
//                 className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
//               />
//             </div>

//             {/* Mobile Filter Button */}
//             <Button
//               variant="outline"
//               onClick={() => setShowMobileFilters(true)}
//               className="lg:hidden border-slate-600 text-slate-300 hover:bg-slate-700 px-3"
//             >
//               <Filter className="w-4 h-4" />
//             </Button>
//           </div>

//           {/* Empty State */}
//           {isEmpty ? (
//             <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 text-center text-slate-400 mt-8">
//               <p className="text-lg font-medium mb-2">
//                 No property data found.
//               </p>
//               <p className="mb-4">
//                 Run a new scrape in{" "}
//                 <a href="/scraper" className="underline text-blue-300">
//                   Scraper Control
//                 </a>{" "}
//                 to collect property data.
//               </p>
//               <a
//                 href="/scraper"
//                 className="inline-block mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
//               >
//                 Go to Scraper Control
//               </a>
//             </div>
//           ) : (
//             <>
//               {/* Active Filters Display & Archive Mode Indicator */}
//               {(filters.location ||
//                 filters.propertyType ||
//                 filters.bedrooms.length > 0 ||
//                 filters.bathrooms.length > 0 ||
//                 filters.promoTags.length > 0 ||
//                 dataSource === "firestore-archive") && (
//                 <div className="flex flex-wrap gap-2 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
//                   <span className="text-slate-400 text-sm">
//                     Active filters:
//                   </span>

//                   {dataSource === "firestore-archive" && (
//                     <span className="bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-xs font-semibold">
//                       Viewing Archived Data
//                     </span>
//                   )}

//                   {filters.location && (
//                     <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-xs">
//                       Location: {filters.location}
//                     </span>
//                   )}

//                   {filters.propertyType && (
//                     <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs">
//                       Type: {filters.propertyType}
//                     </span>
//                   )}

//                   {filters.bedrooms.length > 0 && (
//                     <span className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs">
//                       Beds: {filters.bedrooms.join(", ")}
//                     </span>
//                   )}

//                   {filters.bathrooms.length > 0 && (
//                     <span className="bg-orange-500/20 text-orange-400 px-2 py-1 rounded text-xs">
//                       Baths: {filters.bathrooms.join(", ")}
//                     </span>
//                   )}

//                   {filters.promoTags.length > 0 && (
//                     <span className="bg-pink-500/20 text-pink-400 px-2 py-1 rounded text-xs">
//                       Tags: {filters.promoTags.join(", ")}
//                     </span>
//                   )}

//                   <button
//                     onClick={() =>
//                       setFilters({
//                         keyword: "",
//                         location: "",
//                         priceRange: [0, 1000000],
//                         bedrooms: [],
//                         bathrooms: [],
//                         propertyType: "",
//                         promoTags: [],
//                         startDate: "",
//                         endDate: "",
//                         sourceSite: "",
//                       })
//                     }
//                     className="text-slate-400 hover:text-white text-xs underline"
//                   >
//                     Clear all
//                   </button>
//                 </div>
//               )}

//               {/* Results Count */}
//               <div className="text-sm text-slate-400">
//                 Showing {filteredProperties.length} of {properties.length}{" "}
//                 properties
//               </div>

//               {/* Data Table */}
//               <DataTable properties={filteredProperties} />
//             </>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Download,
  FileText,
  Table,
  Search,
  Filter,
  X,
  RefreshCw,
  Database,
  Archive,
  Globe,
  ChevronDown,
  AlertCircle,
  Settings2,
  FileSpreadsheet,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Property, FilterState, QueryResult } from "@/lib/types";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import { exportToCSV, exportToXLSX, exportToPDF } from "@/lib/export-utils";
import DataTable from "./data-table";
import FilterSidebar from "./filter-sidebar";

type DataSource = "firestore" | "firestore-archive" | "site" | "search";

export default function DataExplorer() {
  const [searchTerm, setSearchTerm] = useState("");
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [showDataSourceMenu, setShowDataSourceMenu] = useState(false);
  const [currentSite] = useState<string>("");
  const [dataSource, setDataSource] = useState<DataSource>("firestore");

  const [properties, setProperties] = useState<Property[]>([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [loading, setLoading] = useState(false);

  const [filters, setFilters] = useState<FilterState>({
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

  // Load data based on current source with debouncing
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (dataSource === "firestore" || dataSource === "firestore-archive") {
        const query: any = {
          filters: {},
          limit: 100,
        };

        if (filters.location) query.filters.location = filters.location;
        if (filters.priceRange) {
          query.filters.price_min = filters.priceRange[0];
          query.filters.price_max = filters.priceRange[1];
        }
        if (filters.bedrooms.length > 0)
          query.filters.bedrooms_min = Math.min(...filters.bedrooms);
        if (filters.bathrooms.length > 0)
          query.filters.bathrooms_min = Math.min(...filters.bathrooms);
        if (filters.propertyType)
          query.filters.property_type = filters.propertyType;

        let firestoreResponse;
        if (dataSource === "firestore-archive") {
          firestoreResponse = await apiClient.queryFirestoreArchive(query);
        } else {
          firestoreResponse = await apiClient.queryFirestore(query);
        }

        let results: Property[] = [];
        if (Array.isArray(firestoreResponse)) {
          results = firestoreResponse;
        } else if (
          firestoreResponse &&
          Array.isArray((firestoreResponse as any).results)
        ) {
          results = (firestoreResponse as any).results;
        }
        setProperties(results);
        setTotalRecords(results.length);
      } else if (dataSource === "search" && searchTerm) {
        const searchResults = await apiClient.searchData({
          query: searchTerm,
          limit: 100,
        });
        const typedSearchResults = searchResults as QueryResult;
        setProperties(typedSearchResults.properties || []);
        setTotalRecords(typedSearchResults.total || 0);
      } else if (dataSource === "site" && currentSite) {
        const siteData = await apiClient.getSiteData(currentSite, {
          limit: 100,
        });
        const typedSiteData = siteData as {
          data?: Property[];
          total_records?: number;
          message?: string;
        };
        setProperties(typedSiteData.data || []);
        setTotalRecords(typedSiteData.total_records || 0);
        if (typedSiteData.message && typedSiteData.data?.length === 0) {
          toast.info(typedSiteData.message);
        }
      }
    } catch (error) {
      toast.error("Failed to load data");
      setProperties([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  }, [dataSource, currentSite, searchTerm, filters]);

  // Debounced effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      loadData();
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [loadData]);

  const filteredProperties = properties.filter((property) => {
    const matchesSearch =
      property.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      property.location.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesKeyword =
      !filters.keyword ||
      property.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
      property.location.toLowerCase().includes(filters.keyword.toLowerCase());

    const matchesLocation =
      !filters.location ||
      property.location.toLowerCase().includes(filters.location.toLowerCase());

    const price =
      typeof property.price === "number"
        ? property.price
        : typeof property.price === "string"
        ? parseFloat(property.price.replace(/[^\d.]/g, "")) || 0
        : 0;

    const matchesPrice =
      price >= filters.priceRange[0] && price <= filters.priceRange[1];

    const bedrooms =
      typeof property.bedrooms === "number"
        ? property.bedrooms
        : typeof property.bedrooms === "string"
        ? parseInt(property.bedrooms) || 0
        : 0;

    const matchesBedrooms =
      filters.bedrooms.length === 0 || filters.bedrooms.includes(bedrooms);

    const bathrooms =
      typeof property.bathrooms === "number"
        ? property.bathrooms
        : typeof property.bathrooms === "string"
        ? parseInt(property.bathrooms) || 0
        : 0;

    const matchesBathrooms =
      filters.bathrooms.length === 0 || filters.bathrooms.includes(bathrooms);

    const matchesType =
      !filters.propertyType ||
      (property.type &&
        property.type.toLowerCase() === filters.propertyType.toLowerCase());

    const matchesPromoTags =
      filters.promoTags.length === 0 ||
      filters.promoTags.some((tag) => {
        switch (tag) {
          case "Featured":
            return property.featured;
          case "New Listing":
            return property.newListing;
          case "Open House":
            return property.openHouse;
          default:
            return false;
        }
      });

    return (
      matchesSearch &&
      matchesKeyword &&
      matchesLocation &&
      matchesPrice &&
      matchesBedrooms &&
      matchesBathrooms &&
      matchesType &&
      matchesPromoTags
    );
  });

  const handleExport = async (format: "csv" | "xlsx" | "pdf") => {
    try {
      switch (format) {
        case "csv":
          exportToCSV(filteredProperties, "property-data");
          break;
        case "xlsx":
          exportToXLSX(filteredProperties, "property-data");
          break;
        case "pdf":
          exportToPDF(filteredProperties, "property-data");
          break;
      }
      toast.success(`Data exported to ${format.toUpperCase()} successfully`);
    } catch {
      toast.error(`Failed to export to ${format.toUpperCase()}`);
    }
  };

  const handleDataSourceChange = (source: DataSource) => {
    setDataSource(source);
    setShowDataSourceMenu(false);
    toast.success(`Switched to ${getDataSourceLabel(source)}`);
  };

  const getDataSourceLabel = (source: DataSource) => {
    switch (source) {
      case "firestore":
        return "Live Data";
      case "firestore-archive":
        return "Archived Data";
      case "site":
        return "Site Data";
      case "search":
        return "Search Mode";
      default:
        return "Unknown";
    }
  };

  const getDataSourceIcon = (source: DataSource) => {
    switch (source) {
      case "firestore":
        return <Database className="w-4 h-4" />;
      case "firestore-archive":
        return <Archive className="w-4 h-4" />;
      case "site":
        return <Globe className="w-4 h-4" />;
      case "search":
        return <Search className="w-4 h-4" />;
      default:
        return <Database className="w-4 h-4" />;
    }
  };

  const activeFilterCount = [
    filters.location,
    filters.propertyType,
    filters.bedrooms.length > 0,
    filters.bathrooms.length > 0,
    filters.promoTags.length > 0,
  ].filter(Boolean).length;

  const clearAllFilters = () => {
    setFilters({
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
    toast.success("Filters cleared");
  };

  const isEmpty = !properties || properties.length === 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 sm:p-6 lg:p-8">
      <div className="max-w-[1600px] mx-auto space-y-6">
        {/* Mobile Filter Overlay */}
        {showMobileFilters && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <div
              className="fixed inset-0 bg-black/80 backdrop-blur-sm"
              onClick={() => setShowMobileFilters(false)}
            />
            <div className="fixed inset-y-0 left-0 w-full max-w-sm bg-slate-900 border-r border-slate-800 shadow-xl overflow-y-auto">
              <div className="sticky top-0 z-10 bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Filter className="w-5 h-5" />
                  Filters
                  {activeFilterCount > 0 && (
                    <span className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {activeFilterCount}
                    </span>
                  )}
                </h3>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowMobileFilters(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
              <div className="p-4">
                <FilterSidebar
                  filters={filters}
                  onFiltersChange={setFilters}
                  onClose={() => setShowMobileFilters(false)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
                Data Explorer
              </h1>
              <p className="text-slate-400 text-sm sm:text-base max-w-2xl">
                Browse, filter, and analyze your property data. Export results
                for further analysis.
              </p>
            </div>

            {/* Quick Stats */}
            <div className="flex flex-wrap gap-3">
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2">
                <div className="text-xs text-slate-400">Total Records</div>
                <div className="text-xl font-bold text-white">
                  {totalRecords}
                </div>
              </div>
              <div className="bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2">
                <div className="text-xs text-slate-400">Filtered</div>
                <div className="text-xl font-bold text-white">
                  {filteredProperties.length}
                </div>
              </div>
            </div>
          </div>

          {/* Action Bar */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search & Filter Controls */}
              <div className="flex-1 flex gap-3">
                {/* Search Input */}
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <Input
                    type="text"
                    placeholder="Search properties by title or location..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500 h-10"
                  />
                </div>

                {/* Mobile Filter Button */}
                <Button
                  onClick={() => setShowMobileFilters(true)}
                  className="lg:hidden bg-slate-700 hover:bg-slate-600 border border-slate-600 relative"
                >
                  <Filter className="w-4 h-4 mr-2" />
                  Filters
                  {activeFilterCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-blue-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                      {activeFilterCount}
                    </span>
                  )}
                </Button>

                {/* Data Source Selector */}
                <div className="relative">
                  <Button
                    onClick={() => setShowDataSourceMenu(!showDataSourceMenu)}
                    className="bg-slate-700 hover:bg-slate-600 border border-slate-600 h-10"
                  >
                    {getDataSourceIcon(dataSource)}
                    <span className="hidden sm:inline ml-2">
                      {getDataSourceLabel(dataSource)}
                    </span>
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>

                  {showDataSourceMenu && (
                    <>
                      <div
                        className="fixed inset-0 z-10"
                        onClick={() => setShowDataSourceMenu(false)}
                      />
                      <div className="absolute right-0 mt-2 w-56 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-20 overflow-hidden">
                        <div className="p-2 space-y-1">
                          <button
                            onClick={() => handleDataSourceChange("firestore")}
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                              dataSource === "firestore"
                                ? "bg-blue-500/20 text-blue-400"
                                : "text-slate-300 hover:bg-slate-700"
                            }`}
                          >
                            <Database className="w-4 h-4" />
                            <div className="text-left flex-1">
                              <div className="text-sm font-medium">
                                Live Data
                              </div>
                              <div className="text-xs text-slate-400">
                                Current properties
                              </div>
                            </div>
                          </button>

                          <button
                            onClick={() =>
                              handleDataSourceChange("firestore-archive")
                            }
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                              dataSource === "firestore-archive"
                                ? "bg-blue-500/20 text-blue-400"
                                : "text-slate-300 hover:bg-slate-700"
                            }`}
                          >
                            <Archive className="w-4 h-4" />
                            <div className="text-left flex-1">
                              <div className="text-sm font-medium">
                                Archived Data
                              </div>
                              <div className="text-xs text-slate-400">
                                Historical listings
                              </div>
                            </div>
                          </button>

                          <button
                            onClick={() => handleDataSourceChange("site")}
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                              dataSource === "site"
                                ? "bg-blue-500/20 text-blue-400"
                                : "text-slate-300 hover:bg-slate-700"
                            }`}
                          >
                            <Globe className="w-4 h-4" />
                            <div className="text-left flex-1">
                              <div className="text-sm font-medium">
                                Site Data
                              </div>
                              <div className="text-xs text-slate-400">
                                Source-specific
                              </div>
                            </div>
                          </button>

                          <button
                            onClick={() => handleDataSourceChange("search")}
                            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                              dataSource === "search"
                                ? "bg-blue-500/20 text-blue-400"
                                : "text-slate-300 hover:bg-slate-700"
                            }`}
                          >
                            <Search className="w-4 h-4" />
                            <div className="text-left flex-1">
                              <div className="text-sm font-medium">
                                Search Mode
                              </div>
                              <div className="text-xs text-slate-400">
                                Advanced query
                              </div>
                            </div>
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {/* Refresh Button */}
                <Button
                  onClick={loadData}
                  disabled={loading}
                  className="bg-slate-700 hover:bg-slate-600 border border-slate-600 h-10"
                >
                  <RefreshCw
                    className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
                  />
                </Button>
              </div>

              {/* Export Buttons */}
              <div className="flex flex-wrap gap-2">
                <Button
                  onClick={() => handleExport("csv")}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-500 text-white"
                  disabled={filteredProperties.length === 0}
                >
                  <Download className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">CSV</span>
                </Button>
                <Button
                  onClick={() => handleExport("xlsx")}
                  size="sm"
                  className="bg-green-600 hover:bg-green-500 text-white"
                  disabled={filteredProperties.length === 0}
                >
                  <FileSpreadsheet className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">XLSX</span>
                </Button>
                <Button
                  onClick={() => handleExport("pdf")}
                  size="sm"
                  className="bg-red-600 hover:bg-red-500 text-white"
                  disabled={filteredProperties.length === 0}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">PDF</span>
                </Button>
              </div>
            </div>
          </div>

          {/* Active Filters Display */}
          {activeFilterCount > 0 && (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <div className="flex flex-wrap items-center gap-2">
                <Settings2 className="w-4 h-4 text-blue-400" />
                <span className="text-blue-400 text-sm font-medium">
                  Active Filters:
                </span>

                {filters.location && (
                  <span className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-xs border border-blue-500/30">
                    📍 {filters.location}
                  </span>
                )}

                {filters.propertyType && (
                  <span className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-xs border border-green-500/30">
                    🏠 {filters.propertyType}
                  </span>
                )}

                {filters.bedrooms.length > 0 && (
                  <span className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-xs border border-purple-500/30">
                    🛏️ {filters.bedrooms.join(", ")} bed
                  </span>
                )}

                {filters.bathrooms.length > 0 && (
                  <span className="bg-orange-500/20 text-orange-300 px-3 py-1 rounded-full text-xs border border-orange-500/30">
                    🚿 {filters.bathrooms.join(", ")} bath
                  </span>
                )}

                {filters.promoTags.length > 0 && (
                  <span className="bg-pink-500/20 text-pink-300 px-3 py-1 rounded-full text-xs border border-pink-500/30">
                    ⭐ {filters.promoTags.join(", ")}
                  </span>
                )}

                <button
                  onClick={clearAllFilters}
                  className="ml-auto text-blue-400 hover:text-blue-300 text-sm font-medium flex items-center gap-1"
                >
                  <X className="w-4 h-4" />
                  Clear All
                </button>
              </div>
            </div>
          )}

          {/* Data Source Indicator */}
          {dataSource === "firestore-archive" && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <Archive className="w-5 h-5 text-yellow-400" />
                <div>
                  <p className="text-yellow-400 font-medium">
                    Viewing Archived Data
                  </p>
                  <p className="text-yellow-400/70 text-sm">
                    You're currently viewing historical/archived property
                    listings.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Desktop Filters Sidebar */}
          <div className="hidden lg:block lg:w-80 lg:flex-shrink-0">
            <div className="sticky top-6">
              <FilterSidebar filters={filters} onFiltersChange={setFilters} />
            </div>
          </div>

          {/* Data Display Area */}
          <div className="flex-1 min-w-0">
            {loading ? (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-12 text-center">
                <RefreshCw className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
                <p className="text-slate-400">Loading properties...</p>
              </div>
            ) : isEmpty ? (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-12 text-center">
                <AlertCircle className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  No Property Data Found
                </h3>
                <p className="text-slate-400 mb-6 max-w-md mx-auto">
                  Run a new scrape in Scraper Control to collect property data,
                  or adjust your filters.
                </p>
                <Button
                  onClick={() => (window.location.href = "/scraper")}
                  className="bg-blue-600 hover:bg-blue-500"
                >
                  Go to Scraper Control
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Results Summary */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="w-5 h-5 text-green-400" />
                      <div>
                        <p className="text-white font-medium">
                          {filteredProperties.length}{" "}
                          {filteredProperties.length === 1
                            ? "Property"
                            : "Properties"}{" "}
                          Found
                        </p>
                        <p className="text-slate-400 text-sm">
                          {filteredProperties.length !== properties.length && (
                            <span>
                              Filtered from {properties.length} total records
                            </span>
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Data Table */}
                <DataTable properties={filteredProperties} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
