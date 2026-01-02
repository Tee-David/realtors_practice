"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Download, FileSpreadsheet, FileJson, FileText } from "lucide-react";
import { toast } from "sonner";

interface ExportButtonProps {
  filters?: any;
  totalCount?: number;
  properties?: any[];
}

export function ExportButton({ filters, totalCount = 0, properties = [] }: ExportButtonProps) {
  const [exporting, setExporting] = useState(false);

  const handleExport = (format: "csv" | "xlsx" | "json") => {
    setExporting(true);
    try {
      if (properties.length === 0) {
        toast.error("No properties to export");
        return;
      }

      // Helper function to escape CSV values
      const escapeCsvValue = (value: any): string => {
        if (value === null || value === undefined) return "";
        const str = String(value);
        // If value contains comma, quote, or newline, wrap in quotes and escape internal quotes
        if (str.includes(",") || str.includes('"') || str.includes("\n")) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      };

      // Extract data with fallback for both nested and flat schemas
      const headers = [
        "Title",
        "Price (NGN)",
        "Location",
        "Bedrooms",
        "Bathrooms",
        "Property Type",
        "Size (sqm)",
        "Furnishing",
        "Status",
        "Source",
        "URL"
      ];

      const rows = properties.map((p) => {
        // Support both nested (Firestore enterprise) and flat schemas
        const title = p.basic_info?.title || p.title || "";
        const price = p.financial?.price || p.price || 0;
        const location =
          p.location?.area ||
          p.location?.full_address ||
          p.location?.lga ||
          (typeof p.location === 'string' ? p.location : "") ||
          "";
        const bedrooms = p.property_details?.bedrooms || p.bedrooms || "";
        const bathrooms = p.property_details?.bathrooms || p.bathrooms || "";
        const propertyType = p.property_details?.property_type || p.property_type || "";
        const size = p.property_details?.size || p.size || "";
        const furnishing = p.property_details?.furnishing || p.furnishing || "";
        const status = p.basic_info?.status || p.status || "";
        const source = p.basic_info?.source || p.basic_info?.site_key || p.source || p.site_key || "";
        const url = p.basic_info?.listing_url || p.listing_url || p.url || "";

        return [
          title,
          price,
          location,
          bedrooms,
          bathrooms,
          propertyType,
          size,
          furnishing,
          status,
          source,
          url
        ].map(escapeCsvValue);
      });

      let content: string;
      let mimeType: string;
      let fileExtension: string;

      if (format === "csv") {
        // Create CSV content
        content = [
          headers.join(","),
          ...rows.map(row => row.join(","))
        ].join("\n");
        mimeType = "text/csv;charset=utf-8;";
        fileExtension = "csv";
      } else if (format === "json") {
        // Create JSON content
        const jsonData = properties.map((p) => ({
          title: p.basic_info?.title || p.title || "",
          price: p.financial?.price || p.price || 0,
          location: p.location?.area || p.location?.full_address || p.location?.lga || (typeof p.location === 'string' ? p.location : "") || "",
          bedrooms: p.property_details?.bedrooms || p.bedrooms || "",
          bathrooms: p.property_details?.bathrooms || p.bathrooms || "",
          propertyType: p.property_details?.property_type || p.property_type || "",
          size: p.property_details?.size || p.size || "",
          furnishing: p.property_details?.furnishing || p.furnishing || "",
          status: p.basic_info?.status || p.status || "",
          source: p.basic_info?.source || p.basic_info?.site_key || p.source || p.site_key || "",
          url: p.basic_info?.listing_url || p.listing_url || p.url || ""
        }));
        content = JSON.stringify(jsonData, null, 2);
        mimeType = "application/json;charset=utf-8;";
        fileExtension = "json";
      } else {
        // XLSX - Create HTML table format (Excel can open HTML tables)
        const htmlRows = rows.map(row =>
          `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`
        ).join('\n');
        content = `
          <html>
            <head><meta charset="utf-8"></head>
            <body>
              <table>
                <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
                <tbody>${htmlRows}</tbody>
              </table>
            </body>
          </html>
        `;
        mimeType = "application/vnd.ms-excel;charset=utf-8;";
        fileExtension = "xls";
      }

      // Create and download file
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `properties-export-${new Date().toISOString().split('T')[0]}.${fileExtension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success(`Successfully exported ${properties.length} properties to ${format.toUpperCase()}`);
    } catch (error) {
      console.error("Export error:", error);
      toast.error("Failed to export properties. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          disabled={exporting || properties.length === 0}
          className="bg-green-600 hover:bg-green-700 border-green-500 text-white"
        >
          <Download className="w-4 h-4 sm:mr-2" />
          <span className="hidden sm:inline">
            {exporting ? "Exporting..." : "Export"}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="bg-slate-800 border-slate-700 z-50"
      >
        <DropdownMenuItem
          onClick={() => handleExport("csv")}
          className="text-slate-200 hover:bg-slate-700 cursor-pointer"
        >
          <FileText className="w-4 h-4 mr-2" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => handleExport("xlsx")}
          className="text-slate-200 hover:bg-slate-700 cursor-pointer"
        >
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Export as Excel
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => handleExport("json")}
          className="text-slate-200 hover:bg-slate-700 cursor-pointer"
        >
          <FileJson className="w-4 h-4 mr-2" />
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
