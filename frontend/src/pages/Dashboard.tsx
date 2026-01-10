import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { AnalysisRun } from '../types'
import { formatDistanceToNow, format } from 'date-fns'
import { ExternalLink, AlertCircle, CheckCircle, Clock, XCircle, FileCode, AlertTriangle, ShieldAlert, Activity, Filter } from 'lucide-react'
import { useState, useMemo } from 'react'

export default function Dashboard() {
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [timeFilter, setTimeFilter] = useState<string>('all')
  
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['runs'],
    queryFn: () => api.getRuns({ limit: 100 }),
    refetchInterval: 10000, // Auto-refresh every 10s
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }


  // Filter and compute stats
  const runs: AnalysisRun[] = data?.data || []
  const fetchError = data?.success === false ? data?.error : null
  
  const filteredRuns = useMemo(() => {
    let filtered = runs
    
    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(run => run.status === statusFilter)
    }
    
    // Time filter
    if (timeFilter === 'today') {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      filtered = filtered.filter(run => new Date(run.started_at) >= today)
    } else if (timeFilter === 'week') {
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      filtered = filtered.filter(run => new Date(run.started_at) >= weekAgo)
    }
    
    return filtered
  }, [runs, statusFilter, timeFilter])
  
  const stats = useMemo(() => {
    const total = runs.length
    const completed = runs.filter(r => r.status === 'completed').length
    const running = runs.filter(r => r.status === 'running').length
    const failed = runs.filter(r => r.status === 'failed').length
    
    let totalFindings = 0
    let criticalFindings = 0
    let filesAnalyzed = 0
    
    runs.forEach(run => {
      if (run.run_metadata) {
        totalFindings += run.run_metadata.findings_count || 0
        filesAnalyzed += run.run_metadata.files_analyzed || 0
      }
    })
    
    return {
      total,
      completed,
      running,
      failed,
      totalFindings,
      criticalFindings,
      filesAnalyzed,
      avgFindingsPerRun: completed > 0 ? Math.round(totalFindings / completed) : 0,
    }
  }, [runs])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <div className="text-slate-400">Loading analysis runs...</div>
        </div>
      </div>
    )
  }

  if (error || fetchError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6 max-w-md">
          <div className="flex items-center space-x-3 mb-3">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <h3 className="text-lg font-semibold text-red-400">Error loading runs</h3>
          </div>
          <p className="text-red-300 text-sm mb-4">
            {fetchError || 'Failed to fetch analysis data from the server.'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm transition"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 mb-2 flex items-center space-x-3 drop-shadow-sm">
              <Activity className="w-10 h-10 text-blue-400 drop-shadow-lg" />
              <span>Analysis Dashboard</span>
            </h1>
            <p className="text-slate-400 text-lg">AI-powered code review insights</p>
          </div>
          {runs.length > 0 && (
            <div className="text-right bg-slate-800/50 backdrop-blur-sm p-4 rounded-xl border border-slate-700/50 shadow-lg">
              <div className="text-3xl font-bold text-white">{stats.total}</div>
              <div className="text-sm text-slate-400">Total Analyses</div>
            </div>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      {runs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-green-500/20 to-green-900/20 backdrop-blur-md rounded-xl p-6 border border-green-500/30 shadow-lg hover:shadow-green-500/20 hover:scale-105 transition-all duration-300 group">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-10 h-10 text-green-500 drop-shadow-md group-hover:scale-110 transition-transform" />
              <span className="text-4xl font-bold text-white drop-shadow-sm">{stats.completed}</span>
            </div>
            <div className="text-green-400 font-bold text-lg">Completed</div>
            <div className="text-xs text-slate-400 mt-1 font-medium">Successfully analyzed</div>
          </div>

          <div className="bg-gradient-to-br from-blue-500/20 to-blue-900/20 backdrop-blur-md rounded-xl p-6 border border-blue-500/30 shadow-lg hover:shadow-blue-500/20 hover:scale-105 transition-all duration-300 group">
            <div className="flex items-center justify-between mb-2">
              <Clock className="w-10 h-10 text-blue-500 animate-pulse drop-shadow-md" />
              <span className="text-4xl font-bold text-white drop-shadow-sm">{stats.running}</span>
            </div>
            <div className="text-blue-400 font-bold text-lg">Running</div>
            <div className="text-xs text-slate-400 mt-1 font-medium">Currently analyzing</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500/20 to-orange-900/20 backdrop-blur-md rounded-xl p-6 border border-orange-500/30 shadow-lg hover:shadow-orange-500/20 hover:scale-105 transition-all duration-300 group">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="w-10 h-10 text-orange-500 drop-shadow-md group-hover:rotate-12 transition-transform" />
              <span className="text-4xl font-bold text-white drop-shadow-sm">{stats.totalFindings}</span>
            </div>
            <div className="text-orange-400 font-bold text-lg">Total Findings</div>
            <div className="text-xs text-slate-400 mt-1 font-medium">{stats.avgFindingsPerRun} avg per run</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/20 to-purple-900/20 backdrop-blur-md rounded-xl p-6 border border-purple-500/30 shadow-lg hover:shadow-purple-500/20 hover:scale-105 transition-all duration-300 group">
            <div className="flex items-center justify-between mb-2">
              <FileCode className="w-10 h-10 text-purple-500 drop-shadow-md group-hover:scale-110 transition-transform" />
              <span className="text-4xl font-bold text-white drop-shadow-sm">{stats.filesAnalyzed}</span>
            </div>
            <div className="text-purple-400 font-bold text-lg">Files Analyzed</div>
            <div className="text-xs text-slate-400 mt-1 font-medium">Across all runs</div>
          </div>
        </div>
      )}

      {/* Filters */}
      {runs.length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur-md rounded-xl p-4 mb-6 border border-slate-700/50 shadow-md">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-slate-300 font-semibold">Filters:</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400 font-medium">Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-slate-900/50 text-slate-300 text-sm rounded-lg px-3 py-1.5 border border-slate-600/50 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
              >
                <option value="all">All</option>
                <option value="completed">Completed</option>
                <option value="running">Running</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400 font-medium">Time:</span>
              <select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
                className="bg-slate-900/50 text-slate-300 text-sm rounded-lg px-3 py-1.5 border border-slate-600/50 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 Days</option>
              </select>
            </div>

            <div className="ml-auto text-sm text-slate-400 font-medium bg-slate-900/30 px-3 py-1 rounded-full border border-slate-700/30">
              Showing {filteredRuns.length} of {runs.length} runs
            </div>
          </div>
        </div>
      )}

      {/* Runs List */}
      {runs.length === 0 ? (
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-12 text-center border-2 border-dashed border-slate-700/50 hover:border-slate-600 transition-colors">
          <Activity className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-300 mb-2">No analyses yet</h3>
          <p className="text-slate-500 mb-6">
            Start by connecting a repository and opening a pull request
          </p>
          <Link
            to="/projects"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-lg transition-all shadow-lg hover:shadow-blue-500/25 hover:scale-105"
          >
            <span>View Projects</span>
            <ExternalLink className="w-4 h-4" />
          </Link>
        </div>
      ) : filteredRuns.length === 0 ? (
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-8 text-center border border-slate-700/50">
          <AlertCircle className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-slate-400">No runs match the current filters</p>
          <button
            onClick={() => {
              setStatusFilter('all')
              setTimeFilter('all')
            }}
            className="mt-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition shadow-md"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredRuns.map((run) => {
            const findings = run.run_metadata?.findings_count || 0
            const files = run.run_metadata?.files_analyzed || 0
            
            return (
              <Link
                key={run.id}
                to={`/runs/${run.id}`}
                className="block bg-gradient-to-r from-slate-800 to-slate-800/50 backdrop-blur-sm rounded-xl p-5 hover:bg-slate-750 transition-all border border-slate-700/50 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/5 hover:scale-[1.01] group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="transform group-hover:scale-110 transition-transform duration-300">
                        {getStatusIcon(run.status)}
                      </div>
                      <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors">
                        {run.pr_title || `PR #${run.pr_number}`}
                      </h3>
                      <span className="text-slate-500 text-sm bg-slate-900/50 px-2 py-0.5 rounded border border-slate-700/50">#{run.pr_number}</span>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-slate-400 mb-3">
                      <span className="flex items-center space-x-1">
                        <span className="font-medium text-slate-300">{run.pr_author}</span>
                      </span>
                      <span>•</span>
                      <span>{formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}</span>
                      <span>•</span>
                      <span className="text-xs text-slate-500">
                        {format(new Date(run.started_at), 'MMM d, yyyy HH:mm')}
                      </span>
                    </div>

                    {run.status === 'completed' && findings > 0 && (
                      <div className="flex items-center space-x-3 flex-wrap gap-2">
                        <div className="flex items-center space-x-2 text-sm bg-orange-500/10 px-2 py-1 rounded-md border border-orange-500/20">
                          <ShieldAlert className="w-4 h-4 text-orange-500" />
                          <span className="text-slate-300 font-semibold">{findings}</span>
                          <span className="text-slate-500">findings</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm bg-blue-500/10 px-2 py-1 rounded-md border border-blue-500/20">
                          <FileCode className="w-4 h-4 text-blue-500" />
                          <span className="text-slate-300">{files}</span>
                          <span className="text-slate-500">files</span>
                        </div>
                      </div>
                    )}

                    {run.status === 'failed' && run.error_message && (
                      <div className="mt-2 text-xs text-red-400 bg-red-500/10 rounded px-3 py-2 border border-red-500/30">
                        Error: {run.error_message.substring(0, 100)}...
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    {run.pr_url && (
                      <a
                        href={run.pr_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-all hover:scale-110"
                        onClick={(e) => e.stopPropagation()}
                        title="View on GitHub"
                      >
                        <ExternalLink className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}

      {/* Footer info */}
      {runs.length > 0 && (
        <div className="mt-8 text-center text-sm text-slate-500">
          Auto-refreshing every 10 seconds • Last updated: {format(new Date(), 'HH:mm:ss')}
        </div>
      )}
    </div>
  )
}
