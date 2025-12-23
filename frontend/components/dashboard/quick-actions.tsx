"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, Play, Save, Settings, Database } from "lucide-react";

interface QuickActionsProps {
  isAdmin?: boolean;
  isScraperRunning?: boolean;
  onNavigate?: (page: string) => void;
  onQuickScrape?: () => void;
}

export function QuickActions({
  isAdmin = false,
  isScraperRunning = false,
  onNavigate,
  onQuickScrape,
}: QuickActionsProps) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {/* Search Properties */}
          <Button
            variant="outline"
            className="h-24 flex flex-col items-center justify-center gap-2 bg-slate-900 border-slate-600 hover:bg-slate-700 hover:border-blue-500"
            onClick={() => onNavigate?.("properties")}
          >
            <Search className="w-6 h-6 text-blue-400" />
            <span className="text-sm text-white">Search Properties</span>
          </Button>

          {/* Saved Searches */}
          <Button
            variant="outline"
            className="h-24 flex flex-col items-center justify-center gap-2 bg-slate-900 border-slate-600 hover:bg-slate-700 hover:border-purple-500"
            onClick={() => onNavigate?.("saved-searches")}
          >
            <Save className="w-6 h-6 text-purple-400" />
            <span className="text-sm text-white">Saved Searches</span>
          </Button>

          {/* Admin: Quick Scrape */}
          {isAdmin && (
            <Button
              variant="outline"
              className="h-24 flex flex-col items-center justify-center gap-2 bg-slate-900 border-slate-600 hover:bg-slate-700 hover:border-green-500 disabled:opacity-50"
              onClick={onQuickScrape}
              disabled={isScraperRunning}
            >
              <Play className="w-6 h-6 text-green-400" />
              <span className="text-sm text-white">
                {isScraperRunning ? "Scraping..." : "Quick Scrape"}
              </span>
            </Button>
          )}

          {/* Admin: Scraper Control */}
          {isAdmin && (
            <Button
              variant="outline"
              className="h-24 flex flex-col items-center justify-center gap-2 bg-slate-900 border-slate-600 hover:bg-slate-700 hover:border-orange-500"
              onClick={() => onNavigate?.("scraper")}
            >
              <Settings className="w-6 h-6 text-orange-400" />
              <span className="text-sm text-white">Scraper Control</span>
            </Button>
          )}

          {/* View All Data */}
          <Button
            variant="outline"
            className="h-24 flex flex-col items-center justify-center gap-2 bg-slate-900 border-slate-600 hover:bg-slate-700 hover:border-cyan-500"
            onClick={() => onNavigate?.("data")}
          >
            <Database className="w-6 h-6 text-cyan-400" />
            <span className="text-sm text-white">Browse Data</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
