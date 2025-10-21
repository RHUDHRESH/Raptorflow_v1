/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Use standalone output for Cloud Run deployment
  output: 'standalone',
  // Enable experimental serverComponentsExternalPackages if needed
  experimental: {
    serverComponentsExternalPackages: [],
  },
  images: {
    domains: [],
    remotePatterns: [],
  },
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig;
