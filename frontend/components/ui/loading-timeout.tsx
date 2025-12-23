"use client";

import { useEffect, useState } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./button";
// import { Button } from "./ui/button";

interface LoadingTimeoutProps {
  children: React.ReactNode;
  timeout?: number; // in milliseconds
  message?: string;
}

export function LoadingTimeout({
  children,
  timeout = 90000, // 90 seconds default
  message = "This is taking longer than expected. The API server may be experiencing issues.",
}: LoadingTimeoutProps) {
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  useEffect(() => {
    // Counter for seconds elapsed
    const counterInterval = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);

    // Timeout detection
    const timeoutId = setTimeout(() => {
      console.error("[LoadingTimeout] Page loading timeout exceeded:", timeout);
      setHasTimedOut(true);
    }, timeout);

    return () => {
      clearInterval(counterInterval);
      clearTimeout(timeoutId);
    };
  }, [timeout]);

  if (hasTimedOut) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950 p-4">
        <div className="max-w-lg w-full">
          <div className="bg-slate-800 border border-yellow-500/20 rounded-lg p-6 space-y-4">
            <div className="flex items-center gap-3 text-yellow-400">
              <AlertCircle className="w-6 h-6 flex-shrink-0" />
              <div>
                <h2 className="text-xl font-bold">Loading Timeout</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Waited {secondsElapsed} seconds
                </p>
              </div>
            </div>

            <p className="text-slate-300">{message}</p>

            <div className="bg-blue-900/20 border border-blue-500/20 rounded p-4 space-y-2">
              <p className="text-sm text-blue-300 font-medium">
                💡 Possible Solutions:
              </p>
              <ul className="text-xs text-slate-400 space-y-1 list-disc list-inside">
                <li>Refresh the page and wait 60+ seconds</li>
                <li>The free-tier API server needs time to wake up</li>
                <li>Check your internet connection</li>
                <li>Try again in a few minutes</li>
              </ul>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => window.location.reload()}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reload Page
              </Button>
              <Button
                onClick={() => setHasTimedOut(false)}
                variant="outline"
                className="flex-1 border-slate-600 text-white"
              >
                Keep Waiting
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
