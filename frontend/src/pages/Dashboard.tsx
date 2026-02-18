import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { AnalysisRun } from '../types'
import { formatDistanceToNow, format } from 'date-fns'
import { ExternalLink, AlertCircle, CheckCircle, Clock, XCircle, FileCode, AlertTriangle, Activity, Filter, RefreshCcw, Shield, ChevronRight } from 'lucide-react'
import { useState, useMemo } from 'react'

export default function Dashboard() {
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [timeFilter, setTimeFilter] = useState<string>('all')
  
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ['runs'],
    queryFn: () => api.getRuns({ limit: 100 }),
    refetchInterval: 10000,
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

  const runs: AnalysisRun[] = data?.data || []
  const fetchError = data?.success === false ? data?.error : null
  
  const filteredRuns = useMemo(() => {
    let filtered = runs
    if (statusFilter !== 'all') {
      filtered = filtered.filter(run => run.status === statusFilter)
    }
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
      filesAnalyzed,
      avgFindingsPerRun: completed > 0 ? Math.round(totalFindings / completed) : 0,
    }
  }, [runs])

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <Activity className="w-8 h-8 text-sand-700 mb-4 animate-pulse" />
        <div className="text-sand-600 text-sm">Loading dashboard...</div>
      </div>
    )
  }

  if (error || fetchError) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="card p-8 max-w-md text-center">
          <div className="w-12 h-12 bg-surface-3 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6 text-sand-500" />
          </div>
          <h3 className="text-lg font-bold text-sand-100 mb-2">Service Temporarily Unavailable</h3>
          <p className="text-sand-500 text-sm mb-6">
            {fetchError || 'Unable to load analysis runs. No data yet or service warming up.'}
          </p>
          <button onClick={() => refetch()} className="btn-primary w-full flex items-center justify-center space-x-2">
            <RefreshCcw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
            <span>Reconnect to Service</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-sand-100 mb-1">
            Dashboard
          </h1>
          <p className="text-sand-600 text-sm">
            Monitor code reviews and security insights across your repositories.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-8 px-3 bg-surface-1 border border-surface-4 rounded-lg flex items-center space-x-2 text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-sand-500">Live</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {runs.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
              </div>
              <span className="text-2xl font-bold text-sand-100">{stats.completed}</span>
            </div>
            <div className="text-sand-600 text-xs font-medium uppercase tracking-wider">Completed</div>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 bg-copper-500/10 border border-copper-500/20 rounded-xl flex items-center justify-center">
                <Clock className="w-4 h-4 text-copper-400" />
              </div>
              <span className="text-2xl font-bold text-sand-100">{stats.running}</span>
            </div>
            <div className="text-sand-600 text-xs font-medium uppercase tracking-wider">Running</div>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center justify-center">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
              </div>
              <span className="text-2xl font-bold text-sand-100">{stats.totalFindings}</span>
            </div>
            <div className="text-sand-600 text-xs font-medium uppercase tracking-wider">Findings</div>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 bg-sand-500/10 border border-sand-500/20 rounded-xl flex items-center justify-center">
                <FileCode className="w-4 h-4 text-sand-400" />
              </div>
              <span className="text-2xl font-bold text-sand-100">{stats.filesAnalyzed}</span>
            </div>
            <div className="text-sand-600 text-xs font-medium uppercase tracking-wider">Files Scanned</div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="space-y-6">
        {/* Filters Bar */}
        {runs.length > 0 && (
          <div className="flex flex-wrap items-center gap-3 p-2.5 bg-surface-1 rounded-xl border border-surface-4">
            <div className="flex items-center px-2 space-x-2 text-sand-600">
              <Filter className="w-4 h-4" />
              <span className="text-xs font-semibold uppercase tracking-wider">Filter</span>
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-surface-0 text-sand-300 text-sm rounded-lg px-3 py-1.5 border border-surface-4 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600 transition-colors cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
            </select>

            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="bg-surface-0 text-sand-300 text-sm rounded-lg px-3 py-1.5 border border-surface-4 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600 transition-colors cursor-pointer"
            >
              <option value="all">All Time</option>
              <option value="today">Past 24 Hours</option>
              <option value="week">Past 7 Days</option>
            </select>

            <div className="ml-auto px-3 py-1 text-xs text-sand-600 font-medium">
              {filteredRuns.length} of {runs.length}
            </div>
          </div>
        )}

        {/* Runs Grid/List */}
        {runs.length === 0 ? (
          <div className="card p-12 text-center border-dashed">
            <div className="w-14 h-14 bg-surface-3 rounded-2xl flex items-center justify-center mx-auto mb-5">
              <Activity className="w-7 h-7 text-sand-600" />
            </div>
            <h3 className="text-lg font-bold text-sand-100 mb-2">No analysis runs yet</h3>
            <p className="text-sand-500 text-sm mb-6 max-w-sm mx-auto">
              Connect a repository to start receiving AI-powered code reviews.
            </p>
            <Link to="/projects" className="btn-primary inline-flex items-center space-x-2">
              <span>Connect Repository</span>
              <ExternalLink className="w-4 h-4" />
            </Link>
          </div>
        ) : filteredRuns.length === 0 ? (
          <div className="card p-8 text-center">
            <p className="text-sand-500 text-sm mb-4">No results match your filters.</p>
            <button
              onClick={() => { setStatusFilter('all'); setTimeFilter('all'); }}
              className="btn-secondary text-xs"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredRuns.map((run) => (
              <Link
                key={run.id}
                to={`/analysis/${run.id}`}
                className="card-interactive p-4 flex items-center justify-between group"
              >
                <div className="flex items-center space-x-4">
                  <div className="p-1.5 bg-surface-3 rounded-lg border border-surface-4">
                    {getStatusIcon(run.status)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2 mb-0.5">
                      <h3 className="text-sm font-semibold text-sand-100 group-hover:text-sand-50 transition-colors">
                        {run.pr_title || `Analysis #${run.pr_number}`}
                      </h3>
                      <span className="text-[11px] text-sand-600 bg-surface-3 px-1.5 py-0.5 rounded-md font-mono">
                        #{run.pr_number}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3 text-xs text-sand-600">
                      <span>{run.pr_author}</span>
                      <span className="text-surface-4">•</span>
                      <span>{formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-5">
                  {run.status === 'completed' && run.risk_score != null && (
                    <div className={`hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                      run.risk_score >= 80 ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                      run.risk_score >= 60 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      run.risk_score >= 35 ? 'bg-copper-500/10 text-copper-400 border border-copper-500/20' :
                      'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      <Shield className="w-3.5 h-3.5" />
                      <span>{Math.round(run.risk_score)}</span>
                    </div>
                  )}
                  {run.status === 'completed' && (
                    <div className="hidden sm:flex items-center space-x-4 text-xs">
                      <div className="text-center">
                        <div className="font-semibold text-sand-200">{run.run_metadata?.findings_count || 0}</div>
                        <div className="text-sand-700">issues</div>
                      </div>
                      <div className="text-center">
                        <div className="font-semibold text-sand-200">{run.run_metadata?.files_analyzed || 0}</div>
                        <div className="text-sand-700">files</div>
                      </div>
                    </div>
                  )}
                  <ChevronRight className="w-4 h-4 text-sand-700 group-hover:text-copper-400 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* System Status Footer */}
      {runs.length > 0 && (
        <div className="flex items-center justify-center space-x-3 pt-4 border-t border-surface-4/50">
          <div className="flex items-center space-x-1.5 text-xs text-sand-600">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>All systems operational</span>
          </div>
          <span className="text-sand-800">•</span>
          <div className="text-xs text-sand-700">
            Updated {format(new Date(), 'HH:mm:ss')}
          </div>
        </div>
      )}
    </div>
  )
}
