"use client";

import React, { useState } from "react";
import { X, Calendar, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";

interface ScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedSites?: string[];
  maxPages?: number;
  geocoding?: boolean;
}

export function ScheduleModal({
  isOpen,
  onClose,
  selectedSites,
  maxPages,
  geocoding,
}: ScheduleModalProps) {
  const [scheduleDate, setScheduleDate] = useState("");
  const [scheduleTime, setScheduleTime] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!scheduleDate || !scheduleTime) {
      toast.error("Please select both date and time");
      return;
    }

    // Combine date and time into ISO format
    const scheduleDateTime = `${scheduleDate}T${scheduleTime}:00`;
    const scheduledTime = new Date(scheduleDateTime);

    // Validate future date
    if (scheduledTime <= new Date()) {
      toast.error("Scheduled time must be in the future");
      return;
    }

    setIsLoading(true);

    try {
      const params: any = {};
      if (selectedSites && selectedSites.length > 0) {
        params.sites = selectedSites;
      }
      if (maxPages !== undefined) {
        params.max_pages = maxPages;
      }
      if (geocoding !== undefined) {
        params.geocode = geocoding;
      }

      await apiClient.scheduleScrape(scheduledTime.toISOString(), params);

      toast.success("Scrape scheduled successfully", {
        description: `Scheduled for ${scheduledTime.toLocaleString()}`,
        duration: 5000,
      });

      setScheduleDate("");
      setScheduleTime("");
      onClose();
    } catch (error) {
      console.error("Failed to schedule scrape:", error);
      toast.error(
        error instanceof Error
          ? error.message
          : "Failed to schedule scrape. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  // Get min date/time (now)
  const now = new Date();
  const minDate = now.toISOString().split("T")[0];
  const minTime =
    scheduleDate === minDate ? now.toTimeString().slice(0, 5) : "00:00";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

      <div className="relative bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md">
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">
              Schedule Scrape Run
            </h3>
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
              Schedule a scraping run to execute at a specific date and time.
              {selectedSites && selectedSites.length > 0 && (
                <span className="block mt-1">
                  <strong>{selectedSites.length} site(s)</strong> selected
                </span>
              )}
            </p>
          </div>

          {/* Date Input */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              Date
            </label>
            <Input
              type="date"
              value={scheduleDate}
              onChange={(e) => setScheduleDate(e.target.value)}
              min={minDate}
              className="bg-slate-700 border-slate-600 text-white"
              disabled={isLoading}
              required
            />
          </div>

          {/* Time Input */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              <Clock className="w-4 h-4 inline mr-1" />
              Time
            </label>
            <Input
              type="time"
              value={scheduleTime}
              onChange={(e) => setScheduleTime(e.target.value)}
              min={minTime}
              className="bg-slate-700 border-slate-600 text-white"
              disabled={isLoading}
              required
            />
          </div>

          {/* Parameters Summary */}
          {(maxPages !== undefined || geocoding !== undefined) && (
            <div className="bg-slate-700/50 rounded-lg p-3 text-sm">
              <p className="font-medium text-slate-300 mb-2">Parameters:</p>
              <ul className="space-y-1 text-slate-400">
                {maxPages !== undefined && <li>• Max Pages: {maxPages}</li>}
                {geocoding !== undefined && (
                  <li>• Geocoding: {geocoding ? "Enabled" : "Disabled"}</li>
                )}
              </ul>
            </div>
          )}

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
                  Scheduling...
                </>
              ) : (
                "Schedule Scrape"
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
