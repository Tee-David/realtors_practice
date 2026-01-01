"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ThemeToggleProps {
  className?: string;
  variant?: "default" | "icon-only";
}

export function ThemeToggle({ className, variant = "default" }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();

  if (variant === "icon-only") {
    return (
      <Button
        onClick={toggleTheme}
        variant="ghost"
        size="sm"
        className={cn("p-2", className)}
        title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      >
        {theme === "dark" ? (
          <Sun className="w-5 h-5 text-yellow-400" />
        ) : (
          <Moon className="w-5 h-5 text-slate-700" />
        )}
      </Button>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        "group w-full flex items-center px-3 py-2 rounded-lg text-left transition-all duration-200",
        "focus:outline-none focus:ring-2 focus:ring-blue-500/50",
        "text-slate-400 hover:bg-slate-800/50 hover:text-white dark:text-slate-400 dark:hover:bg-slate-800/50",
        "bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-transparent",
        className
      )}
      title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
    >
      {theme === "dark" ? (
        <Sun className="w-4 h-4 flex-shrink-0 mr-3 text-yellow-400" />
      ) : (
        <Moon className="w-4 h-4 flex-shrink-0 mr-3 text-slate-700 dark:text-slate-400" />
      )}
      <span className="font-medium">
        {theme === "dark" ? "Light Mode" : "Dark Mode"}
      </span>
    </button>
  );
}
