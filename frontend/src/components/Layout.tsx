import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Activity, GitPullRequest, FolderGit2, Settings, Moon, Sun } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/projects', label: 'Projects', icon: FolderGit2 },
    { path: '/configuration', label: 'Configuration', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-800 transition-colors duration-500">
      <nav className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-md border-b border-gray-200 dark:border-slate-700 shadow-lg sticky top-0 z-50 transition-all duration-300">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2 group">
                <div className="p-2 bg-blue-500/10 rounded-lg group-hover:bg-blue-500/20 transition-colors duration-300">
                  <GitPullRequest className="w-8 h-8 text-blue-600 dark:text-blue-400 transform group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
                  AI Code Review
                </span>
              </Link>
              
              <div className="flex space-x-4">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 ${
                        isActive
                          ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/30 scale-105'
                          : 'text-gray-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700/50 hover:text-gray-900 dark:hover:text-white hover:shadow-sm hover:-translate-y-0.5'
                      }`}
                    >
                      <Icon className={`w-5 h-5 ${isActive ? 'animate-pulse' : ''}`} />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-xl text-gray-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700/50 hover:text-gray-900 dark:hover:text-white transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-5 h-5 text-yellow-400 drop-shadow-[0_0_8px_rgba(250,204,21,0.5)]" />
              ) : (
                <Moon className="w-5 h-5 text-indigo-600 drop-shadow-[0_0_8px_rgba(79,70,229,0.5)]" />
              )}
            </button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8 animate-fade-in">
        {children}
      </main>
    </div>
  )
}
