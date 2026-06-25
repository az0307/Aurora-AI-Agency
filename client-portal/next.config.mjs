/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { hostname: 'uploadthing.com' },
      { hostname: 'utfs.io' },
      { hostname: 'img.clerk.com' },
      { hostname: 'subdomain' },
    ],
  },
}

export default nextConfig
