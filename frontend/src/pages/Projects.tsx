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
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <FolderGit2 className="w-8 h-8 text-sand-700 mb-4 animate-pulse" />
        <div className="text-sand-600 text-sm">Loading repositories...</div>
      </div>
    )
  }

  if (isNetworkError) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="card p-8 text-center max-w-md">
          <Activity className="w-8 h-8 text-amber-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-sand-100 mb-2">Connection Issue</h3>
          <p className="text-sand-500 text-sm mb-6">Unable to reach the server. The service may be warming up.</p>
          <button onClick={() => refetch()} className="btn-primary w-full flex items-center justify-center space-x-2">
            <RefreshCcw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-sand-100 mb-1">Projects</h1>
          <p className="text-sand-600 text-sm">
            Repositories with active AI monitoring.
          </p>
        </div>
        <a
          href="https://github.com/settings/apps/new"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add Repository</span>
        </a>
      </div>

      {fetchError && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 text-amber-400 text-sm">
          {fetchError}
        </div>
      )}

      {projects.length === 0 ? (
        <div className="card p-12 text-center border-dashed max-w-2xl mx-auto">
          <div className="w-14 h-14 bg-surface-3 rounded-2xl flex items-center justify-center mx-auto mb-5">
            <Github className="w-7 h-7 text-sand-600" />
          </div>
          <h3 className="text-lg font-bold text-sand-100 mb-2">No repositories connected</h3>
          <p className="text-sand-500 text-sm mb-8">
            Install the CodeLens AI GitHub App on your repositories to enable automated analysis.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left mb-10">
            <div className="bg-surface-3/50 p-4 rounded-xl border border-surface-4">
              <div className="text-copper-400 font-bold text-sm mb-1">Step 1</div>
              <div className="text-sm text-sand-400">Create a GitHub App to connect your repositories</div>
            </div>
            <div className="bg-surface-3/50 p-4 rounded-xl border border-surface-4">
              <div className="text-copper-400 font-bold text-sm mb-1">Step 2</div>
              <div className="text-sm text-sand-400">Install the app on your target repositories</div>
            </div>
          </div>
          <a
            href="https://github.com/settings/apps/new"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center space-x-2"
          >
            <span>Setup GitHub Integration</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project: Project) => (
            <div key={project.id} className="card-interactive p-5 group">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-surface-3 rounded-lg border border-surface-4">
                    <Github className="w-5 h-5 text-sand-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-sand-100 group-hover:text-sand-50 transition-colors truncate max-w-[180px]">
                      {project.name}
                    </h3>
                    <p className="text-xs text-sand-600 truncate max-w-[180px]">
                      {project.github_repo_full_name}
                    </p>
                  </div>
                </div>
                <div className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded-md text-xs font-medium text-emerald-400">
                  Active
                </div>
              </div>

              <div className="space-y-2 mb-4 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-sand-600 flex items-center space-x-1.5">
                    <Activity className="w-3.5 h-3.5" />
                    <span>Mode</span>
                  </span>
                  <span className="text-sand-300">Automatic</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sand-600 flex items-center space-x-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Connected</span>
                  </span>
                  <span className="text-sand-300">
                    {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <a
                  href={`https://github.com/${project.github_repo_full_name}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 btn-secondary py-1.5 flex items-center justify-center space-x-1.5 text-xs"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>View Repo</span>
                </a>
                <button className="btn-secondary py-1.5 px-2.5" title="Settings">
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
