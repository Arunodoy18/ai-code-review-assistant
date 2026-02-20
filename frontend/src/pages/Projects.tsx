import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { Project } from '../types'
import { FolderGit2, ExternalLink, Activity, Clock, Plus, Github, RefreshCcw, X, GitPullRequest, Zap } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function Projects() {
  const queryClient = useQueryClient()
  const [showAddRepoModal, setShowAddRepoModal] = useState(false)
  const [repoInput, setRepoInput] = useState('')
  const [addRepoError, setAddRepoError] = useState('')
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [showAnalyzeModal, setShowAnalyzeModal] = useState(false)
  const [prNumber, setPrNumber] = useState('')
  const [analyzePrError, setAnalyzePrError] = useState('')

  const addRepoMutation = useMutation({
    mutationFn: (repoFullName: string) => api.addRepo(repoFullName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowAddRepoModal(false)
      setRepoInput('')
      setAddRepoError('')
    },
    onError: (error: any) => {
      setAddRepoError(error.details?.detail || error.message || 'Failed to add repository')
    },
  })

  const analyzePrMutation = useMutation({
    mutationFn: ({ projectId, prNum }: { projectId: number; prNum: number }) =>
      api.analyzePR(projectId, prNum),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['runs'] })
      setShowAnalyzeModal(false)
      setPrNumber('')
      setAnalyzePrError('')
      // Navigate to the run detail page if you have one
      if (data.run_id) {
        window.location.href = `/analysis/${data.run_id}`
      }
    },
    onError: (error: any) => {
      setAnalyzePrError(error.details?.detail || error.message || 'Failed to analyze PR')
    },
  })

  const handleAddRepo = () => {
    if (!repoInput.trim() || !repoInput.includes('/')) {
      setAddRepoError('Please enter a valid repository name (owner/repo)')
      return
    }
    addRepoMutation.mutate(repoInput.trim())
  }

  const handleAnalyzePr = () => {
    const prNum = parseInt(prNumber, 10)
    if (!prNum || prNum <= 0) {
      setAnalyzePrError('Please enter a valid PR number')
      return
    }
    if (!selectedProject) return
    analyzePrMutation.mutate({ projectId: selectedProject.id, prNum })
  }
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
        <button
          onClick={() => setShowAddRepoModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add Repository</span>
        </button>
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
            Add your GitHub repositories to enable AI-powered code review and analysis.
          </p>
          <button
            onClick={() => setShowAddRepoModal(true)}
            className="btn-primary inline-flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Your First Repository</span>
          </button>
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
                <button
                  onClick={() => {
                    setSelectedProject(project)
                    setShowAnalyzeModal(true)
                  }}
                  className="flex-1 btn-primary py-1.5 flex items-center justify-center space-x-1.5 text-xs"
                >
                  <GitPullRequest className="w-3 h-3" />
                  <span>Analyze PR</span>
                </button>
                <a
                  href={`https://github.com/${project.github_repo_full_name}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 btn-secondary py-1.5 flex items-center justify-center space-x-1.5 text-xs"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>View Repo</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Repo Modal */}
      {showAddRepoModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface-1 border border-surface-4 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-sand-100">Add Repository</h3>
              <button
                onClick={() => {
                  setShowAddRepoModal(false)
                  setRepoInput('')
                  setAddRepoError('')
                }}
                className="p-1 hover:bg-surface-3 rounded-lg transition-colors"
                title="Close"
              >
                <X className="w-5 h-5 text-sand-500" />
              </button>
            </div>
            <p className="text-sm text-sand-600 mb-4">
              Enter the full repository name (owner/repo). Your GitHub token will be used to verify access.
            </p>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-sand-300 mb-2 block">
                  Repository
                </label>
                <input
                  type="text"
                  value={repoInput}
                  onChange={(e) => setRepoInput(e.target.value)}
                  placeholder="owner/repo"
                  className="w-full px-4 py-3 bg-surface-2 border border-surface-4 rounded-xl text-sand-200 placeholder:text-sand-700 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600/50 transition-all"
                  onKeyDown={(e) => e.key === 'Enter' && handleAddRepo()}
                />
              </div>
              {addRepoError && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-300">
                  {addRepoError}
                </div>
              )}
              <div className="flex items-center gap-2">
                <button
                  onClick={handleAddRepo}
                  disabled={addRepoMutation.isPending}
                  className="flex-1 btn-primary py-2.5"
                >
                  {addRepoMutation.isPending ? 'Adding...' : 'Add Repository'}
                </button>
                <button
                  onClick={() => {
                    setShowAddRepoModal(false)
                    setRepoInput('')
                    setAddRepoError('')
                  }}
                  className="flex-1 btn-secondary py-2.5"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analyze PR Modal */}
      {showAnalyzeModal && selectedProject && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface-1 border border-surface-4 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-sand-100">Analyze Pull Request</h3>
              <button
                onClick={() => {
                  setShowAnalyzeModal(false)
                  setPrNumber('')
                  setAnalyzePrError('')
                  setSelectedProject(null)
                }}
                className="p-1 hover:bg-surface-3 rounded-lg transition-colors"
                title="Close"
              >
                <X className="w-5 h-5 text-sand-500" />
              </button>
            </div>
            <p className="text-sm text-sand-600 mb-4">
              Enter the PR number to analyze for <strong className="text-sand-300">{selectedProject.github_repo_full_name}</strong>
            </p>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-sand-300 mb-2 block">
                  PR Number
                </label>
                <input
                  type="number"
                  value={prNumber}
                  onChange={(e) => setPrNumber(e.target.value)}
                  placeholder="123"
                  className="w-full px-4 py-3 bg-surface-2 border border-surface-4 rounded-xl text-sand-200 placeholder:text-sand-700 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600/50 transition-all"
                  onKeyDown={(e) => e.key === 'Enter' && handleAnalyzePr()}
                />
              </div>
              {analyzePrError && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-300">
                  {analyzePrError}
                </div>
              )}
              {analyzePrMutation.isPending && (
                <div className="p-3 bg-copper-500/10 border border-copper-500/20 rounded-lg text-sm text-copper-300 flex items-center gap-2">
                  <Zap className="w-4 h-4 animate-pulse" />
                  <span>Running AI analysis...</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <button
                  onClick={handleAnalyzePr}
                  disabled={analyzePrMutation.isPending}
                  className="flex-1 btn-primary py-2.5"
                >
                  {analyzePrMutation.isPending ? 'Analyzing...' : 'Analyze PR'}
                </button>
                <button
                  onClick={() => {
                    setShowAnalyzeModal(false)
                    setPrNumber('')
                    setAnalyzePrError('')
                    setSelectedProject(null)
                  }}
                  className="flex-1 btn-secondary py-2.5"
                  disabled={analyzePrMutation.isPending}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
