import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Code2, Shield, Zap, Users, ArrowDown, ChevronRight, Sparkles, BarChart3, Brain, Eye } from 'lucide-react';

export default function Landing() {
  const [showInfo, setShowInfo] = useState(false);
  const infoRef = useRef<HTMLDivElement>(null);

  const scrollToInfo = () => {
    setShowInfo(true);
    setTimeout(() => {
      infoRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  };

  return (
    <div className="min-h-screen bg-surface-0">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-hero-glow opacity-60" />
        <div className="absolute top-1/4 right-0 w-96 h-96 bg-copper-500/[0.02] rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 left-0 w-96 h-96 bg-sand-500/[0.02] rounded-full blur-[120px]" />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-surface-0/70 backdrop-blur-xl border-b border-surface-4/50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="p-2 bg-surface-2 rounded-xl border border-surface-4">
                <Eye className="w-5 h-5 text-copper-400" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-copper-500 rounded-full animate-pulse-soft" />
            </div>
            <div>
              <span className="text-[15px] font-bold text-sand-100 tracking-tight">CodeLens</span>
              <span className="text-[15px] font-light text-sand-500 ml-1">AI</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="btn-ghost"
            >
              Sign in
            </Link>
            <Link
              to="/signup"
              className="btn-primary"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-16">
        <div className="max-w-3xl mx-auto text-center">
          {/* Status badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-surface-1 border border-surface-4 rounded-full mb-8 animate-fade-up" style={{ animationDelay: '0.1s' }}>
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-sand-400">Powered by Llama 3.3 70B via Groq</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-sand-50 tracking-tight mb-6 leading-[1.1] animate-fade-up" style={{ animationDelay: '0.2s' }}>
            Code review<br />
            <span className="bg-gradient-to-r from-copper-400 via-copper-300 to-sand-300 bg-clip-text text-transparent">
              that thinks.
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-sand-500 mb-12 max-w-xl mx-auto leading-relaxed animate-fade-up" style={{ animationDelay: '0.3s' }}>
            AI-powered pull request analysis with risk scoring, auto-fix generation, 
            and plain-English summaries. Ship faster, ship safer.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-up" style={{ animationDelay: '0.4s' }}>
            <Link
              to="/signup"
              className="btn-primary text-base px-8 py-3.5 flex items-center gap-2"
            >
              Start Reviewing
              <ChevronRight className="w-4 h-4" />
            </Link>
            <button
              onClick={scrollToInfo}
              className="btn-ghost text-base px-6 py-3 flex items-center gap-2"
            >
              See how it works
              <ArrowDown className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Floating metrics */}
        <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex items-center gap-8 text-center animate-fade-up" style={{ animationDelay: '0.6s' }}>
          <div>
            <div className="text-2xl font-bold text-sand-100">0→100</div>
            <div className="text-[11px] font-medium text-sand-600 uppercase tracking-widest mt-1">Risk Score</div>
          </div>
          <div className="w-px h-10 bg-surface-4" />
          <div>
            <div className="text-2xl font-bold text-sand-100">&lt;30s</div>
            <div className="text-[11px] font-medium text-sand-600 uppercase tracking-widest mt-1">Analysis</div>
          </div>
          <div className="w-px h-10 bg-surface-4" />
          <div>
            <div className="text-2xl font-bold text-sand-100">1-Click</div>
            <div className="text-[11px] font-medium text-sand-600 uppercase tracking-widest mt-1">Auto Fix</div>
          </div>
        </div>
      </section>

      {/* Info Section */}
      <section
        ref={infoRef}
        className={`relative py-32 px-6 transition-all duration-700 ${showInfo ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
      >
        <div className="max-w-5xl mx-auto">
          {/* Section heading */}
          <div className="text-center mb-20">
            <span className="text-xs font-bold text-copper-500 uppercase tracking-[0.2em] mb-4 block">What sets us apart</span>
            <h2 className="text-3xl md:text-4xl font-bold text-sand-100 mb-4">
              Features that don't exist<br />anywhere else.
            </h2>
            <p className="text-sand-500 max-w-lg mx-auto">
              Not just another linter. CodeLens AI understands context, calculates risk, 
              generates fixes, and learns from your team's decisions.
            </p>
          </div>

          {/* Feature Cards — Bento Grid */}
          <div className="grid md:grid-cols-2 gap-5 mb-24">
            <BigFeatureCard
              icon={BarChart3}
              number="01"
              title="PR Risk Score"
              description="Every pull request gets a 0-100 risk score combining code complexity, blast radius, sensitive file detection, and AI-powered contextual assessment. Know at a glance if a PR needs extra eyes."
              highlight="critical"
            />
            <BigFeatureCard
              icon={Sparkles}
              number="02"
              title="AI Auto-Fix"
              description="Get one-click AI-generated code patches for every finding. Real unified diffs you can copy and apply directly — not just suggestions, actual working fixes."
              highlight="copper"
            />
            <BigFeatureCard
              icon={Brain}
              number="03"
              title="Learning System"
              description="Dismiss a false positive and CodeLens learns. It remembers patterns per-project, auto-suppressing similar findings in future runs. It gets smarter the more you use it."
              highlight="emerald"
            />
            <BigFeatureCard
              icon={Users}
              number="04"
              title="Plain English Summaries"
              description="AI-generated summaries explain what each PR does, what the risks are, and whether it's safe to merge — written for PMs and stakeholders, not just developers."
              highlight="sand"
            />
          </div>

          {/* Core capabilities */}
          <div className="grid md:grid-cols-3 gap-5 mb-24">
            <FeatureCard
              icon={Code2}
              title="Deep Analysis"
              description="Understands your codebase context. Finds bugs, security issues, and performance problems that linters miss."
            />
            <FeatureCard
              icon={Shield}
              title="Security First"
              description="Detects vulnerabilities, auth bypasses, TOCTOU attacks, race conditions, and injection flaws."
            />
            <FeatureCard
              icon={Zap}
              title="Groq-Fast"
              description="Powered by Llama 3.3 70B on Groq's LPU. Full PR analysis in seconds, not minutes."
            />
          </div>

          {/* How it works */}
          <div className="mb-24">
            <div className="text-center mb-12">
              <span className="text-xs font-bold text-copper-500 uppercase tracking-[0.2em] mb-4 block">Setup</span>
              <h2 className="text-3xl font-bold text-sand-100">Three steps. Five minutes.</h2>
            </div>
            <div className="grid md:grid-cols-3 gap-6">
              <Step number={1} title="Connect your repo" description="Install the GitHub App on your repositories. We only request the permissions we need." />
              <Step number={2} title="Configure rules" description="Set severity levels, focus areas, and custom patterns that match your team's standards." />
              <Step number={3} title="Reviews run automatically" description="Every PR gets full analysis. Findings, risk scores, auto-fixes, and summaries appear instantly." />
            </div>
          </div>

          {/* CTA */}
          <div className="relative overflow-hidden rounded-2xl border border-surface-4 bg-surface-1 p-12 md:p-16 text-center">
            <div className="absolute inset-0 bg-hero-glow opacity-40" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold text-sand-100 mb-4">
                Ready to ship with confidence?
              </h2>
              <p className="text-sand-500 mb-8 max-w-md mx-auto">
                Create an account and connect your first repository in under 5 minutes.
              </p>
              <div className="flex items-center justify-center gap-4">
                <Link
                  to="/signup"
                  className="btn-primary text-base px-8 py-3.5"
                >
                  Create free account
                </Link>
                <Link
                  to="/login"
                  className="btn-secondary text-base px-6 py-3"
                >
                  Sign in
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 border-t border-surface-4/50">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-sand-700" />
            <span className="text-sm text-sand-700">CodeLens AI</span>
          </div>
          <p className="text-xs text-sand-800">
            &copy; 2026 All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

function BigFeatureCard({ icon: Icon, number, title, description, highlight }: { 
  icon: typeof Code2; number: string; title: string; description: string; highlight: string 
}) {
  const accentColor = highlight === 'critical' ? 'text-red-400' :
                      highlight === 'copper' ? 'text-copper-400' :
                      highlight === 'emerald' ? 'text-emerald-400' : 'text-sand-400';
  const accentBg = highlight === 'critical' ? 'bg-red-500/10 border-red-500/20' :
                   highlight === 'copper' ? 'bg-copper-500/10 border-copper-500/20' :
                   highlight === 'emerald' ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-sand-500/10 border-sand-500/20';
  
  return (
    <div className="group relative card p-8 overflow-hidden">
      <div className="absolute top-6 right-6 text-[64px] font-black text-surface-3/60 leading-none select-none">{number}</div>
      <div className={`relative z-10 w-12 h-12 ${accentBg} border rounded-xl flex items-center justify-center mb-5`}>
        <Icon className={`w-6 h-6 ${accentColor}`} />
      </div>
      <h3 className="relative z-10 text-xl font-bold text-sand-100 mb-3">{title}</h3>
      <p className="relative z-10 text-sm text-sand-500 leading-relaxed">{description}</p>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description }: { icon: typeof Code2; title: string; description: string }) {
  return (
    <div className="card p-6">
      <div className="w-10 h-10 bg-surface-2 border border-surface-4 rounded-xl flex items-center justify-center mb-4">
        <Icon className="w-5 h-5 text-sand-400" />
      </div>
      <h3 className="text-sm font-semibold text-sand-100 mb-2">{title}</h3>
      <p className="text-sm text-sand-600 leading-relaxed">{description}</p>
    </div>
  );
}

function Step({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-10 h-10 bg-copper-500/10 border border-copper-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-sm font-bold text-copper-400">{number}</span>
      </div>
      <h3 className="text-sm font-semibold text-sand-100 mb-2">{title}</h3>
      <p className="text-sm text-sand-600">{description}</p>
    </div>
  );
}
