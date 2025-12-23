import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    // !! Danger zone – no type checking at build time
    ignoreBuildErrors: true,
  },
  eslint: {
    // !! Danger zone – no ESLint during build
    ignoreDuringBuilds: true,
  },
  /* any other config you already had */
};

export default nextConfig;
