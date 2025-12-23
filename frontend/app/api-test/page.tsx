"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CheckCircle2, XCircle, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TestResult {
  name: string;
  status: "loading" | "success" | "error";
  message?: string;
  duration?: number;
}

export default function ApiTestPage() {
  const [tests, setTests] = useState<TestResult[]>([
    { name: "Health Check", status: "loading" },
    { name: "Sites List", status: "loading" },
    { name: "Statistics", status: "loading" },
    { name: "Rate Limit", status: "loading" },
  ]);
  const [overallStatus, setOverallStatus] = useState<
    "loading" | "success" | "error"
  >("loading");

  const runTests = async () => {
    setOverallStatus("loading");
    const results: TestResult[] = [];

    // Test 1: Health Check
    try {
      const start = Date.now();
      const health = await apiClient.healthCheck();
      results.push({
        name: "Health Check",
        status: health.status === "healthy" ? "success" : "error",
        message:
          health.status === "healthy"
            ? "Backend is healthy"
            : "Backend returned unhealthy status",
        duration: Date.now() - start,
      });
    } catch (error) {
      results.push({
        name: "Health Check",
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
      });
    }

    // Test 2: Sites List
    try {
      const start = Date.now();
      const sites = await apiClient.listSites();
      results.push({
        name: "Sites List",
        status: "success",
        message: `Found ${sites.total} sites (${sites.enabled} enabled, ${sites.disabled} disabled)`,
        duration: Date.now() - start,
      });
    } catch (error) {
      results.push({
        name: "Sites List",
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
      });
    }

    // Test 3: Statistics
    try {
      const start = Date.now();
      const stats = await apiClient.getOverviewStats();
      results.push({
        name: "Statistics",
        status: "success",
        message: `Total sites: ${
          stats.overview.total_sites || 0
        }, Total listings: ${stats.overview.total_listings || 0}`,
        duration: Date.now() - start,
      });
    } catch (error) {
      results.push({
        name: "Statistics",
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
      });
    }

    // Test 4: Rate Limit
    try {
      const start = Date.now();
      const rateLimit = await apiClient.getRateLimitStatus();
      results.push({
        name: "Rate Limit",
        status: "success",
        message: `Total requests: ${rateLimit.total_requests || 0}`,
        duration: Date.now() - start,
      });
    } catch (error) {
      results.push({
        name: "Rate Limit",
        status: "error",
        message: error instanceof Error ? error.message : "Unknown error",
      });
    }

    setTests(results);

    // Determine overall status
    const hasError = results.some((r) => r.status === "error");
    setOverallStatus(hasError ? "error" : "success");
  };

  useEffect(() => {
    runTests();
  }, []);

  const getStatusIcon = (status: TestResult["status"]) => {
    switch (status) {
      case "loading":
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      case "success":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusColor = (status: TestResult["status"]) => {
    switch (status) {
      case "loading":
        return "border-blue-500";
      case "success":
        return "border-green-500";
      case "error":
        return "border-red-500";
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">
              API Integration Test
            </h1>
            <p className="text-slate-400 mt-2">
              Testing connection to:{" "}
              <code className="text-blue-400">
                https://realtors-practice-api.onrender.com/api
              </code>
            </p>
          </div>
          <Button
            onClick={runTests}
            disabled={overallStatus === "loading"}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {overallStatus === "loading" ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Retest
              </>
            )}
          </Button>
        </div>

        {/* Overall Status */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              {getStatusIcon(overallStatus)}
              Overall Status
            </CardTitle>
            <CardDescription className="text-slate-400">
              {overallStatus === "loading" &&
                "Running tests... First request may take 30-60 seconds if backend is sleeping."}
              {overallStatus === "success" &&
                "✅ All tests passed! Frontend is successfully connected to backend."}
              {overallStatus === "error" &&
                "❌ Some tests failed. Check details below."}
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Individual Tests */}
        <div className="space-y-4">
          {tests.map((test, index) => (
            <Card
              key={index}
              className={`bg-slate-800 border-2 ${getStatusColor(test.status)}`}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(test.status)}
                    <div>
                      <CardTitle className="text-white text-lg">
                        {test.name}
                      </CardTitle>
                      {test.message && (
                        <CardDescription className="text-slate-400 mt-1">
                          {test.message}
                        </CardDescription>
                      )}
                    </div>
                  </div>
                  {test.duration && (
                    <div className="text-slate-400 text-sm">
                      {test.duration}ms
                    </div>
                  )}
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>

        {/* Configuration Info */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-400">Backend URL:</span>
              <code className="text-blue-400">
                {process.env.NEXT_PUBLIC_API_URL ||
                  "https://realtors-practice-api.onrender.com/api"}
              </code>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Environment Variable:</span>
              <code className="text-green-400">
                {process.env.NEXT_PUBLIC_API_URL
                  ? "✅ Set"
                  : "⚠️ Using default"}
              </code>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">API Client:</span>
              <code className="text-green-400">✅ Initialized</code>
            </div>
          </CardContent>
        </Card>

        {/* Next Steps */}
        {overallStatus === "success" && (
          <Card className="bg-green-900/20 border-green-500">
            <CardHeader>
              <CardTitle className="text-green-400">
                🎉 Success! What's Next?
              </CardTitle>
              <CardContent className="text-slate-300 space-y-2 pl-0">
                <p>
                  Your frontend is successfully connected to the deployed
                  backend!
                </p>
                <ul className="list-disc list-inside space-y-1 mt-2">
                  <li>Explore the Dashboard to see scraped data</li>
                  <li>Try the Scraper Control to trigger a scrape</li>
                  <li>Check out Health Monitor for system status</li>
                  <li>When ready, deploy to Vercel for production</li>
                </ul>
              </CardContent>
            </CardHeader>
          </Card>
        )}
      </div>
    </div>
  );
}
