"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";

export function NotificationsAlerts() {
  const [emailConfig, setEmailConfig] = useState("");
  const [webhookConfig, setWebhookConfig] = useState("");

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-4 sm:p-6 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-white">
          Notifications & Alerts
        </h3>
      </div>

      <div className="p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Email Configuration
          </label>
          <Input
            type="email"
            placeholder="Enter email for notifications"
            value={emailConfig}
            onChange={(e) => setEmailConfig(e.target.value)}
            className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Webhook Configuration
          </label>
          <Input
            type="url"
            placeholder="Enter webhook URL"
            value={webhookConfig}
            onChange={(e) => setWebhookConfig(e.target.value)}
            className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
          />
        </div>
      </div>
    </div>
  );
}
