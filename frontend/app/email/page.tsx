"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { EmailConfig, EmailRecipient } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  RefreshCw,
  Mail,
  UserPlus,
  Trash2,
  Send,
  CheckCircle,
} from "lucide-react";
import { toast } from "sonner";

export default function EmailPage() {
  const [config, setConfig] = useState<EmailConfig | null>(null);
  const [recipients, setRecipients] = useState<EmailRecipient[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newRecipientEmail, setNewRecipientEmail] = useState("");
  const [testingConnection, setTestingConnection] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);

  const fetchEmailData = () => {
    setLoading(true);
    Promise.all([apiClient.getEmailConfig(), apiClient.listEmailRecipients()])
      .then(([cfg, recs]) => {
        setConfig(cfg);
        setRecipients(recs);
      })
      .catch((err: any) =>
        setError(err?.message || "Error fetching email data")
      )
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEmailData();
  }, []);

  const handleAddRecipient = async () => {
    if (!newRecipientEmail || !newRecipientEmail.includes("@")) {
      toast.error("Please enter a valid email address");
      return;
    }

    try {
      await apiClient.addEmailRecipient({
        email: newRecipientEmail,
        name: "",
        alerts_enabled: true,
        alert_types: [],
      });
      toast.success("Recipient added successfully");
      setNewRecipientEmail("");
      fetchEmailData();
    } catch (err: any) {
      toast.error(err?.message || "Failed to add recipient");
    }
  };

  const handleRemoveRecipient = async (email: string) => {
    try {
      await apiClient.removeEmailRecipient(email);
      toast.success("Recipient removed");
      fetchEmailData();
    } catch (err: any) {
      toast.error(err?.message || "Failed to remove recipient");
    }
  };

  const handleTestConnection = async () => {
    if (!config) return;
    setTestingConnection(true);
    try {
      const result = await apiClient.testEmailConnection(config);
      if (result.success) {
        toast.success("Connection successful!");
      } else {
        toast.error(result.error || "Connection failed");
      }
    } catch (err: any) {
      toast.error(err?.message || "Connection test failed");
    } finally {
      setTestingConnection(false);
    }
  };

  const handleSendTestEmail = async () => {
    if (recipients.length === 0) {
      toast.error("Please add at least one recipient first");
      return;
    }
    setSendingTest(true);
    try {
      await apiClient.sendTestEmail(recipients[0].email);
      toast.success("Test email sent successfully!");
    } catch (err: any) {
      toast.error(err?.message || "Failed to send test email");
    } finally {
      setSendingTest(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Email Configuration</h1>
          <p className="text-slate-400 mt-1">
            SMTP settings and alert recipients
          </p>
        </div>
        <Button
          onClick={fetchEmailData}
          disabled={loading}
          variant="outline"
          size="sm"
        >
          <RefreshCw
            className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* SMTP Configuration */}
      {config && (
        <div className="bg-slate-800 rounded-lg p-6 space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Mail className="w-5 h-5" />
              SMTP Settings
            </h2>
            <div className="flex gap-2">
              <Button
                onClick={handleTestConnection}
                disabled={testingConnection}
                variant="outline"
                size="sm"
              >
                {testingConnection ? (
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <CheckCircle className="w-4 h-4 mr-2" />
                )}
                Test Connection
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-slate-400">SMTP Host</div>
              <div className="text-white font-medium">{config.smtp_host}</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">SMTP Port</div>
              <div className="text-white font-medium">{config.smtp_port}</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">SMTP User</div>
              <div className="text-white font-medium">{config.smtp_user}</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">Use TLS</div>
              <div className="text-white font-medium">
                {config.use_tls ? "Yes" : "No"}
              </div>
            </div>
            <div>
              <div className="text-sm text-slate-400">From Email</div>
              <div className="text-white font-medium">{config.from_email}</div>
            </div>
            {config.from_name && (
              <div>
                <div className="text-sm text-slate-400">From Name</div>
                <div className="text-white font-medium">{config.from_name}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recipients Management */}
      <div className="bg-slate-800 rounded-lg p-6 space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <UserPlus className="w-5 h-5" />
            Email Recipients ({recipients.length})
          </h2>
          <Button
            onClick={handleSendTestEmail}
            disabled={sendingTest || recipients.length === 0}
            variant="outline"
            size="sm"
          >
            {sendingTest ? (
              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Send className="w-4 h-4 mr-2" />
            )}
            Send Test Email
          </Button>
        </div>

        {/* Add Recipient */}
        <div className="flex gap-2">
          <Input
            type="email"
            placeholder="email@example.com"
            value={newRecipientEmail}
            onChange={(e) => setNewRecipientEmail(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleAddRecipient()}
            className="flex-1 bg-slate-900 border-slate-700 text-white"
          />
          <Button onClick={handleAddRecipient}>Add Recipient</Button>
        </div>

        {/* Recipients List */}
        {recipients.length > 0 ? (
          <div className="space-y-2 mt-4">
            {recipients.map((r) => (
              <div
                key={r.email}
                className="flex items-center justify-between bg-slate-900 rounded-lg p-4"
              >
                <div>
                  <div className="text-white font-medium">{r.email}</div>
                  {r.name && (
                    <div className="text-sm text-slate-400">{r.name}</div>
                  )}
                  <div className="text-xs text-slate-500 mt-1">
                    Alerts: {r.alerts_enabled ? "Enabled" : "Disabled"}
                    {r.alert_types?.length > 0 &&
                      ` • ${r.alert_types.join(", ")}`}
                  </div>
                </div>
                <Button
                  onClick={() => handleRemoveRecipient(r.email)}
                  variant="ghost"
                  size="sm"
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-slate-400 py-8">
            No recipients added yet
          </div>
        )}
      </div>
    </div>
  );
}
