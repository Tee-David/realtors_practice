"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api";
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
}

export function ExportButton({ filters, totalCount = 0 }: ExportButtonProps) {
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format: "csv" | "xlsx" | "json") => {
    setExporting(true);
    try {
      toast.info(`Preparing ${format.toUpperCase()} export...`);

      // Generate export (backend handles limits)
      const job = await apiClient.generateExport({
        format,
        filters,
      });

      // If job has download_url, use it
      if (job.download_url) {
        window.open(job.download_url, "_blank");
        toast.success(`Exported to ${format.toUpperCase()}`);
      } else if (job.job_id) {
        // Wait for file generation, then download
        setTimeout(async () => {
          try {
            const response = await apiClient.downloadExport(job.job_id);
            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `properties_export.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            toast.success(`Downloaded ${format.toUpperCase()}`);
          } catch {
            toast.error("Failed to download");
          }
        }, 2000);
      }
    } catch (error) {
      console.error("Export error:", error);
      toast.error("Export requires backend setup");
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
          disabled={exporting || totalCount === 0}
          className="bg-slate-700 border-slate-600 text-white"
        >
          <Download className="w-4 h-4 sm:mr-2" />
          <span className="hidden sm:inline">
            {exporting ? "Exporting..." : "Export"}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="bg-slate-800 border-slate-700"
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
