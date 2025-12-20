import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Settings, ShieldAlert } from 'lucide-react';

interface Rule {
  id: string;
  name: string;
  description: string;
  category: string;
  default_severity: string;
  enabled_by_default: boolean;
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
  repository_name: string;
  repository_url: string;
}

export default function Configuration() {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all projects
  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await apiClient.get('/projects/');
      return response.data;
    }
  });

  // Fetch all available rules
  const { data: rules = [] } = useQuery<Rule[]>({
    queryKey: ['rules'],
    queryFn: async () => {
      const response = await apiClient.get('/config/rules');
      return response.data;
    }
  });

  // Fetch project configuration
  const { data: config, isLoading: configLoading } = useQuery<ProjectConfig>({
    queryKey: ['project-config', selectedProjectId],
    queryFn: async () => {
      const response = await apiClient.get(`/config/projects/${selectedProjectId}`);
      return response.data;
    },
    enabled: selectedProjectId !== null
  });

  // Update configuration mutation
  const updateConfigMutation = useMutation({
    mutationFn: async (newConfig: Partial<ProjectConfig>) => {
      const response = await apiClient.put(`/config/projects/${selectedProjectId}`, newConfig);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-config', selectedProjectId] });
    }
  });

  // Toggle rule mutation
  const toggleRuleMutation = useMutation({
    mutationFn: async ({ ruleId, enable }: { ruleId: string; enable: boolean }) => {
      const action = enable ? 'enable' : 'disable';
      const response = await apiClient.post(`/config/projects/${selectedProjectId}/rules/${ruleId}/${action}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-config', selectedProjectId] });
    }
  });

  // Update severity mutation
  const updateSeverityMutation = useMutation({
    mutationFn: async ({ ruleId, severity }: { ruleId: string; severity: string }) => {
      const response = await apiClient.post(
        `/config/projects/${selectedProjectId}/rules/${ruleId}/severity`,
        { severity }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project-config', selectedProjectId] });
    }
  });

  const isRuleEnabled = (ruleId: string): boolean => {
    if (!config) return false;
    if (config.enabled_rules.includes(ruleId)) return true;
    if (config.disabled_rules.includes(ruleId)) return false;
    const rule = rules.find(r => r.id === ruleId);
    return rule?.enabled_by_default ?? false;
  };

  const getRuleSeverity = (rule: Rule): string => {
    return config?.severity_overrides?.[rule.id] || rule.default_severity;
  };

  const categories = Array.from(new Set(rules.map(r => r.category)));

  const filteredRules = rules.filter(rule => {
    const matchesCategory = categoryFilter === 'all' || rule.category === categoryFilter;
    const matchesSearch = searchQuery === '' || 
      rule.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rule.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleToggleRule = (ruleId: string, currentlyEnabled: boolean) => {
    toggleRuleMutation.mutate({ ruleId, enable: !currentlyEnabled });
  };

  const handleUpdateSeverity = (ruleId: string, severity: string) => {
    updateSeverityMutation.mutate({ ruleId, severity });
  };

  const handleUpdateAnalysisConfig = (updates: Partial<ProjectConfig['analysis_config']>) => {
    if (!config) return;
    updateConfigMutation.mutate({
      analysis_config: { ...config.analysis_config, ...updates }
    });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/30';
      case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      case 'low': return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
      case 'info': return 'text-slate-400 bg-slate-500/10 border-slate-500/30';
      default: return 'text-slate-400 bg-slate-500/10 border-slate-500/30';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'security': return '🔒';
      case 'bug': return '🐛';
      case 'performance': return '⚡';
      case 'best_practice': return '✨';
      case 'style': return '🎨';
      case 'documentation': return '📝';
      default: return '📋';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 mb-2 drop-shadow-sm">
          Configuration
        </h1>
        <p className="mt-2 text-slate-400 text-lg">
          Customize analysis rules and settings for your projects
        </p>
      </div>

      {/* Project Selector */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900/80 backdrop-blur-md rounded-xl p-6 border border-slate-700/50 shadow-lg">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Select Project
        </label>
        <select
          value={selectedProjectId || ''}
          onChange={(e) => setSelectedProjectId(Number(e.target.value) || null)}
          className="w-full px-4 py-2 bg-slate-900/50 border border-slate-600/50 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
        >
          <option value="">Choose a project...</option>
          {projects.map(project => (
            <option key={project.id} value={project.id}>
              {project.repository_name}
            </option>
          ))}
        </select>
      </div>

      {selectedProjectId && config && (
        <>
          {/* Analysis Settings */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900/80 backdrop-blur-md rounded-xl p-6 border border-slate-700/50 shadow-lg">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-400" />
              <span>Analysis Settings</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Max Findings per Rule
                </label>
                <input
                  type="number"
                  value={config.analysis_config.max_findings_per_rule}
                  onChange={(e) => handleUpdateAnalysisConfig({ max_findings_per_rule: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-slate-900/50 border border-slate-600/50 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  min="1"
                  max="100"
                />
                <p className="mt-1 text-sm text-slate-500">
                  Maximum number of findings to report per rule
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  File Extensions
                </label>
                <input
                  type="text"
                  value={config.analysis_config.file_extensions.join(', ')}
                  onChange={(e) => handleUpdateAnalysisConfig({ 
                    file_extensions: e.target.value.split(',').map(ext => ext.trim()) 
                  })}
                  className="w-full px-4 py-2 bg-slate-900/50 border border-slate-600/50 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder=".py, .js, .ts"
                />
                <p className="mt-1 text-sm text-slate-500">
                  Comma-separated list of file extensions to analyze
                </p>
              </div>
            </div>
          </div>

          {/* Rules Configuration */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900/80 backdrop-blur-md rounded-xl p-6 border border-slate-700/50 shadow-lg">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <ShieldAlert className="w-5 h-5 text-purple-400" />
                <span>Analysis Rules</span>
              </h2>
              
              {/* Search and Filter */}
              <div className="flex flex-col md:flex-row gap-4 mb-4">
                <input
                  type="text"
                  placeholder="Search rules..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 px-4 py-2 bg-slate-900/50 border border-slate-600/50 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="px-4 py-2 bg-slate-900/50 border border-slate-600/50 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {getCategoryIcon(category)} {category.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Rules List */}
            <div className="space-y-3">
              {configLoading ? (
                <div className="text-center py-8 text-slate-500">Loading configuration...</div>
              ) : filteredRules.length === 0 ? (
                <div className="text-center py-8 text-slate-500">No rules found</div>
              ) : (
                filteredRules.map(rule => {
                  const enabled = isRuleEnabled(rule.id);
                  const severity = getRuleSeverity(rule);
                  
                  return (
                    <div
                      key={rule.id}
                      className={`p-4 border rounded-xl transition-all duration-300 ${
                        enabled 
                          ? 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800 hover:border-slate-600 hover:shadow-md' 
                          : 'bg-slate-900/30 border-slate-800/50 opacity-60 hover:opacity-80'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        {/* Toggle Switch */}
                        <button
                          onClick={() => handleToggleRule(rule.id, enabled)}
                          className={`mt-1 relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 ${
                            enabled ? 'bg-blue-600' : 'bg-slate-600'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              enabled ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>

                        {/* Rule Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">{getCategoryIcon(rule.category)}</span>
                            <h3 className="font-medium text-white">{rule.name}</h3>
                            <span className="text-xs text-slate-400 uppercase bg-slate-900/30 px-2 py-0.5 rounded border border-slate-700/30">{rule.category.replace('_', ' ')}</span>
                          </div>
                          <p className="text-sm text-slate-400 mb-2">{rule.description}</p>
                          <code className="text-xs text-slate-500 bg-slate-900/50 px-2 py-1 rounded border border-slate-700/30 font-mono">{rule.id}</code>
                        </div>

                        {/* Severity Selector */}
                        <div className="flex-shrink-0">
                          <label className="block text-xs font-medium text-slate-400 mb-1">Severity</label>
                          <select
                            value={severity}
                            onChange={(e) => handleUpdateSeverity(rule.id, e.target.value)}
                            disabled={!enabled}
                            className={`px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                              getSeverityColor(severity)
                            } ${!enabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                          >
                            <option value="critical" className="bg-slate-800 text-red-400">Critical</option>
                            <option value="high" className="bg-slate-800 text-orange-400">High</option>
                            <option value="medium" className="bg-slate-800 text-yellow-400">Medium</option>
                            <option value="low" className="bg-slate-800 text-blue-400">Low</option>
                            <option value="info" className="bg-slate-800 text-slate-400">Info</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}

      {!selectedProjectId && (
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-12 text-center border-2 border-dashed border-slate-700/50">
          <Settings className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-300 mb-2">No Project Selected</h3>
          <p className="text-slate-500">
            Please select a project from the dropdown above to configure its analysis rules.
          </p>
        </div>
      )}
    </div>
  );
}
