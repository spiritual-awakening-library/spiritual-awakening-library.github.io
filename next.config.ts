import type { NextConfig } from "next";

/**
 * Spiritual Awakening Library — dual-mode Next.js configuration.
 *
 * - Development: `next dev` runs normally for the interactive preview.
 * - Production: `next build` performs a full static export into `out/`
 *   (GitHub Pages compatible). No runtime server features are used.
 */
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: {
    // Static export cannot use the Next.js image optimization server.
    unoptimized: true,
  },
};

export default nextConfig;
