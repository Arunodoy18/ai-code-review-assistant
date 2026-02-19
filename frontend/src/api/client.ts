/**
 * API client with JWT authentication support.
 * Automatically attaches Bearer token from localStorage if available.
 */

const getBaseUrl = (): string => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  return 'http://localhost:8000';
};

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('auth_token');
  if (token && token !== 'demo_session') {
    return { 'Authorization': `Bearer ${token}` };
  }
  return {};
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
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
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

  dismissFinding: async (findingId: number) => {
    const url = `${getBaseUrl()}/api/analysis/findings/${findingId}/dismiss`;
    const response = await fetchWithErrorHandling(url, { method: 'PATCH' });
    return response.json();
  },

  getAutoFix: async (findingId: number) => {
    const url = `${getBaseUrl()}/api/analysis/findings/${findingId}/auto-fix`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  generateFix: async (findingId: number) => {
    const url = `${getBaseUrl()}/api/analysis/findings/${findingId}/generate-fix`;
    const response = await fetchWithErrorHandling(url, { method: 'POST' });
    return response.json();
  },

  getRiskScore: async (runId: number) => {
    const url = `${getBaseUrl()}/api/analysis/runs/${runId}/risk-score`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  getPrSummary: async (runId: number) => {
    const url = `${getBaseUrl()}/api/analysis/runs/${runId}/summary`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  // Configuration API methods
  getRules: async () => {
    const url = `${getBaseUrl()}/api/config/rules`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  getProjectConfig: async (projectId: number) => {
    const url = `${getBaseUrl()}/api/config/projects/${projectId}`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  updateProjectConfig: async (projectId: number, config: any) => {
    const url = `${getBaseUrl()}/api/config/projects/${projectId}`;
    const response = await fetchWithErrorHandling(url, {
      method: 'PUT',
      body: JSON.stringify(config),
    });
    return response.json();
  },

  enableRule: async (projectId: number, ruleId: string) => {
    const url = `${getBaseUrl()}/api/config/projects/${projectId}/rules/${ruleId}/enable`;
    const response = await fetchWithErrorHandling(url, { method: 'POST' });
    return response.json();
  },

  disableRule: async (projectId: number, ruleId: string) => {
    const url = `${getBaseUrl()}/api/config/projects/${projectId}/rules/${ruleId}/disable`;
    const response = await fetchWithErrorHandling(url, { method: 'POST' });
    return response.json();
  },

  // API Keys management (SaaS per-user keys)
  getApiKeys: async () => {
    const url = `${getBaseUrl()}/api/auth/api-keys`;
    const response = await fetchWithErrorHandling(url, { method: 'GET' });
    return response.json();
  },

  updateApiKeys: async (keys: {
    groq_api_key?: string;
    openai_api_key?: string;
    anthropic_api_key?: string;
    google_api_key?: string;
    preferred_llm_provider?: string;
  }) => {
    const url = `${getBaseUrl()}/api/auth/api-keys`;
    const response = await fetchWithErrorHandling(url, {
      method: 'PUT',
      body: JSON.stringify(keys),
    });
    return response.json();
  },
};
