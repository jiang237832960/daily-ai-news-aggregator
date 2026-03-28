/** @type {import('next').NextConfig} */
const nextConfig = {
  server: {
    allowedHosts: ['.monkeycode-ai.online']
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
