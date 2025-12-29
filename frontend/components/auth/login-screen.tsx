"use client";

import type React from "react";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Eye, EyeOff, Info, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { TypewriterEffect } from "@/components/ui/typewriter-effect";
import { Globe } from "@/components/ui/globe";

interface LoginScreenProps {
  onLogin: () => void;
}

const powerfulFeatures = [
  { text: "Aggregate Unlimited Real Estate Sites", className: "text-blue-400 font-bold" },
  { text: "Smart Property Search & Filtering", className: "text-green-400 font-bold" },
  { text: "Advanced Data Analytics & Insights", className: "text-purple-400 font-bold" },
  { text: "Real-Time Price Tracking", className: "text-yellow-400 font-bold" },
  { text: "Location-Based Market Intelligence", className: "text-pink-400 font-bold" },
  { text: "Automated Property Scraping", className: "text-cyan-400 font-bold" },
  { text: "Export to CSV, Excel & JSON", className: "text-orange-400 font-bold" },
  { text: "Save & Track Favorite Searches", className: "text-indigo-400 font-bold" },
  { text: "Email Alerts for New Listings", className: "text-red-400 font-bold" },
  { text: "Property Quality Scoring", className: "text-teal-400 font-bold" },
  { text: "Interactive Data Visualization", className: "text-lime-400 font-bold" },
  { text: "Comprehensive Market Trends", className: "text-fuchsia-400 font-bold" },
];

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!emailOrUsername || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    setIsLoading(true);

    // Check credentials from localStorage
    // First check admin credentials
    const adminCreds = localStorage.getItem("adminCredentials");
    if (adminCreds) {
      try {
        const admin = JSON.parse(adminCreds);
        const storedPassword = atob(admin.password); // Decode base64

        // Check if input matches email or username
        if (
          (emailOrUsername === admin.email || emailOrUsername === admin.username) &&
          password === storedPassword
        ) {
          setTimeout(() => {
            setIsLoading(false);
            toast.success(`Welcome back, ${admin.username}!`);
            localStorage.setItem("isAuthenticated", "true");
            onLogin();
          }, 1500);
          return;
        }
      } catch (e) {
        // Ignore parse errors
      }
    }

    // Check other users
    const users = localStorage.getItem("users");
    if (users) {
      try {
        const userList = JSON.parse(users);
        const user = userList.find(
          (u: any) => u.email === emailOrUsername || u.username === emailOrUsername
        );

        if (user) {
          const storedPassword = atob(user.password); // Decode base64
          if (password === storedPassword) {
            setTimeout(() => {
              setIsLoading(false);
              toast.success(`Welcome back, ${user.username}!`);
              localStorage.setItem("isAuthenticated", "true");
              onLogin();
            }, 1500);
            return;
          }
        }
      } catch (e) {
        // Ignore parse errors
      }
    }

    // If we get here, credentials are invalid
    setTimeout(() => {
      setIsLoading(false);
      toast.error("Invalid email/username or password");
    }, 1500);
  };

  const handleForgotPassword = () => {
    toast.info("Password reset link sent to your email");
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-0 overflow-hidden">
      <div className="w-full h-screen flex flex-col lg:flex-row">
        {/* Left Side - Globe & Branding */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
          {/* Globe Background */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-full h-full">
              <Globe className="w-full h-full" />
            </div>
          </div>

          {/* Content Overlay */}
          <div className="relative z-10 flex flex-col items-center justify-center w-full p-12 text-center">
            <div className="mb-8 bg-slate-900/80 backdrop-blur-md rounded-3xl p-8 border border-slate-700/50">
              <div className="inline-block mb-6">
                <img
                  src="/realtor.png"
                  alt="Realtors' Practice Logo"
                  className="w-24 h-24 object-contain"
                />
              </div>
              <h1 className="text-5xl font-bold text-white mb-4">
                Realtors' Practice
              </h1>
              <p className="text-xl text-blue-300 mb-8">
                Property Aggregation Platform
              </p>

              <div className="space-y-4 max-w-lg">
                <div className="flex items-center justify-center gap-2">
                  <Sparkles className="w-5 h-5 text-yellow-400" />
                  <span className="text-slate-300 text-lg">Powered by</span>
                </div>
                <div className="h-16 flex items-center justify-center">
                  <TypewriterEffect words={powerfulFeatures} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-8 lg:p-12 bg-slate-900">
          <div className="w-full max-w-md space-y-6 sm:space-y-8">
            {/* Mobile Logo (only shown on mobile) */}
            <div className="lg:hidden text-center space-y-3 sm:space-y-4">
              <div className="flex justify-center">
                <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl flex items-center justify-center">
                  <img
                    src="/realtor.png"
                    alt="Realtors' Practice Logo"
                    className="w-full h-full object-contain"
                  />
                </div>
              </div>
              <div className="space-y-1 sm:space-y-2">
                <h1 className="text-2xl sm:text-3xl font-bold text-white">
                  Realtors' Practice
                </h1>
                <p className="text-sm sm:text-base text-slate-400 px-4 sm:px-0">
                  Property Aggregation Platform
                </p>
              </div>
            </div>

            {/* Welcome Text */}
            <div className="text-center lg:text-left space-y-2">
              <h2 className="text-2xl sm:text-3xl font-bold text-white">
                Welcome Back
              </h2>
              <p className="text-sm sm:text-base text-slate-400">
                Please log in to your account to continue
              </p>
            </div>

            {/* Info Banner */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 sm:p-4">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-blue-300 font-medium">
                    First Load Notice
                  </p>
                  <p className="text-xs text-blue-200/80 mt-1">
                    After logging in, the dashboard may take 30-60 seconds to load
                    while our server wakes up. Please be patient on your first
                    visit.
                  </p>
                </div>
              </div>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-5 sm:space-y-6">
              <div className="space-y-4 sm:space-y-5">
                <div>
                  <label
                    htmlFor="emailOrUsername"
                    className="block text-sm font-medium text-slate-300 mb-1.5 sm:mb-2"
                  >
                    Email or Username
                  </label>
                  <Input
                    id="emailOrUsername"
                    type="text"
                    value={emailOrUsername}
                    onChange={(e) => setEmailOrUsername(e.target.value)}
                    className="w-full h-11 sm:h-12 bg-slate-800 border-slate-700 text-white placeholder-slate-400 focus:border-blue-500 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="Enter your email or username"
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-slate-300 mb-1.5 sm:mb-2"
                  >
                    Password
                  </label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full h-11 sm:h-12 bg-slate-800 border-slate-700 text-white placeholder-slate-400 focus:border-blue-500 focus:ring-blue-500 pr-10 sm:pr-12 text-sm sm:text-base"
                      placeholder="Enter your password"
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 sm:right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors"
                      disabled={isLoading}
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4 sm:w-5 sm:h-5" />
                      ) : (
                        <Eye className="w-4 h-4 sm:w-5 sm:h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Remember Me and Forgot Password */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="remember"
                    checked={rememberMe}
                    onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                    disabled={isLoading}
                  />
                  <label
                    htmlFor="remember"
                    className="text-xs sm:text-sm text-slate-300 cursor-pointer"
                  >
                    Remember me
                  </label>
                </div>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-xs sm:text-sm text-blue-400 hover:text-blue-300 transition-colors"
                  disabled={isLoading}
                >
                  Forgot your password?
                </button>
              </div>

              {/* Login Button */}
              <Button
                type="submit"
                className="w-full h-11 sm:h-12 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Logging in...</span>
                  </div>
                ) : (
                  "Log in"
                )}
              </Button>

            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
