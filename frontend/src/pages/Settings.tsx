import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api as apiClient } from '../api/client';
import { ApiKeysResponse } from '../types';
import { Github, CheckCircle2, AlertCircle, Eye, EyeOff, Loader } from 'lucide-react';

export default function Settings() {
  const queryClient = useQueryClient();
  const [githubToken, setGithubToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [testingGitHub, setTestingGitHub] = useState(false);
  const [githubTestResult, setGithubTestResult] = useState<any>(null);

  const { data: apiKeys, isLoading } = useQuery<ApiKeysResponse>({
    queryKey: ['api-keys'],
    queryFn: apiClient.getApiKeys,
  });

  const saveMutation = useMutation({
    mutationFn: (keys: any) => apiClient.updateApiKeys(keys),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      setSaveSuccess(true);
      setSaveError('');
      setGithubToken('');
      setGithubTestResult(null);
      setTimeout(() => setSaveSuccess(false), 3000);
    },
    onError: (error: any) => {
      setSaveError(error.message || 'Failed to save GitHub token');
      setSaveSuccess(false);
    },
  });

  const handleSave = () => {
    if (githubToken) {
      saveMutation.mutate({ github_token: githubToken });
    }
  };

  const handleClearToken = () => {
    saveMutation.mutate({ github_token: '' });
  };

  const handleTestGitHub = async () => {
    setTestingGitHub(true);
    setGithubTestResult(null);
    try {
      const result = await apiClient.testGitHubToken();
      setGithubTestResult(result);
    } catch (error: any) {
      setGithubTestResult({ valid: false, error: error.message || 'Token test failed' });
    } finally {
      setTestingGitHub(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-copper-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-sand-100 flex items-center gap-3">
          <div className="p-2 bg-surface-2 rounded-xl border border-surface-4">
            <Github className="w-6 h-6 text-copper-400" />
          </div>
          GitHub Integration
        </h1>
        <p className="text-sand-500 mt-2">
          Connect your GitHub account to analyze your repositories. AI-powered analysis is provided by our service — no additional API keys needed!
        </p>
      </div>

      {/* Status Banners */}
      {saveSuccess && (
        <div className="flex items-center gap-3 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <p className="text-sm text-emerald-300">GitHub token saved successfully!</p>
        </div>
      )}
      {saveError && (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-sm text-red-300">{saveError}</p>
        </div>
      )}

      {/* GitHub Integration Card */}
      <div className="bg-surface-1 border border-surface-4 rounded-2xl p-6">
        <div className="space-y-4">
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-sand-300 mb-2">
              <Github className="w-4 h-4 text-sand-600" />
              GitHub Personal Access Token
              {apiKeys?.has_github_token && (
                <span className="text-[10px] px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">
                  ✓ connected
                </span>
              )}
              {apiKeys?.github_username && (
                <span className="text-xs text-sand-500">
                  @{apiKeys.github_username}
                </span>
              )}
            </label>
            <div className="relative">
              <input
                type={showToken ? 'text' : 'password'}
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                placeholder={apiKeys?.has_github_token ? '••••••••••••••••••••' : 'ghp_...'}
                className="w-full px-4 py-3 pr-12 bg-surface-2 border border-surface-4 rounded-xl text-sand-200 placeholder:text-sand-700 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600/50 transition-all text-sm font-mono"
              />
              <button
                onClick={() => setShowToken(!showToken)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-sand-600 hover:text-sand-400 transition-colors"
              >
                {showToken ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            {apiKeys?.has_github_token && (
              <>
                <button
                  onClick={handleTestGitHub}
                  disabled={testingGitHub}
                  className="text-sm px-4 py-2 bg-surface-3 hover:bg-surface-4 text-sand-300 rounded-lg transition-colors border border-surface-5 disabled:opacity-50 flex items-center gap-2"
                >
                  {testingGitHub ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    'Test Connection'
                  )}
                </button>
                <button
                  onClick={handleClearToken}
                  className="text-sm text-red-400/70 hover:text-red-400 transition-colors"
                >
                  Remove token
                </button>
              </>
            )}
          </div>

          {/* Test Result */}
          {githubTestResult && (
            <div
              className={`p-4 rounded-lg border text-sm ${
                githubTestResult.valid
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                  : 'bg-red-500/10 border-red-500/20 text-red-300'
              }`}
            >
              {githubTestResult.valid ? (
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>
                    ✓ Connected as <strong>@{githubTestResult.login}</strong>
                  </span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>{githubTestResult.error}</span>
                </div>
              )}
            </div>
          )}

          {/* Instructions */}
          <div className="bg-surface-2/50 border border-surface-4 rounded-lg p-4 space-y-2">
            <p className="text-xs font-medium text-sand-400">How to create a GitHub token:</p>
            <ol className="text-xs text-sand-600 space-y-1 list-decimal list-inside">
              <li>Go to <a
                href="https://github.com/settings/tokens/new?scopes=repo"
                target="_blank"
                rel="noopener noreferrer"
                className="text-copper-400 hover:text-copper-300 underline"
              >
                github.com/settings/tokens
              </a></li>
              <li>Click "Generate new token (classic)"</li>
              <li>Give it a name like "CodeLens AI"</li>
              <li>Select the <code className="px-1.5 py-0.5 bg-surface-3 rounded text-[11px] font-mono">repo</code> scope</li>
              <li>Click "Generate token" and paste it above</li>
            </ol>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-between pt-2">
        <p className="text-xs text-sand-700">
          🔒 Your token is stored encrypted and never shared
        </p>
        <button
          onClick={handleSave}
          disabled={saveMutation.isPending || !githubToken}
          className="px-6 py-2.5 bg-copper-600 hover:bg-copper-500 disabled:opacity-50 disabled:cursor-not-allowed text-surface-0 text-sm font-semibold rounded-xl transition-all shadow-md hover:shadow-lg"
        >
          {saveMutation.isPending ? 'Saving...' : 'Save Token'}
        </button>
      </div>
    </div>
  );
}
