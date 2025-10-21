import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Scraper Dashboard",
  description: "Control panel for real estate scraper",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-gray-50 text-gray-900`}>
        <div className="min-h-screen grid grid-rows-[auto_1fr]">
          <header className="border-b bg-white">
            <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
              <h1 className="text-lg font-semibold">Scraper Dashboard</h1>
              <nav className="flex items-center gap-4 text-sm text-gray-600">
                <a href="/" className="hover:text-black">Overview</a>
                <a href="/scrape" className="hover:text-black">Scrape</a>
                <a href="/sites" className="hover:text-black">Sites</a>
                <a href="/data" className="hover:text-black">Data</a>
                <a href="/logs" className="hover:text-black">Logs</a>
                <a href="/settings" className="hover:text-black">Settings</a>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl w-full px-4 py-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
