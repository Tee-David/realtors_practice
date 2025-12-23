"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, AlertCircle, Loader2 } from "lucide-react";

export function ApiHealthCheck() {
  const [status, setStatus] = useState<{
    isChecking: boolean;
    isHealthy: boolean | null;
    message: string;
    apiUrl: string;
  }>({
    isChecking: true,
    isHealthy: null,
    message: "Checking API connection...",
    apiUrl:
      process.env.NEXT_PUBLIC_API_URL ||
      "https://realtors-practice-api.onrender.com/api",
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        console.log("[ApiHealthCheck] Testing API connection...");
        const result = await apiClient.healthCheck();
        console.log("[ApiHealthCheck] Health check result:", result);

        setStatus({
          isChecking: false,
          isHealthy: true,
          message: "API is responding normally",
          apiUrl: status.apiUrl,
        });
      } catch (error) {
        console.error("[ApiHealthCheck] Health check failed:", error);
        setStatus({
          isChecking: false,
          isHealthy: false,
          message:
            error instanceof Error ? error.message : "Failed to connect to API",
          apiUrl: status.apiUrl,
        });
      }
    };

    checkHealth();
  }, []);

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white text-sm flex items-center gap-2">
          API Status
          {status.isChecking && <Loader2 className="w-4 h-4 animate-spin" />}
          {!status.isChecking && status.isHealthy && (
            <CheckCircle className="w-4 h-4 text-green-500" />
          )}
          {!status.isChecking && !status.isHealthy && (
            <XCircle className="w-4 h-4 text-red-500" />
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-xs text-slate-400">
          <span className="font-medium">Endpoint:</span>
          <br />
          <code className="text-blue-400">{status.apiUrl}</code>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={
              status.isHealthy === null
                ? "secondary"
                : status.isHealthy
                ? "default"
                : "destructive"
            }
            className={
              status.isHealthy === null
                ? "bg-slate-600"
                : status.isHealthy
                ? "bg-green-600"
                : "bg-red-600"
            }
          >
            {status.message}
          </Badge>
        </div>
        {!status.isHealthy && !status.isChecking && (
          <div className="mt-2 p-2 bg-yellow-900/20 border border-yellow-700 rounded text-xs text-yellow-400 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>
              <strong>Possible issues:</strong>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li>
                  API server may be down or starting up (Render free tier sleeps
                  after 15min inactivity)
                </li>
                <li>CORS policy blocking requests from this domain</li>
                <li>Network connectivity issues</li>
                <li>Firewall or proxy blocking the API</li>
              </ul>
              <p className="mt-2">
                <strong>Try:</strong> Wait 30-60 seconds for the API to wake up,
                then refresh the page.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
