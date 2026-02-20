/**
 * Runtime configuration.
 * Uses env.ts as single source of truth for API URL.
 */
import { getApiBaseUrl } from './env';

interface RuntimeConfig {
  API_URL: string;
  ENVIRONMENT: string;
  VERSION: string;
}

export const config: RuntimeConfig = {
  API_URL: getApiBaseUrl(),
  ENVIRONMENT: import.meta.env.MODE || 'development',
  VERSION: '1.0.0',
};

if (import.meta.env.DEV) {
  console.log('[Config] Development mode:', {
    apiUrl: config.API_URL,
    environment: config.ENVIRONMENT,
  });
}

export default config;
