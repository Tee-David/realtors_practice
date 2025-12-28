import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(date: string): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(date));
}

export function formatDateTime(date: string): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case "active":
    case "completed":
    case "success":
      return "bg-green-500/20 text-green-400 border border-green-500/30";
    case "inactive":
    case "failed":
      return "bg-red-500/20 text-red-400 border border-red-500/30";
    case "running":
      return "bg-blue-500/20 text-blue-400 border border-blue-500/30";
    default:
      return "bg-gray-500/20 text-gray-400 border border-gray-500/30";
  }
}

export function getRoleColor(role: string): string {
  switch (role.toLowerCase()) {
    case "admin":
      return "bg-purple-500/20 text-purple-400 border border-purple-500/30";
    case "editor":
      return "bg-blue-500/20 text-blue-400 border border-blue-500/30";
    case "viewer":
      return "bg-slate-500/20 text-slate-400 border border-slate-500/30";
    default:
      return "bg-gray-500/20 text-gray-400 border border-gray-500/30";
  }
}

export const getPageTitle = (tab: string) => {
  switch (tab) {
    case "dashboard":
      return "Dashboard";
    case "data":
      return "Data Explorer";
    case "scraper":
      return "Scraper Control";
    case "users":
      return "User Management";
    default:
      return "Dashboard";
  }
};

export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
