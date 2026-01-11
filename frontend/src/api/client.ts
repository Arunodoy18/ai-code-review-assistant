import config from '../config/runtime';

const getBaseUrl = (): string => config.API_URL;

const isProduction = (): boolean => config.IS_PRODUCTION;

const log = (level: 'debug' | 'info' | 'warn' | 'error', ...args: any[]) => {
  // Only log debug in development or when explicitly enabled
  if (level === 'debug' && isProduction() && sessionStorage.getItem('debug') !== 'true') {
    return;
  }
  console[level]('[API]', ...args);
};

interface ApiError extends Error {
  status?: number;
  statusText?: string;
  details?: any;
}

class NetworkError extends Error implements ApiError {
  status?: number;
  statusText?: string;
  
  constructor(message: string, status?: number, statusText?: string) {
    super(message);
    this.name = 'NetworkError';
    this.status = status;
    this.statusText = statusText;
  }
}

const fetchWithRetry = async (
  url: string,
  options: RequestInit = {},
  retries: number = 2
): Promise<Response> => {
  const isProductionEnv = isProduction();
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      log('debug', `${options.method || 'GET'} ${url} (attempt ${attempt + 1}/${retries + 1})`);
      
      const response = await fetch(url, {
        ...options,
        credentials: isProductionEnv ? 'omit' : 'include',  // Match backend CORS config
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      // Success - return response
      if (response.ok) {
        log('debug', `✓ ${options.method || 'GET'} ${url} - ${response.status}`);
        return response;
      }
      
      // Client error (4xx) - don't retry
      if (response.status >= 400 && response.status < 500) {
        log('warn', `Client error ${response.status} for ${url}`);
        throw new NetworkError(
          `API Error: ${response.statusText}`,
          response.status,
          response.statusText
        );
      }
      
      // Server error (5xx) - retry
      if (attempt < retries) {
        const backoff = Math.min(1000 * Math.pow(2, attempt), 5000);
        log('warn', `Server error ${response.status}, retrying in ${backoff}ms...`);
        await new Promise(resolve => setTimeout(resolve, backoff));
        continue;
      }
      
      throw new NetworkError(
        `API Error: ${response.statusText}`,
        response.status,
        response.statusText
      );
      
    } catch (error) {
      // Network error (no response)
      if (error instanceof TypeError) {
        if (attempt < retries) {
          const backoff = Math.min(1000 * Math.pow(2, attempt), 5000);
          log('warn', `Network error, retrying in ${backoff}ms...`, error);
          await new Promise(resolve => setTimeout(resolve, backoff));
          continue;
        }
        log('error', 'Network request failed after retries:', error);
        throw new NetworkError(
          'Unable to reach the server. Please check your connection and try again.'
        );
      }
      // Re-throw other errors (like NetworkError from above)
      throw error;
    }
  }
  
  throw new NetworkError('Request failed after all retries');
};

export const apiClient = {
  get: async (endpoint: string) => {
    const url = `${getBaseUrl()}${endpoint}`;
    const response = await fetchWithRetry(url, { method: 'GET' });
    return { data: await response.json() };
  },
  
  post: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`;
    const response = await fetchWithRetry(url, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return { data: await response.json() };
  },
  
  put: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`;
    const response = await fetchWithRetry(url, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
    return { data: await response.json() };
  },
};

export const api = {
  health: async () => {
    const response = await fetchWithRetry(`${getBaseUrl()}/health`, { method: 'GET' });
    return response.json();
  },

  ready: async () => {
    const response = await fetchWithRetry(`${getBaseUrl()}/health/ready`, { method: 'GET' });
    return response.json();
  },

  getProjects: async () => {
    const url = `${getBaseUrl()}/api/projects`;
    const response = await fetchWithRetry(url, { method: 'GET' });
    const data = await response.json();
    return data;
  },

  getProject: async (id: number) => {
    const url = `${getBaseUrl()}/api/projects/${id}`;
    const response = await fetchWithRetry(url, { method: 'GET' });
    return response.json();
  },

  updateProject: async (id: number, data: any) => {
    const url = `${getBaseUrl()}/api/projects/${id}`;
    const response = await fetchWithRetry(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
    return response.json();
  },

  getRuns: async (params?: { project_id?: number; pr_number?: number; limit?: number; offset?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.project_id) queryParams.append('project_id', params.project_id.toString());
    if (params?.pr_number) queryParams.append('pr_number', params.pr_number.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const url = `${getBaseUrl()}/api/analysis/runs?${queryParams}`;
    const response = await fetchWithRetry(url, { method: 'GET' });
    return response.json();
  },

  getRun: async (id: number) => {
    const url = `${getBaseUrl()}/api/analysis/runs/${id}`;
    const response = await fetchWithRetry(url, { method: 'GET' });
    return response.json();
  },

  getRunFindings: async (runId: number, params?: { severity?: string; category?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.severity) queryParams.append('severity', params.severity);
    if (params?.category) queryParams.append('category', params.category);

    const url = `${getBaseUrl()}/api/analysis/runs/${runId}/findings?${queryParams}`;
    const response = await fetchWithRetry(url, { method: 'GET' });
    return response.json();
  },

  rerunAnalysis: async (runId: number) => {
    const url = `${getBaseUrl()}/api/analysis/runs/${runId}/rerun`;
    const response = await fetchWithRetry(url, { method: 'POST' });
    return response.json();
  },

  resolveFinding: async (findingId: number) => {
    const url = `${getBaseUrl()}/api/analysis/findings/${findingId}/resolve`;
    const response = await fetchWithRetry(url, { method: 'PATCH' });
    return response.json();
  },
};
