import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getApiBaseUrl } from '../config/env';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getBaseUrl = (): string => getApiBaseUrl();

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('auth_user');
    const storedToken = localStorage.getItem('auth_token');
    
    if (storedUser && storedToken && storedToken !== 'demo_session') {
      try {
        setUser(JSON.parse(storedUser));
        setToken(storedToken);
        // Verify token is still valid
        fetch(`${getBaseUrl()}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${storedToken}` },
        }).then(res => {
          if (!res.ok) {
            // Token expired, clear state
            localStorage.removeItem('auth_user');
            localStorage.removeItem('auth_token');
            setUser(null);
            setToken(null);
          }
        }).catch(() => {
          // Backend unreachable, keep local session
        });
      } catch {
        localStorage.removeItem('auth_user');
        localStorage.removeItem('auth_token');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${getBaseUrl()}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Login failed' }));
        return { success: false, error: error.detail || 'Invalid credentials' };
      }

      const data = await response.json();
      const userData: User = {
        id: data.user?.id?.toString() || email,
        email: data.user?.email || email,
        name: data.user?.name || email.split('@')[0],
      };
      
      setUser(userData);
      setToken(data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(userData));
      localStorage.setItem('auth_token', data.access_token);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Unable to reach server. Please try again.' };
    }
  };

  const signup = async (name: string, email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${getBaseUrl()}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Signup failed' }));
        return { success: false, error: error.detail || 'Could not create account' };
      }

      const data = await response.json();
      const userData: User = {
        id: data.user?.id?.toString() || email,
        email: data.user?.email || email,
        name: data.user?.name || name,
      };
      
      setUser(userData);
      setToken(data.access_token);
      localStorage.setItem('auth_user', JSON.stringify(userData));
      localStorage.setItem('auth_token', data.access_token);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: 'Unable to reach server. Please try again.' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        token,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
