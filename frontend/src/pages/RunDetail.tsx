import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import { Finding } from '../types'
import { ArrowLeft, AlertTriangle, ShieldAlert, Zap, Code, CheckCircle, Clock, XCircle, FileCode, Sparkles, Filter, RefreshCw, ExternalLink, ChevronRight } from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { useState, useMemo } from 'react'

export default function RunDetail() {
  const { runId } = useParams<{ runId: string }>()
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [showAIOnly, setShowAIOnly] = useState(false)

  const { data: run, isLoading: runLoading } = useQuery({
    queryKey: ['run', runId],
    queryFn: () => api.getRun(Number(runId)),
  })

  const { data: findingsData, isLoading: findingsLoading, refetch, isRefetching } = useQuery({
    queryKey: ['findings', runId],
    queryFn: () => api.getRunFindings(Number(runId)),
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-emerald-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-amber-500" />
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ShieldAlert className="w-5 h-5 text-red-500" />
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-amber-500" />
      case 'medium':
        return <Zap className="w-5 h-5 text-indigo-400" />
      default:
        return <Code className="w-5 h-5 text-slate-400" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/10 text-red-400 border-red-500/20'
      case 'high':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      case 'medium':
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20'
    }
  }

  const findings: Finding[] = findingsData?.findings || []

  const filteredFindings = useMemo(() => {
    return findings.filter(finding => {
      if (severityFilter !== 'all' && finding.severity !== severityFilter) return false
      if (categoryFilter !== 'all' && finding.category !== categoryFilter) return false
      if (showAIOnly && finding.is_ai_generated !== 1) return false
      return true
    })
  }, [findings, severityFilter, categoryFilter, showAIOnly])

  const groupedByFile = useMemo(() => {
    const grouped: Record<string, Finding[]> = {}
    filteredFindings.forEach(finding => {
      if (!grouped[finding.file_path]) {
        grouped[finding.file_path] = []
      }
      grouped[finding.file_path].push(finding)
    })
    return grouped
  }, [filteredFindings])

  const categories = useMemo(() => {
    return Array.from(new Set(findings.map(f => f.category)))
  }, [findings])

  if (runLoading || findingsLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] animate-pulse">
        <Sparkles className="w-12 h-12 text-indigo-500/50 mb-4 animate-bounce" />
        <div className="text-slate-500 font-medium text-lg">Processing Analysis...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center space-x-2 text-sm">
        <Link to="/" className="text-slate-500 hover:text-indigo-400 transition-colors">Dashboard</Link>
        <ChevronRight className="w-4 h-4 text-slate-700" />
        <span className="text-slate-100 font-medium">Analysis Report</span>
      </div>

      {/* Main Header Card */}
      <div className="card-premium p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5">
          <GitPullRequest className="w-32 h-32 text-white" />
        </div>
        
        <div className="relative z-10">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full flex items-center space-x-2">
                  {getStatusIcon(run?.status || 'pending')}
                  <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                    {run?.status}
                  </span>
                </div>
                {run?.is_ai_generated === 1 && (
                  <div className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full flex items-center space-x-2">
                    <Sparkles className="w-3 h-3 text-indigo-400" />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">AI Enhanced</span>
                  </div>
                )}
              </div>
              
              <h1 className="text-4xl font-bold text-white tracking-tight leading-tight max-w-3xl">
                {run?.pr_title || `Analysis #${run?.pr_number}`}
              </h1>
              
              <div className="flex flex-wrap items-center gap-6 text-sm">
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500">Author</span>
                  <span className="text-slate-200 font-semibold">{run?.pr_author}</span>
                </div>
                <div className="w-1 h-1 rounded-full bg-slate-700 hidden sm:block" />
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500">Triggered</span>
                  <span className="text-slate-200 font-semibold">
                    {formatDistanceToNow(new Date(run?.started_at || Date.now()), { addSuffix: true })}
                  </span>
                </div>
                <div className="w-1 h-1 rounded-full bg-slate-700 hidden sm:block" />
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500">PR Reference</span>
                  <span className="text-indigo-400 font-mono font-bold">#{run?.pr_number}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button 
                onClick={() => refetch()} 
                className="btn-secondary p-2.5" 
                title="Refresh Findings"
              >
                <RefreshCw className={`w-5 h-5 ${isRefetching ? 'animate-spin' : ''}`} />
              </button>
              {run?.pr_url && (
                <a 
                  href={run.pr_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="btn-primary flex items-center space-x-2 px-6"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>View Pull Request</span>
                </a>
              )}
            </div>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-1 bg-white/5 rounded-2xl border border-white/5">
            <div className="bg-[#0b1220]/50 p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-white mb-1">{run?.run_metadata?.files_analyzed || 0}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Files Scanned</div>
            </div>
            <div className="bg-[#0b1220]/50 p-4 rounded-xl text-center border-l border-white/5">
              <div className="text-2xl font-bold text-red-400 mb-1">{findings.filter(f => f.severity === 'critical').length}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Critical</div>
            </div>
            <div className="bg-[#0b1220]/50 p-4 rounded-xl text-center border-l border-white/5">
              <div className="text-2xl font-bold text-amber-400 mb-1">{findings.filter(f => f.severity === 'high').length}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">High Severity</div>
            </div>
            <div className="bg-[#0b1220]/50 p-4 rounded-xl text-center border-l border-white/5">
              <div className="text-2xl font-bold text-indigo-400 mb-1">{findings.filter(f => f.is_ai_generated === 1).length}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">AI Insights</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-6 pb-2">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 text-slate-400">
            <Filter className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-widest">Filter Results</span>
          </div>
          
          <select 
            value={severityFilter} 
            onChange={(e) => setSeverityFilter(e.target.value)} 
            className="bg-[#0f172a] text-slate-300 text-xs rounded-lg px-4 py-2 border border-white/10 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all cursor-pointer"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical Only</option>
            <option value="high">High Severity</option>
            <option value="medium">Medium Severity</option>
            <option value="low">Low Severity</option>
          </select>

          <select 
            value={categoryFilter} 
            onChange={(e) => setCategoryFilter(e.target.value)} 
            className="bg-[#0f172a] text-slate-300 text-xs rounded-lg px-4 py-2 border border-white/10 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all cursor-pointer"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (<option key={cat} value={cat}>{cat}</option>))}
          </select>

          <button
            onClick={() => setShowAIOnly(!showAIOnly)}
            className={`px-4 py-2 rounded-lg text-xs font-medium border transition-all flex items-center space-x-2 ${
              showAIOnly 
                ? 'bg-indigo-500/10 border-indigo-500/40 text-indigo-300 shadow-[0_0_15px_rgba(79,70,229,0.1)]' 
                : 'bg-[#0f172a] border-white/10 text-slate-400 hover:text-white hover:border-white/20'
            }`}
          >
            <Sparkles className={`w-3.5 h-3.5 ${showAIOnly ? 'animate-pulse' : ''}`} />
            <span>AI Discoveries</span>
          </button>
        </div>
        
        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="text-slate-200">{filteredFindings.length}</span> results
        </div>
      </div>

      {/* Findings List */}
      {filteredFindings.length === 0 ? (
        <div className="card-premium p-16 text-center border-dashed border-white/10">
          <div className="w-20 h-20 bg-emerald-500/5 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-emerald-500/40" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No findings reported</h3>
          <p className="text-slate-400 max-w-sm mx-auto leading-relaxed">
            Your code passed all automated checks and AI security reviews. No issues detected in this analysis run.
          </p>
        </div>
      ) : (
        <div className="space-y-10">
          {Object.entries(groupedByFile).map(([filePath, fileFindings]) => (
            <div key={filePath} className="space-y-4">
              <div className="flex items-center space-x-3 px-2">
                <FileCode className="w-5 h-5 text-indigo-400" />
                <h3 className="font-mono text-sm text-slate-300 font-semibold">{filePath}</h3>
                <div className="h-[1px] flex-1 bg-white/5" />
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                  {fileFindings.length} {fileFindings.length === 1 ? 'Finding' : 'Findings'}
                </span>
              </div>
              
              <div className="space-y-4">
                {fileFindings.map((finding) => (
                  <div key={finding.id} className="card-premium p-0 overflow-hidden group">
                    <div className="flex flex-col md:flex-row">
                      {/* Left Severity Stripe */}
                      <div className={`w-1 md:w-1.5 self-stretch ${
                        finding.severity === 'critical' ? 'bg-red-500' : 
                        finding.severity === 'high' ? 'bg-amber-500' : 
                        finding.severity === 'medium' ? 'bg-indigo-500' : 'bg-slate-700'
                      }`} />
                      
                      <div className="flex-1 p-6">
                        <div className="flex items-start justify-between mb-4 gap-4">
                          <div className="space-y-2">
                            <div className="flex items-center space-x-3 flex-wrap gap-2">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest border shadow-sm ${getSeverityColor(finding.severity)}`}>
                                {finding.severity}
                              </span>
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest text-slate-500 bg-white/5 border border-white/5">
                                {finding.category}
                              </span>
                              {finding.is_ai_generated === 1 && (
                                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 flex items-center space-x-1.5">
                                  <Sparkles className="w-3 h-3" />
                                  <span>AI Analysis</span>
                                </span>
                              )}
                            </div>
                            <h4 className="text-lg font-bold text-white group-hover:text-indigo-300 transition-colors">
                              {finding.title}
                            </h4>
                          </div>
                          
                          {finding.line_number && (
                            <div className="text-right">
                              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Location</div>
                              <div className="font-mono text-sm text-indigo-400 bg-indigo-500/5 px-3 py-1 rounded border border-indigo-500/10">
                                Line {finding.line_number}
                              </div>
                            </div>
                          )}
                        </div>

                        <p className="text-slate-400 text-sm leading-relaxed mb-6 max-w-4xl">
                          {finding.description}
                        </p>

                        {finding.suggestion && (
                          <div className="mb-6 bg-emerald-500/[0.03] border border-emerald-500/10 rounded-xl p-5 relative overflow-hidden group/suggestion">
                            <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/30" />
                            <div className="flex items-start space-x-4">
                              <div className="p-1.5 bg-emerald-500/10 rounded-lg">
                                <Zap className="w-4 h-4 text-emerald-500" />
                              </div>
                              <div className="space-y-1">
                                <div className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">Recommended Action</div>
                                <p className="text-slate-200 text-sm font-medium leading-relaxed">
                                  {finding.suggestion}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {finding.code_snippet && (
                          <div className="relative rounded-xl overflow-hidden border border-white/5 shadow-inner bg-black/40 group/code">
                            <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/5">
                              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Contextual Code Snippet</span>
                              <div className="flex space-x-1.5">
                                <div className="w-2 h-2 rounded-full bg-white/5" />
                                <div className="w-2 h-2 rounded-full bg-white/5" />
                                <div className="w-2 h-2 rounded-full bg-white/5" />
                              </div>
                            </div>
                            <pre className="p-4 text-xs font-mono text-slate-300 overflow-x-auto selection:bg-indigo-500/40">
                              <code>{finding.code_snippet}</code>
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Footer System Status */}
      <div className="pt-12 pb-6 flex items-center justify-center border-t border-white/5">
        <div className="text-xs text-slate-600 font-medium flex items-center space-x-2">
          <Clock className="w-3.5 h-3.5" />
          <span>Report generated {format(new Date(run?.completed_at || Date.now()), 'MMMM do, yyyy HH:mm:ss')}</span>
        </div>
      </div>
    </div>
  )
}
