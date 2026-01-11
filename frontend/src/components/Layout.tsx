import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Activity, GitPullRequest, FolderGit2, Settings } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/projects', label: 'Projects', icon: FolderGit2 },
    { path: '/configuration', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-[#0b1220] text-slate-100 selection:bg-indigo-500/30">
      <nav className="sticky top-0 z-50 bg-[#0b1220]/80 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/10">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-10">
              <Link to="/" className="flex items-center space-x-3 group">
                <div className="p-2 bg-gradient-to-br from-indigo-500/20 to-blue-500/20 rounded-lg border border-indigo-500/20 group-hover:border-indigo-500/40 transition-all duration-300">
                  <GitPullRequest className="w-6 h-6 text-indigo-400 transform group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <span className="text-lg font-bold tracking-tight text-white group-hover:text-indigo-300 transition-colors">
                  AI Code Review
                </span>
              </Link>
              
              <div className="hidden md:flex items-center space-x-1">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 group ${
                        isActive
                          ? 'bg-white/5 text-indigo-400 font-semibold'
                          : 'text-slate-400 hover:text-slate-100 hover:bg-white/5'
                      }`}
                    >
                      <Icon className={`w-4 h-4 transition-transform duration-200 ${isActive ? 'text-indigo-400' : 'group-hover:scale-110'}`} />
                      <span className="text-sm font-medium">{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="h-4 w-[1px] bg-white/10 hidden sm:block mx-2" />
              <button className="text-slate-400 hover:text-white transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-10 max-w-7xl animate-fade-in">
        {children}
      </main>
      
      <footer className="border-t border-white/5 py-10 mt-10">
        <div className="container mx-auto px-6 text-center">
          <p className="text-slate-500 text-sm">
            &copy; 2026 AI Code Review Assistant
          </p>
        </div>
      </footer>
    </div>
  )
}
