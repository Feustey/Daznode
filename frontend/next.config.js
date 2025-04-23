/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/network/:path*',
        destination: 'http://localhost:8000/api/v1/network/:path*',
      },
      {
        source: '/node/:path*',
        destination: 'http://localhost:8000/api/v1/node/:path*',
      }
    ];
  },
};

module.exports = nextConfig;
