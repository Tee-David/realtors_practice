"use client";

import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  loading?: boolean;
  variant?: "default" | "success" | "warning" | "danger" | "info";
  trend?: {
    value: number;
    label: string;
  };
  description?: string;
}

const variantStyles = {
  default: "bg-slate-800 border-slate-700",
  success: "bg-green-500/10 border-green-500/20",
  warning: "bg-yellow-500/10 border-yellow-500/20",
  danger: "bg-red-500/10 border-red-500/20",
  info: "bg-blue-500/10 border-blue-500/20",
};

const iconVariantStyles = {
  default: "text-slate-400",
  success: "text-green-400",
  warning: "text-yellow-400",
  danger: "text-red-400",
  info: "text-blue-400",
};

export function StatsCard({
  title,
  value,
  icon: Icon,
  loading = false,
  variant = "default",
  trend,
  description,
}: StatsCardProps) {
  if (loading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-6">
          <Skeleton className="h-4 w-24 mb-4" />
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-3 w-20" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        "border transition-all hover:scale-[1.02]",
        variantStyles[variant]
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <Icon className={cn("w-5 h-5", iconVariantStyles[variant])} />
        </div>

        <div className="space-y-1">
          <h3 className="text-3xl font-bold text-white">{value}</h3>

          {trend && (
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "text-sm font-medium",
                  trend.value > 0
                    ? "text-green-400"
                    : trend.value < 0
                    ? "text-red-400"
                    : "text-slate-400"
                )}
              >
                {trend.value > 0 ? "+" : ""}
                {trend.value}%
              </span>
              <span className="text-xs text-slate-500">{trend.label}</span>
            </div>
          )}

          {description && (
            <p className="text-xs text-slate-500 mt-2">{description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
