"use client";

import { useEffect, useState } from "react";
import { Activity, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface KeepAliveIndicatorProps {
  /**
   * Whether to show the indicator
   * Default: true in production, false in development
   */
  show?: boolean;

  /**
   * Position of the indicator
   */
  position?: "bottom-right" | "bottom-left" | "top-right" | "top-left";
}

/**
 * Visual indicator showing keep-alive status
 * Displays in the corner to show backend is being kept alive
 */
export function KeepAliveIndicator({
  show = process.env.NODE_ENV === "production",
  position = "bottom-right",
}: KeepAliveIndicatorProps) {
  const [isActive, setIsActive] = useState(false);
  const [lastPing, setLastPing] = useState<Date | null>(null);

  useEffect(() => {
    if (!show) return;

    // Listen for keep-alive events (we'll emit these from the hook)
    const handleKeepAlive = (event: CustomEvent) => {
      setIsActive(true);
      setLastPing(new Date());

      // Flash the indicator
      setTimeout(() => setIsActive(false), 2000);
    };

    window.addEventListener("keep-alive-ping" as any, handleKeepAlive);

    return () => {
      window.removeEventListener("keep-alive-ping" as any, handleKeepAlive);
    };
  }, [show]);

  if (!show) return null;

  const positionClasses = {
    "bottom-right": "bottom-4 right-4",
    "bottom-left": "bottom-4 left-4",
    "top-right": "top-4 right-4",
    "top-left": "top-4 left-4",
  };

  return (
    <div
      className={cn(
        "fixed z-50 flex items-center gap-2 px-3 py-2 rounded-full",
        "bg-slate-800/90 backdrop-blur-sm border border-slate-700/50",
        "text-xs text-slate-400 shadow-lg",
        "transition-all duration-300",
        positionClasses[position],
        isActive && "bg-green-900/90 border-green-700/50 text-green-400"
      )}
      title={
        lastPing
          ? `Last ping: ${lastPing.toLocaleTimeString()}`
          : "Keep-alive active"
      }
    >
      {isActive ? (
        <>
          <Activity className="w-3 h-3 animate-pulse" />
          <span className="font-medium">Pinging...</span>
        </>
      ) : (
        <>
          <Wifi className="w-3 h-3" />
          <span>Keep-alive</span>
        </>
      )}
    </div>
  );
}
