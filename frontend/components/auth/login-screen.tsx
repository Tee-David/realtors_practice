"use client";

import type React from "react";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Eye, EyeOff, Info } from "lucide-react";
import { toast } from "sonner";
import StatsCarouselCount from "@/components/ui/stats-carousel";
import { RevealText } from "@/components/ui/reveal-text";
import dynamic from "next/dynamic";
import { useAuth } from "@/contexts/AuthContext";

const World = dynamic(() => import("@/components/ui/globe").then((m) => m.World), {
  ssr: false,
});

interface LoginScreenProps {
  onLogin: () => void;
}

const globeConfig = {
  pointSize: 4,
  globeColor: "#1d072e",
  showAtmosphere: true,
  atmosphereColor: "#FFFFFF",
  atmosphereAltitude: 0.1,
  emissive: "#1d072e",
  emissiveIntensity: 0.1,
  shininess: 0.9,
  polygonColor: "rgba(255,255,255,0.7)",
  ambientLight: "#38bdf8",
  directionalLeftLight: "#ffffff",
  directionalTopLight: "#ffffff",
  pointLight: "#ffffff",
  arcTime: 1000,
  arcLength: 0.9,
  rings: 1,
  maxRings: 3,
  initialPosition: { lat: 6.5244, lng: 3.3792 }, // Lagos, Nigeria
  autoRotate: true,
  autoRotateSpeed: 0.5,
};

const colors = ["#06b6d4", "#3b82f6", "#6366f1"];
const sampleArcs = [
  {
    order: 1,
    startLat: 6.5244,
    startLng: 3.3792,
    endLat: 51.5074,
    endLng: -0.1278,
    arcAlt: 0.3,
    color: colors[0],
  },
  {
    order: 2,
    startLat: 6.5244,
    startLng: 3.3792,
    endLat: 40.7128,
    endLng: -74.0060,
    arcAlt: 0.3,
    color: colors[1],
  },
  {
    order: 3,
    startLat: 6.5244,
    startLng: 3.3792,
    endLat: -33.8688,
    endLng: 151.2093,
    arcAlt: 0.3,
    color: colors[2],
  },
];

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [statsData, setStatsData] = useState([
    { value: 50, suffix: "+", label: "Real Estate Sites Aggregated" },
    { value: 352, suffix: "", label: "Properties Currently Listed" },
    { value: 100, suffix: "%", label: "Lagos Coverage" },
  ]);

  const { signIn, sendPasswordReset } = useAuth();

  // Fetch real stats data from API
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

        // Fetch dashboard stats for properties count
        const dashboardRes = await fetch(`${apiUrl}/firestore/dashboard`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        // Fetch sites data for enabled sites count
        const sitesRes = await fetch(`${apiUrl}/sites`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });

        let propertiesCount = 352; // Fallback
        let sitesCount = 50; // Fallback

        if (dashboardRes.ok) {
          const dashboardData = await dashboardRes.json();
          // Extract total properties from dashboard data
          if (dashboardData?.by_listing_type) {
            propertiesCount = Object.values(dashboardData.by_listing_type).reduce(
              (sum: number, val: any) => sum + (typeof val === 'number' ? val : 0),
              0
            ) || propertiesCount;
          }
        }

        if (sitesRes.ok) {
          const sitesData = await sitesRes.json();
          if (sitesData?.enabled !== undefined) {
            sitesCount = sitesData.enabled;
          }
        }

        // Update stats with real data
        setStatsData([
          { value: sitesCount, suffix: "+", label: "Real Estate Sites Aggregated" },
          { value: propertiesCount, suffix: "", label: "Properties Currently Listed" },
          { value: 100, suffix: "%", label: "Lagos Coverage" },
        ]);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
        // Keep fallback values on error
      }
    };

    fetchStats();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!emailOrUsername || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailOrUsername)) {
      toast.error("Please enter a valid email address");
      return;
    }

    setIsLoading(true);

    try {
      // Use Firebase authentication
      const result = await signIn(emailOrUsername, password);

      if (result.success) {
        toast.success("Login successful! Welcome back.");
        onLogin();
      } else {
        toast.error(result.error || "Login failed. Please check your credentials.");
      }
    } catch (error: any) {
      console.error("Login error:", error);
      toast.error(error.message || "An error occurred during login");
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!emailOrUsername) {
      toast.error("Please enter your email address");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailOrUsername)) {
      toast.error("Please enter a valid email address");
      return;
    }

    try {
      const result = await sendPasswordReset(emailOrUsername);
      if (result.success) {
        toast.success("Password reset email sent! Check your inbox.");
      } else {
        toast.error(result.error || "Failed to send password reset email");
      }
    } catch (error: any) {
      toast.error(error.message || "An error occurred");
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-0 overflow-hidden">
      <div className="w-full h-screen flex flex-col lg:flex-row">
        {/* Left Side - Globe, Powered By, & Stats */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
          {/* Content Container */}
          <div className="relative z-10 flex flex-col items-center justify-center w-full h-full p-8 xl:p-12 gap-8">
            {/* Globe - Very Large (70%) */}
            <div className="w-full flex-1 flex items-center justify-center">
              <div className="w-full h-full">
                <World data={sampleArcs} globeConfig={globeConfig} />
              </div>
            </div>

            {/* Powered By Text */}
            <div className="text-center">
              <p className="text-xl xl:text-2xl text-blue-200 italic font-light">
                Powered by Data & Intelligence
              </p>
            </div>

            {/* Stats Carousel - Normal Size */}
            <div className="w-full max-w-md scale-75">
              <StatsCarouselCount stats={statsData} className="py-0" />
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-8 lg:p-12 bg-slate-900">
          <div className="w-full max-w-md space-y-6 sm:space-y-8">
            {/* Logo and Branding - Desktop & Mobile */}
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <img
                  src="/realtor.png"
                  alt="Realtors' Practice Logo"
                  className="w-20 h-20 sm:w-24 sm:h-24 object-contain"
                />
              </div>
              <div className="space-y-1">
                <h1 className="text-3xl sm:text-4xl font-bold text-white">
                  Realtors' Practice
                </h1>
                <p className="text-base sm:text-lg text-blue-300">
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
                    Email Address
                  </label>
                  <Input
                    id="emailOrUsername"
                    type="email"
                    value={emailOrUsername}
                    onChange={(e) => setEmailOrUsername(e.target.value)}
                    className="w-full h-11 sm:h-12 bg-slate-800 border-slate-700 text-white placeholder-slate-400 focus:border-blue-500 focus:ring-blue-500 text-sm sm:text-base"
                    placeholder="Enter your email address"
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
