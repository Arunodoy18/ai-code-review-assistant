import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import { Finding } from '../types'
import { AlertTriangle, Zap, CheckCircle, Clock, XCircle, FileCode, Sparkles, Filter, RefreshCw, ExternalLink, ChevronRight, Eye, Shield, Copy, ThumbsDown, Wrench, FileText, ChevronDown, ChevronUp } from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { useState, useMemo } from 'react'

export default function RunDetail() {
  const { id: runId } = useParams<{ id: string }>()
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [showAIOnly, setShowAIOnly] = useState(false)
  const [expandedFixes, setExpandedFixes] = useState<Set<number>>(new Set())
  const [showSummary, setShowSummary] = useState(true)
  const queryClient = useQueryClient()

  const { data: run, isLoading: runLoading, error: runError } = useQuery({
    queryKey: ['run', runId],
    queryFn: () => api.getRun(Number(runId)),
  })

  const { data: findingsData, isLoading: findingsLoading, error: findingsError, refetch, isRefetching } = useQuery({
    queryKey: ['findings', runId],
    queryFn: () => api.getRunFindings(Number(runId)),
  })

  const { data: riskData } = useQuery({
    queryKey: ['risk-score', runId],
    queryFn: () => api.getRiskScore(Number(runId)),
    enabled: !!run && run.status === 'completed',
  })

  const { data: summaryData } = useQuery({
    queryKey: ['pr-summary', runId],
    queryFn: () => api.getPrSummary(Number(runId)),
    enabled: !!run && run.status === 'completed',
  })

  const dismissMutation = useMutation({
    mutationFn: (findingId: number) => api.dismissFinding(findingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['findings', runId] })
    },
  })

  const generateFixMutation = useMutation({
    mutationFn: (findingId: number) => api.generateFix(findingId),
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-emerald-400" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />
      case 'running':
        return <Clock className="w-5 h-5 text-copper-400 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-sand-500 animate-pulse-soft" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500/10 text-red-400 border-red-500/20'
      case 'high':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
      case 'medium':
        return 'bg-copper-500/10 text-copper-400 border-copper-500/20'
      default:
        return 'bg-sand-500/10 text-sand-400 border-sand-500/20'
    }
  }

  const findings: Finding[] = findingsData?.findings || []
  const hasError = runError || findingsError

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
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <Sparkles className="w-12 h-12 text-copper-500/50 mb-4 animate-float" />
        <div className="text-sand-500 font-medium text-lg">Processing Analysis...</div>
      </div>
    )
  }

  if (hasError) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="card p-8 max-w-md text-center">
          <div className="w-16 h-16 bg-red-500/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <AlertTriangle className="w-8 h-8 text-red-400" />
          </div>
          <h3 className="text-xl font-bold text-sand-100 mb-2">Analysis Not Found</h3>
          <p className="text-sand-500 mb-8 leading-relaxed">
            The requested analysis run could not be loaded. It may have been deleted or the service is temporarily unavailable.
          </p>
          <div className="space-y-3">
            <button onClick={() => refetch()} className="btn-primary w-full flex items-center justify-center space-x-2">
              <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
              <span>Retry Loading</span>
            </button>
            <Link to="/" className="btn-secondary w-full block text-center">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center space-x-2 text-sm">
        <Link to="/" className="text-sand-600 hover:text-copper-400 transition-colors">Dashboard</Link>
        <ChevronRight className="w-4 h-4 text-sand-800" />
        <span className="text-sand-200 font-medium">Analysis Report</span>
      </div>

      {/* Main Header Card */}
      <div className="card p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-[0.03]">
          <Eye className="w-32 h-32 text-sand-200" />
        </div>
        
        <div className="relative z-10">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="px-3 py-1 bg-surface-3 border border-surface-4 rounded-full flex items-center space-x-2">
                  {getStatusIcon(run?.status || 'pending')}
                  <span className="text-[10px] font-bold uppercase tracking-widest text-sand-500">
                    {run?.status}
                  </span>
                </div>
                {run?.is_ai_generated === 1 && (
                  <div className="px-3 py-1 bg-copper-500/10 border border-copper-500/20 rounded-full flex items-center space-x-2">
                    <Sparkles className="w-3 h-3 text-copper-400" />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-copper-400">AI Enhanced</span>
                  </div>
                )}
              </div>
              
              <h1 className="text-3xl md:text-4xl font-bold text-sand-50 tracking-tight leading-tight max-w-3xl">
                {run?.pr_title || `Analysis #${run?.pr_number}`}
              </h1>
              
              <div className="flex flex-wrap items-center gap-6 text-sm">
                <div className="flex items-center space-x-2">
                  <span className="text-sand-600">Author</span>
                  <span className="text-sand-200 font-semibold">{run?.pr_author}</span>
                </div>
                <div className="w-1 h-1 rounded-full bg-surface-4 hidden sm:block" />
                <div className="flex items-center space-x-2">
                  <span className="text-sand-600">Triggered</span>
                  <span className="text-sand-200 font-semibold">
                    {formatDistanceToNow(new Date(run?.started_at || Date.now()), { addSuffix: true })}
                  </span>
                </div>
                <div className="w-1 h-1 rounded-full bg-surface-4 hidden sm:block" />
                <div className="flex items-center space-x-2">
                  <span className="text-sand-600">PR Reference</span>
                  <span className="text-copper-400 font-mono font-bold">#{run?.pr_number}</span>
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
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-1.5 bg-surface-3/50 rounded-2xl border border-surface-4">
            <div className="bg-surface-0/60 p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-sand-100 mb-1">{run?.run_metadata?.files_analyzed || 0}</div>
              <div className="text-[10px] font-bold text-sand-700 uppercase tracking-widest">Files Scanned</div>
            </div>
            <div className="bg-surface-0/60 p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-red-400 mb-1">{findings.filter(f => f.severity === 'critical').length}</div>
              <div className="text-[10px] font-bold text-sand-700 uppercase tracking-widest">Critical</div>
            </div>
            <div className="bg-surface-0/60 p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-amber-400 mb-1">{findings.filter(f => f.severity === 'high').length}</div>
              <div className="text-[10px] font-bold text-sand-700 uppercase tracking-widest">High Severity</div>
            </div>
            <div className="bg-surface-0/60 p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-copper-400 mb-1">{findings.filter(f => f.is_ai_generated === 1).length}</div>
              <div className="text-[10px] font-bold text-sand-700 uppercase tracking-widest">AI Insights</div>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Score Panel */}
      {riskData?.risk_score != null && (
        <div className={`card p-6 relative overflow-hidden border-l-4 ${
          riskData.risk_score >= 80 ? 'border-l-red-500' :
          riskData.risk_score >= 60 ? 'border-l-amber-500' :
          riskData.risk_score >= 35 ? 'border-l-copper-500' :
          'border-l-emerald-500'
        }`}>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center space-x-6">
              <div className={`w-20 h-20 rounded-2xl flex flex-col items-center justify-center ${
                riskData.risk_score >= 80 ? 'bg-red-500/10' :
                riskData.risk_score >= 60 ? 'bg-amber-500/10' :
                riskData.risk_score >= 35 ? 'bg-copper-500/10' :
                'bg-emerald-500/10'
              }`}>
                <Shield className={`w-6 h-6 mb-1 ${
                  riskData.risk_score >= 80 ? 'text-red-400' :
                  riskData.risk_score >= 60 ? 'text-amber-400' :
                  riskData.risk_score >= 35 ? 'text-copper-400' :
                  'text-emerald-400'
                }`} />
                <span className={`text-2xl font-black ${
                  riskData.risk_score >= 80 ? 'text-red-400' :
                  riskData.risk_score >= 60 ? 'text-amber-400' :
                  riskData.risk_score >= 35 ? 'text-copper-400' :
                  'text-emerald-400'
                }`}>{Math.round(riskData.risk_score)}</span>
              </div>
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-sand-600 mb-1">PR Risk Score</div>
                <div className={`text-lg font-bold capitalize ${
                  riskData.risk_score >= 80 ? 'text-red-400' :
                  riskData.risk_score >= 60 ? 'text-amber-400' :
                  riskData.risk_score >= 35 ? 'text-copper-400' :
                  'text-emerald-400'
                }`}>
                  {riskData.risk_score >= 80 ? 'Critical Risk' :
                   riskData.risk_score >= 60 ? 'High Risk' :
                   riskData.risk_score >= 35 ? 'Medium Risk' :
                   'Low Risk'}
                </div>
                {riskData.risk_breakdown?.explanation && (
                  <p className="text-sand-500 text-sm mt-1 max-w-2xl">{riskData.risk_breakdown.explanation}</p>
                )}
              </div>
            </div>
            {riskData.risk_breakdown?.breakdown && (
              <div className="grid grid-cols-5 gap-3 text-center">
                {([
                  ['Size', riskData.risk_breakdown.breakdown.size_impact],
                  ['Severity', riskData.risk_breakdown.breakdown.severity_impact],
                  ['Blast', riskData.risk_breakdown.breakdown.blast_radius],
                  ['Complex', riskData.risk_breakdown.breakdown.complexity],
                  ['AI Adj', riskData.risk_breakdown.breakdown.ai_adjustment],
                ] as [string, number | undefined][]).map(([label, value]) => (
                  <div key={label} className="bg-surface-3 rounded-lg p-2 border border-surface-4">
                    <div className="text-sm font-bold text-sand-200">{value ?? 0}</div>
                    <div className="text-[9px] font-bold text-sand-700 uppercase tracking-widest">{label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* PR Summary for Stakeholders */}
      {summaryData?.has_summary && (
        <div className="card p-6 relative overflow-hidden">
          <button
            onClick={() => setShowSummary(!showSummary)}
            className="flex items-center justify-between w-full text-left"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-copper-500/10 border border-copper-500/20 rounded-xl">
                <FileText className="w-5 h-5 text-copper-400" />
              </div>
              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-sand-600">AI Summary</div>
                <div className="text-sm font-semibold text-sand-200">Plain English PR Summary</div>
              </div>
            </div>
            {showSummary ? <ChevronUp className="w-5 h-5 text-sand-600" /> : <ChevronDown className="w-5 h-5 text-sand-600" />}
          </button>
          {showSummary && (
            <div className="mt-4 pl-14">
              <p className="text-sand-400 text-sm leading-relaxed whitespace-pre-wrap">{summaryData.pr_summary}</p>
            </div>
          )}
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-6 pb-2">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 text-sand-600">
            <Filter className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-widest">Filter Results</span>
          </div>
          
          <select 
            value={severityFilter} 
            onChange={(e) => setSeverityFilter(e.target.value)} 
            className="bg-surface-1 text-sand-300 text-xs rounded-lg px-4 py-2 border border-surface-4 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600 transition-all cursor-pointer"
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
            className="bg-surface-1 text-sand-300 text-xs rounded-lg px-4 py-2 border border-surface-4 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600 transition-all cursor-pointer"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (<option key={cat} value={cat}>{cat}</option>))}
          </select>

          <button
            onClick={() => setShowAIOnly(!showAIOnly)}
            className={`px-4 py-2 rounded-lg text-xs font-medium border transition-all flex items-center space-x-2 ${
              showAIOnly 
                ? 'bg-copper-500/10 border-copper-500/30 text-copper-300 shadow-glow' 
                : 'bg-surface-1 border-surface-4 text-sand-500 hover:text-sand-200 hover:border-surface-4'
            }`}
          >
            <Sparkles className={`w-3.5 h-3.5 ${showAIOnly ? 'animate-pulse' : ''}`} />
            <span>AI Discoveries</span>
          </button>
        </div>
        
        <div className="text-xs text-sand-600 font-medium">
          Showing <span className="text-sand-200">{filteredFindings.length}</span> results
        </div>
      </div>

      {/* Findings List */}
      {filteredFindings.length === 0 ? (
        <div className="card p-16 text-center border-dashed">
          <div className="w-20 h-20 bg-emerald-500/5 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-emerald-500/40" />
          </div>
          <h3 className="text-xl font-bold text-sand-100 mb-2">No findings reported</h3>
          <p className="text-sand-500 max-w-sm mx-auto leading-relaxed">
            Your code passed all automated checks and AI security reviews. No issues detected in this analysis run.
          </p>
        </div>
      ) : (
        <div className="space-y-10">
          {Object.entries(groupedByFile).map(([filePath, fileFindings]) => (
            <div key={filePath} className="space-y-4">
              <div className="flex items-center space-x-3 px-2">
                <FileCode className="w-5 h-5 text-copper-400" />
                <h3 className="font-mono text-sm text-sand-300 font-semibold">{filePath}</h3>
                <div className="h-[1px] flex-1 bg-surface-4/50" />
                <span className="text-[10px] font-bold uppercase tracking-widest text-sand-700">
                  {fileFindings.length} {fileFindings.length === 1 ? 'Finding' : 'Findings'}
                </span>
              </div>
              
              <div className="space-y-4">
                {fileFindings.map((finding) => (
                  <div key={finding.id} className="card p-0 overflow-hidden group">
                    <div className="flex flex-col md:flex-row">
                      {/* Left Severity Stripe */}
                      <div className={`w-full h-1 md:w-1.5 md:h-auto self-stretch ${
                        finding.severity === 'critical' ? 'bg-red-500' : 
                        finding.severity === 'high' ? 'bg-amber-500' : 
                        finding.severity === 'medium' ? 'bg-copper-500' : 'bg-sand-700'
                      }`} />
                      
                      <div className="flex-1 p-6">
                        <div className="flex items-start justify-between mb-4 gap-4">
                          <div className="space-y-2">
                            <div className="flex items-center space-x-3 flex-wrap gap-2">
                              <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest border ${getSeverityColor(finding.severity)}`}>
                                {finding.severity}
                              </span>
                              <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest text-sand-500 bg-surface-3 border border-surface-4">
                                {finding.category}
                              </span>
                              {finding.is_ai_generated === 1 && (
                                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-widest text-copper-400 bg-copper-500/10 border border-copper-500/20 flex items-center space-x-1.5">
                                  <Sparkles className="w-3 h-3" />
                                  <span>AI Analysis</span>
                                </span>
                              )}
                            </div>
                            <h4 className="text-lg font-bold text-sand-100 group-hover:text-copper-300 transition-colors">
                              {finding.title}
                            </h4>
                          </div>
                          
                          {finding.line_number && (
                            <div className="text-right">
                              <div className="text-[10px] font-bold text-sand-700 uppercase tracking-widest mb-1">Location</div>
                              <div className="font-mono text-sm text-copper-400 bg-copper-500/5 px-3 py-1 rounded-lg border border-copper-500/10">
                                Line {finding.line_number}
                              </div>
                            </div>
                          )}
                        </div>

                        <p className="text-sand-500 text-sm leading-relaxed mb-6 max-w-4xl">
                          {finding.description}
                        </p>

                        {finding.suggestion && (
                          <div className="mb-6 bg-emerald-500/[0.03] border border-emerald-500/10 rounded-xl p-5 relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/30" />
                            <div className="flex items-start space-x-4">
                              <div className="p-1.5 bg-emerald-500/10 rounded-lg">
                                <Zap className="w-4 h-4 text-emerald-400" />
                              </div>
                              <div className="space-y-1">
                                <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Recommended Action</div>
                                <p className="text-sand-200 text-sm font-medium leading-relaxed">
                                  {finding.suggestion}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {finding.code_snippet && (
                          <div className="relative rounded-xl overflow-hidden border border-surface-4 bg-surface-0/80">
                            <div className="flex items-center justify-between px-4 py-2 bg-surface-3/50 border-b border-surface-4">
                              <span className="text-[10px] font-bold text-sand-700 uppercase tracking-widest">Contextual Code Snippet</span>
                              <div className="flex space-x-1.5">
                                <div className="w-2 h-2 rounded-full bg-surface-4" />
                                <div className="w-2 h-2 rounded-full bg-surface-4" />
                                <div className="w-2 h-2 rounded-full bg-surface-4" />
                              </div>
                            </div>
                            <pre className="p-4 text-xs font-mono text-sand-300 overflow-x-auto selection:bg-copper-500/30">
                              <code>{finding.code_snippet}</code>
                            </pre>
                          </div>
                        )}

                        {/* Auto-Fix Panel */}
                        {(finding.auto_fix_code || finding.severity === 'critical' || finding.severity === 'high') && (
                          <div className="mt-4">
                            <button
                              onClick={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                                const newSet = new Set(expandedFixes)
                                if (newSet.has(finding.id)) {
                                  newSet.delete(finding.id)
                                } else {
                                  newSet.add(finding.id)
                                  if (!finding.auto_fix_code) {
                                    generateFixMutation.mutate(finding.id)
                                  }
                                }
                                setExpandedFixes(newSet)
                              }}
                              className="flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-medium bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 transition-all"
                            >
                              <Wrench className="w-3.5 h-3.5" />
                              <span>{finding.auto_fix_code ? 'View AI Fix' : 'Generate AI Fix'}</span>
                              {expandedFixes.has(finding.id) ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </button>
                            
                            {expandedFixes.has(finding.id) && (
                              <div className="mt-3 relative rounded-xl overflow-hidden border border-emerald-500/10 bg-surface-0/80">
                                <div className="flex items-center justify-between px-4 py-2 bg-emerald-500/5 border-b border-emerald-500/10">
                                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest flex items-center space-x-2">
                                    <Sparkles className="w-3 h-3" />
                                    <span>AI-Generated Fix</span>
                                  </span>
                                  {(finding.auto_fix_code || generateFixMutation.data?.auto_fix_code) && (
                                    <button
                                      onClick={(e) => {
                                        e.preventDefault()
                                        e.stopPropagation()
                                        navigator.clipboard.writeText(finding.auto_fix_code || generateFixMutation.data?.auto_fix_code || '')
                                      }}
                                      className="flex items-center space-x-1 px-2 py-1 rounded text-[10px] text-sand-500 hover:text-sand-200 hover:bg-surface-3 transition-all"
                                    >
                                      <Copy className="w-3 h-3" />
                                      <span>Copy Patch</span>
                                    </button>
                                  )}
                                </div>
                                <pre className="p-4 text-xs font-mono text-sand-300 overflow-x-auto selection:bg-emerald-500/30">
                                  <code>{
                                    generateFixMutation.isPending ? 'Generating fix...' :
                                    (finding.auto_fix_code || generateFixMutation.data?.auto_fix_code || 'No fix available')
                                  }</code>
                                </pre>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex items-center space-x-3 mt-4 pt-4 border-t border-surface-4/50">
                          {finding.is_dismissed !== 1 && (
                            <button
                              onClick={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                                dismissMutation.mutate(finding.id)
                              }}
                              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-sand-500 hover:text-amber-400 hover:bg-amber-500/10 border border-surface-4 hover:border-amber-500/20 transition-all"
                            >
                              <ThumbsDown className="w-3.5 h-3.5" />
                              <span>Not a Bug</span>
                            </button>
                          )}
                          {finding.is_dismissed === 1 && (
                            <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-amber-400 bg-amber-500/10 border border-amber-500/20">
                              <ThumbsDown className="w-3.5 h-3.5" />
                              <span>Dismissed — Pattern learned</span>
                            </span>
                          )}
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

      {/* Footer System Status */}
      <div className="pt-12 pb-6 flex items-center justify-center border-t border-surface-4/50">
        <div className="text-xs text-sand-700 font-medium flex items-center space-x-2">
          <Clock className="w-3.5 h-3.5" />
          <span>Report generated {format(new Date(run?.completed_at || Date.now()), 'MMMM do, yyyy HH:mm:ss')}</span>
        </div>
      </div>
    </div>
  )
}
