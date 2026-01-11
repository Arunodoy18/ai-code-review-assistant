/**
 * Runtime configuration for local development.
 * This project is configured for localhost-only development.
 * For deployment configuration, see /docs/ folder.
 */

interface RuntimeConfig {
  API_URL: string;
  ENVIRONMENT: 'development';
  VERSION: string;
}

const getApiUrl = (): string => {
  // Allow override via Vite env variable if needed
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // Default: localhost for local development
  return 'http://localhost:8000';
};

export const config: RuntimeConfig = {
  API_URL: getApiUrl(),
  ENVIRONMENT: 'development',
  VERSION: '1.0.0',
};

console.log('[Config] Local development mode:', {
  apiUrl: config.API_URL,
  environment: config.ENVIRONMENT,
});

export default config;
