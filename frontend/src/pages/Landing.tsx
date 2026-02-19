import { Link } from 'react-router-dom';
import { Code2, Shield, Zap, Users, ChevronRight, Sparkles, BarChart3, Brain, Eye, GitPullRequest, Terminal, ArrowRight, Check } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-surface-0 text-sand-300">
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[700px] bg-hero-glow opacity-70" />
        <div className="absolute top-[20%] right-[-5%] w-[500px] h-[500px] bg-copper-500/[0.03] rounded-full blur-[150px]" />
        <div className="absolute bottom-[10%] left-[-5%] w-[400px] h-[400px] bg-sand-500/[0.02] rounded-full blur-[120px]" />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-surface-0/80 backdrop-blur-xl border-b border-surface-4/50">
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
            <Link to="/login" className="btn-ghost">Sign in</Link>
            <Link to="/signup" className="btn-primary">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* ─── Hero Section ─── */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-16">
        <div className="max-w-3xl mx-auto text-center">
          {/* Status badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-surface-1 border border-surface-4 rounded-full mb-8">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-sand-400">Powered by Llama 3.3 70B via Groq</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-sand-50 tracking-tight mb-6 leading-[1.1]">
            Code review<br />
            <span className="bg-gradient-to-r from-copper-400 via-copper-300 to-sand-300 bg-clip-text text-transparent">
              that thinks.
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-sand-500 mb-12 max-w-xl mx-auto leading-relaxed">
            AI-powered pull request analysis with risk scoring, auto-fix generation, 
            and plain-English summaries. Ship faster, ship safer.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/signup"
              className="btn-primary text-base px-8 py-3.5 flex items-center gap-2"
            >
              Start Reviewing
              <ChevronRight className="w-4 h-4" />
            </Link>
            <a
              href="#features"
              className="btn-ghost text-base px-6 py-3 flex items-center gap-2"
            >
              See how it works
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Floating metrics bar */}
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2">
          <div className="flex items-center gap-6 md:gap-10 px-8 py-4 bg-surface-1/80 backdrop-blur-md border border-surface-4 rounded-2xl">
            <div className="text-center">
              <div className="text-2xl font-bold text-sand-100">0→100</div>
              <div className="text-[10px] font-semibold text-sand-600 uppercase tracking-widest mt-1">Risk Score</div>
            </div>
            <div className="w-px h-10 bg-surface-4" />
            <div className="text-center">
              <div className="text-2xl font-bold text-sand-100">&lt;30s</div>
              <div className="text-[10px] font-semibold text-sand-600 uppercase tracking-widest mt-1">Analysis</div>
            </div>
            <div className="w-px h-10 bg-surface-4" />
            <div className="text-center">
              <div className="text-2xl font-bold text-sand-100">1-Click</div>
              <div className="text-[10px] font-semibold text-sand-600 uppercase tracking-widest mt-1">Auto Fix</div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Social Proof Bar ─── */}
      <section className="relative py-10 px-6 border-y border-surface-4/50">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 text-center">
          <div>
            <div className="text-3xl font-extrabold text-sand-100">4</div>
            <div className="text-xs text-sand-600 mt-1">LLM Providers</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-sand-100">12+</div>
            <div className="text-xs text-sand-600 mt-1">Built-in Rules</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-sand-100">5 min</div>
            <div className="text-xs text-sand-600 mt-1">Setup Time</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-sand-100">100%</div>
            <div className="text-xs text-sand-600 mt-1">Open Source</div>
          </div>
        </div>
      </section>

      {/* ─── What Sets Us Apart ─── */}
      <section id="features" className="relative py-28 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs font-bold text-copper-500 uppercase tracking-[0.2em] mb-4 block">What sets us apart</span>
            <h2 className="text-3xl md:text-4xl font-bold text-sand-100 mb-4">
              Features that don't exist<br />anywhere else.
            </h2>
            <p className="text-sand-500 max-w-lg mx-auto">
              Not just another linter. CodeLens AI understands context, calculates risk, 
              generates fixes, and learns from your team's decisions.
            </p>
          </div>

          {/* Bento Grid */}
          <div className="grid md:grid-cols-2 gap-5 mb-20">
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

          {/* Core Capabilities */}
          <div className="grid md:grid-cols-3 gap-5">
            <FeatureCard
              icon={Code2}
              title="Deep Analysis"
              description="Understands your codebase context. Finds bugs, security issues, and performance problems that basic linters miss."
            />
            <FeatureCard
              icon={Shield}
              title="Security First"
              description="Detects vulnerabilities, auth bypasses, TOCTOU attacks, race conditions, injection flaws, and hardcoded secrets."
            />
            <FeatureCard
              icon={Zap}
              title="Groq-Fast"
              description="Powered by Llama 3.3 70B on Groq's LPU inference. Full PR analysis completes in seconds, not minutes."
            />
          </div>
        </div>
      </section>

      {/* ─── How the Analysis Works ─── */}
      <section className="relative py-28 px-6 border-t border-surface-4/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs font-bold text-copper-500 uppercase tracking-[0.2em] mb-4 block">Under the hood</span>
            <h2 className="text-3xl md:text-4xl font-bold text-sand-100 mb-4">
              What happens when a PR is opened
            </h2>
            <p className="text-sand-500 max-w-lg mx-auto">
              Every pull request triggers a multi-stage analysis pipeline that combines
              static rules with AI reasoning.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Pipeline steps */}
            <div className="space-y-4">
              <PipelineStep
                step="1"
                icon={GitPullRequest}
                title="Webhook Received"
                description="GitHub sends a webhook event when a PR is opened or updated. We parse the diff and identify changed files."
              />
              <PipelineStep
                step="2"
                icon={Terminal}
                title="Static Rule Engine"
                description="12+ built-in rules check for security issues, code smells, error handling gaps, and performance anti-patterns."
              />
              <PipelineStep
                step="3"
                icon={Brain}
                title="AI Contextual Review"
                description="Llama 3.3 70B analyzes each file change with full context — understanding intent, not just syntax."
              />
              <PipelineStep
                step="4"
                icon={BarChart3}
                title="Risk Scoring"
                description="A hybrid algorithm produces a 0-100 risk score considering complexity, blast radius, and sensitive file changes."
              />
              <PipelineStep
                step="5"
                icon={Sparkles}
                title="Fix Generation"
                description="For every finding, the AI generates a working unified diff patch you can apply with one click."
              />
            </div>

            {/* Mock analysis output */}
            <div className="card p-0 overflow-hidden self-start">
              <div className="px-5 py-3 bg-surface-2 border-b border-surface-4 flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/60" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/60" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/60" />
                </div>
                <span className="text-xs font-mono text-sand-600">analysis-output.json</span>
              </div>
              <div className="p-5 font-mono text-xs leading-relaxed text-sand-500 overflow-x-auto">
                <div className="text-sand-700">{"// CodeLens AI Analysis Result"}</div>
                <div>{"{"}</div>
                <div className="pl-4">
                  <span className="text-copper-400">"risk_score"</span>: <span className="text-amber-400">73</span>,
                </div>
                <div className="pl-4">
                  <span className="text-copper-400">"risk_level"</span>: <span className="text-emerald-400">"high"</span>,
                </div>
                <div className="pl-4">
                  <span className="text-copper-400">"summary"</span>: <span className="text-emerald-400">"This PR modifies the</span>
                </div>
                <div className="pl-8">
                  <span className="text-emerald-400">authentication middleware and adds</span>
                </div>
                <div className="pl-8">
                  <span className="text-emerald-400">a new API route without rate limiting."</span>,
                </div>
                <div className="pl-4">
                  <span className="text-copper-400">"findings"</span>: <span className="text-sand-600">[</span>
                </div>
                <div className="pl-8">{"{"}</div>
                <div className="pl-12">
                  <span className="text-copper-400">"severity"</span>: <span className="text-red-400">"critical"</span>,
                </div>
                <div className="pl-12">
                  <span className="text-copper-400">"rule"</span>: <span className="text-emerald-400">"AUTH_BYPASS"</span>,
                </div>
                <div className="pl-12">
                  <span className="text-copper-400">"message"</span>: <span className="text-emerald-400">"Missing auth</span>
                </div>
                <div className="pl-16">
                  <span className="text-emerald-400">check on /api/admin endpoint"</span>,
                </div>
                <div className="pl-12">
                  <span className="text-copper-400">"has_auto_fix"</span>: <span className="text-amber-400">true</span>
                </div>
                <div className="pl-8">{"}"}</div>
                <div className="pl-4">
                  <span className="text-sand-600">]</span>
                </div>
                <div>{"}"}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Setup Steps ─── */}
      <section className="relative py-28 px-6 border-t border-surface-4/50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs font-bold text-copper-500 uppercase tracking-[0.2em] mb-4 block">Getting started</span>
            <h2 className="text-3xl md:text-4xl font-bold text-sand-100">Three steps. Five minutes.</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <Step number={1} title="Connect your repo" description="Install the CodeLens AI GitHub App on your repositories. We only request the minimum permissions needed." />
            <Step number={2} title="Configure rules" description="Set severity levels, choose focus areas, and define custom patterns that match your team's coding standards." />
            <Step number={3} title="Reviews run automatically" description="Every PR gets full analysis: findings, risk scores, auto-fixes, and plain-English summaries appear instantly." />
          </div>
        </div>
      </section>

      {/* ─── Tech Stack / Supported ─── */}
      <section className="relative py-20 px-6 border-t border-surface-4/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h3 className="text-lg font-bold text-sand-100 mb-2">Built with production-grade infrastructure</h3>
            <p className="text-sm text-sand-600">Modern stack. Battle-tested components. Enterprise-ready from day one.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <TechBadge label="FastAPI" sub="Backend" />
            <TechBadge label="React 18" sub="Frontend" />
            <TechBadge label="PostgreSQL" sub="Database" />
            <TechBadge label="Groq LPU" sub="Inference" />
            <TechBadge label="Celery" sub="Task Queue" />
            <TechBadge label="Redis" sub="Cache" />
            <TechBadge label="JWT Auth" sub="Security" />
            <TechBadge label="GitHub App" sub="Integration" />
          </div>
        </div>
      </section>

      {/* ─── Pricing / Why Free ─── */}
      <section className="relative py-28 px-6 border-t border-surface-4/50">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div>
              <span className="text-xs font-bold text-copper-500 uppercase tracking-[0.2em] mb-4 block">Open source</span>
              <h2 className="text-3xl font-bold text-sand-100 mb-4">Free. Forever. No catch.</h2>
              <p className="text-sand-500 mb-6 leading-relaxed">
                CodeLens AI is open source and free to self-host. Bring your own Groq API key 
                (free tier available) and deploy on your infrastructure. No vendor lock-in, no 
                per-seat pricing, no surprise bills.
              </p>
              <ul className="space-y-3">
                <BulletPoint text="Unlimited repositories" />
                <BulletPoint text="Unlimited team members" />
                <BulletPoint text="All features included" />
                <BulletPoint text="Self-hosted — your data stays yours" />
                <BulletPoint text="MIT Licensed" />
              </ul>
            </div>
            <div className="card p-8 text-center">
              <div className="text-5xl font-extrabold text-sand-50 mb-2">$0</div>
              <div className="text-sm text-sand-600 mb-6">per month, forever</div>
              <div className="border-t border-surface-4 pt-6 space-y-3 text-sm text-left">
                <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400 shrink-0" /><span className="text-sand-400">PR Risk Scoring (0-100)</span></div>
                <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400 shrink-0" /><span className="text-sand-400">AI Auto-Fix Generation</span></div>
                <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400 shrink-0" /><span className="text-sand-400">Natural Language Summaries</span></div>
                <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400 shrink-0" /><span className="text-sand-400">Learning / False-Positive Suppression</span></div>
                <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400 shrink-0" /><span className="text-sand-400">Security & Performance Rules</span></div>
                <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400 shrink-0" /><span className="text-sand-400">Multi-LLM (Groq, OpenAI, Anthropic, Google)</span></div>
              </div>
              <Link to="/signup" className="btn-primary w-full mt-8 flex items-center justify-center gap-2">
                Get Started <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Final CTA ─── */}
      <section className="relative py-28 px-6 border-t border-surface-4/50">
        <div className="max-w-3xl mx-auto">
          <div className="relative overflow-hidden rounded-2xl border border-surface-4 bg-surface-1 p-12 md:p-16 text-center">
            <div className="absolute inset-0 bg-hero-glow opacity-50" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold text-sand-100 mb-4">
                Ready to ship with confidence?
              </h2>
              <p className="text-sand-500 mb-8 max-w-md mx-auto">
                Create an account and connect your first repository in under 5 minutes. 
                No credit card required.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to="/signup" className="btn-primary text-base px-8 py-3.5">
                  Create free account
                </Link>
                <Link to="/login" className="btn-secondary text-base px-6 py-3">
                  Sign in
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="py-12 px-6 border-t border-surface-4/50">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-sand-700" />
            <span className="text-sm font-medium text-sand-700">CodeLens AI</span>
          </div>
          <div className="flex items-center gap-6 text-xs text-sand-700">
            <span>Open Source</span>
            <span>MIT License</span>
            <span>&copy; 2026</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ─── Sub-components ─── */

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
    <div className="group relative card p-8 overflow-hidden hover:border-surface-4/80 transition-all duration-300">
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
    <div className="card p-6 hover:border-surface-4/80 transition-all duration-300">
      <div className="w-10 h-10 bg-surface-2 border border-surface-4 rounded-xl flex items-center justify-center mb-4">
        <Icon className="w-5 h-5 text-sand-400" />
      </div>
      <h3 className="text-sm font-semibold text-sand-100 mb-2">{title}</h3>
      <p className="text-sm text-sand-600 leading-relaxed">{description}</p>
    </div>
  );
}

function PipelineStep({ step, icon: Icon, title, description }: { step: string; icon: typeof Code2; title: string; description: string }) {
  return (
    <div className="flex gap-4 items-start">
      <div className="shrink-0 w-10 h-10 bg-copper-500/10 border border-copper-500/20 rounded-xl flex items-center justify-center">
        <Icon className="w-5 h-5 text-copper-400" />
      </div>
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold text-copper-500 uppercase tracking-widest">Step {step}</span>
        </div>
        <h3 className="text-sm font-semibold text-sand-100 mb-1">{title}</h3>
        <p className="text-xs text-sand-600 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

function Step({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-copper-500/10 border border-copper-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-base font-bold text-copper-400">{number}</span>
      </div>
      <h3 className="text-sm font-semibold text-sand-100 mb-2">{title}</h3>
      <p className="text-sm text-sand-600 leading-relaxed">{description}</p>
    </div>
  );
}

function TechBadge({ label, sub }: { label: string; sub: string }) {
  return (
    <div className="bg-surface-1 border border-surface-4 rounded-xl p-4 text-center hover:border-surface-4/80 transition-colors">
      <div className="text-sm font-semibold text-sand-200">{label}</div>
      <div className="text-[10px] text-sand-700 uppercase tracking-wider mt-1">{sub}</div>
    </div>
  );
}

function BulletPoint({ text }: { text: string }) {
  return (
    <li className="flex items-center gap-2.5 list-none">
      <div className="w-5 h-5 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center justify-center shrink-0">
        <Check className="w-3 h-3 text-emerald-400" />
      </div>
      <span className="text-sm text-sand-400">{text}</span>
    </li>
  );
}
