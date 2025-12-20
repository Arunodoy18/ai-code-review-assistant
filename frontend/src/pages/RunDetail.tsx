import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import { Finding } from '../types'
import { ArrowLeft, AlertTriangle, ShieldAlert, Zap, Code, CheckCircle, Clock, XCircle, FileCode, Sparkles, Filter, RefreshCw, ExternalLink } from 'lucide-react'
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

  const { data: findingsData, isLoading: findingsLoading, refetch } = useQuery({
    queryKey: ['findings', runId],
    queryFn: () => api.getRunFindings(Number(runId)),
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />
      case 'running':
        return <Clock className="w-6 h-6 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-6 h-6 text-yellow-500" />
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ShieldAlert className="w-5 h-5 text-red-500" />
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-orange-500" />
      case 'medium':
        return <Zap className="w-5 h-5 text-yellow-500" />
      default:
        return <Code className="w-5 h-5 text-blue-500" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/10 text-red-400 border-red-500/30'
      case 'high':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/30'
      case 'medium':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30'
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

  const filteredByFile = useMemo(() => {
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
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <div className="text-slate-400">Loading analysis details...</div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <Link to="/" className="inline-flex items-center space-x-2 text-slate-400 hover:text-white mb-6 transition-colors group">
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        <span>Back to Dashboard</span>
      </Link>

      <div className="bg-gradient-to-br from-slate-800 to-slate-900/80 backdrop-blur-md rounded-xl p-6 mb-6 border border-slate-700/50 shadow-lg">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-slate-800/50 rounded-lg border border-slate-700/50 shadow-sm">
              {getStatusIcon(run?.status || 'pending')}
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-1">{run?.pr_title || 'Loading...'}</h1>
              <div className="flex items-center space-x-3 text-sm text-slate-400">
                <span className="bg-slate-800/50 px-2 py-0.5 rounded border border-slate-700/50">PR #{run?.pr_number}</span>
                <span>•</span>
                <span>by <span className="text-slate-300 font-medium">{run?.pr_author}</span></span>
                <span>•</span>
                <span>{formatDistanceToNow(new Date(run?.started_at || Date.now()), { addSuffix: true })}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button 
              onClick={() => refetch()} 
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-all hover:rotate-180" 
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            {run?.pr_url && (
              <a 
                href={run.pr_url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-lg text-sm transition-all shadow-lg hover:shadow-blue-500/25 hover:scale-105 flex items-center space-x-2"
              >
                <span>View on GitHub</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>

        {run?.run_metadata && (
          <div className="flex items-center space-x-6 text-sm bg-slate-900/30 p-3 rounded-lg border border-slate-700/30">
            <div className="flex items-center space-x-2">
              <FileCode className="w-4 h-4 text-blue-400" />
              <span className="text-slate-300 font-medium">{run.run_metadata.files_analyzed || 0}</span>
              <span className="text-slate-500">files analyzed</span>
            </div>
            {run.run_metadata.rule_findings !== undefined && (
              <div className="flex items-center space-x-2">
                <Code className="w-4 h-4 text-green-400" />
                <span className="text-slate-300 font-medium">{run.run_metadata.rule_findings}</span>
                <span className="text-slate-500">rule-based</span>
              </div>
            )}
            {run.run_metadata.ai_findings !== undefined && (
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span className="text-slate-300 font-medium">{run.run_metadata.ai_findings}</span>
                <span className="text-slate-500">AI insights</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {['critical', 'high', 'medium', 'low'].map((severity) => {
          const count = findings.filter((f) => f.severity === severity).length
          const Icon = severity === 'critical' ? ShieldAlert : severity === 'high' ? AlertTriangle : severity === 'medium' ? Zap : Code
          const isSelected = severityFilter === severity
          
          return (
            <button 
              key={severity} 
              onClick={() => setSeverityFilter(isSelected ? 'all' : severity)} 
              className={`
                relative overflow-hidden rounded-xl p-4 border transition-all duration-300 group
                ${isSelected 
                  ? `${getSeverityColor(severity)} ring-2 ring-offset-2 ring-offset-slate-900 shadow-lg scale-105` 
                  : `bg-slate-800/50 backdrop-blur-sm border-slate-700/50 hover:bg-slate-800 hover:border-slate-600 hover:scale-105 hover:shadow-lg`
                }
              `}
            >
              <div className="flex items-center justify-between mb-2 relative z-10">
                <Icon className={`w-6 h-6 ${isSelected ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'}`} />
                <span className="text-3xl font-bold">{count}</span>
              </div>
              <div className="text-sm uppercase font-bold tracking-wider opacity-80 relative z-10">{severity}</div>
              {isSelected && <div className="absolute inset-0 bg-white/5" />}
            </button>
          )
        })}
      </div>

      <div className="bg-slate-800/50 backdrop-blur-md rounded-xl p-4 mb-6 border border-slate-700/50 shadow-md">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-blue-400" />
              <span className="text-sm font-semibold text-slate-300">Filter:</span>
            </div>
            <select 
              value={categoryFilter} 
              onChange={(e) => setCategoryFilter(e.target.value)} 
              className="bg-slate-900/50 text-slate-300 text-sm rounded-lg px-3 py-1.5 border border-slate-600/50 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
            >
              <option value="all">All Categories</option>
              {categories.map(cat => (<option key={cat} value={cat}>{cat}</option>))}
            </select>
            <label className="flex items-center space-x-2 cursor-pointer group">
              <div className="relative">
                <input type="checkbox" checked={showAIOnly} onChange={(e) => setShowAIOnly(e.target.checked)} className="sr-only peer" />
                <div className="w-9 h-5 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
              </div>
              <span className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">AI Only</span>
            </label>
          </div>
          <div className="text-sm text-slate-400 bg-slate-900/30 px-3 py-1 rounded-full border border-slate-700/30">
            Showing {filteredFindings.length} of {findings.length} issues
          </div>
        </div>
      </div>

      {findings.length === 0 && (
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-12 text-center border-2 border-dashed border-slate-700/50">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4 drop-shadow-lg" />
          <h3 className="text-2xl font-bold text-white mb-2">No issues found!</h3>
          <p className="text-slate-400">Great job! Your code looks clean.</p>
        </div>
      )}

      {filteredFindings.length > 0 && (
        <div className="space-y-6">
          {Object.entries(filteredByFile).map(([filePath, fileFindings]) => (
            <div key={filePath} className="bg-slate-800/40 backdrop-blur-sm rounded-xl overflow-hidden border border-slate-700/50 shadow-lg hover:shadow-blue-500/5 transition-all duration-300">
              <div className="bg-gradient-to-r from-slate-800 to-slate-900/80 px-6 py-4 border-b border-slate-700/50 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileCode className="w-5 h-5 text-blue-400" />
                  <h3 className="font-mono text-sm text-white font-medium">{filePath}</h3>
                </div>
                <span className="text-xs font-medium bg-slate-700/50 text-slate-300 px-2 py-1 rounded-full border border-slate-600/50">
                  {fileFindings.length} findings
                </span>
              </div>
              <div className="divide-y divide-slate-700/50">
                {fileFindings.map((finding) => (
                  <div key={finding.id} className="p-6 hover:bg-slate-800/30 transition-colors group">
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0 mt-1 transform group-hover:scale-110 transition-transform">
                        {getSeverityIcon(finding.severity)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2 flex-wrap gap-2">
                          <h4 className="text-white font-semibold">{finding.title}</h4>
                          {finding.line_number && (<span className="text-xs px-2 py-1 bg-slate-700/50 text-slate-300 rounded border border-slate-600/50">Line {finding.line_number}</span>)}
                          {finding.is_ai_generated === 1 && (
                            <span className="text-xs px-2 py-1 bg-purple-500/10 text-purple-400 rounded border border-purple-500/20 flex items-center space-x-1">
                              <Sparkles className="w-3 h-3" />
                              <span>AI Insight</span>
                            </span>
                          )}
                        </div>
                        <p className="text-slate-300 text-sm mb-4 leading-relaxed">{finding.description}</p>
                        {finding.suggestion && (
                          <div className="bg-green-500/5 border border-green-500/10 rounded-lg p-4 mb-4 backdrop-blur-sm">
                            <div className="flex items-center space-x-2 mb-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                              <p className="text-xs font-bold text-green-400 uppercase tracking-wide">Suggestion</p>
                            </div>
                            <p className="text-sm text-green-300/90">{finding.suggestion}</p>
                          </div>
                        )}
                        {finding.code_snippet && (
                          <div className="bg-slate-950/50 rounded-lg p-4 mb-4 border border-slate-800 shadow-inner">
                            <pre className="text-xs text-slate-300 font-mono overflow-x-auto custom-scrollbar"><code>{finding.code_snippet}</code></pre>
                          </div>
                        )}
                        <div className="flex items-center space-x-3 gap-2">
                          <span className={`text-xs px-3 py-1 rounded-full border font-medium shadow-sm ${getSeverityColor(finding.severity)}`}>{finding.severity.toUpperCase()}</span>
                          <span className="text-xs px-3 py-1 bg-slate-700/50 text-slate-300 rounded-full border border-slate-600/50">{finding.category}</span>
                          {finding.rule_id && (<span className="text-xs text-slate-500 font-mono bg-slate-900/30 px-2 py-1 rounded">{finding.rule_id}</span>)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {findings.length > 0 && (
        <div className="mt-8 p-4 bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/30 text-center text-sm text-slate-500">
          Analysis completed at {format(new Date(run?.completed_at || Date.now()), 'MMM d, yyyy HH:mm:ss')}
        </div>
      )}
    </div>
  )
}
