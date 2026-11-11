/** @type {import('next').NextConfig} */
const apiBase = process.env.NEXT_PUBLIC_API_INTERNAL || "http://127.0.0.1:8000";

const nextConfig = {
  reactStrictMode: true,
  experimental: { proxyTimeout: 300000 },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: apiBase + "/api/:path*" },
      { source: "/samples/:path*", destination: apiBase + "/samples/:path*" },
    ];
  },
};
module.exports = nextConfig;