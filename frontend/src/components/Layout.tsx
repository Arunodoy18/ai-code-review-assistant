import { ReactNode, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Activity, Eye, FolderGit2, Settings, LogOut, User } from 'lucide-react'
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
    <div className="min-h-screen bg-surface-0 text-sand-200">
      <nav className="sticky top-0 z-50 bg-surface-0/80 backdrop-blur-xl border-b border-surface-4/50">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2.5 group">
                <div className="relative p-1.5 bg-surface-2 rounded-lg border border-surface-4 group-hover:border-copper-800 transition-colors">
                  <Eye className="w-5 h-5 text-copper-400 group-hover:text-copper-300 transition-colors" />
                  <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-copper-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <div>
                  <span className="text-sm font-bold text-sand-100">CodeLens</span>
                  <span className="text-sm font-light text-sand-500 ml-0.5">AI</span>
                </div>
              </Link>
              
              <div className="hidden md:flex items-center space-x-1">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg transition-all duration-200 ${
                        isActive
                          ? 'bg-surface-2 text-sand-100 shadow-inner-glow border border-surface-4'
                          : 'text-sand-500 hover:text-sand-200 hover:bg-surface-1'
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? 'text-copper-400' : ''}`} />
                      <span className="text-sm font-medium">{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </div>

            <div className="relative">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 px-2 py-1.5 rounded-lg text-sand-500 hover:text-sand-200 hover:bg-surface-1 transition-colors"
              >
                <div className="w-7 h-7 bg-surface-3 rounded-full flex items-center justify-center border border-surface-4">
                  <User className="w-3.5 h-3.5 text-sand-500" />
                </div>
                <span className="text-sm hidden sm:block">{user?.name || 'User'}</span>
              </button>
              
              {showUserMenu && (
                <>
                  <div className="fixed inset-0" onClick={() => setShowUserMenu(false)} />
                  <div className="absolute right-0 mt-2 w-52 bg-surface-2 border border-surface-4 rounded-xl shadow-card-hover py-1.5 z-50 animate-fade-in">
                    <div className="px-4 py-2.5 border-b border-surface-4">
                      <p className="text-sm font-semibold text-sand-100">{user?.name}</p>
                      <p className="text-xs text-sand-600 truncate">{user?.email}</p>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-2.5 px-4 py-2.5 text-sm text-sand-500 hover:text-sand-200 hover:bg-surface-3/50 transition-colors"
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
      
      <footer className="border-t border-surface-4/50 py-6 mt-8">
        <div className="container mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye className="w-3.5 h-3.5 text-sand-800" />
            <span className="text-xs text-sand-800">CodeLens AI</span>
          </div>
          <p className="text-xs text-sand-800">
            &copy; 2026 All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
