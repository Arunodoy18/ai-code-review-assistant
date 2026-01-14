import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api as apiClient } from '../api/client';
import { ShieldAlert, Sliders, Search, Filter, CheckCircle2, AlertCircle } from 'lucide-react';

interface Rule {
  rule_id: string;
  name: string;
  description: string;
  category: string;
  default_severity: string;
  languages: string[];
  configurable: boolean;
  requires_ai: boolean;
}

interface ProjectConfig {
  enabled_rules: string[];
  disabled_rules: string[];
  severity_overrides: Record<string, string>;
  analysis_config: {
    max_findings_per_rule: number;
    ignore_patterns: string[];
    file_extensions: string[];
  };
}

interface Project {
  id: number;
  name: string;
  github_repo_full_name: string;
}

export default function Configuration() {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all projects
  const { data: projectsResponse } = useQuery({
    queryKey: ['projects'],
    queryFn: apiClient.getProjects
  });
  const projects: Project[] = (projectsResponse as any)?.data || (Array.isArray(projectsResponse) ? projectsResponse : []);

  // Fetch all available rules
  const { data: rulesResponse, isLoading: rulesLoading, error: rulesError } = useQuery({
    queryKey: ['rules'],
    queryFn: async () => {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/config/rules`);
      if (!response.ok) throw new Error('Failed to fetch rules');
      return response.json();
    },
    retry: 1
  });
  const rules: Rule[] = Array.isArray(rulesResponse) ? rulesResponse : [];

  // Fetch project configuration
  const { data: config, isLoading: configLoading } = useQuery<ProjectConfig>({
    queryKey: ['project-config', selectedProjectId],
    queryFn: async () => {
      const response = await (apiClient as any).getProjectConfig(selectedProjectId);
      return response;
    },
    enabled: selectedProjectId !== null
  });

  // Update configuration mutation
  const updateConfigMutation = useMutation({
    mutationFn: async (newConfig: Partial<ProjectConfig>) => {
      const response = await (apiClient as any).updateProjectConfig(selectedProjectId, newConfig);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-config', selectedProjectId] });
    }
  });

  const isRuleEnabled = (ruleId: string): boolean => {
    if (!config) return false;
    if (config.enabled_rules.includes(ruleId)) return true;
    if (config.disabled_rules.includes(ruleId)) return false;
    const rule = rules.find(r => r.rule_id === ruleId);
    return rule?.configurable ?? false;
  };

  const getRuleSeverity = (rule: Rule): string => {
    return config?.severity_overrides?.[rule.rule_id] || rule.default_severity;
  };

  const categories = Array.from(new Set(rules.map(r => r.category)));

  const filteredRules = rules.filter(rule => {
    const matchesCategory = categoryFilter === 'all' || rule.category === categoryFilter;
    const matchesSearch = searchQuery === '' || 
      rule.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rule.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      default: return 'text-neutral-400 bg-neutral-800 border-neutral-700';
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-100 mb-1">Settings</h1>
          <p className="text-neutral-500 text-sm">
            Configure analysis rules and parameters for your repositories.
          </p>
        </div>
      </div>

      {/* Project Selector */}
      <div className="card-premium p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Sliders className="w-5 h-5 text-neutral-400" />
          <h2 className="text-base font-medium text-neutral-100">Select Repository</h2>
        </div>
        
        <div className="relative">
          <select
            value={selectedProjectId || ''}
            onChange={(e) => setSelectedProjectId(Number(e.target.value) || null)}
            className="w-full h-10 pl-3 pr-10 bg-neutral-950 border border-neutral-800 rounded-md text-neutral-200 text-sm focus:border-neutral-700 focus:outline-none transition-colors appearance-none cursor-pointer"
          >
            <option value="">Choose a repository...</option>
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                {project.github_repo_full_name}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-neutral-500">
            <Filter className="w-4 h-4" />
          </div>
        </div>
      </div>

      {selectedProjectId ? (
        <div className="space-y-6">
          {/* Analysis Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card-premium p-5">
              <h3 className="text-sm font-medium text-neutral-100 mb-4 flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <span>Thresholds</span>
              </h3>
              <div>
                <label className="block text-xs text-neutral-500 mb-2">
                  Max findings per rule
                </label>
                <input
                  type="number"
                  value={config?.analysis_config.max_findings_per_rule || 10}
                  onChange={(e) => updateConfigMutation.mutate({ 
                    analysis_config: { ...config!.analysis_config, max_findings_per_rule: Number(e.target.value) } 
                  })}
                  className="w-full h-9 px-3 bg-neutral-950 border border-neutral-800 rounded-md text-neutral-100 text-sm focus:border-neutral-700 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div className="card-premium p-5">
              <h3 className="text-sm font-medium text-neutral-100 mb-4 flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-neutral-400" />
                <span>Scope</span>
              </h3>
              <div>
                <label className="block text-xs text-neutral-500 mb-2">
                  File extensions
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {(config?.analysis_config.file_extensions || ['.py', '.js', '.ts']).map(ext => (
                    <span key={ext} className="px-2 py-1 bg-neutral-800 text-neutral-300 border border-neutral-700 rounded text-xs font-mono">
                      {ext}
                    </span>
                  ))}
                  <button className="px-2 py-1 bg-neutral-900 border border-dashed border-neutral-700 text-neutral-500 rounded text-xs hover:text-neutral-300 hover:border-neutral-600 transition-colors">
                    + Add
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Rules Configuration */}
          <div className="card-premium p-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              <h2 className="text-base font-medium text-neutral-100 flex items-center space-x-2">
                <ShieldAlert className="w-5 h-5 text-neutral-400" />
                <span>Analysis Rules</span>
              </h2>
              
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
                  <input
                    type="text"
                    placeholder="Search rules..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-56 h-9 pl-9 pr-3 bg-neutral-950 border border-neutral-800 rounded-md text-sm text-neutral-100 focus:border-neutral-700 focus:outline-none transition-colors"
                  />
                </div>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="h-9 px-3 bg-neutral-950 border border-neutral-800 rounded-md text-sm text-neutral-300 focus:border-neutral-700 focus:outline-none transition-colors cursor-pointer"
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-3">
              {configLoading || rulesLoading ? (
                <div className="text-center py-12 text-neutral-500 text-sm">
                  Loading rules...
                </div>
              ) : rulesError ? (
                <div className="text-center py-12 text-neutral-500 text-sm">
                  Unable to load rules. Make sure the backend is running.
                </div>
              ) : filteredRules.length === 0 ? (
                <div className="text-center py-12 bg-neutral-900/50 rounded-lg border border-dashed border-neutral-800">
                  <p className="text-neutral-500 text-sm">No rules match your search.</p>
                </div>
              ) : (
                filteredRules.map(rule => {
                  const enabled = isRuleEnabled(rule.rule_id);
                  const severity = getRuleSeverity(rule);
                  
                  return (
                    <div
                      key={rule.rule_id}
                      className={`p-4 rounded-lg border transition-colors ${
                        enabled 
                          ? 'bg-neutral-900/50 border-neutral-800 hover:border-neutral-700' 
                          : 'bg-neutral-950 border-neutral-900 opacity-50'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <button
                          className={`mt-0.5 relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full transition-colors ${
                            enabled ? 'bg-green-600' : 'bg-neutral-700'
                          }`}
                        >
                          <span
                            className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                              enabled ? 'translate-x-4' : 'translate-x-0.5'
                            } mt-0.5`}
                          />
                        </button>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-sm font-medium text-neutral-100">{rule.name}</h3>
                            <span className="text-xs text-neutral-600 bg-neutral-800 px-1.5 py-0.5 rounded">
                              {rule.category.replace('_', ' ')}
                            </span>
                          </div>
                          <p className="text-xs text-neutral-500 mb-2">{rule.description}</p>
                          <code className="text-xs font-mono text-neutral-600">{rule.rule_id}</code>
                        </div>

                        <div className="shrink-0">
                          <select
                            value={severity}
                            disabled={!enabled}
                            className={`px-2 py-1 text-xs rounded border focus:outline-none transition-colors cursor-pointer ${
                              getSeverityColor(severity)
                            } ${!enabled ? 'cursor-not-allowed opacity-50' : ''}`}
                          >
                            <option value="critical">Critical</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="card-premium p-12 text-center">
          <div className="w-12 h-12 bg-neutral-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sliders className="w-6 h-6 text-neutral-500" />
          </div>
          <h3 className="text-lg font-semibold text-neutral-100 mb-2">Select a repository</h3>
          <p className="text-neutral-500 text-sm max-w-sm mx-auto">
            Choose a repository from the dropdown above to configure its analysis settings.
          </p>
        </div>
      )}
    </div>
  );
}
