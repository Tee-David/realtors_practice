"use client";

import { ScraperControl } from "@/components/scraper/scraper-control";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

/**
 * Scraper Control Admin Page
 * Consolidates 20 API endpoints for scraper management:
 * - Scraping Control: start, stop, validate, quick scrape
 * - Monitoring: status, progress, logs, health
 * - History: scrape history, metrics, performance
 * - Site Management: list sites, enable/disable, test, configure
 * - GitHub Actions: trigger workflows, check status
 * - Rate Limiting: configure limits, check status
 */

export default function ScraperPage() {
  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white">
          Scraper Control
        </h1>
        <p className="text-sm sm:text-base text-slate-400 mt-1">
          Admin panel for managing web scraping operations and site
          configuration
        </p>
      </div>

      {/* Admin Notice */}
      <Card className="bg-blue-900/20 border-blue-700">
        <CardHeader>
          <CardTitle className="text-blue-400 flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded">
              ADMIN ONLY
            </span>
            Scraper Management
          </CardTitle>
          <CardDescription className="text-blue-300">
            This page contains powerful scraping controls. Use with caution as
            scraping operations can affect all enabled sites and consume
            significant resources.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Main Scraper Control Component */}
      <ScraperControl />
    </div>
  );
}
