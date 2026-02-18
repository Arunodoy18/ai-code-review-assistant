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
    queryFn: apiClient.getRules,
    retry: 1
  });
  const rules: Rule[] = Array.isArray(rulesResponse) ? rulesResponse : [];

  // Fetch project configuration
  const { data: config, isLoading: configLoading } = useQuery<ProjectConfig>({
    queryKey: ['project-config', selectedProjectId],
    queryFn: () => apiClient.getProjectConfig(selectedProjectId!),
    enabled: selectedProjectId !== null
  });

  // Update configuration mutation
  const updateConfigMutation = useMutation({
    mutationFn: (newConfig: Partial<ProjectConfig>) =>
      apiClient.updateProjectConfig(selectedProjectId!, newConfig),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-config', selectedProjectId] });
    }
  });

  // Toggle rule mutation
  const toggleRuleMutation = useMutation({
    mutationFn: ({ ruleId, enable }: { ruleId: string; enable: boolean }) =>
      enable
        ? apiClient.enableRule(selectedProjectId!, ruleId)
        : apiClient.disableRule(selectedProjectId!, ruleId),
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
      case 'high': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'medium': return 'text-copper-400 bg-copper-500/10 border-copper-500/20';
      default: return 'text-sand-400 bg-surface-3 border-surface-4';
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-sand-100 mb-1">Settings</h1>
          <p className="text-sand-600 text-sm">
            Configure analysis rules and parameters for your repositories.
          </p>
        </div>
      </div>

      {/* Project Selector */}
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Sliders className="w-5 h-5 text-copper-400" />
          <h2 className="text-base font-semibold text-sand-100">Select Repository</h2>
        </div>
        
        <div className="relative">
          <select
            value={selectedProjectId || ''}
            onChange={(e) => setSelectedProjectId(Number(e.target.value) || null)}
            className="w-full h-11 pl-3 pr-10 bg-surface-1 border border-surface-4 rounded-xl text-sand-200 text-sm focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600 transition-colors appearance-none cursor-pointer"
          >
            <option value="">Choose a repository...</option>
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                {project.github_repo_full_name}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-sand-600">
            <Filter className="w-4 h-4" />
          </div>
        </div>
      </div>

      {selectedProjectId ? (
        <div className="space-y-6">
          {/* Analysis Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-sand-100 mb-4 flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Thresholds</span>
              </h3>
              <div>
                <label className="block text-xs text-sand-600 mb-2">
                  Max findings per rule
                </label>
                <input
                  type="number"
                  value={config?.analysis_config.max_findings_per_rule || 10}
                  onChange={(e) => updateConfigMutation.mutate({ 
                    analysis_config: { ...config!.analysis_config, max_findings_per_rule: Number(e.target.value) } 
                  })}
                  className="input"
                />
              </div>
            </div>

            <div className="card p-5">
              <h3 className="text-sm font-semibold text-sand-100 mb-4 flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-sand-500" />
                <span>Scope</span>
              </h3>
              <div>
                <label className="block text-xs text-sand-600 mb-2">
                  File extensions
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {(config?.analysis_config.file_extensions || ['.py', '.js', '.ts']).map(ext => (
                    <span key={ext} className="px-2 py-1 bg-surface-3 text-sand-300 border border-surface-4 rounded-lg text-xs font-mono">
                      {ext}
                    </span>
                  ))}
                  <button className="px-2 py-1 bg-surface-1 border border-dashed border-surface-4 text-sand-600 rounded-lg text-xs hover:text-sand-300 hover:border-copper-700 transition-colors">
                    + Add
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Rules Configuration */}
          <div className="card p-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              <h2 className="text-base font-semibold text-sand-100 flex items-center space-x-2">
                <ShieldAlert className="w-5 h-5 text-copper-400" />
                <span>Analysis Rules</span>
              </h2>
              
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-sand-700" />
                  <input
                    type="text"
                    placeholder="Search rules..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input w-56 pl-9"
                  />
                </div>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="h-11 px-3 bg-surface-1 border border-surface-4 rounded-xl text-sm text-sand-300 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600 transition-colors cursor-pointer"
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
                <div className="text-center py-12 text-sand-600 text-sm">
                  Loading rules...
                </div>
              ) : rulesError ? (
                <div className="text-center py-12 text-sand-600 text-sm">
                  Unable to load rules. Make sure the backend is running.
                </div>
              ) : filteredRules.length === 0 ? (
                <div className="text-center py-12 bg-surface-1 rounded-xl border border-dashed border-surface-4">
                  <p className="text-sand-600 text-sm">No rules match your search.</p>
                </div>
              ) : (
                filteredRules.map(rule => {
                  const enabled = isRuleEnabled(rule.rule_id);
                  const severity = getRuleSeverity(rule);
                  
                  return (
                    <div
                      key={rule.rule_id}
                      className={`p-4 rounded-xl border transition-all duration-200 ${
                        enabled 
                          ? 'bg-surface-1 border-surface-4 hover:border-copper-800' 
                          : 'bg-surface-0 border-surface-4/50 opacity-50'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <button
                          onClick={() => toggleRuleMutation.mutate({ ruleId: rule.rule_id, enable: !enabled })}
                          className={`mt-0.5 relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full transition-colors duration-200 ${
                            enabled ? 'bg-copper-600' : 'bg-surface-4'
                          }`}
                        >
                          <span
                            className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform duration-200 ${
                              enabled ? 'translate-x-4' : 'translate-x-0.5'
                            } mt-0.5`}
                          />
                        </button>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-sm font-semibold text-sand-100">{rule.name}</h3>
                            <span className="text-[10px] text-sand-600 bg-surface-3 border border-surface-4 px-1.5 py-0.5 rounded-md uppercase tracking-wider font-bold">
                              {rule.category.replace('_', ' ')}
                            </span>
                          </div>
                          <p className="text-xs text-sand-500 mb-2">{rule.description}</p>
                          <code className="text-xs font-mono text-sand-700">{rule.rule_id}</code>
                        </div>

                        <div className="shrink-0">
                          <select
                            value={severity}
                            disabled={!enabled}
                            onChange={(e) => updateConfigMutation.mutate({
                              severity_overrides: { ...config?.severity_overrides, [rule.rule_id]: e.target.value }
                            })}
                            className={`px-2 py-1 text-xs rounded-lg border focus:outline-none transition-colors cursor-pointer ${
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
        <div className="card p-12 text-center">
          <div className="w-14 h-14 bg-surface-3 rounded-2xl flex items-center justify-center mx-auto mb-5">
            <Sliders className="w-7 h-7 text-sand-600" />
          </div>
          <h3 className="text-lg font-bold text-sand-100 mb-2">Select a repository</h3>
          <p className="text-sand-500 text-sm max-w-sm mx-auto">
            Choose a repository from the dropdown above to configure its analysis settings.
          </p>
        </div>
      )}
    </div>
  );
}
