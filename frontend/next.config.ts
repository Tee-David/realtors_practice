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
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.naijalandlord.com',
      },
      {
        protocol: 'https',
        hostname: '**.propertypro.ng',
      },
      {
        protocol: 'https',
        hostname: '**.jiji.ng',
      },
      {
        protocol: 'https',
        hostname: '**.npc.ng',
      },
      {
        protocol: 'https',
        hostname: '**.cwlagos.com',
      },
      // Wildcard to allow all HTTPS images (broader approach)
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  /* any other config you already had */
};

export default nextConfig;
