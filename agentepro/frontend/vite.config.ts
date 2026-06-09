/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// En Docker el backend es accesible como http://backend:8000; en local, localhost.
const proxyTarget = process.env.VITE_PROXY_TARGET ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': proxyTarget,
      '/webhooks': proxyTarget,
      '/socket.io': {
        target: proxyTarget,
        ws: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      reportsDirectory: 'coverage',
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/main.tsx',
        'src/App.tsx',
        'src/router.tsx',
        'src/vite-env.d.ts',
        'src/**/*.d.ts',
        'src/pages/**',
        'src/components/common/AnimatedBackground.tsx',
        'src/components/landing/ParticleField.tsx',
        'src/**/*.test.{ts,tsx}',
        'src/test/**',
        '**/*.config.*',
      ],
    },
  },
})
