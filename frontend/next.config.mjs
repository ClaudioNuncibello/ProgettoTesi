/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configurazioni per evitare blocchi di contenuto
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
  // Headers di sicurezza più permissivi per sviluppo
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
}

export default nextConfig
