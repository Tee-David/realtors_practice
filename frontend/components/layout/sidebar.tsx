"use client";

import { useState, useCallback } from "react";
import {
  LayoutDashboard,
  Settings,
  Home,
  Database,
  LogOut,
  Bookmark,
  Play,
  FileCheck,
  Wrench,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import {
  Sidebar as AceternitySidebar,
  SidebarBody,
  SidebarLink,
} from "@/components/ui/sidebar";
import { motion } from "motion/react";

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

export function Sidebar({ currentPage, onPageChange, onLogout }: SidebarProps) {
  const [open, setOpen] = useState(false);

  // Handle page navigation
  const handleNavigation = useCallback(
    (pageId: string) => {
      onPageChange(pageId);
    },
    [onPageChange]
  );

  // Handle logout
  const handleLogout = useCallback(() => {
    if (onLogout) {
      onLogout();
    } else {
      toast.info("Logging out...");
    }
  }, [onLogout]);

  // Create links with custom onClick instead of href
  const links = navigation.map((item) => {
    const Icon = item.icon;
    return {
      label: item.name,
      href: "#", // Placeholder, won't be used
      icon: (
        <Icon
          className={cn(
            "h-5 w-5 flex-shrink-0",
            currentPage === item.id ? "text-blue-400" : "text-slate-400"
          )}
        />
      ),
      onClick: (e: React.MouseEvent) => {
        e.preventDefault();
        handleNavigation(item.id);
      },
      isActive: currentPage === item.id,
    };
  });

  return (
    <div
      className={cn(
        "flex flex-col md:flex-row bg-slate-900 w-full flex-1 border-slate-700"
      )}
    >
      <AceternitySidebar open={open} setOpen={setOpen} animate={true}>
        <SidebarBody className="justify-between gap-10 bg-slate-900 border-r border-slate-700">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            {open ? <Logo /> : <LogoIcon />}
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <div
                  key={idx}
                  onClick={link.onClick}
                  className={cn(
                    "cursor-pointer flex items-center justify-start gap-2 group/sidebar py-2 px-2 rounded-lg transition-colors",
                    link.isActive
                      ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white"
                      : "text-slate-300 hover:bg-slate-800/50 hover:text-white"
                  )}
                >
                  {link.icon}
                  <motion.span
                    animate={{
                      display: open ? "inline-block" : "none",
                      opacity: open ? 1 : 0,
                    }}
                    className="text-sm group-hover/sidebar:translate-x-1 transition duration-150 whitespace-pre inline-block !p-0 !m-0"
                  >
                    {link.label}
                  </motion.span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div
              onClick={handleLogout}
              className="cursor-pointer flex items-center justify-start gap-2 group/sidebar py-2 px-2 rounded-lg transition-colors text-red-400 hover:bg-red-500/10 hover:text-red-300"
            >
              <LogOut className="h-5 w-5 flex-shrink-0" />
              <motion.span
                animate={{
                  display: open ? "inline-block" : "none",
                  opacity: open ? 1 : 0,
                }}
                className="text-sm group-hover/sidebar:translate-x-1 transition duration-150 whitespace-pre inline-block !p-0 !m-0"
              >
                Sign Out
              </motion.span>
            </div>

            {/* Copyright Footer */}
            {open && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 pt-4 px-2 text-xs text-slate-500 border-t border-slate-800"
              >
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
              </motion.div>
            )}
          </div>
        </SidebarBody>
      </AceternitySidebar>
    </div>
  );
}

export const Logo = () => {
  return (
    <div className="flex items-center space-x-3 py-2 px-2">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center">
        <img
          src="/favicon.ico"
          alt="Realtors' Practice Logo"
          className="w-10 h-10 object-contain"
        />
      </div>
      <div className="flex-1 min-w-0">
        <h1 className="text-base font-bold text-white truncate">
          Realtors' Practice
        </h1>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <p className="text-xs text-slate-400">System Online</p>
        </div>
      </div>
    </div>
  );
};

export const LogoIcon = () => {
  return (
    <div className="flex items-center justify-center py-2">
      <img
        src="/favicon.ico"
        alt="Realtors' Practice Logo"
        className="w-10 h-10 object-contain"
      />
    </div>
  );
};
