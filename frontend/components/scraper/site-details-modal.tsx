"use client";

import { useEffect, useMemo, useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { useApi, useApiMutation } from "@/lib/hooks/useApi";
import { apiClient } from "@/lib/api";
import { Site } from "@/lib/types";
import { toast } from "sonner";

interface SiteDetailsModalProps {
  siteKey: string | null;
  isOpen: boolean;
  onClose: () => void;
  onSaved?: () => void;
}

export function SiteDetailsModal({
  siteKey,
  isOpen,
  onClose,
  onSaved,
}: SiteDetailsModalProps) {
  const { data, refetch, loading, error } = useApi<Site | { site: Site }>(
    () => apiClient.getSite(siteKey || ""),
    { immediate: false }
  );
  const updateMutation = useApiMutation((updates: Partial<Site>) =>
    apiClient.updateSite(siteKey || "", updates)
  );

  const site: Site | undefined = useMemo(() => {
    if (!data) return undefined;
    return (data as { site?: Site })?.site || (data as Site);
  }, [data]);

  const [form, setForm] = useState<Partial<Site>>({});

  useEffect(() => {
    if (isOpen && siteKey) {
      refetch();
    }
  }, [isOpen, siteKey, refetch]);

  useEffect(() => {
    if (site) {
      setForm({
        name: site.name,
        url: site.url,
        parser: site.parser,
        enabled: site.enabled,
        notes: site.notes || "",
      });
    }
  }, [site]);

  if (!isOpen) return null;

  const handleChange = <K extends keyof Site>(field: K, value: Site[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    if (!siteKey) return;
    try {
      await updateMutation.mutate(form);
      toast.success("Site updated successfully");
      onSaved?.();
      onClose();
    } catch {
      toast.error("Failed to update site");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-2xl bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-700 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white">Edit Site</h3>
            <p className="text-slate-400 text-sm">{siteKey}</p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={onClose}
              variant="ghost"
              className="text-slate-300 hover:text-white"
            >
              Close
            </Button>
            <Button
              onClick={handleSave}
              disabled={updateMutation.loading}
              className="bg-blue-500 hover:bg-blue-600 disabled:opacity-70"
            >
              {updateMutation.loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                </span>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </div>
        <div className="p-4 sm:p-6 space-y-4">
          {loading && (
            <div className="text-slate-400">Loading site details...</div>
          )}
          {error && (
            <div className="text-red-400">
              Error loading site details: {String(error)}
            </div>
          )}
          {site && (
            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                handleSave();
              }}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-1">
                    Name
                  </label>
                  <Input
                    value={form.name || ""}
                    onChange={(e) => handleChange("name", e.target.value)}
                    placeholder="Site name"
                  />
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-1">
                    Parser
                  </label>
                  <Input
                    value={form.parser || ""}
                    onChange={(e) => handleChange("parser", e.target.value)}
                    placeholder="Parser identifier"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">URL</label>
                <Input
                  value={form.url || ""}
                  onChange={(e) => handleChange("url", e.target.value)}
                  placeholder="https://example.com"
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={!!form.enabled}
                  onCheckedChange={(checked) =>
                    handleChange("enabled", Boolean(checked))
                  }
                />
                <span className="text-slate-300 text-sm">Enabled</span>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">
                  Notes
                </label>
                <textarea
                  className="w-full rounded-md border border-slate-600 bg-slate-900 text-slate-200 p-3 text-sm"
                  rows={4}
                  value={form.notes || ""}
                  onChange={(e) => handleChange("notes", e.target.value)}
                  placeholder="Internal notes..."
                />
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
