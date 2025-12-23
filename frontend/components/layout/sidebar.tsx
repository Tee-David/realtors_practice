"use client";

import { useState, useCallback } from "react";
import {
  LayoutDashboard,
  Settings,
  Home,
  Database,
  Menu,
  X,
  ChevronRight,
  LogOut,
  Activity,
  Bookmark,
  Play,
  FileCheck,
  Wrench,
} from "lucide-react";
import { cn } from "../../lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  onLogout?: () => void;
}

// Navigation configuration with descriptions and badges (ordered by importance)
const navigation = [
  // Primary user features
  {
    name: "Dashboard",
    icon: LayoutDashboard,
    id: "dashboard",
    description: "System overview & stats",
    badge: null,
  },
  {
    name: "Data Explorer",
    icon: Database,
    id: "data-explorer",
    description: "Explore & export property data",
    badge: null,
  },
  // Admin features
  {
    name: "Scraper Control",
    icon: Play,
    id: "scraper",
    description: "Manage scraping ops",
    badge: "ADMIN",
  },
  {
    name: "Properties",
    icon: Home,
    id: "properties",
    description: "Browse & search listings",
    badge: null,
  },
  {
    name: "Scrape Results",
    icon: FileCheck,
    id: "scrape-results",
    description: "Verify scrape success",
    badge: "INFO",
  },
  {
    name: "Saved Searches",
    icon: Bookmark,
    id: "saved-searches",
    description: "Your alerts & preferences",
    badge: null,
  },

  // Admin features
  {
    name: "Settings",
    icon: Settings,
    id: "settings",
    description: "System configuration",
    badge: "ADMIN",
  },
  // Developer & diagnostic tools
  {
    name: "API Test",
    icon: Wrench,
    id: "api-test",
    description: "Test API connection",
    badge: "DEV",
  },
];

// Footer navigation
const footerNavigation = [
  // { name: "Help & Support", icon: HelpCircle, action: "help" },
  { name: "Sign Out", icon: LogOut, action: "logout" },
];

export function Sidebar({ currentPage, onPageChange, onLogout }: SidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  // Keeping for future desktop collapse feature
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_isCollapsed, _setIsCollapsed] = useState(false);

  // Handle mobile menu toggle
  const toggleMobile = useCallback(() => {
    setIsMobileOpen((prev) => !prev);
  }, []);

  // Handle page navigation
  const handleNavigation = useCallback(
    (pageId: string) => {
      onPageChange(pageId);
      setIsMobileOpen(false); // Close mobile menu after navigation
    },
    [onPageChange]
  );

  // Handle footer actions
  const handleFooterAction = useCallback(
    (action: string) => {
      switch (action) {
        case "help":
          toast.info("Help documentation will open soon");
          break;
        case "logout":
          if (onLogout) {
            onLogout();
          } else {
            toast.info("Logging out...");
          }
          break;
      }
    },
    [onLogout]
  );

  // Sidebar content component
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const SidebarContent = ({ isMobile = false }: { isMobile?: boolean }) => (
    <div className="flex flex-col h-full overflow-y-auto scrollbar-thin scrollbar-thumb-blue-500 scrollbar-track-slate-900">
      {/* Logo and brand */}
      <div className="flex items-center space-x-3 p-6 border-b border-slate-700">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
          <Database className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-lg font-bold text-white truncate">
            Realtor Scraper
          </h1>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <p className="text-xs text-slate-400">System Online</p>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-3">
          Navigation
        </div>
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => handleNavigation(item.id)}
              className={cn(
                "group w-full flex items-center justify-between px-3 py-3 rounded-xl text-left transition-all duration-200",
                "focus:outline-none focus:ring-2 focus:ring-blue-500/50",
                isActive
                  ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg"
                  : "text-slate-300 hover:bg-slate-800/50 hover:text-white"
              )}
            >
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                <Icon
                  className={cn(
                    "w-5 h-5 flex-shrink-0",
                    isActive ? "text-white" : "text-slate-400"
                  )}
                />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{item.name}</div>
                  <div className="text-xs opacity-75 truncate">
                    {item.description}
                  </div>
                </div>
              </div>

              {/* Badge or arrow */}
              <div className="flex items-center space-x-2">
                {item.badge && (
                  <span
                    className={cn(
                      "text-xs px-2 py-0.5 rounded-full font-medium",
                      isActive
                        ? "bg-white/20 text-white"
                        : "bg-slate-700 text-slate-300"
                    )}
                  >
                    {item.badge}
                  </span>
                )}
                {isActive && <ChevronRight className="w-4 h-4 text-white/70" />}
              </div>
            </button>
          );
        })}
      </nav>

      {/* Footer Navigation */}
      <div className="p-4 border-t border-slate-700 space-y-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-3">
          Account
        </div>
        {footerNavigation.map((item) => {
          const Icon = item.icon;
          const isLogout = item.action === "logout";

          return (
            <button
              key={item.action}
              onClick={() => handleFooterAction(item.action)}
              className={cn(
                "w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-all duration-200",
                "focus:outline-none focus:ring-2 focus:ring-blue-500/50",
                isLogout
                  ? "text-red-400 hover:bg-red-500/10 hover:text-red-300"
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-white"
              )}
            >
              <Icon className="w-4 h-4" />
              <span className="font-medium">{item.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile menu button */}
      <Button
        onClick={toggleMobile}
        variant="ghost"
        size="sm"
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-slate-800/90 backdrop-blur-sm border border-slate-700 text-white hover:bg-slate-700"
      >
        <Menu className="w-5 h-5" />
      </Button>

      {/* Mobile sidebar overlay */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-40 flex">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            onClick={toggleMobile}
          />

          {/* Mobile sidebar */}
          <div className="relative flex flex-col w-full max-w-[90vw] bg-slate-900 border-r border-slate-700 shadow-2xl overflow-y-auto">
            <Button
              onClick={toggleMobile}
              variant="ghost"
              size="sm"
              className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white z-10"
            >
              <X className="w-5 h-5" />
            </Button>
            <SidebarContent isMobile={true} />
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-slate-900 border-r border-slate-700 shadow-xl overflow-y-auto max-h-screen">
        <SidebarContent />
      </div>
    </>
  );
}
