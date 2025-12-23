"use client";

import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./button";

interface ApiStatusBannerProps {
  message: string;
  onRetry?: () => void;
  type?: "warning" | "error" | "info";
}

export function ApiStatusBanner({
  message,
  onRetry,
  type = "warning",
}: ApiStatusBannerProps) {
  const bgColor = {
    warning: "bg-yellow-500/10 border-yellow-500/20",
    error: "bg-red-500/10 border-red-500/20",
    info: "bg-blue-500/10 border-blue-500/20",
  }[type];

  const textColor = {
    warning: "text-yellow-400",
    error: "text-red-400",
    info: "text-blue-400",
  }[type];

  return (
    <div
      className={`flex items-center justify-between gap-4 p-4 rounded-lg border ${bgColor} ${textColor}`}
    >
      <div className="flex items-center gap-3">
        <AlertCircle className="w-5 h-5 flex-shrink-0" />
        <div>
          <p className="font-medium">{message}</p>
          <p className="text-xs text-slate-400 mt-1">
            The API server may need 30-60 seconds to wake up from sleep mode
          </p>
        </div>
      </div>
      {onRetry && (
        <Button
          onClick={onRetry}
          size="sm"
          variant="outline"
          className="border-current hover:bg-current/10 flex-shrink-0"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      )}
    </div>
  );
}
