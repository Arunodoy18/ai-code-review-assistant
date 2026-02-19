export interface Project {
  id: number
  name: string
  github_repo_full_name: string
  github_installation_id?: number | null
  config: Record<string, any>
  created_at: string
  updated_at: string
}

export interface AnalysisRun {
  id: number
  project_id: number
  pr_number: number
  pr_url: string
  pr_title: string
  pr_author: string
  base_sha: string
  head_sha: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at: string
  completed_at?: string
  error_message?: string
  risk_score?: number | null
  risk_breakdown?: {
    score?: number
    label?: string
    explanation?: string
    breakdown?: {
      size_impact?: number
      severity_impact?: number
      blast_radius?: number
      complexity?: number
      ai_adjustment?: number
    }
  }
  pr_summary?: string | null
  run_metadata?: {
    files_analyzed?: number
    findings_count?: number
    rule_findings?: number
    ai_findings?: number
    [key: string]: any
  }
}

export interface Finding {
  id: number
  run_id: number
  file_path: string
  line_number?: number
  end_line_number?: number
  severity: 'critical' | 'high' | 'medium' | 'low'
  category: 'bug' | 'security' | 'performance' | 'best_practice'
  rule_id?: string
  title: string
  description: string
  suggestion?: string
  code_snippet?: string
  is_ai_generated: number
  is_resolved: number
  is_dismissed?: number
  auto_fix_code?: string | null
  created_at: string
  finding_metadata?: Record<string, any>
}

export interface ApiKeysResponse {
  has_groq_key: boolean
  has_openai_key: boolean
  has_anthropic_key: boolean
  has_google_key: boolean
  preferred_llm_provider: string
  has_github_token: boolean
  github_username?: string | null
}

export interface ApiKeysRequest {
  groq_api_key?: string
  openai_api_key?: string
  anthropic_api_key?: string
  google_api_key?: string
  preferred_llm_provider?: string
  github_token?: string
}
