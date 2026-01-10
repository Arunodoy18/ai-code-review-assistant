import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { Project } from '../types'
import { FolderGit2, ExternalLink, Activity, Clock, Settings, Plus, Github, RefreshCcw } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function Projects() {
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ['projects'],
    queryFn: api.getProjects,
  })

  const projects: Project[] = data?.data || (Array.isArray(data) ? data : [])
  const fetchError = data?.success === false ? data?.error : null
  const isNetworkError = error && !data

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] animate-pulse">
        <FolderGit2 className="w-12 h-12 text-indigo-500/50 mb-4 animate-bounce" />
        <div className="text-slate-500 font-medium text-lg">Loading repositories...</div>
      </div>
    )
  }

  if (isNetworkError) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="glass-panel p-8 text-center border-amber-500/20 max-w-md">
          <Activity className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">Connection Issue</h3>
          <p className="text-slate-400 mb-6">Unable to reach the server. The service may be warming up.</p>
          <button onClick={() => refetch()} className="btn-primary w-full flex items-center justify-center space-x-2">
            <RefreshCcw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Connected Projects</h1>
          <p className="text-slate-400 max-w-2xl leading-relaxed">
            Repositories with active AI monitoring. Open a pull request on any of these to trigger an analysis.
          </p>
        </div>
        <a
          href="https://github.com/settings/apps/new"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary flex items-center space-x-2 shadow-indigo-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>Add Repository</span>
        </a>
      </div>

      {fetchError && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 text-amber-300 text-sm">
          Note: {fetchError}
        </div>
      )}

      {projects.length === 0 ? (
        <div className="card-premium p-16 text-center border-dashed border-white/10 max-w-3xl mx-auto">
          <div className="w-20 h-20 bg-indigo-500/5 rounded-full flex items-center justify-center mx-auto mb-8">
            <Github className="w-10 h-10 text-slate-500" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-4">No repositories connected yet</h3>
          <p className="text-slate-400 mb-10 leading-relaxed">
            Install the AI Code Review GitHub App on your repositories to enable automated analysis and security scanning.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left mb-10">
            <div className="bg-white/5 p-4 rounded-xl border border-white/5">
              <div className="text-indigo-400 font-bold mb-1">Step 1</div>
              <div className="text-sm text-slate-300">Create GitHub App following GITHUB_APP_SETUP.md</div>
            </div>
            <div className="bg-white/5 p-4 rounded-xl border border-white/5">
              <div className="text-indigo-400 font-bold mb-1">Step 2</div>
              <div className="text-sm text-slate-300">Install app on your target repositories</div>
            </div>
          </div>
          <a
            href="https://github.com/settings/apps/new"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center space-x-2 px-10 py-3"
          >
            <span>Setup GitHub Integration</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project: Project) => (
            <div key={project.id} className="card-premium p-6 group">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-indigo-500/10 rounded-xl border border-indigo-500/20 group-hover:bg-indigo-500/20 transition-all">
                    <Github className="w-6 h-6 text-indigo-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white group-hover:text-indigo-300 transition-colors truncate max-w-[180px]">
                      {project.name}
                    </h3>
                    <p className="text-xs text-slate-500 font-medium truncate max-w-[180px]">
                      {project.github_repo_full_name}
                    </p>
                  </div>
                </div>
                <div className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
                  Active
                </div>
              </div>

              <div className="space-y-4 mb-8">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-medium flex items-center space-x-2">
                    <Activity className="w-3.5 h-3.5" />
                    <span>Review Mode</span>
                  </span>
                  <span className="text-slate-300 font-semibold">Automatic</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-medium flex items-center space-x-2">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Connected</span>
                  </span>
                  <span className="text-slate-300 font-semibold">
                    {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <a
                  href={`https://github.com/${project.github_repo_full_name}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 btn-secondary py-2 flex items-center justify-center space-x-2 text-xs"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>Repository</span>
                </a>
                <button className="btn-secondary py-2 px-3 text-slate-400 hover:text-white" title="Project Settings">
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
