"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Info, Save, Mail, AlertTriangle, RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface EnvVariable {
  key: string;
  value: any;
  type: "text" | "number" | "boolean" | "password" | "select";
  description: string;
  options?: string[];
  requiresRestart?: boolean;
  critical?: boolean;
}

interface EnvSectionProps {
  title: string;
  description: string;
  variables: EnvVariable[];
  onSave: (changes: Record<string, any>) => Promise<void>;
  onTestEmail?: () => Promise<void>;
  showTestEmail?: boolean;
}

export function EnvSection({
  title,
  description,
  variables,
  onSave,
  onTestEmail,
  showTestEmail = false,
}: EnvSectionProps) {
  const [changes, setChanges] = useState<Record<string, any>>({});
  const [saving, setSaving] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [testing, setTesting] = useState(false);

  const handleChange = (key: string, value: any) => {
    setChanges((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const getCurrentValue = (envVar: EnvVariable) => {
    return changes[envVar.key] !== undefined ? changes[envVar.key] : envVar.value;
  };

  const hasChanges = Object.keys(changes).length > 0;
  const hasCriticalChanges = Object.keys(changes).some((key) => {
    const envVar = variables.find((v) => v.key === key);
    return envVar?.critical;
  });
  const requiresRestart = Object.keys(changes).some((key) => {
    const envVar = variables.find((v) => v.key === key);
    return envVar?.requiresRestart;
  });

  const handleSave = async () => {
    if (!hasChanges) {
      toast.info("No changes to save");
      return;
    }

    // Show confirmation for critical changes
    if (hasCriticalChanges) {
      setShowConfirmDialog(true);
      return;
    }

    await performSave();
  };

  const performSave = async () => {
    try {
      setSaving(true);
      await onSave(changes);

      if (requiresRestart) {
        toast.warning("Changes saved! Server restart required", {
          description: "Some changes require a server restart to take effect",
          duration: 5000,
        });
      } else {
        toast.success("Changes saved successfully!");
      }

      setChanges({});
      setShowConfirmDialog(false);
    } catch (error: any) {
      toast.error(error.message || "Failed to save changes");
    } finally {
      setSaving(false);
    }
  };

  const handleTestEmail = async () => {
    if (!onTestEmail) return;

    try {
      setTesting(true);
      await onTestEmail();
    } finally {
      setTesting(false);
    }
  };

  const renderInput = (envVar: EnvVariable) => {
    const currentValue = getCurrentValue(envVar);

    switch (envVar.type) {
      case "boolean":
        return (
          <div className="flex items-center justify-between">
            <Switch
              checked={currentValue}
              onCheckedChange={(checked) => handleChange(envVar.key, checked)}
            />
            <span className="text-sm text-slate-400">
              {currentValue ? "Enabled" : "Disabled"}
            </span>
          </div>
        );

      case "number":
        return (
          <Input
            type="number"
            value={currentValue}
            onChange={(e) => handleChange(envVar.key, Number(e.target.value))}
            className="bg-slate-900 border-slate-600 text-white"
          />
        );

      case "select":
        return (
          <select
            value={currentValue}
            onChange={(e) => handleChange(envVar.key, e.target.value)}
            className="w-full h-10 px-3 bg-slate-900 border border-slate-600 text-white rounded-md"
          >
            {envVar.options?.map((option) => (
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
            onChange={(e) => handleChange(envVar.key, e.target.value)}
            className="bg-slate-900 border-slate-600 text-white"
            placeholder="••••••••"
          />
        );

      default:
        return (
          <Input
            type="text"
            value={currentValue}
            onChange={(e) => handleChange(envVar.key, e.target.value)}
            className="bg-slate-900 border-slate-600 text-white"
          />
        );
    }
  };

  return (
    <>
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <CardTitle className="text-white">{title}</CardTitle>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <Info className="w-4 h-4 text-slate-400" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-sm">
                      <p>{description}</p>
                      {variables.some((v) => v.requiresRestart) && (
                        <p className="mt-2 text-yellow-400 text-xs">
                          ⚠️ Some settings require server restart
                        </p>
                      )}
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <CardDescription className="text-slate-400 mt-1">
                {description}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {showTestEmail && onTestEmail && (
                <Button
                  onClick={handleTestEmail}
                  disabled={testing}
                  size="sm"
                  variant="outline"
                  className="border-slate-600 hover:bg-slate-700"
                >
                  <Mail className="w-4 h-4 mr-2" />
                  {testing ? "Sending..." : "Test Email"}
                </Button>
              )}
              <Button
                onClick={handleSave}
                disabled={!hasChanges || saving}
                size="sm"
                className="bg-green-600 hover:bg-green-700"
              >
                <Save className="w-4 h-4 mr-2" />
                {saving ? "Saving..." : "Save"}
                {hasChanges && (
                  <Badge className="ml-2 bg-orange-600 text-xs">
                    {Object.keys(changes).length}
                  </Badge>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {variables.map((envVar) => (
              <div
                key={envVar.key}
                className="p-4 bg-slate-900 rounded-lg border border-slate-700 space-y-2"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Label className="text-slate-300 font-medium">
                        {envVar.key}
                      </Label>
                      {envVar.requiresRestart && (
                        <Badge variant="outline" className="text-xs border-yellow-600 text-yellow-400">
                          <RefreshCw className="w-3 h-3 mr-1" />
                          Restart
                        </Badge>
                      )}
                      {envVar.critical && (
                        <Badge variant="outline" className="text-xs border-red-600 text-red-400">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Critical
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {envVar.description}
                    </p>
                  </div>
                  {changes[envVar.key] !== undefined && (
                    <Badge className="bg-orange-600 text-xs ml-2 flex-shrink-0">
                      Modified
                    </Badge>
                  )}
                </div>
                <div className="mt-2">{renderInput(envVar)}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Confirmation Dialog for Critical Changes */}
      <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <AlertDialogContent className="bg-slate-800 border-slate-700">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              Confirm Critical Changes
            </AlertDialogTitle>
            <AlertDialogDescription className="text-slate-300">
              You are about to modify critical system settings. This could affect your application's behavior or stability.
              {requiresRestart && (
                <p className="mt-2 text-yellow-400">
                  ⚠️ A server restart will be required for these changes to take effect.
                </p>
              )}
              <div className="mt-4 space-y-2">
                <p className="font-medium">Changes to be applied:</p>
                <ul className="list-disc list-inside text-sm">
                  {Object.keys(changes).map((key) => {
                    const envVar = variables.find((v) => v.key === key);
                    return (
                      <li key={key}>
                        <span className="font-mono text-blue-400">{key}</span>
                        {envVar?.critical && (
                          <Badge className="ml-2 bg-red-600 text-xs">Critical</Badge>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-slate-700 hover:bg-slate-600">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={performSave}
              className="bg-green-600 hover:bg-green-700"
            >
              Confirm & Save
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
