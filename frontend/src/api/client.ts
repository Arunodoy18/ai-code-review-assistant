/**
 * API client for local development.
 * Simple fetch wrapper with no retry logic or production-specific behavior.
 * Backend failures will fail gracefully without blocking the UI.
 */

const getBaseUrl = (): string => {
  // Allow override via Vite env variable if needed
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Default: localhost for local development
  return 'http://localhost:8000';
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

const fetchWithErrorHandling = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  try {
    const response = await fetch(url, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new NetworkError(
        `API Error: ${response.statusText}`,
        response.status,
        response.statusText
      );
    }
    
    return response;
  } catch (error) {
    if (error instanceof TypeError) {
      // Network error - backend not running or unreachable
      throw new NetworkError(
        'Backend server is not reachable. Make sure it is running on http://localhost:8000'
      );
    }
    throw error;
  }
};

export const apiClient = {
  get: async (endpoint: string) => {
    const url = `${getBaseUrl()}${endpoint}`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return { data: await response.json() };
  },
  
  post: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`;
    const response = await fetchWithErrorHandling(url, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return { data: await response.json() };
  },
  
  put: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`;
    const response = await fetchWithErrorHandling(url, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
    return { data: await response.json() };
  },
};

export const api = {
  health: async () => {
    const response = await fetchWithErrorHandling(`${getBaseUrl()}/health`, { method: 'GET' });
    return response.json();
  },

  ready: async () => {
    const response = await fetchWithErrorHandling(`${getBaseUrl()}/health/ready`, { method: 'GET' });
    return response.json();
  },

  getProjects: async () => {
    const url = `${getBaseUrl()}/api/projects`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    const data = await response.json();
    return data;
  },

  getProject: async (id: number) => {
    const url = `${getBaseUrl()}/api/projects/${id}`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  updateProject: async (id: number, data: any) => {
    const url = `${getBaseUrl()}/api/projects/${id}`;
    const response = await fetchWithErrorHandling(url, {
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
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  getRun: async (id: number) => {
    const url = `${getBaseUrl()}/api/analysis/runs/${id}`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  getRunFindings: async (runId: number, params?: { severity?: string; category?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.severity) queryParams.append('severity', params.severity);
    if (params?.category) queryParams.append('category', params.category);

    const url = `${getBaseUrl()}/api/analysis/runs/${runId}/findings?${queryParams}`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  rerunAnalysis: async (runId: number) => {
    const url = `${getBaseUrl()}/api/analysis/runs/${runId}/rerun`;
    const response = await fetchWithErrorHandling(url, { method: 'POST' });
    return response.json();
  },

  resolveFinding: async (findingId: number) => {
    const url = `${getBaseUrl()}/api/analysis/findings/${findingId}/resolve`;
    const response = await fetchWithErrorHandling(url, { method: 'PATCH' });
    return response.json();
  },
};
