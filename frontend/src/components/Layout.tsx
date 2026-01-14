import { ReactNode, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Activity, GitPullRequest, FolderGit2, Settings, LogOut, User } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/projects', label: 'Projects', icon: FolderGit2 },
    { path: '/configuration', label: 'Settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <nav className="sticky top-0 z-50 bg-neutral-950/80 backdrop-blur-xl border-b border-neutral-800/50">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2.5 group">
                <div className="p-1.5 bg-neutral-900 rounded-lg border border-neutral-800 group-hover:border-neutral-700 transition-colors">
                  <GitPullRequest className="w-5 h-5 text-neutral-400 group-hover:text-neutral-300 transition-colors" />
                </div>
                <span className="text-sm font-semibold text-neutral-100">
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
                      className={`flex items-center space-x-2 px-3 py-1.5 rounded-md transition-colors ${
                        isActive
                          ? 'bg-neutral-800/50 text-neutral-100'
                          : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/30'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </div>

            <div className="relative">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 px-2 py-1.5 rounded-md text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/30 transition-colors"
              >
                <div className="w-6 h-6 bg-neutral-800 rounded-full flex items-center justify-center">
                  <User className="w-3.5 h-3.5 text-neutral-400" />
                </div>
                <span className="text-sm hidden sm:block">{user?.name || 'User'}</span>
              </button>
              
              {showUserMenu && (
                <>
                  <div className="fixed inset-0" onClick={() => setShowUserMenu(false)} />
                  <div className="absolute right-0 mt-1 w-48 bg-neutral-900 border border-neutral-800 rounded-lg shadow-xl py-1 z-50">
                    <div className="px-3 py-2 border-b border-neutral-800">
                      <p className="text-sm font-medium text-neutral-200">{user?.name}</p>
                      <p className="text-xs text-neutral-500 truncate">{user?.email}</p>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/50 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign out</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-8 max-w-7xl">
        {children}
      </main>
      
      <footer className="border-t border-neutral-800/50 py-6 mt-8">
        <div className="container mx-auto px-6 text-center">
          <p className="text-neutral-600 text-xs">
            &copy; 2026 AI Code Review Assistant
          </p>
        </div>
      </footer>
    </div>
  )
}
