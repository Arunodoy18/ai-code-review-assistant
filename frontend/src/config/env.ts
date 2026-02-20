/**
 * Environment configuration — single source of truth for API URL.
 * In production, set VITE_API_URL to your Render backend URL.
 */

const FALLBACK_API_URL = 'http://localhost:8000';

export const getApiBaseUrl = (): string => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  return FALLBACK_API_URL;
};
