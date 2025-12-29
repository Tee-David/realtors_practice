"use client";
import React, { useState, useCallback } from "react";
import { LoginScreen } from "@/components/auth/login-screen";
import { Dashboard } from "@/components/dashboard/dashboard";
import DataExplorer from "@/components/data/data-explorer";
// import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { ScraperControl } from "@/components/scraper/scraper-control";
import { UserManagement } from "@/components/user/user-management";
import StatusPage from "./status/page";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { LoadingTimeout } from "@/components/ui/loading-timeout";
import { ErrorBoundary } from "@/components/error-boundary";
import { toast } from "sonner";
import { useKeepAlive } from "@/lib/hooks/useKeepAlive";
import { KeepAliveIndicator } from "@/components/ui/keep-alive-indicator";

// Static imports for ALL pages to avoid React.lazy() issues on Vercel
import DashboardPage from "./dashboard/page";
import PropertiesPage from "./properties/page";
import DataExplorerPage from "./data-explorer/page";
import SettingsPage from "./settings/page";
import SavedSearchesPage from "./saved-searches/page";
import ApiTestPage from "./api-test/page";
import ScrapeResultsPage from "./scrape-results/page";
import ScraperPage from "./scraper/page";
import RateLimitPage from "./rate-limit/page";
import PriceIntelligencePage from "./price-intelligence/page";
import MarketTrendsPage from "./market-trends/page";
import SearchPage from "./search/page";
import ExportPage from "./export/page";
import FirestorePage from "./firestore/page";
import GithubPage from "./github/page";
import DuplicatesPage from "./duplicates/page";
import QualityPage from "./quality/page";
import SchedulePage from "./schedule/page";
import HealthPage from "./health/page";
import EmailPage from "./email/page";
import AlertsPage from "./alerts/page";
import TopPerformersPage from "./top-performers/page";
import SiteHealthPage from "./site-health/page";

export default function Home() {
  const [activeTab, setActiveTab] = useState("login");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Keep backend alive to prevent Render from sleeping
  useKeepAlive({
    enabled: true, // Enable in both dev and production for testing
    interval: 12 * 60 * 1000, // 12 minutes
  });

  // Check for stored authentication on mount
  React.useEffect(() => {
    const storedAuth = localStorage.getItem("isAuthenticated");
    const storedTab = localStorage.getItem("activeTab");

    if (storedAuth === "true") {
      setIsAuthenticated(true);
      setActiveTab(storedTab || "dashboard");
      console.log("[Home] Restored session - authenticated:", true);
    }
  }, []);

  // Debug: Track activeTab changes
  React.useEffect(() => {
    console.log("[Home] activeTab changed to:", activeTab);
  }, [activeTab]);

  const handleLogin = useCallback(() => {
    setIsAuthenticated(true);
    setActiveTab("dashboard");
    // Persist authentication
    localStorage.setItem("isAuthenticated", "true");
    localStorage.setItem("activeTab", "dashboard");
    toast.success("Login successful! Welcome back.");
  }, []);

  const handleLogout = useCallback(() => {
    setIsAuthenticated(false);
    setActiveTab("login");
    // Clear authentication
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("activeTab");
    toast.info("Logged out successfully");
  }, []);

  const handlePageChange = useCallback((page: string) => {
    console.log("[Home] Page change requested:", page);
    setActiveTab(page);
    // Persist active tab
    if (page !== "login") {
      localStorage.setItem("activeTab", page);
    }
  }, []);

  // Listen for navigation events from dashboard and other components
  React.useEffect(() => {
    const handleNavigateEvent = (event: Event) => {
      const customEvent = event as CustomEvent<{ page: string }>;
      if (customEvent.detail?.page) {
        handlePageChange(customEvent.detail.page);
      }
    };

    window.addEventListener("navigate", handleNavigateEvent);

    return () => {
      window.removeEventListener("navigate", handleNavigateEvent);
    };
  }, [handlePageChange]);

  // Move renderContent before conditional return to maintain hook order
  const renderContent = useCallback(() => {
    console.log("[Home] Rendering content for activeTab:", activeTab);
    switch (activeTab) {
      case "dashboard":
        return <DashboardPage />;
      case "properties":
        return <PropertiesPage />;
      case "data-explorer":
        return <DataExplorerPage />;
      case "settings":
        return <SettingsPage />;
      case "saved-searches":
        return <SavedSearchesPage />;
      case "api-test":
        return <ApiTestPage />;
      case "scrape-results":
        return <ScrapeResultsPage />;
      case "scraper":
        return <ScraperPage />;
      case "status":
        return <StatusPage />;
      case "users":
        return <UserManagement />;
      case "rate-limit":
        return <RateLimitPage />;
      case "price-intelligence":
        return <PriceIntelligencePage />;
      case "market-trends":
        return <MarketTrendsPage />;
      case "search":
        return <SearchPage />;
      case "export":
        return <ExportPage />;
      case "firestore":
        return <FirestorePage />;
      case "github":
        return <GithubPage />;
      case "duplicates":
        return <DuplicatesPage />;
      case "quality":
        return <QualityPage />;
      case "schedule":
        return <SchedulePage />;
      case "health":
        return <HealthPage />;
      case "email":
        return <EmailPage />;
      case "alerts":
        return <AlertsPage />;
      case "top-performers":
        return <TopPerformersPage />;
      case "site-health":
        return <SiteHealthPage />;
      default:
        return <Dashboard />;
    }
  }, [activeTab]);

  // Conditional return after all hooks
  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col md:flex-row w-full">
      {/* Keep-alive indicator */}
      <KeepAliveIndicator show={true} position="bottom-right" />

      <div className="w-full md:w-64 flex-shrink-0">
        <Sidebar
          currentPage={activeTab}
          onPageChange={handlePageChange}
          onLogout={handleLogout}
        />
      </div>

      <div className="flex-1 flex flex-col min-h-screen w-full">
        <main
          className="flex-1 overflow-auto bg-slate-900 p-2 sm:p-4 pt-16 md:pt-2"
          key={activeTab}
        >
          <ErrorBoundary>{renderContent()}</ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
