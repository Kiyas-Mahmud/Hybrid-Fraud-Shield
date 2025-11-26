'use client';

import * as authApi from '@/lib/api/auth';
import { LoginRequest, RegisterRequest, User } from '@/lib/types';
import { useRouter } from 'next/navigation';
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = authApi.getToken();
        if (token) {
          // Try to get current user
          const currentUser = await authApi.getCurrentUser();
          setUser(currentUser);
        }
      } catch (err) {
        // Token invalid or expired, clear it
        authApi.logout();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = useCallback(async (credentials: LoginRequest) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Attempting login with:', { username: credentials.username });
      const response = await authApi.login(credentials);
      console.log('Login response:', response);
      
      // Get user profile after login
      const currentUser = await authApi.getCurrentUser();
      console.log('Current user:', currentUser);
      setUser(currentUser);
      
      // Small delay to ensure state is updated
      setTimeout(() => {
        console.log('Redirecting to dashboard...');
        router.replace('/dashboard');
      }, 100);
    } catch (err: any) {
      console.error('Login error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Invalid username or password';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [router]);

  const register = useCallback(async (userData: RegisterRequest) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authApi.register(userData);
      
      // Get user profile after registration
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [router]);

  const logout = useCallback(() => {
    authApi.logout();
    setUser(null);
    router.push('/login');
  }, [router]);

  const value: AuthContextType = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
