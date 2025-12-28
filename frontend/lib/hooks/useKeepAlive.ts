"use client";

import { useEffect, useRef } from "react";
import { apiClient } from "@/lib/api";

interface KeepAliveOptions {
  /**
   * Interval in milliseconds between pings
   * Default: 12 minutes (720000ms) - safely before Render's 15min timeout
   */
  interval?: number;

  /**
   * Whether to enable keep-alive pings
   * Default: true in production, false in development
   */
  enabled?: boolean;

  /**
   * Custom ping function
   * Default: uses health check endpoint
   */
  pingFn?: () => Promise<any>;
}

/**
 * Hook to keep the backend server alive by periodically pinging it.
 * Prevents Render free tier from sleeping due to inactivity.
 *
 * Usage:
 * ```tsx
 * useKeepAlive(); // Uses defaults
 * useKeepAlive({ interval: 600000 }); // 10 minutes
 * ```
 */
export function useKeepAlive(options: KeepAliveOptions = {}) {
  const {
    interval = 12 * 60 * 1000, // 12 minutes (before Render's 15min timeout)
    enabled = process.env.NODE_ENV === "production",
    pingFn = () => apiClient.healthCheck(),
  } = options;

  const pingCountRef = useRef(0);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;

    if (!enabled) {
      console.log("[KeepAlive] Disabled - not pinging backend");
      return;
    }

    console.log(
      `[KeepAlive] Starting keep-alive pings (interval: ${
        interval / 60000
      } minutes)`
    );

    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    const ping = async () => {
      if (!isMountedRef.current || !enabled) return;

      pingCountRef.current++;
      const currentPing = pingCountRef.current;

      try {
        console.log(
          `[KeepAlive] Ping #${currentPing} at ${new Date().toLocaleTimeString()}`
        );

        // Emit event for UI indicator
        if (typeof window !== "undefined") {
          window.dispatchEvent(
            new CustomEvent("keep-alive-ping", {
              detail: { ping: currentPing, timestamp: new Date() },
            })
          );
        }

        await pingFn();

        console.log(
          `[KeepAlive] Ping #${currentPing} successful - backend is awake`
        );
      } catch (error) {
        console.warn(
          `[KeepAlive] Ping #${currentPing} failed - backend may be waking up:`,
          error instanceof Error ? error.message : error
        );
      }

      // Schedule next ping
      if (isMountedRef.current && enabled) {
        timeoutId = setTimeout(ping, interval);
      }
    }; // Start pinging after initial delay (1 minute)
    // This gives the app time to load before starting keep-alive
    const initialDelay = 60 * 1000; // 1 minute
    console.log("[KeepAlive] Initial ping in 1 minute...");
    timeoutId = setTimeout(() => {
      ping();
    }, initialDelay);

    return () => {
      isMountedRef.current = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      console.log(`[KeepAlive] Stopped (total pings: ${pingCountRef.current})`);
    };
  }, [enabled, interval, pingFn]);
}
