import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Don't rewrite the path - keep /api prefix
      },
    },
  },
  // Ensure SPA routing works - all routes fallback to index.html
  appType: 'spa',
  historyApiFallback: {
    rewrites: [
      { from: /\/listings.*/, to: '/index.html' }
    ]
  }
});
