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
  Bookmark,
  Play,
  FileCheck,
  Wrench,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  onLogout?: () => void;
}

// Navigation configuration
const navigation = [
  {
    name: "Dashboard",
    icon: LayoutDashboard,
    id: "dashboard",
    description: "System overview & stats",
  },
  {
    name: "Properties",
    icon: Home,
    id: "properties",
    description: "Browse and export listings",
  },
  {
    name: "Data Explorer",
    icon: Database,
    id: "data-explorer",
    description: "Advanced search & filtering",
  },
  {
    name: "Scraper Control",
    icon: Play,
    id: "scraper",
    description: "Manage scraping ops",
  },
  {
    name: "Scrape Results",
    icon: FileCheck,
    id: "scrape-results",
    description: "Verify scrape success",
  },
  {
    name: "Saved Searches",
    icon: Bookmark,
    id: "saved-searches",
    description: "Your alerts & preferences",
  },
  {
    name: "Settings",
    icon: Settings,
    id: "settings",
    description: "System configuration",
  },
  {
    name: "API Test",
    icon: Wrench,
    id: "api-test",
    description: "Test API connection",
  },
];

// Footer navigation
const footerNavigation = [
  { name: "Sign Out", icon: LogOut, action: "logout" },
];

export function Sidebar({ currentPage, onPageChange, onLogout }: SidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isDesktopExpanded, setIsDesktopExpanded] = useState(true);

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
  const SidebarContent = ({ isMobile = false }: { isMobile?: boolean }) => (
    <div className="flex flex-col h-full overflow-y-auto scrollbar-thin scrollbar-thumb-blue-500 scrollbar-track-slate-900">
      {/* Logo and brand - Hidden on mobile since it's already in the sticky header */}
      {!isMobile && (
        <div className="flex items-center space-x-3 p-6 border-b border-slate-700">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0">
            <img
              src="/realtor.png"
              alt="Realtors' Practice Logo"
              className="w-10 h-10 object-contain"
            />
          </div>
          {isDesktopExpanded && (
            <div className="flex-1 min-w-0 transition-opacity duration-300">
              <h1 className="text-lg font-bold text-white truncate">
                Realtors' Practice
              </h1>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <p className="text-xs text-slate-400">System Online</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {!isMobile && isDesktopExpanded && (
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-3">
            Navigation
          </div>
        )}
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => handleNavigation(item.id)}
              className={cn(
                "group w-full flex items-center px-3 py-3 rounded-xl text-left transition-all duration-200",
                "focus:outline-none focus:ring-2 focus:ring-blue-500/50",
                isActive
                  ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg"
                  : "text-slate-300 hover:bg-slate-800/50 hover:text-white",
                (isMobile || isDesktopExpanded) ? "justify-between" : "justify-center"
              )}
              title={!isDesktopExpanded && !isMobile ? item.name : undefined}
            >
              <div className={cn(
                "flex items-center space-x-3 flex-1 min-w-0",
                (!isDesktopExpanded && !isMobile) && "justify-center"
              )}>
                <Icon
                  className={cn(
                    "w-5 h-5 flex-shrink-0",
                    isActive ? "text-white" : "text-slate-400"
                  )}
                />
                {(isMobile || isDesktopExpanded) && (
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{item.name}</div>
                    <div className="text-xs opacity-75 truncate">
                      {item.description}
                    </div>
                  </div>
                )}
              </div>

              {/* Badge or arrow */}
              {(isMobile || isDesktopExpanded) && isActive && (
                <ChevronRight className="w-4 h-4 text-white/70 flex-shrink-0" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Navigation */}
      <div className="p-4 border-t border-slate-700 space-y-1">
        {!isMobile && isDesktopExpanded && (
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-3">
            Account
          </div>
        )}
        {footerNavigation.map((item) => {
          const Icon = item.icon;
          const isLogout = item.action === "logout";

          return (
            <button
              key={item.action}
              onClick={() => handleFooterAction(item.action)}
              className={cn(
                "w-full flex items-center px-3 py-2 rounded-lg text-left transition-all duration-200",
                "focus:outline-none focus:ring-2 focus:ring-blue-500/50",
                isLogout
                  ? "text-red-400 hover:bg-red-500/10 hover:text-red-300"
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-white",
                (isMobile || isDesktopExpanded) ? "space-x-3" : "justify-center"
              )}
              title={!isDesktopExpanded && !isMobile ? item.name : undefined}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {(isMobile || isDesktopExpanded) && (
                <span className="font-medium">{item.name}</span>
              )}
            </button>
          );
        })}

        {/* Copyright Footer */}
        {(isMobile || isDesktopExpanded) && (
          <div className="mt-4 pt-4 px-3 text-xs text-slate-500 border-t border-slate-800">
            <p>
              © {new Date().getFullYear()}{" "}
              <a
                href="https://realtorspractice.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 hover:underline transition-colors"
              >
                Realtors' Practice
              </a>
            </p>
            <p className="mt-1">
              Powered by{" "}
              <a
                href="https://wedigcreativity.com.ng"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 hover:underline transition-colors"
              >
                WDC Solutions
              </a>
            </p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile header bar with menu button */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 shadow-lg">
        <div className="flex items-center justify-between px-4 py-3">
          <Button
            onClick={toggleMobile}
            variant="ghost"
            size="sm"
            className="p-2 text-white hover:bg-slate-800"
          >
            <Menu className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-2">
            <img
              src="/realtor.png"
              alt="Logo"
              className="w-6 h-6 object-contain"
            />
            <span className="text-sm font-medium text-white">Realtors' Practice</span>
          </div>
          <div className="w-8" /> {/* Spacer for balance */}
        </div>
      </div>

      {/* Mobile sidebar overlay */}
      {isMobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            onClick={toggleMobile}
          />

          {/* Mobile sidebar */}
          <div className="relative flex flex-col w-full max-w-[90vw] bg-slate-900 border-r border-slate-700 shadow-2xl overflow-y-auto animate-in slide-in-from-left duration-300">
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
      <div
        className={cn(
          "hidden md:flex md:flex-col md:fixed md:inset-y-0 bg-slate-900 border-r border-slate-700 shadow-xl overflow-y-auto transition-all duration-300 ease-in-out",
          isDesktopExpanded ? "md:w-64" : "md:w-20"
        )}
        onMouseEnter={() => setIsDesktopExpanded(true)}
        onMouseLeave={() => setIsDesktopExpanded(false)}
      >
        <SidebarContent />
      </div>
    </>
  );
}
