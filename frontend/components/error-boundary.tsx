"use client";

import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[ErrorBoundary] Caught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex items-center justify-center min-h-screen bg-slate-950">
          <div className="max-w-md w-full mx-4">
            <div className="bg-slate-800 border border-red-500/20 rounded-lg p-6 space-y-4">
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-6 h-6 flex-shrink-0" />
                <h2 className="text-xl font-bold">Something went wrong</h2>
              </div>

              <p className="text-slate-300">
                {this.state.error?.message || "An unexpected error occurred"}
              </p>

              <div className="bg-slate-900 rounded p-3 text-xs text-slate-400 font-mono overflow-auto max-h-40">
                {this.state.error?.stack || "No stack trace available"}
              </div>

              <Button
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.reload();
                }}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reload Page
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
