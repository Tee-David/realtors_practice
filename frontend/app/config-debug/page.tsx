"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function ConfigDebugPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const hasApiUrl = !!apiUrl;
  const nodeEnv = process.env.NODE_ENV;

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Configuration Debug</h1>
        <p className="text-slate-400 mt-1">
          Environment variables and configuration status
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* API URL Configuration */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              {hasApiUrl ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <XCircle className="w-5 h-5 text-red-500" />
              )}
              API URL Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-slate-400 mb-1">Status:</p>
              <Badge
                variant={hasApiUrl ? "default" : "destructive"}
                className={hasApiUrl ? "bg-green-600" : "bg-red-600"}
              >
                {hasApiUrl ? "Configured" : "Not Configured"}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-1">Value:</p>
              <code className="text-xs bg-slate-900 px-2 py-1 rounded text-blue-400 block break-all">
                {apiUrl || "(not set)"}
              </code>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-1">
                Environment Variable:
              </p>
              <code className="text-xs bg-slate-900 px-2 py-1 rounded text-purple-400">
                NEXT_PUBLIC_API_URL
              </code>
            </div>
          </CardContent>
        </Card>

        {/* Node Environment */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              Node Environment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-slate-400 mb-1">
                Current Environment:
              </p>
              <Badge
                variant="default"
                className={
                  nodeEnv === "production"
                    ? "bg-blue-600"
                    : nodeEnv === "development"
                    ? "bg-yellow-600"
                    : "bg-gray-600"
                }
              >
                {nodeEnv || "unknown"}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-1">Build Time:</p>
              <code className="text-xs bg-slate-900 px-2 py-1 rounded text-green-400">
                {new Date().toISOString()}
              </code>
            </div>
          </CardContent>
        </Card>

        {/* Browser Information */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              Browser Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-slate-400 mb-1">User Agent:</p>
              <code className="text-xs bg-slate-900 px-2 py-1 rounded text-blue-400 block break-all">
                {typeof window !== "undefined" ? navigator.userAgent : "SSR"}
              </code>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-1">Online Status:</p>
              <Badge
                variant={
                  typeof window !== "undefined" && navigator.onLine
                    ? "default"
                    : "destructive"
                }
                className={
                  typeof window !== "undefined" && navigator.onLine
                    ? "bg-green-600"
                    : "bg-red-600"
                }
              >
                {typeof window !== "undefined"
                  ? navigator.onLine
                    ? "Online"
                    : "Offline"
                  : "Checking..."}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
              Configuration Checklist
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                {hasApiUrl ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-500 mt-0.5" />
                )}
                <span className="text-slate-300">
                  NEXT_PUBLIC_API_URL environment variable
                </span>
              </li>
              <li className="flex items-start gap-2">
                {typeof window !== "undefined" && navigator.onLine ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-500 mt-0.5" />
                )}
                <span className="text-slate-300">
                  Internet connection active
                </span>
              </li>
              <li className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
                <span className="text-slate-300">
                  Check browser console for API errors
                </span>
              </li>
              <li className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
                <span className="text-slate-300">
                  Verify CORS is enabled on API server
                </span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Instructions */}
      {!hasApiUrl && (
        <Card className="bg-yellow-900/20 border-yellow-700">
          <CardHeader>
            <CardTitle className="text-yellow-400 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Configuration Required
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-yellow-200 text-sm">
              The API URL environment variable is not configured. To fix this:
            </p>
            <ol className="list-decimal list-inside space-y-2 text-yellow-200 text-sm">
              <li>
                <strong>For Vercel:</strong>
                <ul className="list-disc list-inside ml-6 mt-1 space-y-1 text-yellow-300">
                  <li>Go to your project settings on Vercel</li>
                  <li>Navigate to Environment Variables</li>
                  <li>
                    Add:{" "}
                    <code className="bg-slate-900 px-1 rounded">
                      NEXT_PUBLIC_API_URL
                    </code>
                  </li>
                  <li>
                    Value:{" "}
                    <code className="bg-slate-900 px-1 rounded">
                      https://realtors-practice-api.onrender.com/api
                    </code>
                  </li>
                  <li>Redeploy your application</li>
                </ul>
              </li>
              <li>
                <strong>For Local Development:</strong>
                <ul className="list-disc list-inside ml-6 mt-1 space-y-1 text-yellow-300">
                  <li>
                    Create{" "}
                    <code className="bg-slate-900 px-1 rounded">
                      .env.local
                    </code>{" "}
                    file
                  </li>
                  <li>
                    Add:{" "}
                    <code className="bg-slate-900 px-1 rounded">
                      NEXT_PUBLIC_API_URL=https://realtors-practice-api.onrender.com/api
                    </code>
                  </li>
                  <li>Restart your development server</li>
                </ul>
              </li>
            </ol>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
