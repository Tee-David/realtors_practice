import type React from "react";
import type { Metadata } from "next";
import { Red_Hat_Display } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";

const redHatDisplay = Red_Hat_Display({
  subsets: ["latin"],
  variable: "--font-red-hat",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Property Insights - Real Estate Scraper",
  description: "Professional real estate data scraping and management platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${redHatDisplay.variable} antialiased`} suppressHydrationWarning>
      <body suppressHydrationWarning className="font-sans bg-slate-900 text-white min-h-screen">
        {children}
        <Toaster position="top-right" theme="dark" />
      </body>
    </html>
  );
}
