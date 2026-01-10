const PRODUCTION_BACKEND_URL = 'https://codereview-backend.jollysea-c5c0b121.centralus.azurecontainerapps.io';

const getBaseUrl = () => {
  if ((window as any).__RUNTIME_CONFIG__?.API_URL) {
    return (window as any).__RUNTIME_CONFIG__.API_URL;
  }
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  if (window.location.hostname.includes('azurecontainerapps.io')) {
    return PRODUCTION_BACKEND_URL;
  }
  return 'http://localhost:8000';
};

const fetchWithCredentials = async (url: string, options: RequestInit = {}) => {
  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  return response;
};

export const apiClient = {
  get: async (endpoint: string) => {
    const url = `${getBaseUrl()}${endpoint}`;
    console.debug('[API] GET', url);
    const response = await fetchWithCredentials(url);
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return { data: await response.json() };
  },
  post: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`;
    console.debug('[API] POST', url);
    const response = await fetchWithCredentials(url, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return { data: await response.json() };
  },
  put: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`;
    console.debug('[API] PUT', url);
    const response = await fetchWithCredentials(url, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return { data: await response.json() };
  },
};

export const api = {
  health: async () => {
    const response = await fetchWithCredentials(`${getBaseUrl()}/health`);
    return response.json();
  },

  ready: async () => {
    const response = await fetchWithCredentials(`${getBaseUrl()}/health/ready`);
    return response.json();
  },

  getProjects: async () => {
    const url = `${getBaseUrl()}/api/projects`;
    console.debug('[API] projects', url);
    const response = await fetchWithCredentials(url);
    const data = await response.json();
    return data;
  },

  getProject: async (id: number) => {
    const url = `${getBaseUrl()}/api/projects/${id}`;
    console.debug('[API] project', url);
    const response = await fetchWithCredentials(url);
    return response.json();
  },

  updateProject: async (id: number, data: any) => {
    const response = await fetchWithCredentials(`${getBaseUrl()}/api/projects/${id}`, {
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
    console.debug('[API] runs', url);
    const response = await fetchWithCredentials(url);
    return response.json();
  },

  getRun: async (id: number) => {
    const response = await fetchWithCredentials(`${getBaseUrl()}/api/analysis/runs/${id}`);
    return response.json();
  },

  getRunFindings: async (runId: number, params?: { severity?: string; category?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.severity) queryParams.append('severity', params.severity);
    if (params?.category) queryParams.append('category', params.category);

    const response = await fetchWithCredentials(`${getBaseUrl()}/api/analysis/runs/${runId}/findings?${queryParams}`);
    return response.json();
  },

  rerunAnalysis: async (runId: number) => {
    const response = await fetchWithCredentials(`${getBaseUrl()}/api/analysis/runs/${runId}/rerun`, {
      method: 'POST',
    });
    return response.json();
  },

  resolveFinding: async (findingId: number) => {
    const response = await fetchWithCredentials(`${getBaseUrl()}/api/analysis/findings/${findingId}/resolve`, {
      method: 'PATCH',
    });
    return response.json();
  },
};
