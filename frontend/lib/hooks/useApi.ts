"use client";
import { useState, useEffect, useCallback, useRef } from "react";
// import { ApiError } from "../api";

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiOptions {
  immediate?: boolean;
  onError?: (error: any) => void;
}

export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions = {}
): UseApiState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const isMountedRef = useRef(true);

  // Store options in ref to avoid recreating execute on every options change
  const optionsRef = useRef(options);
  optionsRef.current = options;

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Store the latest apiCall in a ref to avoid dependency issues
  const apiCallRef = useRef(apiCall);
  useEffect(() => {
    apiCallRef.current = apiCall;
  }, [apiCall]);

  const execute = useCallback(async () => {
    if (!isMountedRef.current) return;

    // Only log in development
    if (process.env.NODE_ENV === "development") {
      console.log("[useApi] Starting request...");
    }

    setState((prev: UseApiState<T>) => ({
      ...prev,
      loading: true,
      error: null,
    }));

    // Create abort controller for request cancellation
    const controller = new AbortController();
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    // Add timeout to prevent infinite loading (120 second timeout for cold starts)
    timeoutId = setTimeout(() => {
      if (isMountedRef.current) {
        controller.abort();
        console.error("[useApi] Request timeout after 120 seconds");
        setState((prev: UseApiState<T>) => ({
          ...prev,
          loading: false,
          error:
            "API timeout: The server is taking longer than expected. Please wait and refresh the page.",
        }));
      }
    }, 120000); // 120 second timeout

    try {
      // Use apiCallRef to get the latest apiCall without causing re-renders
      const data = await apiCallRef.current();

      if (timeoutId) clearTimeout(timeoutId);

      if (isMountedRef.current) {
        if (process.env.NODE_ENV === "development") {
          console.log("[useApi] Request succeeded:", data);
        }
        setState({ data, loading: false, error: null });
      }
    } catch (error) {
      if (timeoutId) clearTimeout(timeoutId);

      if (!isMountedRef.current) return;

      // Skip timeout errors that we already handled
      if (error instanceof Error && error.name === "AbortError") {
        return;
      }

      let errorMessage = "An error occurred";
      if (error && typeof error === "object" && "message" in error) {
        errorMessage = (error as any).message || errorMessage;
      } else if (typeof error === "string") {
        errorMessage = error;
      }

      // Only log error if no custom error handler is provided
      if (!optionsRef.current.onError) {
        console.error("[useApi] Request failed:", errorMessage, error);
      }

      setState((prev: UseApiState<T>) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));

      if (optionsRef.current.onError) {
        optionsRef.current.onError(error);
      }
    }
  }, []); // Empty deps - use refs to avoid infinite loops

  useEffect(() => {
    // Execute on mount if immediate is not false
    if (optionsRef.current.immediate !== false) {
      execute();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  return {
    ...state,
    refetch: execute,
  };
}

export function useApiMutation<T, P = unknown>(
  apiCall: (params: P) => Promise<T>
): {
  mutate: (params: P) => Promise<T>;
  loading: boolean;
  error: string | null;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(
    async (params: P): Promise<T> => {
      if (process.env.NODE_ENV === "development") {
        console.log("[useApiMutation] Starting mutation with params:", params);
      }
      setLoading(true);
      setError(null);

      try {
        const result = await apiCall(params);
        if (process.env.NODE_ENV === "development") {
          console.log("[useApiMutation] Mutation succeeded:", result);
        }
        setLoading(false);
        return result;
      } catch (err) {
        let errorMessage = "An error occurred";
        if (err && typeof err === "object" && "message" in err) {
          errorMessage = (err as any).message || errorMessage;
        }
        console.error("[useApiMutation] Mutation failed:", errorMessage, err);
        setError(errorMessage);
        setLoading(false);
        throw err;
      }
    },
    [apiCall]
  );

  return { mutate, loading, error };
}

// Polling hook for real-time updates
export function usePolling<T>(
  apiCall: () => Promise<T>,
  interval: number = 5000,
  enabled: boolean = true
): UseApiState<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const isMountedRef = useRef(true);
  const intervalRef = useRef(interval);
  const enabledRef = useRef(enabled);
  const pollCountRef = useRef(0);
  const apiCallRef = useRef(apiCall);

  // Update refs with latest values
  intervalRef.current = interval;
  enabledRef.current = enabled;

  // Update apiCallRef when apiCall changes
  useEffect(() => {
    apiCallRef.current = apiCall;
  }, [apiCall]);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!enabled) return;

  let timeoutId: ReturnType<typeof setTimeout> | undefined;
    pollCountRef.current = 0;
    let consecutiveErrors = 0;

    const poll = async () => {
      if (!isMountedRef.current || !enabledRef.current) return;

      pollCountRef.current++;
      const currentPoll = pollCountRef.current;

      if (process.env.NODE_ENV === "development") {
        console.log(
          `[usePolling] Poll #${currentPoll} starting (interval: ${intervalRef.current}ms)`
        );
      }

      try {
        setState((prev: UseApiState<T>) => ({
          ...prev,
          loading: true,
          error: null,
        }));

        // Use apiCallRef to avoid dependency issues
        const data = await apiCallRef.current();

        if (isMountedRef.current) {
          if (process.env.NODE_ENV === "development") {
            console.log(`[usePolling] Poll #${currentPoll} succeeded:`, data);
          }
          setState({ data, loading: false, error: null });
          // Reset consecutive error count on success
          consecutiveErrors = 0;
        }
      } catch (error) {
        if (!isMountedRef.current) return;

        consecutiveErrors++;
        let errorMessage = "An error occurred";
        if (error && typeof error === "object" && "message" in error) {
          errorMessage = (error as any).message || errorMessage;
        }
        
        if (process.env.NODE_ENV === "development") {
          console.warn(
            `[usePolling] Poll #${currentPoll} failed (attempt #${consecutiveErrors}):`,
            errorMessage
          );
        }
        
        setState((prev: UseApiState<T>) => ({
          ...prev,
          loading: false,
          error: consecutiveErrors > 3 ? errorMessage : null, // Only show error after 3 consecutive failures
        }));
      }

      // Schedule next poll only if still enabled and mounted
      if (enabledRef.current && isMountedRef.current) {
        // Exponential backoff: if there have been errors, increase interval
        const backoffMultiplier = Math.min(2 ** (consecutiveErrors - 1), 4);
        const nextInterval = intervalRef.current * backoffMultiplier;
        timeoutId = setTimeout(poll, nextInterval);
      }
    };

    // Start polling immediately
    if (process.env.NODE_ENV === "development") {
      console.log(
        `[usePolling] Starting polling (interval: ${intervalRef.current}ms, enabled: ${enabled})`
      );
    }
    poll();

    return () => {
      if (process.env.NODE_ENV === "development") {
        console.log(
          `[usePolling] Stopping polling (total polls: ${pollCountRef.current})`
        );
      }
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled]); // Only depend on enabled - apiCall is handled by ref

  return state;
}
