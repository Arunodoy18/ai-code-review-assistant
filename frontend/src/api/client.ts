const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

// Generic API client for flexible usage
export const apiClient = {
  get: async (endpoint: string) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`)
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`)
    return { data: await response.json() }
  },
  post: async (endpoint: string, body?: any) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`)
    return { data: await response.json() }
  },
  put: async (endpoint: string, body?: any) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.json()
  },

  ready: async () => {
    const response = await fetch(`${API_BASE_URL}/health/ready`)
    return response.json()
  },

  // Projects
  getProjects: async () => {
    const response = await fetch(`${API_BASE_URL}/api/projects`)
    return response.json()
  },

  getProject: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/projects/${id}`)
    return response.json()
  },

  updateProject: async (id: number, data: any) => {
    const response = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
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
    
    const response = await fetch(`${API_BASE_URL}/api/analysis/runs?${queryParams}`)
    return response.json()
  },

  getRun: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/api/analysis/runs/${id}`)
    return response.json()
  },

  getRunFindings: async (runId: number, params?: { severity?: string; category?: string }) => {
    const queryParams = new URLSearchParams()
    if (params?.severity) queryParams.append('severity', params.severity)
    if (params?.category) queryParams.append('category', params.category)
    
    const response = await fetch(`${API_BASE_URL}/api/analysis/runs/${runId}/findings?${queryParams}`)
    return response.json()
  },

  rerunAnalysis: async (runId: number) => {
    const response = await fetch(`${API_BASE_URL}/api/analysis/runs/${runId}/rerun`, {
      method: 'POST',
    })
    return response.json()
  },

  resolveFinding: async (findingId: number) => {
    const response = await fetch(`${API_BASE_URL}/api/analysis/findings/${findingId}/resolve`, {
      method: 'PATCH',
    })
    return response.json()
  },
}
