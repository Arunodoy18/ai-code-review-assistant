import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getBaseUrl = (): string => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  return 'http://localhost:8000';
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('auth_user');
    const token = localStorage.getItem('auth_token');
    
    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
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

      // If endpoint doesn't exist (404), fall back to demo mode
      if (response.status === 404) {
        console.warn('Auth endpoint not available, using demo mode');
        const demoUser: User = {
          id: Date.now().toString(),
          email,
          name: email.split('@')[0],
        };
        setUser(demoUser);
        localStorage.setItem('auth_user', JSON.stringify(demoUser));
        localStorage.setItem('auth_token', 'demo_session');
        return { success: true };
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Login failed' }));
        return { success: false, error: error.detail || 'Invalid credentials' };
      }

      const data = await response.json();
      const userData: User = {
        id: data.user?.id || email,
        email: data.user?.email || email,
        name: data.user?.name || email.split('@')[0],
      };
      
      setUser(userData);
      localStorage.setItem('auth_user', JSON.stringify(userData));
      localStorage.setItem('auth_token', data.access_token || 'session');
      
      return { success: true };
    } catch (error) {
      console.warn('Auth request failed, using demo mode:', error);
      // For demo purposes, allow local login when backend auth is not available
      const demoUser: User = {
        id: Date.now().toString(),
        email,
        name: email.split('@')[0],
      };
      setUser(demoUser);
      localStorage.setItem('auth_user', JSON.stringify(demoUser));
      localStorage.setItem('auth_token', 'demo_session');
      return { success: true };
    }
  };

  const signup = async (name: string, email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${getBaseUrl()}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      // If endpoint doesn't exist (404) or server error, fall back to demo mode
      if (response.status === 404) {
        console.warn('Auth endpoint not available, using demo mode');
        const demoUser: User = {
          id: Date.now().toString(),
          email,
          name,
        };
        setUser(demoUser);
        localStorage.setItem('auth_user', JSON.stringify(demoUser));
        localStorage.setItem('auth_token', 'demo_session');
        return { success: true };
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Signup failed' }));
        return { success: false, error: error.detail || 'Could not create account' };
      }

      const data = await response.json();
      const userData: User = {
        id: data.user?.id || email,
        email: data.user?.email || email,
        name: data.user?.name || name,
      };
      
      setUser(userData);
      localStorage.setItem('auth_user', JSON.stringify(userData));
      localStorage.setItem('auth_token', data.access_token || 'session');
      
      return { success: true };
    } catch (error) {
      console.warn('Auth request failed, using demo mode:', error);
      // For demo purposes, allow local signup when backend auth is not available
      const demoUser: User = {
        id: Date.now().toString(),
        email,
        name,
      };
      setUser(demoUser);
      localStorage.setItem('auth_user', JSON.stringify(demoUser));
      localStorage.setItem('auth_token', 'demo_session');
      return { success: true };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
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
