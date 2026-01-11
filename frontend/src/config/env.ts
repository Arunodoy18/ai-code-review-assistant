/**
 * Simple environment configuration for local development.
 * Always defaults to localhost backend.
 */

const LOCAL_API_URL = 'http://localhost:8000'

export const getApiBaseUrl = (): string => {
  // Allow override via Vite env variable if needed
  if ((import.meta as any).env?.VITE_API_URL) {
    return (import.meta as any).env.VITE_API_URL
  }
  
  return LOCAL_API_URL
}
