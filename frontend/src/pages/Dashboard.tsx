import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { AnalysisRun } from '../types'
import { formatDistanceToNow, format } from 'date-fns'
import { ExternalLink, AlertCircle, CheckCircle, Clock, XCircle, FileCode, AlertTriangle, Activity, Filter, RefreshCcw } from 'lucide-react'
import { useState, useMemo } from 'react'

export default function Dashboard() {
  // TEST: Confirm component renders
  console.log('[Dashboard] Component rendering')
  
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [timeFilter, setTimeFilter] = useState<string>('all')
  
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ['runs'],
    queryFn: () => api.getRuns({ limit: 100 }),
    refetchInterval: 10000,
  })

  console.log('[Dashboard] State:', { isLoading, hasError: !!error, hasData: !!data })


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
      <div className="flex flex-col items-center justify-center h-[60vh] animate-pulse">
        <Activity className="w-12 h-12 text-indigo-500/50 mb-4 animate-bounce" />
        <div className="text-slate-500 font-medium">Initializing Dashboard...</div>
        <div style={{ marginTop: '20px', padding: '10px', background: 'yellow', color: 'black' }}>
          TEST: Loading state is rendering
        </div>
      </div>
    )
  }

  if (error || fetchError) {
    console.log('[Dashboard] Rendering error state', error, fetchError)
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="glass-panel p-8 max-w-md text-center border-red-500/20">
          <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Service Temporarily Unavailable</h3>
          <p className="text-slate-400 mb-8 leading-relaxed">
            {fetchError || 'Unable to load analysis runs. No data yet or service warming up.'}
          </p>
          <div style={{ marginTop: '20px', padding: '10px', background: 'red', color: 'white' }}>
            TEST: Error state is rendering. Error: {error?.toString() || fetchError || 'Unknown'}
          </div>
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
    <div className="space-y-10">
      <div style={{ padding: '20px', background: 'green', color: 'white', fontSize: '18px', marginBottom: '20px' }}>
        TEST: Success state rendering. Found {runs.length} runs
      </div>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
            Analysis Dashboard
          </h1>
          <p className="text-slate-400 max-w-2xl leading-relaxed">
            Monitor AI-powered code reviews and security insights across your repositories in real-time.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="h-10 px-4 bg-white/5 border border-white/5 rounded-lg flex items-center space-x-2 text-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-slate-300 font-medium">Live System</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {runs.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card-premium p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2 bg-emerald-500/10 rounded-lg">
                <CheckCircle className="w-6 h-6 text-emerald-500" />
              </div>
              <span className="text-2xl font-bold text-white">{stats.completed}</span>
            </div>
            <div className="text-slate-400 text-sm font-medium">Completed Runs</div>
          </div>

          <div className="card-premium p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Clock className="w-6 h-6 text-blue-500 animate-pulse" />
              </div>
              <span className="text-2xl font-bold text-white">{stats.running}</span>
            </div>
            <div className="text-slate-400 text-sm font-medium">Active Analysis</div>
          </div>

          <div className="card-premium p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2 bg-amber-500/10 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-amber-500" />
              </div>
              <span className="text-2xl font-bold text-white">{stats.totalFindings}</span>
            </div>
            <div className="text-slate-400 text-sm font-medium">Critical Findings</div>
          </div>

          <div className="card-premium p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2 bg-indigo-500/10 rounded-lg">
                <FileCode className="w-6 h-6 text-indigo-500" />
              </div>
              <span className="text-2xl font-bold text-white">{stats.filesAnalyzed}</span>
            </div>
            <div className="text-slate-400 text-sm font-medium">Files Scanned</div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="space-y-6">
        {/* Filters Bar */}
        {runs.length > 0 && (
          <div className="flex flex-wrap items-center gap-4 bg-white/5 p-2 rounded-xl border border-white/5">
            <div className="flex items-center px-3 py-1.5 space-x-2 text-slate-400">
              <Filter className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Refine View</span>
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[#0b1220] text-slate-300 text-sm rounded-lg px-3 py-1.5 border border-white/10 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
            </select>

            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="bg-[#0b1220] text-slate-300 text-sm rounded-lg px-3 py-1.5 border border-white/10 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all cursor-pointer"
            >
              <option value="all">All Time</option>
              <option value="today">Past 24 Hours</option>
              <option value="week">Past 7 Days</option>
            </select>

            <div className="ml-auto px-4 py-1.5 text-xs font-medium text-slate-500 bg-[#0b1220]/50 rounded-lg border border-white/5">
              Showing {filteredRuns.length} of {runs.length} Records
            </div>
          </div>
        )}

        {/* Runs Grid/List */}
        {runs.length === 0 ? (
          <div className="card-premium p-16 text-center border-dashed border-white/10">
            <div className="w-20 h-20 bg-indigo-500/5 rounded-full flex items-center justify-center mx-auto mb-6">
              <Activity className="w-10 h-10 text-slate-600" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Ready to Start Analyzing?</h3>
            <p className="text-slate-400 mb-8 max-w-sm mx-auto leading-relaxed">
              Connect your first repository to begin receiving AI-powered code reviews on every pull request.
            </p>
            <Link to="/projects" className="btn-primary inline-flex items-center space-x-2 px-8">
              <span>Connect Repository</span>
              <ExternalLink className="w-4 h-4" />
            </Link>
          </div>
        ) : filteredRuns.length === 0 ? (
          <div className="card-premium p-12 text-center border-dashed border-white/10">
            <p className="text-slate-400 mb-4">No results match your current filter criteria.</p>
            <button
              onClick={() => { setStatusFilter('all'); setTimeFilter('all'); }}
              className="btn-secondary text-xs"
            >
              Reset All Filters
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredRuns.map((run) => (
              <Link
                key={run.id}
                to={`/runs/${run.id}`}
                className="card-premium p-5 group flex items-center justify-between"
              >
                <div className="flex items-center space-x-5">
                  <div className="p-2 bg-slate-900 rounded-lg group-hover:bg-slate-800 transition-colors">
                    {getStatusIcon(run.status)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-3 mb-1">
                      <h3 className="font-bold text-slate-100 group-hover:text-indigo-400 transition-colors">
                        {run.pr_title || `Analysis #${run.pr_number}`}
                      </h3>
                      <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 bg-white/5 px-2 py-0.5 rounded">
                        PR-{run.pr_number}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-xs text-slate-500">
                      <span className="font-medium text-slate-400">{run.pr_author}</span>
                      <span className="w-1 h-1 rounded-full bg-slate-700" />
                      <span>{formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-8">
                  {run.status === 'completed' && (
                    <div className="hidden sm:flex items-center space-x-6">
                      <div className="text-center">
                        <div className="text-sm font-bold text-slate-200">{run.run_metadata?.findings_count || 0}</div>
                        <div className="text-[10px] uppercase text-slate-500 font-bold">Issues</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-bold text-slate-200">{run.run_metadata?.files_analyzed || 0}</div>
                        <div className="text-[10px] uppercase text-slate-500 font-bold">Files</div>
                      </div>
                    </div>
                  )}
                  <div className="p-2 text-slate-600 group-hover:text-white transition-all transform group-hover:translate-x-1">
                    <ExternalLink className="w-4 h-4" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* System Status Footer */}
      {runs.length > 0 && (
        <div className="flex items-center justify-center space-x-4 pt-6 border-t border-white/5">
          <div className="flex items-center space-x-2 text-[10px] font-bold uppercase tracking-widest text-slate-500">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>All Systems Operational</span>
          </div>
          <span className="text-slate-700">•</span>
          <div className="text-[10px] font-bold uppercase tracking-widest text-slate-600">
            Last Refresh: {format(new Date(), 'HH:mm:ss')}
          </div>
        </div>
      )}
    </div>
  )
}
