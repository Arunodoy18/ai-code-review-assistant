import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api as apiClient } from '../api/client';
import { Settings, ShieldAlert, Sliders, Search, Filter, CheckCircle2, AlertCircle } from 'lucide-react';

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
  name: string;
  github_repo_full_name: string;
}

export default function Configuration() {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all projects
  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: apiClient.getProjects
  });

  // Fetch all available rules
  const { data: rules = [] } = useQuery<Rule[]>({
    queryKey: ['rules'],
    queryFn: async () => {
      const response = await (apiClient as any).getRules();
      return response;
    }
  });

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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'medium': return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20';
      default: return 'text-slate-400 bg-white/5 border-white/5';
    }
  };

  return (
    <div className="space-y-10 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">System Configuration</h1>
          <p className="text-slate-400 max-w-2xl leading-relaxed">
            Fine-tune analysis parameters and security rules to match your organization's coding standards.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-widest text-slate-500 bg-white/5 px-4 py-2 rounded-lg border border-white/5">
          <Settings className="w-4 h-4" />
          <span>Global Settings</span>
        </div>
      </div>

      {/* Project Selector */}
      <div className="card-premium p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-indigo-500/10 rounded-lg">
            <Sliders className="w-5 h-5 text-indigo-400" />
          </div>
          <h2 className="text-xl font-bold text-white">Project Context</h2>
        </div>
        
        <div className="relative group">
          <select
            value={selectedProjectId || ''}
            onChange={(e) => setSelectedProjectId(Number(e.target.value) || null)}
            className="w-full h-12 pl-4 pr-10 bg-[#0b1220] border border-white/10 rounded-xl text-slate-200 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all appearance-none cursor-pointer"
          >
            <option value="">Select a repository to configure...</option>
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                {project.github_repo_full_name}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none text-slate-500">
            <Filter className="w-4 h-4" />
          </div>
        </div>
      </div>

      {selectedProjectId ? (
        <div className="space-y-8">
          {/* Analysis Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="card-premium p-8">
              <h3 className="text-lg font-bold text-white mb-6 flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                <span>Thresholds</span>
              </h3>
              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                    Maximum findings per rule
                  </label>
                  <input
                    type="number"
                    value={config?.analysis_config.max_findings_per_rule || 10}
                    onChange={(e) => updateConfigMutation.mutate({ 
                      analysis_config: { ...config!.analysis_config, max_findings_per_rule: Number(e.target.value) } 
                    })}
                    className="w-full h-11 px-4 bg-[#0b1220] border border-white/10 rounded-xl text-white focus:border-indigo-500 focus:outline-none transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="card-premium p-8">
              <h3 className="text-lg font-bold text-white mb-6 flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-indigo-400" />
                <span>Scope</span>
              </h3>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                  Target File Extensions
                </label>
                <div className="flex flex-wrap gap-2">
                  {(config?.analysis_config.file_extensions || ['.py', '.js', '.ts']).map(ext => (
                    <span key={ext} className="px-3 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-lg text-sm font-mono">
                      {ext}
                    </span>
                  ))}
                  <button className="px-3 py-1 bg-white/5 border border-dashed border-white/10 text-slate-500 rounded-lg text-sm hover:text-white hover:border-white/20 transition-all">
                    + Add
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Rules Configuration */}
          <div className="card-premium p-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
              <h2 className="text-xl font-bold text-white flex items-center space-x-3">
                <ShieldAlert className="w-6 h-6 text-indigo-400" />
                <span>Analysis Rules Engine</span>
              </h2>
              
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search rules..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-64 h-10 pl-10 pr-4 bg-[#0b1220] border border-white/10 rounded-xl text-sm text-white focus:border-indigo-500 focus:outline-none transition-all"
                  />
                </div>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="h-10 px-4 bg-[#0b1220] border border-white/10 rounded-xl text-sm text-slate-300 focus:border-indigo-500 focus:outline-none transition-all cursor-pointer"
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

            <div className="grid gap-4">
              {configLoading ? (
                <div className="text-center py-20 text-slate-600 animate-pulse uppercase tracking-widest text-xs font-bold">
                  Synchronizing Rule Registry...
                </div>
              ) : filteredRules.length === 0 ? (
                <div className="text-center py-20 bg-white/5 rounded-2xl border border-dashed border-white/5">
                  <p className="text-slate-500 font-medium">No rules match your search parameters.</p>
                </div>
              ) : (
                filteredRules.map(rule => {
                  const enabled = isRuleEnabled(rule.id);
                  const severity = getRuleSeverity(rule);
                  
                  return (
                    <div
                      key={rule.id}
                      className={`group p-6 rounded-2xl border transition-all duration-300 ${
                        enabled 
                          ? 'bg-white/[0.02] border-white/5 hover:border-white/10 hover:bg-white/[0.04]' 
                          : 'bg-black/20 border-white/[0.02] opacity-50'
                      }`}
                    >
                      <div className="flex items-start gap-6">
                        <button
                          className={`mt-1 relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                            enabled ? 'bg-indigo-500' : 'bg-slate-700'
                          }`}
                        >
                          <span
                            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                              enabled ? 'translate-x-5' : 'translate-x-0'
                            }`}
                          />
                        </button>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-bold text-white group-hover:text-indigo-300 transition-colors">{rule.name}</h3>
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded">
                              {rule.category.replace('_', ' ')}
                            </span>
                          </div>
                          <p className="text-sm text-slate-400 leading-relaxed mb-3">{rule.description}</p>
                          <code className="text-[10px] font-mono text-slate-600 bg-black/40 px-2 py-1 rounded border border-white/5">{rule.id}</code>
                        </div>

                        <div className="shrink-0 flex flex-col items-end gap-2">
                          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Severity</span>
                          <select
                            value={severity}
                            disabled={!enabled}
                            className={`px-3 py-1.5 text-xs font-bold rounded-lg border focus:outline-none transition-all cursor-pointer ${
                              getSeverityColor(severity)
                            } ${!enabled ? 'cursor-not-allowed opacity-50' : ''}`}
                          >
                            <option value="critical">CRITICAL</option>
                            <option value="high">HIGH</option>
                            <option value="medium">MEDIUM</option>
                            <option value="low">LOW</option>
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
        <div className="card-premium p-20 text-center border-dashed border-white/10">
          <div className="w-20 h-20 bg-indigo-500/5 rounded-full flex items-center justify-center mx-auto mb-6">
            <Sliders className="w-10 h-10 text-slate-600" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No Context Selected</h3>
          <p className="text-slate-400 max-w-sm mx-auto leading-relaxed">
            Please choose a repository from the project selector to view and manage its specific analysis configuration.
          </p>
        </div>
      )}
    </div>
  );
}
