import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  sassOptions: {
    includePaths: ["./styles"],
  },
  experimental: {
    optimizePackageImports: ["gsap", "@react-three/drei", "@react-three/fiber"],
  },
};

export default nextConfig;
