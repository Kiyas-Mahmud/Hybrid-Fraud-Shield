import { AuthResponse, LoginRequest, RegisterRequest, User } from '@/lib/types';
import apiClient from './client';

/**
 * Login user
 */
export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const formData = new FormData();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await apiClient.post<AuthResponse>('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  // Store token in localStorage
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
  }

  return response.data;
}

/**
 * Register new user
 */
export async function register(userData: RegisterRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/register', userData);

  // Store token in localStorage
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token);
  }

  return response.data;
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>('/auth/me');
  
  // Store user in localStorage
  localStorage.setItem('user', JSON.stringify(response.data));
  
  return response.data;
}

/**
 * Logout user
 */
export function logout(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
}

/**
 * Get stored token
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Auth API object for grouped imports
 */
export const authApi = {
  login,
  register,
  getCurrentUser,
  logout,
  isAuthenticated,
  getToken,
};
