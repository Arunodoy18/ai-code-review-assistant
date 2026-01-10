const LOCAL_API_FALLBACK = 'http://localhost:8000'

declare global {
  interface Window {
    __ENV__?: Record<string, string>
  }
}

const isBrowser = typeof window !== 'undefined'

const getRuntimeEnv = (): Record<string, string> => {
  if (!isBrowser) {
    return {}
  }
  return window.__ENV__ ?? {}
}

const deriveBackendFromHostname = (): string | undefined => {
  if (!isBrowser) {
    return undefined
  }

  const { protocol, hostname } = window.location
  if (hostname.includes('frontend')) {
    return `${protocol}//${hostname.replace('frontend', 'backend')}`
  }

  return undefined
}

export const getApiBaseUrl = (): string => {
  return (
    getRuntimeEnv().VITE_API_URL ||
    (import.meta as any).env?.VITE_API_URL ||
    deriveBackendFromHostname() ||
    LOCAL_API_FALLBACK
  )
}
