// Read API URL from window object (injected by index.html before bundle loads)
// Build timestamp: 2026-01-09T19:30:00Z
const getBaseUrl = () => {
  return (window as any).__RUNTIME_CONFIG__?.API_URL || 'http://localhost:8000';
};

// Generic API client for flexible usage
export const apiClient = {
  get: async (endpoint: string) => {
    const url = `${getBaseUrl()}${endpoint}`
    console.debug('[API] GET', url)
    const response = await fetch(url)
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`)
    return { data: await response.json() }
  },
  post: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`
    console.debug('[API] POST', url)
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`)
    return { data: await response.json() }
  },
  put: async (endpoint: string, body?: any) => {
    const url = `${getBaseUrl()}${endpoint}`
    console.debug('[API] PUT', url)
    const response = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`)
    return { data: await response.json() }
  }
}

export const api = {
  // Health
  health: async () => {
    const response = await fetch(`${getBaseUrl()}/health`)
    return response.json()
  },

  ready: async () => {
    const response = await fetch(`${getBaseUrl()}/health/ready`)
    return response.json()
  },

  // Projects
  getProjects: async () => {
    const url = `${getBaseUrl()}/api/projects`
    console.debug('[API] projects', url)
    const response = await fetch(url)
    return response.json()
  },

  getProject: async (id: number) => {
    const url = `${getBaseUrl()}/api/projects/${id}`
    console.debug('[API] project', url)
    const response = await fetch(url)
    return response.json()
  },

  updateProject: async (id: number, data: any) => {
    const response = await fetch(`${getBaseUrl()}/api/projects/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return response.json()
  },

  // Analysis Runs
  getRuns: async (params?: { project_id?: number; pr_number?: number; limit?: number; offset?: number }) => {
    const queryParams = new URLSearchParams()
    if (params?.project_id) queryParams.append('project_id', params.project_id.toString())
    if (params?.pr_number) queryParams.append('pr_number', params.pr_number.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.offset) queryParams.append('offset', params.offset.toString())
    
    const url = `${getBaseUrl()}/api/analysis/runs?${queryParams}`
    console.debug('[API] runs', url)
    const response = await fetch(url)
    return response.json()
  },

  getRun: async (id: number) => {
    const response = await fetch(`${getBaseUrl()}/api/analysis/runs/${id}`)
    return response.json()
  },

  getRunFindings: async (runId: number, params?: { severity?: string; category?: string }) => {
    const queryParams = new URLSearchParams()
    if (params?.severity) queryParams.append('severity', params.severity)
    if (params?.category) queryParams.append('category', params.category)
    
    const response = await fetch(`${getBaseUrl()}/api/analysis/runs/${runId}/findings?${queryParams}`)
    return response.json()
  },

  rerunAnalysis: async (runId: number) => {
    const response = await fetch(`${getBaseUrl()}/api/analysis/runs/${runId}/rerun`, {
      method: 'POST',
    })
    return response.json()
  },

  resolveFinding: async (findingId: number) => {
    const response = await fetch(`${getBaseUrl()}/api/analysis/findings/${findingId}/resolve`, {
      method: 'PATCH',
    })
    return response.json()
  },
}
