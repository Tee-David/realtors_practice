"use client";

import { useState, useCallback, useMemo } from "react";
import { DashboardOverview } from "./dashboard-overview";
import { ScraperControl } from "@/components/scraper/scraper-control";
import { UserManagement } from "@/components/user/user-management";
import { ErrorBoundary } from "@/components/common/error-boundary";
import { Loader2 } from "lucide-react";
import { Suspense } from "react";
import DataExplorer from "../data/data-explorer";

// Page configuration with metadata
const PAGE_CONFIG = {
  dashboard: {
    title: "Dashboard",
    description: "Overview of system metrics and activities",
    component: DashboardOverview,
  },
  scraper: {
    title: "Scraper Control & Configurations",
    description: "Manage and configure data scraping operations",
    component: ScraperControl,
  },
  data: {
    title: "Data Explorer",
    description: "Browse, search, and export scraped data",
    component: DataExplorer,
  },
  users: {
    title: "User Management",
    description: "Manage user accounts and permissions",
    component: UserManagement,
  },
} as const;

type PageKey = keyof typeof PAGE_CONFIG;

// Loading component for page transitions
const PageLoader = ({ pageName }: { pageName: string }) => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="flex flex-col items-center gap-4">
      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      <p className="text-slate-400">Loading {pageName}...</p>
    </div>
  </div>
);

// Error fallback component
const PageError = ({ error, retry }: { error: Error; retry: () => void }) => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="text-center p-6 bg-red-500/10 border border-red-500/20 rounded-lg">
      <h3 className="text-red-400 font-semibold mb-2">Something went wrong</h3>
      <p className="text-slate-400 mb-4">{error.message}</p>
      <button
        onClick={retry}
        className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
      >
        Try Again
      </button>
    </div>
  </div>
);

export function Dashboard() {
  const [currentPage, setCurrentPage] = useState<PageKey>("dashboard");
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Memoized page configuration
  const currentPageConfig = useMemo(
    () => PAGE_CONFIG[currentPage],
    [currentPage]
  );

  // Handle page changes with loading state
  const handlePageChange = useCallback(
    async (page: string) => {
      if (page === currentPage || !(page in PAGE_CONFIG)) return;

      setIsTransitioning(true);

      // Small delay for smooth transition
      setTimeout(() => {
        setCurrentPage(page as PageKey);
        setIsTransitioning(false);
      }, 150);
    },
    [currentPage]
  );

  // Memoized page renderer with error boundary
  const renderCurrentPage = useMemo(() => {
    if (isTransitioning) {
      return <PageLoader pageName={currentPageConfig.title} />;
    }

    const PageComponent = currentPageConfig.component;

    return (
      <ErrorBoundary
        fallback={(error, retry) => <PageError error={error} retry={retry} />}
      >
        <Suspense fallback={<PageLoader pageName={currentPageConfig.title} />}>
          <div className="animate-fadeIn">
            <PageComponent />
          </div>
        </Suspense>
      </ErrorBoundary>
    );
  }, [currentPageConfig, isTransitioning]);

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Main content with proper scrolling */}
      <main className="flex-1 overflow-auto">
        <div className="p-6">{renderCurrentPage}</div>
      </main>

      {/* Optional: Page-specific actions bar */}
      <div className="border-t border-slate-700 bg-slate-800/50 px-6 py-3">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Page: {currentPageConfig.title}</span>
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
}
