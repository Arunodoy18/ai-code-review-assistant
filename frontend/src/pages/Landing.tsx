import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { GitPullRequest, Code2, GitBranch, Shield, Zap, Users, ArrowDown, ChevronRight } from 'lucide-react';

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
    <div className="min-h-screen bg-neutral-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-neutral-950/80 backdrop-blur-md border-b border-neutral-900">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 bg-neutral-900 rounded-lg border border-neutral-800">
              <GitPullRequest className="w-5 h-5 text-neutral-400" />
            </div>
            <span className="text-sm font-semibold text-neutral-100">AI Code Review</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="px-3 py-1.5 text-sm text-neutral-400 hover:text-neutral-200 transition-colors duration-200"
            >
              Sign in
            </Link>
            <Link
              to="/signup"
              className="px-3 py-1.5 text-sm bg-neutral-800 hover:bg-neutral-700 text-neutral-200 rounded-md transition-colors duration-200"
            >
              Sign up
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="min-h-screen flex flex-col items-center justify-center px-6 pt-14">
        <div className="max-w-2xl mx-auto text-center animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-neutral-900 rounded-2xl border border-neutral-800 mb-8">
            <GitPullRequest className="w-8 h-8 text-neutral-400" />
          </div>
          
          <h1 className="text-4xl md:text-5xl font-semibold text-neutral-100 tracking-tight mb-4">
            Code review, automated
          </h1>
          
          <p className="text-lg text-neutral-400 mb-10 max-w-md mx-auto leading-relaxed">
            Get instant, intelligent feedback on every pull request. 
            Built for teams who ship with confidence.
          </p>

          <button
            onClick={scrollToInfo}
            className="inline-flex items-center gap-2 px-6 py-3 bg-amber-800 hover:bg-amber-700 text-neutral-100 font-medium rounded-lg transition-colors duration-200"
          >
            Get Started
            <ChevronRight className="w-4 h-4" />
          </button>

          <div className="mt-16 animate-pulse-subtle">
            <button
              onClick={scrollToInfo}
              className="text-neutral-600 hover:text-neutral-400 transition-colors duration-200"
              aria-label="Learn more"
            >
              <ArrowDown className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Info Section */}
      <section
        ref={infoRef}
        className={`py-24 px-6 transition-opacity duration-300 ${showInfo ? 'opacity-100' : 'opacity-0'}`}
      >
        <div className="max-w-4xl mx-auto">
          {/* What it does */}
          <div className="mb-20">
            <h2 className="text-2xl font-semibold text-neutral-100 mb-4">What it does</h2>
            <p className="text-neutral-400 leading-relaxed max-w-2xl">
              AI Code Review analyzes your pull requests automatically, identifying bugs, 
              security issues, and code quality concerns before they reach production. 
              It integrates directly with your GitHub workflow—no context switching required.
            </p>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mb-20">
            <FeatureCard
              icon={Code2}
              title="Deep Analysis"
              description="Understands your codebase context to provide relevant, actionable feedback."
            />
            <FeatureCard
              icon={Shield}
              title="Security First"
              description="Catches vulnerabilities and security anti-patterns before they ship."
            />
            <FeatureCard
              icon={Zap}
              title="Fast Feedback"
              description="Reviews complete within minutes, not hours. Keep your flow state."
            />
          </div>

          {/* Who it's for */}
          <div className="mb-20">
            <h2 className="text-2xl font-semibold text-neutral-100 mb-4">Built for developers</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-neutral-900 rounded-lg border border-neutral-800 flex items-center justify-center">
                  <GitBranch className="w-5 h-5 text-neutral-500" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-neutral-200 mb-1">Development teams</h3>
                  <p className="text-sm text-neutral-500">
                    Ship faster with automated first-pass reviews. Free up senior engineers for architecture decisions.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-neutral-900 rounded-lg border border-neutral-800 flex items-center justify-center">
                  <Users className="w-5 h-5 text-neutral-500" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-neutral-200 mb-1">Open source maintainers</h3>
                  <p className="text-sm text-neutral-500">
                    Scale your review capacity. Maintain quality standards across hundreds of contributions.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* How it works */}
          <div className="mb-20">
            <h2 className="text-2xl font-semibold text-neutral-100 mb-6">How it works</h2>
            <div className="space-y-4">
              <Step number={1} title="Connect your repository" description="Link your GitHub repos in one click. We only request the permissions we need." />
              <Step number={2} title="Configure your rules" description="Set severity levels, focus areas, and custom patterns that match your team's standards." />
              <Step number={3} title="Review automatically" description="Every PR gets analyzed. Comments appear inline, just like a human reviewer." />
            </div>
          </div>

          {/* CTA */}
          <div className="text-center py-12 border-t border-neutral-900">
            <h2 className="text-xl font-semibold text-neutral-100 mb-3">Ready to start?</h2>
            <p className="text-neutral-500 mb-6">Create an account or sign in to continue.</p>
            <div className="flex items-center justify-center gap-3">
              <Link
                to="/signup"
                className="px-5 py-2.5 bg-amber-800 hover:bg-amber-700 text-neutral-100 font-medium text-sm rounded-lg transition-colors duration-200"
              >
                Create account
              </Link>
              <Link
                to="/login"
                className="px-5 py-2.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-medium text-sm rounded-lg transition-colors duration-200"
              >
                Sign in
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-neutral-900">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-xs text-neutral-600">
            AI Code Review Assistant
          </p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description }: { icon: typeof Code2; title: string; description: string }) {
  return (
    <div className="p-5 bg-neutral-900/50 border border-neutral-800 rounded-lg">
      <div className="w-9 h-9 bg-neutral-800 rounded-lg flex items-center justify-center mb-3">
        <Icon className="w-4 h-4 text-neutral-400" />
      </div>
      <h3 className="text-sm font-medium text-neutral-200 mb-1.5">{title}</h3>
      <p className="text-sm text-neutral-500 leading-relaxed">{description}</p>
    </div>
  );
}

function Step({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-7 h-7 bg-amber-900/30 border border-amber-800/50 rounded-full flex items-center justify-center">
        <span className="text-xs font-medium text-amber-600">{number}</span>
      </div>
      <div>
        <h3 className="text-sm font-medium text-neutral-200">{title}</h3>
        <p className="text-sm text-neutral-500">{description}</p>
      </div>
    </div>
  );
}
