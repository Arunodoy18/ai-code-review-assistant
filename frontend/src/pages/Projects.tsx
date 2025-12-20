import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { Project } from '../types'
import { FolderGit2, ExternalLink, Activity, Clock, CheckCircle, Settings } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function Projects() {
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: api.getProjects,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <div className="text-slate-400">Loading projects...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Error loading projects</div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 mb-2 flex items-center space-x-3 drop-shadow-sm">
              <FolderGit2 className="w-10 h-10 text-blue-400 drop-shadow-lg" />
              <span>Projects</span>
            </h1>
            <p className="text-slate-400 text-lg">Manage connected GitHub repositories for code review</p>
          </div>
          {projects && projects.length > 0 && (
            <div className="text-right bg-slate-800/50 backdrop-blur-sm p-4 rounded-xl border border-slate-700/50 shadow-lg">
              <div className="text-3xl font-bold text-white">{projects.length}</div>
              <div className="text-sm text-slate-400">Connected</div>
            </div>
          )}
        </div>
      </div>

      {(!projects || projects.length === 0) ? (
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-12 text-center border-2 border-dashed border-slate-700/50 hover:border-slate-600 transition-colors">
          <FolderGit2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-300 mb-2">No projects yet</h3>
          <p className="text-slate-500 mb-6">
            Install the GitHub App to connect repositories and start analyzing pull requests
          </p>
          <a
            href="https://github.com/apps/your-app-name/installations/new"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-lg transition-all shadow-lg hover:shadow-blue-500/25 hover:scale-105"
          >
            <span>Install GitHub App</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project: Project) => (
            <div
              key={project.id}
              className="bg-gradient-to-br from-slate-800 to-slate-900/80 backdrop-blur-md rounded-xl p-6 border border-slate-700/50 hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10 hover:scale-105 transition-all duration-300 group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3 flex-1">
                  <div className="p-3 bg-blue-500/10 rounded-lg border border-blue-500/20 group-hover:bg-blue-500/20 transition-colors">
                    <FolderGit2 className="w-6 h-6 text-blue-500 group-hover:scale-110 transition-transform" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-lg font-semibold text-white truncate group-hover:text-blue-400 transition-colors">
                      {project.name}
                    </h3>
                    <p className="text-sm text-slate-400 truncate">
                      {project.github_repo_full_name}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center space-x-2">
                    <Activity className="w-4 h-4" />
                    <span>Status</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-green-400 font-medium">Active</span>
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center space-x-2">
                    <Clock className="w-4 h-4" />
                    <span>Added</span>
                  </span>
                  <span className="text-slate-300">
                    {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-4 border-t border-slate-700">
                <a
                  href={`https://github.com/${project.github_repo_full_name}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white rounded-lg text-sm transition"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>View on GitHub</span>
                </a>
                <button
                  className="p-2 bg-slate-700 hover:bg-slate-600 text-slate-400 hover:text-white rounded-lg transition"
                  title="Project settings"
                >
                  <Settings className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-3 text-xs text-slate-500 text-center">
                Installation ID: {project.github_installation_id}
              </div>
            </div>
          ))}
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="mt-8 p-4 bg-slate-800 rounded-lg border border-slate-700 text-center">
          <p className="text-sm text-slate-400">
            Need to add more repositories? Install the GitHub App on additional repos
          </p>
          <a
            href="https://github.com/apps/your-app-name/installations/new"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 mt-3 text-sm text-blue-400 hover:text-blue-300"
          >
            <span>Manage installations</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      )}
    </div>
  )
}
