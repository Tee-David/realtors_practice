"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";
import { cn } from "@/lib/utils";

interface ThemeSwitchProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "icon-click";
  showLabel?: boolean;
}

const ThemeSwitch = React.forwardRef<HTMLDivElement, ThemeSwitchProps>(
  (
    {
      className,
      variant = "default",
      showLabel = false,
      ...props
    },
    ref
  ) => {
    const { theme, toggleTheme, setTheme } = useTheme();

    const modes = ["light", "dark"];
    const icons = [
      <Sun key="sun" className="h-4 w-4" />,
      <Moon key="moon" className="h-4 w-4" />,
    ];

    const currentModeIndex = theme === "dark" ? 1 : 0;

    const handleToggle = React.useCallback(() => {
      console.log('[ThemeSwitch] Toggle clicked, current theme:', theme);
      toggleTheme();
      console.log('[ThemeSwitch] Toggle theme called');
    }, [toggleTheme, theme]);

    const handleIconClick = (index: number) => {
      setTheme(index === 0 ? "light" : "dark");
    };

    return (
      <div className="flex items-center gap-3">
        <div
          className={cn(
            "relative inline-flex h-8 w-14 rounded-full border border-slate-700 bg-slate-800 p-1 shadow-sm transition-colors cursor-pointer hover:border-slate-600",
            className
          )}
          onClick={variant === "default" ? handleToggle : undefined}
          ref={ref}
          {...props}
        >
          <div className="flex w-full h-full items-center justify-between px-0.5">
            {icons.map((icon, idx) => (
              <div
                key={`theme-icon-${idx}`}
                className={cn(
                  "flex h-5 w-5 items-center justify-center rounded-full z-10 transition-all duration-200",
                  currentModeIndex === idx
                    ? "text-slate-900"
                    : "text-slate-400 hover:text-slate-300"
                )}
                onClick={(e) => {
                  if (variant === "icon-click") {
                    e.stopPropagation();
                    handleIconClick(idx);
                  }
                }}
              >
                {icon}
              </div>
            ))}
          </div>

          {/* Animated slider */}
          <div
            className={cn(
              "absolute top-1 h-6 w-6 rounded-full bg-blue-500 transition-all duration-300 ease-in-out shadow-md",
              currentModeIndex === 0 ? "left-1" : "left-7"
            )}
          />
        </div>

        {showLabel && (
          <span className="text-sm text-slate-400 font-medium">
            {theme === "dark" ? "Dark" : "Light"}
          </span>
        )}
      </div>
    );
  }
);

ThemeSwitch.displayName = "ThemeSwitch";

export { ThemeSwitch };
