"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Eye, EyeOff, Shield, CheckCircle2, AlertCircle } from "lucide-react";
import { toast } from "sonner";

export default function SetAdminPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [adminCreated, setAdminCreated] = useState(false);

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validatePassword = (password: string) => {
    // Minimum 8 characters, at least one letter and one number
    return password.length >= 8 && /[A-Za-z]/.test(password) && /\d/.test(password);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!username || !email || !password || !confirmPassword) {
      toast.error("All fields are required");
      return;
    }

    if (!validateEmail(email)) {
      toast.error("Please enter a valid email address");
      return;
    }

    if (!validatePassword(password)) {
      toast.error("Password must be at least 8 characters with letters and numbers");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setIsCreating(true);

    try {
      // TODO: Replace with actual API call to create admin
      // For now, store in localStorage (NOT SECURE - for demo only)
      const adminCredentials = {
        username,
        email,
        password: btoa(password), // Base64 encoding (NOT SECURE - just for demo)
        createdAt: new Date().toISOString(),
      };

      localStorage.setItem("adminCredentials", JSON.stringify(adminCredentials));

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      toast.success("Admin account created successfully!", {
        description: "You can now use these credentials to log in",
      });

      setAdminCreated(true);

      // Clear form
      setUsername("");
      setEmail("");
      setPassword("");
      setConfirmPassword("");
    } catch (error: any) {
      toast.error("Failed to create admin account", {
        description: error.message || "Please try again",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleReset = () => {
    setUsername("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setAdminCreated(false);
  };

  if (adminCreated) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-slate-800 border-slate-700">
          <CardContent className="pt-12 pb-8 text-center space-y-6">
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center">
                <CheckCircle2 className="w-10 h-10 text-green-400" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-white">Admin Created!</h2>
              <p className="text-slate-400">
                Your admin account has been created successfully. You can now use these credentials to log in to the dashboard.
              </p>
            </div>
            <div className="space-y-3">
              <Button
                onClick={() => (window.location.href = "/")}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                Go to Login
              </Button>
              <Button
                variant="outline"
                onClick={handleReset}
                className="w-full border-slate-600 hover:bg-slate-700"
              >
                Create Another Admin
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 sm:p-6">
      <Card className="w-full max-w-lg bg-slate-800 border-slate-700">
        <CardHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-blue-400" />
            </div>
            <CardTitle className="text-2xl text-white">Create Admin Account</CardTitle>
          </div>
          <p className="text-sm text-slate-400">
            Set up administrator credentials to access the platform
          </p>
        </CardHeader>

        <CardContent>
          {/* Security Warning */}
          <div className="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="text-amber-300 font-medium">Security Notice</p>
              <p className="text-amber-200/80 mt-1">
                This page should be secured and only accessible during initial setup. In production, implement proper authentication backend.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div className="space-y-2">
              <Label htmlFor="username" className="text-slate-300">
                Username *
              </Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter admin username"
                className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                disabled={isCreating}
                required
              />
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-300">
                Email Address *
              </Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@example.com"
                className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
                disabled={isCreating}
                required
              />
            </div>

            {/* Password */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-300">
                Password *
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 8 characters"
                  className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500 pr-12"
                  disabled={isCreating}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                  disabled={isCreating}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              <p className="text-xs text-slate-500">
                Must be at least 8 characters with letters and numbers
              </p>
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-slate-300">
                Confirm Password *
              </Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500 pr-12"
                  disabled={isCreating}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                  disabled={isCreating}
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isCreating}
              className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-medium"
            >
              {isCreating ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Creating Admin...</span>
                </div>
              ) : (
                <>
                  <Shield className="w-5 h-5 mr-2" />
                  Create Admin Account
                </>
              )}
            </Button>

            {/* Cancel Button */}
            <Button
              type="button"
              variant="outline"
              onClick={() => (window.location.href = "/")}
              disabled={isCreating}
              className="w-full border-slate-600 hover:bg-slate-700"
            >
              Cancel
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
