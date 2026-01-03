"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Save, Bell, BellOff } from "lucide-react";
import { toast } from "sonner";

export function NotificationsAlerts() {
  const [emailConfig, setEmailConfig] = useState("");
  const [webhookConfig, setWebhookConfig] = useState("");
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [webhookEnabled, setWebhookEnabled] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveNotifications = async () => {
    if (!emailConfig && !webhookConfig) {
      toast.error("Please enter at least one notification method");
      return;
    }

    setIsSaving(true);
    try {
      // TODO: Replace with actual API call when backend endpoint is available
      // await fetch('/api/notifications/config', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email: emailConfig, webhook: webhookConfig })
      // });

      // Simulated API call
      await new Promise(resolve => setTimeout(resolve, 500));

      toast.success("Notification settings saved successfully!");
    } catch (error) {
      console.error("Error saving notifications:", error);
      toast.error("Failed to save notification settings");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-4 sm:p-6 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-white">
          Notifications & Alerts
        </h3>
      </div>

      <div className="p-4 sm:p-6 space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-slate-300">
                Email Configuration
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setEmailEnabled(!emailEnabled)}
                className={`h-8 px-2 ${emailEnabled ? 'text-green-400' : 'text-slate-400'}`}
              >
                {emailEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
                <span className="ml-1 text-xs">{emailEnabled ? 'Enabled' : 'Disabled'}</span>
              </Button>
            </div>
            <Input
              type="email"
              placeholder="Enter email for notifications"
              value={emailConfig}
              onChange={(e) => setEmailConfig(e.target.value)}
              className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
              disabled={!emailEnabled}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-slate-300">
                Webhook Configuration
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setWebhookEnabled(!webhookEnabled)}
                className={`h-8 px-2 ${webhookEnabled ? 'text-green-400' : 'text-slate-400'}`}
              >
                {webhookEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
                <span className="ml-1 text-xs">{webhookEnabled ? 'Enabled' : 'Disabled'}</span>
              </Button>
            </div>
            <Input
              type="url"
              placeholder="Enter webhook URL"
              value={webhookConfig}
              onChange={(e) => setWebhookConfig(e.target.value)}
              className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
              disabled={!webhookEnabled}
            />
          </div>
        </div>

        <div className="flex justify-end">
          <Button
            onClick={handleSaveNotifications}
            disabled={isSaving || (!emailEnabled && !webhookEnabled)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Save className="w-4 h-4 mr-2" />
            {isSaving ? "Saving..." : "Save Notification Settings"}
          </Button>
        </div>
      </div>
    </div>
  );
}
