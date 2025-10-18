/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:7863',
  },
  async rewrites() {
    return [
      {
        source: '/api/research/:path*',
        destination: `${process.env.BACKEND_URL || 'http://localhost:7863'}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
