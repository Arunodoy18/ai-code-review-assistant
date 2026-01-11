/**
 * Runtime configuration loader for the frontend.
 * Centralizes environment variable detection with fallback logic
 * to ensure production stability even when env vars are missing.
 */

interface RuntimeConfig {
  API_URL: string;
  ENVIRONMENT: 'development' | 'production' | 'test';
  VERSION: string;
  IS_PRODUCTION: boolean;
}

// Hardcoded production fallback (from Azure deployment config)
const PRODUCTION_BACKEND_URL = 'https://codereview-backend.jollysea-c5c0b121.centralus.azurecontainerapps.io';

const getApiUrl = (): string => {
  // 1. Check window.__RUNTIME_CONFIG__ (set by Docker/CI in index.html)
  if ((window as any).__RUNTIME_CONFIG__?.API_URL) {
    return (window as any).__RUNTIME_CONFIG__.API_URL;
  }

  // 2. Check Vite env variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // 3. Detect Azure environment by hostname
  if (window.location.hostname.includes('azurecontainerapps.io')) {
    console.info('[Config] Detected Azure environment, using production backend fallback');
    return PRODUCTION_BACKEND_URL;
  }

  // 4. Default to localhost for development
  return 'http://localhost:8000';
};

const getEnvironment = (): 'development' | 'production' | 'test' => {
  const env = (window as any).__RUNTIME_CONFIG__?.ENVIRONMENT || import.meta.env.MODE;
  if (env === 'production' || window.location.hostname.includes('azurecontainerapps.io')) {
    return 'production';
  }
  return env as any;
};

export const config: RuntimeConfig = {
  API_URL: getApiUrl(),
  ENVIRONMENT: getEnvironment(),
  VERSION: (window as any).__RUNTIME_CONFIG__?.VERSION || '1.0.0',
  IS_PRODUCTION: getEnvironment() === 'production',
};

console.log('[Config] Initialized:', {
  apiUrl: config.API_URL,
  environment: config.ENVIRONMENT,
  isProduction: config.IS_PRODUCTION,
});

export default config;
