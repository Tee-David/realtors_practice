/**
 * Authentication API Hooks
 *
 * Provides hooks for interacting with the backend authentication API
 */

'use client';

import { useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export function useAuthAPI() {
  const { getIdToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Make an authenticated API request
   */
  const makeAuthRequest = useCallback(
    async <T = any>(
      endpoint: string,
      options: RequestInit = {}
    ): Promise<APIResponse<T>> => {
      setLoading(true);
      setError(null);

      try {
        // Get Firebase ID token
        const token = await getIdToken();

        if (!token) {
          throw new Error('No authentication token available');
        }

        // Make request with Authorization header
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
          }
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || data.error || 'Request failed');
        }

        setLoading(false);
        return { success: true, data };
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);
        setLoading(false);
        return { success: false, error: errorMessage };
      }
    },
    [getIdToken]
  );

  /**
   * Verify token with backend
   */
  const verifyToken = useCallback(async (idToken: string): Promise<APIResponse> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Token verification failed');
      }

      setLoading(false);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Verification failed';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, []);

  /**
   * Get current user from backend
   */
  const getCurrentUser = useCallback(async (): Promise<APIResponse> => {
    return makeAuthRequest('/api/auth/user/me');
  }, [makeAuthRequest]);

  /**
   * Update current user profile
   */
  const updateUserProfile = useCallback(
    async (updates: { displayName?: string; photoURL?: string }): Promise<APIResponse> => {
      return makeAuthRequest('/api/auth/user/me', {
        method: 'PUT',
        body: JSON.stringify(updates)
      });
    },
    [makeAuthRequest]
  );

  /**
   * Get user by ID (admin or self)
   */
  const getUserById = useCallback(
    async (uid: string): Promise<APIResponse> => {
      return makeAuthRequest(`/api/auth/user/${uid}`);
    },
    [makeAuthRequest]
  );

  /**
   * List all users (admin only)
   */
  const listUsers = useCallback(
    async (limit: number = 100): Promise<APIResponse> => {
      return makeAuthRequest(`/api/auth/users?limit=${limit}`);
    },
    [makeAuthRequest]
  );

  /**
   * Delete user (admin or self)
   */
  const deleteUser = useCallback(
    async (uid: string): Promise<APIResponse> => {
      return makeAuthRequest(`/api/auth/user/${uid}`, {
        method: 'DELETE'
      });
    },
    [makeAuthRequest]
  );

  /**
   * Update user role (admin only)
   */
  const updateUserRole = useCallback(
    async (uid: string, role: 'admin' | 'user'): Promise<APIResponse> => {
      return makeAuthRequest(`/api/auth/user/${uid}/role`, {
        method: 'PUT',
        body: JSON.stringify({ role })
      });
    },
    [makeAuthRequest]
  );

  /**
   * Request password reset
   */
  const requestPasswordReset = useCallback(async (email: string): Promise<APIResponse> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/password-reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Password reset request failed');
      }

      setLoading(false);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Request failed';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, []);

  /**
   * Logout from backend (revoke tokens)
   */
  const logoutFromBackend = useCallback(async (): Promise<APIResponse> => {
    return makeAuthRequest('/api/auth/logout', {
      method: 'POST'
    });
  }, [makeAuthRequest]);

  /**
   * Check auth service health
   */
  const checkAuthHealth = useCallback(async (): Promise<APIResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/health`);
      const data = await response.json();
      return { success: true, data };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Health check failed';
      return { success: false, error: errorMessage };
    }
  }, []);

  return {
    loading,
    error,
    verifyToken,
    getCurrentUser,
    updateUserProfile,
    getUserById,
    listUsers,
    deleteUser,
    updateUserRole,
    requestPasswordReset,
    logoutFromBackend,
    checkAuthHealth,
    makeAuthRequest
  };
}
