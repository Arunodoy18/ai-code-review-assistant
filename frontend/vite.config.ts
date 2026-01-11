import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const buildTime = process.env.BUILD_TIME || Date.now().toString();
  
  return {
    plugins: [react()],
    server: {
      host: true,
      port: 5173,
      watch: {
        usePolling: true
      }
    },
    build: {
      sourcemap: mode === 'production' ? false : true,  // No sourcemaps in production
      rollupOptions: {
        output: {
          // Use BUILD_TIME env var for cache busting (set during Docker build)
          entryFileNames: `assets/[name]-[hash]-${buildTime}.js`,
          chunkFileNames: `assets/[name]-[hash]-${buildTime}.js`,
          assetFileNames: `assets/[name]-[hash]-${buildTime}.[ext]`
        }
      },
      // Production optimizations
      minify: mode === 'production' ? 'esbuild' : false,
      chunkSizeWarningLimit: 1000,
    },
    // Define global constants
    define: {
      __BUILD_TIME__: JSON.stringify(buildTime),
    },
  };
});
