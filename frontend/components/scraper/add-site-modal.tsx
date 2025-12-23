"use client";

import type React from "react";
import { useState } from "react";
import { X, Globe, Link as LinkIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";

interface AddSiteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSiteAdded?: () => void; // Callback to refresh sites list
}

export function AddSiteModal({
  isOpen,
  onClose,
  onSiteAdded,
}: AddSiteModalProps) {
  const [siteName, setSiteName] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [siteKey, setSiteKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!siteName || !baseUrl) {
      toast.error("Please fill in all required fields");
      return;
    }

    // Generate site_key from siteName if not provided
    const generatedSiteKey =
      siteKey ||
      siteName
        .toLowerCase()
        .replace(/\s+/g, "_")
        .replace(/[^a-z0-9_]/g, "");

    setIsLoading(true);

    try {
      const siteData = {
        site_key: generatedSiteKey,
        name: siteName,
        base_url: baseUrl,
        enabled: false, // New sites start disabled by default
      };

      const response = await apiClient.createSite(siteData);

      toast.success("Site added successfully!", {
        description: `Site key: ${response.site_key}`,
        duration: 5000,
      });

      // Reset form
      setSiteName("");
      setBaseUrl("");
      setSiteKey("");

      // Call callback to refresh sites list
      if (onSiteAdded) {
        onSiteAdded();
      }

      onClose();
    } catch (error) {
      console.error("Failed to add site:", error);
      toast.error(
        error instanceof Error
          ? error.message
          : "Failed to add site. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

      <div className="relative bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md">
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Add New Site</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1"
            disabled={isLoading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4">
          {/* Info Box */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
            <p className="text-sm text-blue-300">
              Add a new site to the scraper configuration. The site will be
              disabled by default.
            </p>
          </div>

          {/* Site Name */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Site Name <span className="text-red-400">*</span>
            </label>
            <Input
              type="text"
              value={siteName}
              onChange={(e) => setSiteName(e.target.value)}
              placeholder="e.g., Property Finder Nigeria"
              className="bg-slate-700 border-slate-600 text-white"
              disabled={isLoading}
              required
            />
          </div>

          {/* Base URL */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              <LinkIcon className="w-4 h-4 inline mr-1" />
              Base URL <span className="text-red-400">*</span>
            </label>
            <Input
              type="url"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="https://example.com"
              className="bg-slate-700 border-slate-600 text-white"
              disabled={isLoading}
              required
            />
            <p className="text-xs text-slate-400 mt-1">
              The main URL of the website to scrape
            </p>
          </div>

          {/* Site Key (Optional) */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Site Key (Optional)
            </label>
            <Input
              type="text"
              value={siteKey}
              onChange={(e) => setSiteKey(e.target.value)}
              placeholder="Auto-generated from name"
              className="bg-slate-700 border-slate-600 text-white"
              disabled={isLoading}
            />
            <p className="text-xs text-slate-400 mt-1">
              Unique identifier (auto-generated if not provided)
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col-reverse sm:flex-row gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent"
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="animate-spin mr-2 w-4 h-4 border-b-2 border-white rounded-full inline-block"></span>
                  Adding...
                </>
              ) : (
                "Add Site"
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
