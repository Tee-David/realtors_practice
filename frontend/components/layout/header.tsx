"use client";

import { Bell, Settings, User, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { toast } from "sonner";
import { useState } from "react";

interface HeaderProps {
  title: string;
  description?: string;
}

export function Header({ title, description }: HeaderProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const handleNotificationClick = () => {
    toast.info("No new notifications");
  };

  const handleSettingsClick = () => {
    toast.info("Settings panel coming soon");
  };

  const handleProfileAction = (action: string) => {
    switch (action) {
      case "profile":
        toast.info("Profile settings coming soon");
        break;
      case "preferences":
        toast.info("User preferences coming soon");
        break;
      case "logout":
        toast.info("Logging out...");
        break;
    }
  };

  return (
    <header className="bg-slate-900/95 backdrop-blur-sm border-b border-slate-700 shadow-lg">
      {/* Main header content */}
      <div className="px-4 sm:px-6 py-3 sm:py-4">
        <div className="flex items-center justify-between gap-2 sm:gap-4">
          {/* Left side - Title with proper spacing for mobile menu */}
          <div className="flex-1 min-w-0 max-w-full sm:max-w-none pl-12 lg:pl-0">
            <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-white truncate">
              {title}
            </h1>
            {description && (
              <p className="hidden sm:block text-xs sm:text-sm text-slate-400 mt-1 truncate">
                {description}
              </p>
            )}
          </div>

          {/* Center - Desktop Search (hidden on mobile) */}
          <div className="hidden lg:flex flex-1 max-w-md mx-4 xl:mx-6">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                type="text"
                placeholder="Search across all data..."
                className="pl-10 bg-slate-800/50 border-slate-600 text-white placeholder:text-slate-400 focus:bg-slate-800"
              />
            </div>
          </div>

          {/* Right side - Actions (responsive) */}
          <div className="flex items-center gap-1 sm:gap-2 lg:gap-3">
            {/* Mobile search toggle */}
            <Button
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              variant="ghost"
              size="sm"
              className="lg:hidden text-slate-400 hover:text-white hover:bg-slate-800 p-2"
            >
              <Search className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>

            {/* Notifications */}
            <div className="relative">
              <Button
                onClick={handleNotificationClick}
                variant="ghost"
                size="sm"
                className="relative text-slate-400 hover:text-white hover:bg-slate-800 p-1.5 sm:p-2"
              >
                <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
                <Badge
                  variant="destructive"
                  className="absolute -top-0.5 -right-0.5 sm:-top-1 sm:-right-1 w-1.5 h-1.5 sm:w-2 sm:h-2 p-0 flex items-center justify-center"
                >
                  <span className="sr-only">3 notifications</span>
                </Badge>
              </Button>
            </div>

            {/* Settings (hidden on smallest screens) */}
            <Button
              onClick={handleSettingsClick}
              variant="ghost"
              size="sm"
              className="hidden xs:flex text-slate-400 hover:text-white hover:bg-slate-800 p-1.5 sm:p-2"
            >
              <Settings className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>

            {/* User menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="relative h-8 w-8 sm:h-10 sm:w-10 rounded-full hover:bg-slate-800"
                >
                  <Avatar className="h-8 w-8 sm:h-10 sm:w-10">
                    <AvatarFallback className="bg-blue-500 text-white font-semibold text-xs sm:text-sm">
                      AD
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent
                className="w-48 sm:w-56 bg-slate-800 border-slate-700 z-50"
                align="end"
                forceMount
              >
                <div className="flex flex-col space-y-1 p-2">
                  <p className="text-sm font-medium text-white truncate">
                    Admin User
                  </p>
                  <p className="text-xs text-slate-400 truncate">
                    admin@realtorscraper.com
                  </p>
                </div>

                <DropdownMenuSeparator className="bg-slate-700" />

                <DropdownMenuItem
                  className="text-slate-300 focus:bg-slate-700 focus:text-white cursor-pointer"
                  onClick={() => handleProfileAction("profile")}
                >
                  <User className="mr-2 h-4 w-4 flex-shrink-0" />
                  <span className="truncate">Profile Settings</span>
                </DropdownMenuItem>

                <DropdownMenuItem
                  className="text-slate-300 focus:bg-slate-700 focus:text-white cursor-pointer"
                  onClick={() => handleProfileAction("preferences")}
                >
                  <Settings className="mr-2 h-4 w-4 flex-shrink-0" />
                  <span className="truncate">Preferences</span>
                </DropdownMenuItem>

                <DropdownMenuSeparator className="bg-slate-700" />

                <DropdownMenuItem
                  className="text-red-400 focus:bg-red-500/10 focus:text-red-300 cursor-pointer"
                  onClick={() => handleProfileAction("logout")}
                >
                  <span className="truncate">Sign Out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Mobile search (collapsible) */}
      {isSearchOpen && (
        <div className="lg:hidden px-4 sm:px-6 pb-3 sm:pb-4 border-t border-slate-700/50">
          <div className="relative ml-12 lg:ml-0">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              type="text"
              placeholder="Search across all data..."
              className="pl-10 bg-slate-800/50 border-slate-600 text-white placeholder:text-slate-400 focus:bg-slate-800"
              autoFocus
            />
          </div>
        </div>
      )}

      {/* Mobile description (shown when search is closed) */}
      {description && !isSearchOpen && (
        <div className="sm:hidden px-4 pb-3 border-t border-slate-700/50">
          <p className="text-xs text-slate-400 truncate pl-12 lg:pl-0">
            {description}
          </p>
        </div>
      )}
    </header>
  );
}
