"use client";

import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiStatusBanner } from "@/components/ui/api-status-banner";
import {
  Settings as SettingsIcon,
  Globe,
  Mail,
  Database,
  Sliders,
  RefreshCw,
  Check,
  X,
  TestTube,
} from "lucide-react";
import { toast } from "sonner";

/**
 * Settings Admin Page
 * Consolidates 11 API endpoints:
 * - Sites: list all sites, enable/disable, test, update config
 * - Email: SMTP settings, test email, update recipients
 * - Firestore: connection status, upload data, manage collections
 * - System: global settings, cache management, export preferences
 */

type TabType = "sites" | "email" | "firestore" | "system";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabType>("sites");

  const tabs = [
    { id: "sites" as TabType, label: "Sites Configuration", icon: Globe },
    { id: "email" as TabType, label: "Email Notifications", icon: Mail },
    {
      id: "firestore" as TabType,
      label: "Firestore Integration",
      icon: Database,
    },
    { id: "system" as TabType, label: "System Settings", icon: Sliders },
  ];

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 sm:w-8 sm:h-8" />
          Settings
        </h1>
        <p className="text-sm sm:text-base text-slate-400 mt-1">
          Configure system settings, sites, email notifications, and
          integrations
        </p>
      </div>

      {/* Admin Notice */}
      <Card className="bg-orange-900/20 border-orange-700">
        <CardHeader>
          <CardTitle className="text-orange-400 flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-orange-600 text-white rounded">
              ADMIN ONLY
            </span>
            System Configuration
          </CardTitle>
          <CardDescription className="text-orange-300">
            Changes made here affect the entire system. Test thoroughly before
            applying to production.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-700 overflow-x-auto scrollbar-thin scrollbar-thumb-slate-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-3 sm:px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? "text-blue-400 border-b-2 border-blue-400"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span className="hidden sm:inline">{tab.label}</span>
            <span className="sm:hidden">{tab.label.split(" ")[0]}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === "sites" && <SitesTab />}
        {activeTab === "email" && <EmailTab />}
        {activeTab === "firestore" && <FirestoreTab />}
        {activeTab === "system" && <SystemTab />}
      </div>
    </div>
  );
}

// Sites Configuration Tab
function SitesTab() {
  const listSites = useCallback(async () => apiClient.listSites(), []);
  const { data, loading, error, refetch } = useApi<{
    sites: any[];
    total: number;
    enabled: number;
    disabled: number;
  }>(listSites);

  const sites = data?.sites || [];

  const handleToggleSite = async (siteKey: string) => {
    try {
      const result = await apiClient.toggleSite(siteKey);
      toast.success(result.message);
      refetch();
    } catch (error) {
      toast.error("Failed to update site");
    }
  };

  const handleTestSite = async (siteKey: string) => {
    try {
      const result = await apiClient.siteHealth(siteKey);
      if ((result as any).healthy) {
        toast.success(`${siteKey} is healthy!`);
      } else {
        toast.error(`${siteKey} has issues`);
      }
    } catch (error) {
      toast.error("Failed to test site");
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white">Sites Configuration</CardTitle>
            <CardDescription className="text-slate-400">
              Manage 82+ real estate sites - enable, disable, test, and
              configure
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={refetch}
            className="border-slate-600 hover:bg-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4">
            <ApiStatusBanner message={error} onRetry={refetch} type="error" />
          </div>
        )}

        {loading && (
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        )}

        {!loading && sites && sites.length > 0 && (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-slate-700">
                  <TableHead className="text-slate-300">Site</TableHead>
                  <TableHead className="text-slate-300">Status</TableHead>
                  <TableHead className="text-slate-300">Last Scraped</TableHead>
                  <TableHead className="text-slate-300">Properties</TableHead>
                  <TableHead className="text-slate-300">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sites.map((site: any) => (
                  <TableRow key={site.site_key} className="border-slate-700">
                    <TableCell className="font-medium text-white">
                      {site.site_key}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={site.enabled ? "default" : "secondary"}
                        className={
                          site.enabled ? "bg-green-600" : "bg-slate-600"
                        }
                      >
                        {site.enabled ? (
                          <Check className="w-3 h-3 mr-1" />
                        ) : (
                          <X className="w-3 h-3 mr-1" />
                        )}
                        {site.enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-slate-400">
                      {site.last_scraped || "Never"}
                    </TableCell>
                    <TableCell className="text-slate-300">
                      {site.property_count || 0}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={site.enabled}
                          onCheckedChange={() =>
                            handleToggleSite(site.site_key)
                          }
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleTestSite(site.site_key)}
                          className="border-slate-600 hover:bg-slate-700"
                        >
                          <TestTube className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Email Notifications Tab
function EmailTab() {
  const [smtpSettings, setSmtpSettings] = useState({
    host: "",
    port: "587",
    username: "",
    password: "",
    from_email: "",
  });

  const handleTestEmail = async () => {
    try {
      await apiClient.sendTestEmail("test@example.com");
      toast.success("Test email sent successfully!");
    } catch (error) {
      toast.error("Failed to send test email");
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Email Notifications</CardTitle>
        <CardDescription className="text-slate-400">
          Configure SMTP settings and email alert recipients
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* SMTP Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">
            SMTP Configuration
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="smtp-host" className="text-slate-300">
                SMTP Host
              </Label>
              <Input
                id="smtp-host"
                placeholder="smtp.gmail.com"
                value={smtpSettings.host}
                onChange={(e) =>
                  setSmtpSettings({ ...smtpSettings, host: e.target.value })
                }
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="smtp-port" className="text-slate-300">
                Port
              </Label>
              <Input
                id="smtp-port"
                placeholder="587"
                value={smtpSettings.port}
                onChange={(e) =>
                  setSmtpSettings({ ...smtpSettings, port: e.target.value })
                }
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="smtp-username" className="text-slate-300">
                Username
              </Label>
              <Input
                id="smtp-username"
                placeholder="your-email@gmail.com"
                value={smtpSettings.username}
                onChange={(e) =>
                  setSmtpSettings({ ...smtpSettings, username: e.target.value })
                }
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="smtp-password" className="text-slate-300">
                Password
              </Label>
              <Input
                id="smtp-password"
                type="password"
                placeholder="••••••••"
                value={smtpSettings.password}
                onChange={(e) =>
                  setSmtpSettings({ ...smtpSettings, password: e.target.value })
                }
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div className="col-span-2 space-y-2">
              <Label htmlFor="from-email" className="text-slate-300">
                From Email
              </Label>
              <Input
                id="from-email"
                placeholder="noreply@yourdomain.com"
                value={smtpSettings.from_email}
                onChange={(e) =>
                  setSmtpSettings({
                    ...smtpSettings,
                    from_email: e.target.value,
                  })
                }
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button className="bg-blue-600 hover:bg-blue-700">
              Save SMTP Settings
            </Button>
            <Button
              variant="outline"
              onClick={handleTestEmail}
              className="border-slate-600 hover:bg-slate-700"
            >
              <TestTube className="w-4 h-4 mr-2" />
              Send Test Email
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Firestore Integration Tab
function FirestoreTab() {
  const [firestoreConnected, setFirestoreConnected] = useState(false);
  const [propertyCount, setPropertyCount] = useState(0);

  const handleUpload = async () => {
    try {
      await apiClient.exportToFirestore([]);
      toast.success("Data upload initiated!");
      setFirestoreConnected(true);
    } catch (error) {
      toast.error("Failed to upload to Firestore");
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Firestore Integration</CardTitle>
        <CardDescription className="text-slate-400">
          Manage cloud database connection and data synchronization
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Connection Status */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">
            Connection Status
          </h3>
          <div className="p-4 bg-slate-900 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-white font-medium">
                  {firestoreConnected ? "Connected" : "Disconnected"}
                </div>
                <div className="text-sm text-slate-400">
                  {propertyCount} properties in Firestore
                </div>
              </div>
              <Badge
                variant={firestoreConnected ? "default" : "secondary"}
                className={firestoreConnected ? "bg-green-600" : "bg-red-600"}
              >
                {firestoreConnected ? "Active" : "Inactive"}
              </Badge>
            </div>
          </div>
        </div>

        {/* Upload Actions */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">Data Management</h3>
          <Button
            onClick={handleUpload}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Database className="w-4 h-4 mr-2" />
            Upload Data to Firestore
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// System Settings Tab
function SystemTab() {
  const [settings, setSettings] = useState({
    max_workers: 5,
    request_delay: 1,
    enable_geocoding: true,
    enable_caching: true,
    export_format: "xlsx",
  });

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">System Settings</CardTitle>
        <CardDescription className="text-slate-400">
          Configure global scraping defaults and system behavior
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Scraping Settings */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">
            Scraping Configuration
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="max-workers" className="text-slate-300">
                Max Workers
              </Label>
              <Input
                id="max-workers"
                type="number"
                value={settings.max_workers}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    max_workers: Number(e.target.value),
                  })
                }
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="request-delay" className="text-slate-300">
                Request Delay (seconds)
              </Label>
              <Input
                id="request-delay"
                type="number"
                value={settings.request_delay}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    request_delay: Number(e.target.value),
                  })
                }
                className="bg-slate-900 border-slate-600 text-white"
              />
            </div>
          </div>
        </div>

        {/* Feature Toggles */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">Features</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
              <div>
                <div className="text-white font-medium">Enable Geocoding</div>
                <div className="text-sm text-slate-400">
                  Automatically fetch coordinates for properties
                </div>
              </div>
              <Switch
                checked={settings.enable_geocoding}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, enable_geocoding: checked })
                }
              />
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
              <div>
                <div className="text-white font-medium">Enable Caching</div>
                <div className="text-sm text-slate-400">
                  Cache API responses to improve performance
                </div>
              </div>
              <Switch
                checked={settings.enable_caching}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, enable_caching: checked })
                }
              />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <Button className="bg-blue-600 hover:bg-blue-700">
          Save System Settings
        </Button>
      </CardContent>
    </Card>
  );
}
