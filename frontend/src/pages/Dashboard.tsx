import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { AnalysisRun } from '../types'
import { formatDistanceToNow, format } from 'date-fns'
import { ExternalLink, AlertCircle, CheckCircle, Clock, XCircle, FileCode, AlertTriangle, Activity, Filter, RefreshCcw } from 'lucide-react'
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
        return <CheckCircle className="w-5 h-5 text-emerald-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-amber-500" />
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
    console.log('[Dashboard] Rendering loading state')
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <Activity className="w-8 h-8 text-neutral-600 mb-4 animate-pulse" />
        <div className="text-neutral-500 text-sm">Loading dashboard...</div>
      </div>
    )
  }

  if (error || fetchError) {
    console.log('[Dashboard] Rendering error state', error, fetchError)
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="glass-panel p-8 max-w-md text-center">
          <div className="w-12 h-12 bg-neutral-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6 text-neutral-400" />
          </div>
          <h3 className="text-lg font-semibold text-neutral-100 mb-2">Service Temporarily Unavailable</h3>
          <p className="text-neutral-400 text-sm mb-6">
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

  console.log('[Dashboard] Rendering success state with data:', runs.length, 'runs')

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-100 mb-1">
            Dashboard
          </h1>
          <p className="text-neutral-500 text-sm">
            Monitor code reviews and security insights across your repositories.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-8 px-3 bg-neutral-900 border border-neutral-800 rounded-md flex items-center space-x-2 text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
            <span className="text-neutral-400">Live</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {runs.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card-premium p-4">
            <div className="flex items-center justify-between mb-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-xl font-semibold text-neutral-100">{stats.completed}</span>
            </div>
            <div className="text-neutral-500 text-xs">Completed</div>
          </div>

          <div className="card-premium p-4">
            <div className="flex items-center justify-between mb-3">
              <Clock className="w-5 h-5 text-blue-500" />
              <span className="text-xl font-semibold text-neutral-100">{stats.running}</span>
            </div>
            <div className="text-neutral-500 text-xs">Running</div>
          </div>

          <div className="card-premium p-4">
            <div className="flex items-center justify-between mb-3">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              <span className="text-xl font-semibold text-neutral-100">{stats.totalFindings}</span>
            </div>
            <div className="text-neutral-500 text-xs">Findings</div>
          </div>

          <div className="card-premium p-4">
            <div className="flex items-center justify-between mb-3">
              <FileCode className="w-5 h-5 text-neutral-400" />
              <span className="text-xl font-semibold text-neutral-100">{stats.filesAnalyzed}</span>
            </div>
            <div className="text-neutral-500 text-xs">Files Scanned</div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="space-y-6">
        {/* Filters Bar */}
        {runs.length > 0 && (
          <div className="flex flex-wrap items-center gap-3 p-2 bg-neutral-900 rounded-lg border border-neutral-800">
            <div className="flex items-center px-2 space-x-2 text-neutral-500">
              <Filter className="w-4 h-4" />
              <span className="text-xs font-medium">Filter</span>
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-neutral-950 text-neutral-300 text-sm rounded-md px-3 py-1.5 border border-neutral-800 focus:border-neutral-700 focus:outline-none transition-colors cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
            </select>

            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="bg-neutral-950 text-neutral-300 text-sm rounded-md px-3 py-1.5 border border-neutral-800 focus:border-neutral-700 focus:outline-none transition-colors cursor-pointer"
            >
              <option value="all">All Time</option>
              <option value="today">Past 24 Hours</option>
              <option value="week">Past 7 Days</option>
            </select>

            <div className="ml-auto px-3 py-1 text-xs text-neutral-500">
              {filteredRuns.length} of {runs.length}
            </div>
          </div>
        )}

        {/* Runs Grid/List */}
        {runs.length === 0 ? (
          <div className="card-premium p-12 text-center border-dashed">
            <div className="w-12 h-12 bg-neutral-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Activity className="w-6 h-6 text-neutral-500" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-100 mb-2">No analysis runs yet</h3>
            <p className="text-neutral-500 text-sm mb-6 max-w-sm mx-auto">
              Connect a repository to start receiving AI-powered code reviews.
            </p>
            <Link to="/projects" className="btn-primary inline-flex items-center space-x-2">
              <span>Connect Repository</span>
              <ExternalLink className="w-4 h-4" />
            </Link>
          </div>
        ) : filteredRuns.length === 0 ? (
          <div className="card-premium p-8 text-center">
            <p className="text-neutral-500 text-sm mb-4">No results match your filters.</p>
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
                to={`/runs/${run.id}`}
                className="card-premium p-4 flex items-center justify-between group"
              >
                <div className="flex items-center space-x-4">
                  <div className="p-1.5 bg-neutral-800 rounded-md">
                    {getStatusIcon(run.status)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2 mb-0.5">
                      <h3 className="text-sm font-medium text-neutral-100 group-hover:text-white transition-colors">
                        {run.pr_title || `Analysis #${run.pr_number}`}
                      </h3>
                      <span className="text-xs text-neutral-600 bg-neutral-800 px-1.5 py-0.5 rounded">
                        #{run.pr_number}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3 text-xs text-neutral-500">
                      <span>{run.pr_author}</span>
                      <span>•</span>
                      <span>{formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  {run.status === 'completed' && (
                    <div className="hidden sm:flex items-center space-x-4 text-xs">
                      <div className="text-center">
                        <div className="font-medium text-neutral-200">{run.run_metadata?.findings_count || 0}</div>
                        <div className="text-neutral-600">issues</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-neutral-200">{run.run_metadata?.files_analyzed || 0}</div>
                        <div className="text-neutral-600">files</div>
                      </div>
                    </div>
                  )}
                  <ExternalLink className="w-4 h-4 text-neutral-600 group-hover:text-neutral-400 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* System Status Footer */}
      {runs.length > 0 && (
        <div className="flex items-center justify-center space-x-3 pt-4 border-t border-neutral-800">
          <div className="flex items-center space-x-1.5 text-xs text-neutral-500">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
            <span>All systems operational</span>
          </div>
          <span className="text-neutral-700">•</span>
          <div className="text-xs text-neutral-600">
            Updated {format(new Date(), 'HH:mm:ss')}
          </div>
        </div>
      )}
    </div>
  )
}
