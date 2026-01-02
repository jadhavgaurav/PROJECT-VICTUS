import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient } from '../api/client';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  provider: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: any) => Promise<void>;
  msg_login: (credentials: any) => Promise<void>; // Alias if needed
  signup: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check auth on mount
  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const response = await apiClient.get('/api/auth/me');
      setUser(response.data);
    } catch (error) {
      console.log("Not authenticated");
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function login(credentials: any) {
    await apiClient.post('/api/auth/login', credentials);
    await checkAuth();
  }
  
  // Backward compatibility alias if existing code uses different name
  async function msg_login(credentials: any) {
      await login(credentials);
  }

  async function signup(data: any) {
    await apiClient.post('/api/auth/signup', data);
    await checkAuth();
  }

  async function logout() {
    try {
      await apiClient.post('/api/auth/logout');
    } finally {
      setUser(null);
      // Optional: Redirect to login
      window.location.href = '/login';
    }
  }

  return (
    <AuthContext.Provider value={{ 
        user, 
        loading, 
        login, 
        msg_login, 
        signup, 
        logout,
        checkAuth,
        isAuthenticated: !!user 
    }}>
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
