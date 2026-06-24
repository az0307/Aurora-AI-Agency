import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  // B3.3 — set VITE_BASE='/<repo>/' for project Pages; '/' for user/org Pages or a real host
  base: process.env.VITE_BASE || '/',
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  },
  server: {
    port: 3000,
    host: true
  }
})
