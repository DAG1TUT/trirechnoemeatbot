import type { NextConfig } from "next";

const wpUrl = process.env.WORDPRESS_URL;

// Extract hostname from WP URL for next/image optimization.
let wpHostname: string | null = null;
if (wpUrl) {
  try {
    wpHostname = new URL(wpUrl).hostname;
  } catch {
    // malformed URL — ignore, images will be unoptimized
  }
}

const nextConfig: NextConfig = {
  // Standalone output bundles only the files needed to run the app —
  // required for optimal Docker / Railway deployment.
  output: "standalone",

  images: {
    remotePatterns: wpHostname
      ? [
          // Support both http (local Docker) and https (production)
          { protocol: "http",  hostname: wpHostname },
          { protocol: "https", hostname: wpHostname },
        ]
      : [],
    unoptimized: !wpHostname,
  },
};

export default nextConfig;
