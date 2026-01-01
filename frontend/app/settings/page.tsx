"use client";

import { useState, useCallback, useEffect } from "react";
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
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { mockUsers } from "@/lib/mockData";

/**
 * Settings Admin Page
 * Consolidates 11 API endpoints:
 * - Sites: list all sites, enable/disable, test, update config
 * - Email: SMTP settings, test email, update recipients
 * - Firestore: connection status, upload data, manage collections
 * - System: global settings, cache management, export preferences
 */

type TabType = "sites" | "email" | "firestore" | "system" | "users";

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
    { id: "users" as TabType, label: "User Management", icon: Users },
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
        {activeTab === "users" && <UsersTab />}
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
              Manage real estate sites — enable, disable, test, and configure
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
  const [envCategories, setEnvCategories] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [envChanges, setEnvChanges] = useState<Record<string, any>>({});

  // Load environment variables on mount
  useEffect(() => {
    loadEnvVariables();
  }, []);

  const loadEnvVariables = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getEnvCategories();
      if (response.success) {
        setEnvCategories(response.categories);
      }
    } catch (error) {
      toast.error("Failed to load environment variables");
    } finally {
      setLoading(false);
    }
  };

  const handleEnvChange = (key: string, value: any) => {
    setEnvChanges((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSaveEnvVariables = async () => {
    if (Object.keys(envChanges).length === 0) {
      toast.info("No changes to save");
      return;
    }

    try {
      setSaving(true);
      const response = await apiClient.updateEnvVariables(envChanges);
      if (response.success) {
        toast.success(response.message);
        setEnvChanges({});
        await loadEnvVariables(); // Reload to show updated values
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to save environment variables");
    } finally {
      setSaving(false);
    }
  };

  const handleUpload = async () => {
    try {
      await apiClient.exportToFirestore([]);
      toast.success("Data upload initiated!");
      setFirestoreConnected(true);
    } catch (error) {
      toast.error("Failed to upload to Firestore");
    }
  };

  const renderEnvInput = (envVar: any) => {
    const currentValue =
      envChanges[envVar.key] !== undefined
        ? envChanges[envVar.key]
        : envVar.value;

    switch (envVar.type) {
      case "boolean":
        return (
          <Switch
            checked={currentValue}
            onCheckedChange={(checked) => handleEnvChange(envVar.key, checked)}
          />
        );

      case "number":
        return (
          <Input
            type="number"
            value={currentValue}
            onChange={(e) =>
              handleEnvChange(envVar.key, Number(e.target.value))
            }
            className="bg-slate-900 border-slate-600 text-white"
          />
        );

      case "select":
        return (
          <select
            value={currentValue}
            onChange={(e) => handleEnvChange(envVar.key, e.target.value)}
            className="w-full h-10 px-3 bg-slate-900 border border-slate-600 text-white rounded-md"
          >
            {envVar.options?.map((option: string) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );

      case "password":
        return (
          <Input
            type="password"
            value={currentValue}
            onChange={(e) => handleEnvChange(envVar.key, e.target.value)}
            className="bg-slate-900 border-slate-600 text-white"
            placeholder="••••••••"
          />
        );

      default:
        return (
          <Input
            type="text"
            value={currentValue}
            onChange={(e) => handleEnvChange(envVar.key, e.target.value)}
            className="bg-slate-900 border-slate-600 text-white"
          />
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Firestore Connection Status */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Firestore Connection</CardTitle>
          <CardDescription className="text-slate-400">
            Manage cloud database connection and data synchronization
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Connection Status */}
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

          {/* Upload Actions */}
          <Button
            onClick={handleUpload}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Database className="w-4 h-4 mr-2" />
            Upload Data to Firestore
          </Button>
        </CardContent>
      </Card>

      {/* Environment Variables Configuration */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white">
                Environment Variables
              </CardTitle>
              <CardDescription className="text-slate-400">
                Configure project settings - changes persist to backend .env file
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={loadEnvVariables}
                disabled={loading}
                className="border-slate-600 hover:bg-slate-700"
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
              <Button
                onClick={handleSaveEnvVariables}
                disabled={saving || Object.keys(envChanges).length === 0}
                className="bg-green-600 hover:bg-green-700"
              >
                {saving ? "Saving..." : "Save Changes"}
                {Object.keys(envChanges).length > 0 && (
                  <Badge className="ml-2 bg-orange-600">
                    {Object.keys(envChanges).length}
                  </Badge>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(envCategories).map(([category, variables]: [string, any]) => (
                <div key={category} className="space-y-4">
                  <h3 className="text-lg font-semibold text-white border-b border-slate-700 pb-2">
                    {category}
                  </h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {variables.map((envVar: any) => (
                      <div
                        key={envVar.key}
                        className="p-4 bg-slate-900 rounded-lg border border-slate-700 space-y-2"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <Label className="text-slate-300 font-medium">
                              {envVar.key}
                            </Label>
                            <p className="text-xs text-slate-400 mt-1">
                              {envVar.description}
                            </p>
                          </div>
                          {envChanges[envVar.key] !== undefined && (
                            <Badge className="bg-orange-600 text-xs ml-2">
                              Modified
                            </Badge>
                          )}
                        </div>
                        <div className="mt-2">{renderEnvInput(envVar)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
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

// User Management Tab
function UsersTab() {
  const [users, setUsers] = useState<any[]>([]);
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUser, setNewUser] = useState({
    username: "",
    email: "",
    password: "",
    role: "user",
  });
  const [resetPasswordEmail, setResetPasswordEmail] = useState("");

  const loadUsers = () => {
    // Load admin credentials
    const adminCreds = localStorage.getItem("adminCredentials");
    const usersList = [];

    if (adminCreds) {
      try {
        const admin = JSON.parse(adminCreds);
        usersList.push({
          email: admin.email,
          username: admin.username,
          role: "admin",
          createdAt: admin.createdAt,
        });
      } catch (e) {
        // Ignore parse errors
      }
    }

    // Load additional users (if any stored)
    const storedUsers = localStorage.getItem("users");
    if (storedUsers) {
      try {
        const parsed = JSON.parse(storedUsers);
        usersList.push(...parsed);
      } catch (e) {
        // Ignore parse errors
      }
    }

    // If no users in localStorage, use mock data
    if (usersList.length === 0) {
      const mockUsersList = mockUsers.map((user) => ({
        email: user.email,
        username: user.name,
        role: user.role.toLowerCase(),
        createdAt: new Date().toISOString(),
      }));
      usersList.push(...mockUsersList);
    }

    setUsers(usersList);
  };

  const handleAddUser = () => {
    if (!newUser.username || !newUser.email || !newUser.password) {
      toast.error("All fields are required");
      return;
    }

    // Validate email
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newUser.email)) {
      toast.error("Invalid email address");
      return;
    }

    // Validate password
    if (
      newUser.password.length < 8 ||
      !/[A-Za-z]/.test(newUser.password) ||
      !/\d/.test(newUser.password)
    ) {
      toast.error("Password must be at least 8 characters with letters and numbers");
      return;
    }

    // Check if email already exists
    if (users.some((u) => u.email === newUser.email)) {
      toast.error("User with this email already exists");
      return;
    }

    // Add new user
    const userToAdd = {
      ...newUser,
      password: btoa(newUser.password), // Base64 encoding (NOT SECURE - for demo only)
      createdAt: new Date().toISOString(),
    };

    const existingUsers = JSON.parse(localStorage.getItem("users") || "[]");
    existingUsers.push(userToAdd);
    localStorage.setItem("users", JSON.stringify(existingUsers));

    toast.success(`User ${newUser.username} added successfully`);
    setShowAddUser(false);
    setNewUser({ username: "", email: "", password: "", role: "user" });
    loadUsers();
  };

  const handleRemoveUser = (email: string) => {
    if (email === users.find((u) => u.role === "admin")?.email) {
      toast.error("Cannot remove admin user");
      return;
    }

    const existingUsers = JSON.parse(localStorage.getItem("users") || "[]");
    const filtered = existingUsers.filter((u: any) => u.email !== email);
    localStorage.setItem("users", JSON.stringify(filtered));

    toast.success("User removed successfully");
    loadUsers();
  };

  const handleResetPassword = () => {
    if (!resetPasswordEmail) {
      toast.error("Please enter an email address");
      return;
    }

    const user = users.find((u) => u.email === resetPasswordEmail);
    if (!user) {
      toast.error("User not found");
      return;
    }

    // In production, this would send a password reset email
    toast.success(
      `Password reset email would be sent to ${resetPasswordEmail}`,
      {
        description: "Implement actual email sending in production",
      }
    );
    setResetPasswordEmail("");
  };

  // Load users on mount
  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <div className="space-y-6">
      {/* Security Warning */}
      <Card className="bg-amber-900/20 border-amber-700">
        <CardHeader>
          <CardTitle className="text-amber-400 flex items-center gap-2">
            <Users className="w-5 h-5" />
            User Management
          </CardTitle>
          <CardDescription className="text-amber-300">
            This is a demo implementation using localStorage. In production, implement proper backend user management with database storage, password hashing, and authentication.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Current Users */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white">Current Users</CardTitle>
              <CardDescription>
                Manage user accounts and permissions
              </CardDescription>
            </div>
            <Button
              onClick={() => setShowAddUser(!showAddUser)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {showAddUser ? "Cancel" : "Add User"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {showAddUser && (
            <div className="mb-6 p-4 bg-slate-900 rounded-lg space-y-4">
              <h3 className="text-white font-medium">Add New User</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">Username</Label>
                  <Input
                    value={newUser.username}
                    onChange={(e) =>
                      setNewUser({ ...newUser, username: e.target.value })
                    }
                    placeholder="john_doe"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Email</Label>
                  <Input
                    type="email"
                    value={newUser.email}
                    onChange={(e) =>
                      setNewUser({ ...newUser, email: e.target.value })
                    }
                    placeholder="john@example.com"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Password</Label>
                  <Input
                    type="password"
                    value={newUser.password}
                    onChange={(e) =>
                      setNewUser({ ...newUser, password: e.target.value })
                    }
                    placeholder="Min 8 chars, letters + numbers"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Role</Label>
                  <select
                    value={newUser.role}
                    onChange={(e) =>
                      setNewUser({ ...newUser, role: e.target.value })
                    }
                    className="w-full h-10 px-3 bg-slate-800 border border-slate-600 text-white rounded-md"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>
              <Button
                onClick={handleAddUser}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                Create User
              </Button>
            </div>
          )}

          <Table>
            <TableHeader>
              <TableRow className="border-slate-700">
                <TableHead className="text-slate-300">Username</TableHead>
                <TableHead className="text-slate-300">Email</TableHead>
                <TableHead className="text-slate-300">Role</TableHead>
                <TableHead className="text-slate-300">Created</TableHead>
                <TableHead className="text-slate-300">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.length === 0 ? (
                <TableRow className="border-slate-700">
                  <TableCell colSpan={5} className="text-center text-slate-400">
                    No users found. Create an admin user at /set-admin
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user, index) => (
                  <TableRow key={index} className="border-slate-700">
                    <TableCell className="text-white">
                      {user.username}
                    </TableCell>
                    <TableCell className="text-slate-300">
                      {user.email}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={user.role === "admin" ? "default" : "secondary"}
                        className={
                          user.role === "admin"
                            ? "bg-orange-600"
                            : "bg-blue-600"
                        }
                      >
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-slate-400 text-sm">
                      {new Date(user.createdAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {user.role !== "admin" ? (
                        <Button
                          onClick={() => handleRemoveUser(user.email)}
                          variant="destructive"
                          size="sm"
                        >
                          Remove
                        </Button>
                      ) : (
                        <span className="text-slate-500 text-sm">Protected</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Reset Password */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Reset User Password</CardTitle>
          <CardDescription>
            Send password reset link to user's email
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Input
              type="email"
              value={resetPasswordEmail}
              onChange={(e) => setResetPasswordEmail(e.target.value)}
              placeholder="user@example.com"
              className="bg-slate-900 border-slate-600 text-white"
            />
            <Button
              onClick={handleResetPassword}
              className="bg-blue-600 hover:bg-blue-700 whitespace-nowrap"
            >
              Send Reset Link
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
