import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api as apiClient } from '../api/client';
import { ApiKeysResponse } from '../types';
import { Key, Shield, Zap, Brain, Globe, CheckCircle2, AlertCircle, Eye, EyeOff, Sparkles } from 'lucide-react';

const LLM_PROVIDERS = [
  { value: 'groq', label: 'Groq', description: 'Llama 3.3 70B — fastest inference', icon: Zap },
  { value: 'openai', label: 'OpenAI', description: 'GPT-4 Turbo — highest accuracy', icon: Brain },
  { value: 'anthropic', label: 'Anthropic', description: 'Claude 3 — balanced reasoning', icon: Shield },
  { value: 'google', label: 'Google', description: 'Gemini Pro — cost effective', icon: Globe },
];

export default function Settings() {
  const queryClient = useQueryClient();
  const [groqKey, setGroqKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [googleKey, setGoogleKey] = useState('');
  const [provider, setProvider] = useState('groq');
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');

  const { data: apiKeys, isLoading } = useQuery<ApiKeysResponse>({
    queryKey: ['api-keys'],
    queryFn: apiClient.getApiKeys,
  });

  useEffect(() => {
    if (apiKeys) {
      setProvider(apiKeys.preferred_llm_provider || 'groq');
    }
  }, [apiKeys]);

  const saveMutation = useMutation({
    mutationFn: (keys: any) => apiClient.updateApiKeys(keys),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      setSaveSuccess(true);
      setSaveError('');
      // Clear the key fields after save
      setGroqKey('');
      setOpenaiKey('');
      setAnthropicKey('');
      setGoogleKey('');
      setTimeout(() => setSaveSuccess(false), 3000);
    },
    onError: (error: any) => {
      setSaveError(error.message || 'Failed to save API keys');
      setSaveSuccess(false);
    },
  });

  const handleSave = () => {
    const keys: any = { preferred_llm_provider: provider };
    if (groqKey) keys.groq_api_key = groqKey;
    if (openaiKey) keys.openai_api_key = openaiKey;
    if (anthropicKey) keys.anthropic_api_key = anthropicKey;
    if (googleKey) keys.google_api_key = googleKey;
    saveMutation.mutate(keys);
  };

  const handleClearKey = (keyName: string) => {
    const keys: any = {};
    keys[keyName] = '';
    saveMutation.mutate(keys);
  };

  const toggleShowKey = (key: string) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-copper-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-sand-100 flex items-center gap-3">
          <div className="p-2 bg-surface-2 rounded-xl border border-surface-4">
            <Key className="w-6 h-6 text-copper-400" />
          </div>
          API Keys & Provider
        </h1>
        <p className="text-sand-500 mt-2">
          Configure your LLM API keys for AI-powered code analysis. Your keys are encrypted and never shared.
        </p>
      </div>

      {/* Status Banner */}
      {saveSuccess && (
        <div className="flex items-center gap-3 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <p className="text-sm text-emerald-300">API keys saved successfully.</p>
        </div>
      )}
      {saveError && (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-sm text-red-300">{saveError}</p>
        </div>
      )}

      {/* Preferred Provider */}
      <div className="bg-surface-1 border border-surface-4 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-sand-100 mb-1 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-copper-400" />
          Preferred AI Provider
        </h2>
        <p className="text-sm text-sand-600 mb-5">
          Choose which LLM provider powers your code reviews. You need at least one API key configured.
        </p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {LLM_PROVIDERS.map((p) => {
            const Icon = p.icon;
            const isSelected = provider === p.value;
            const hasKey = apiKeys ? (apiKeys as any)[`has_${p.value}_key`] : false;
            
            return (
              <button
                key={p.value}
                onClick={() => setProvider(p.value)}
                className={`flex items-start gap-3 p-4 rounded-xl border transition-all duration-200 text-left ${
                  isSelected
                    ? 'bg-copper-500/10 border-copper-500/40 shadow-inner-glow'
                    : 'bg-surface-2 border-surface-4 hover:border-surface-6'
                }`}
              >
                <div className={`p-2 rounded-lg ${isSelected ? 'bg-copper-500/20' : 'bg-surface-3'}`}>
                  <Icon className={`w-5 h-5 ${isSelected ? 'text-copper-400' : 'text-sand-500'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-semibold ${isSelected ? 'text-copper-300' : 'text-sand-200'}`}>
                      {p.label}
                    </span>
                    {hasKey && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">
                        active
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-sand-600 mt-0.5">{p.description}</p>
                </div>
                <div className={`mt-1 w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 ${
                  isSelected ? 'border-copper-400' : 'border-surface-6'
                }`}>
                  {isSelected && <div className="w-2 h-2 bg-copper-400 rounded-full" />}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* API Keys */}
      <div className="bg-surface-1 border border-surface-4 rounded-2xl p-6 space-y-5">
        <div>
          <h2 className="text-lg font-semibold text-sand-100 mb-1 flex items-center gap-2">
            <Shield className="w-5 h-5 text-copper-400" />
            API Keys
          </h2>
          <p className="text-sm text-sand-600">
            Enter your API keys below. Keys are masked after saving — leave blank to keep existing key unchanged.
          </p>
        </div>

        {/* Groq */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-sand-300">
            <Zap className="w-4 h-4 text-sand-600" />
            Groq API Key
            {apiKeys?.has_groq_key && (
              <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">configured</span>
            )}
          </label>
          <div className="relative">
            <input
              type={showKeys.groq ? 'text' : 'password'}
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              placeholder={apiKeys?.has_groq_key ? '••••••••••••••••••••' : 'gsk_...'}
              className="w-full px-4 py-3 bg-surface-2 border border-surface-4 rounded-xl text-sand-200 placeholder:text-sand-700 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600/50 transition-all text-sm font-mono"
            />
            <button
              onClick={() => toggleShowKey('groq')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-sand-600 hover:text-sand-400"
            >
              {showKeys.groq ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {apiKeys?.has_groq_key && (
            <button onClick={() => handleClearKey('groq_api_key')} className="text-xs text-red-400/70 hover:text-red-400 transition-colors">
              Remove key
            </button>
          )}
        </div>

        {/* OpenAI */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-sand-300">
            <Brain className="w-4 h-4 text-sand-600" />
            OpenAI API Key
            {apiKeys?.has_openai_key && (
              <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">configured</span>
            )}
          </label>
          <div className="relative">
            <input
              type={showKeys.openai ? 'text' : 'password'}
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              placeholder={apiKeys?.has_openai_key ? '••••••••••••••••••••' : 'sk-...'}
              className="w-full px-4 py-3 bg-surface-2 border border-surface-4 rounded-xl text-sand-200 placeholder:text-sand-700 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600/50 transition-all text-sm font-mono"
            />
            <button
              onClick={() => toggleShowKey('openai')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-sand-600 hover:text-sand-400"
            >
              {showKeys.openai ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {apiKeys?.has_openai_key && (
            <button onClick={() => handleClearKey('openai_api_key')} className="text-xs text-red-400/70 hover:text-red-400 transition-colors">
              Remove key
            </button>
          )}
        </div>

        {/* Anthropic */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-sand-300">
            <Shield className="w-4 h-4 text-sand-600" />
            Anthropic API Key
            {apiKeys?.has_anthropic_key && (
              <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">configured</span>
            )}
          </label>
          <div className="relative">
            <input
              type={showKeys.anthropic ? 'text' : 'password'}
              value={anthropicKey}
              onChange={(e) => setAnthropicKey(e.target.value)}
              placeholder={apiKeys?.has_anthropic_key ? '••••••••••••••••••••' : 'sk-ant-...'}
              className="w-full px-4 py-3 bg-surface-2 border border-surface-4 rounded-xl text-sand-200 placeholder:text-sand-700 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600/50 transition-all text-sm font-mono"
            />
            <button
              onClick={() => toggleShowKey('anthropic')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-sand-600 hover:text-sand-400"
            >
              {showKeys.anthropic ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {apiKeys?.has_anthropic_key && (
            <button onClick={() => handleClearKey('anthropic_api_key')} className="text-xs text-red-400/70 hover:text-red-400 transition-colors">
              Remove key
            </button>
          )}
        </div>

        {/* Google */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-sand-300">
            <Globe className="w-4 h-4 text-sand-600" />
            Google AI API Key
            {apiKeys?.has_google_key && (
              <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">configured</span>
            )}
          </label>
          <div className="relative">
            <input
              type={showKeys.google ? 'text' : 'password'}
              value={googleKey}
              onChange={(e) => setGoogleKey(e.target.value)}
              placeholder={apiKeys?.has_google_key ? '••••••••••••••••••••' : 'AIza...'}
              className="w-full px-4 py-3 bg-surface-2 border border-surface-4 rounded-xl text-sand-200 placeholder:text-sand-700 focus:border-copper-600 focus:outline-none focus:ring-1 focus:ring-copper-600/50 transition-all text-sm font-mono"
            />
            <button
              onClick={() => toggleShowKey('google')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-sand-600 hover:text-sand-400"
            >
              {showKeys.google ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {apiKeys?.has_google_key && (
            <button onClick={() => handleClearKey('google_api_key')} className="text-xs text-red-400/70 hover:text-red-400 transition-colors">
              Remove key
            </button>
          )}
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-between pt-2">
        <p className="text-xs text-sand-700">
          Your keys are stored encrypted and never leave our servers.
        </p>
        <button
          onClick={handleSave}
          disabled={saveMutation.isPending}
          className="px-6 py-2.5 bg-copper-600 hover:bg-copper-500 disabled:opacity-50 text-surface-0 text-sm font-semibold rounded-xl transition-all shadow-md hover:shadow-lg"
        >
          {saveMutation.isPending ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}
