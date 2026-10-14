import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@neurogenesis/contracts"],
};

export default nextConfig;
