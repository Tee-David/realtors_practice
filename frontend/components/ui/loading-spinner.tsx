import React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl";
  label?: string;
  fullScreen?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: "w-6 h-6",
  md: "w-10 h-10",
  lg: "w-16 h-16",
  xl: "w-24 h-24",
};

export function LoadingSpinner({
  size = "lg",
  label = "Loading...",
  fullScreen = true,
  className,
}: LoadingSpinnerProps) {
  const content = (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-4",
        fullScreen && "min-h-screen",
        className
      )}
    >
      <Loader2
        className={cn(sizeClasses[size], "animate-spin text-blue-500")}
      />
      {label && (
        <div className="text-center space-y-2">
          <p className="text-slate-200 text-base sm:text-lg font-medium animate-pulse">
            {label}
          </p>
          <p className="text-slate-400 text-xs sm:text-sm max-w-md px-4">
            First load may take 30-60 seconds while the server wakes up
          </p>
        </div>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-slate-900 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
}

// Inline variant for smaller loading states
export function InlineSpinner({
  size = "sm",
  className,
}: {
  size?: "sm" | "md";
  className?: string;
}) {
  return (
    <Loader2
      className={cn(
        size === "sm" ? "w-4 h-4" : "w-6 h-6",
        "animate-spin text-blue-500",
        className
      )}
    />
  );
}
