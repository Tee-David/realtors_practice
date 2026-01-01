/**
 * Authentication Context
 *
 * Provides authentication state and methods throughout the application
 */

'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, onAuthStateChanged } from 'firebase/auth';
import { auth } from '@/lib/firebase/config';
import {
  registerWithEmail,
  signInWithEmail,
  signOutUser,
  resetPassword,
  updateUserProfile,
  getUserIdToken,
  AuthResult
} from '@/lib/firebase/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<AuthResult>;
  signUp: (email: string, password: string, displayName?: string) => Promise<AuthResult>;
  logout: () => Promise<AuthResult>;
  sendPasswordReset: (email: string) => Promise<AuthResult>;
  updateProfile: (updates: { displayName?: string; photoURL?: string }) => Promise<AuthResult>;
  getIdToken: () => Promise<string | null>;
  isAdmin: boolean;
  userRole: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    // Subscribe to auth state changes (only if Firebase is configured)
    if (!auth) {
      console.warn('Firebase Auth not initialized. User authentication is disabled.');
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);

        // Get user's custom claims (role)
        try {
          const idTokenResult = await firebaseUser.getIdTokenResult();
          const role = idTokenResult.claims.role as string | undefined;
          setUserRole(role || 'user');
        } catch (error) {
          console.error('Error getting user role:', error);
          setUserRole('user');
        }
      } else {
        setUser(null);
        setUserRole(null);
      }
      setLoading(false);
    });

    // Cleanup subscription
    return () => unsubscribe();
  }, []);

  const signIn = async (email: string, password: string): Promise<AuthResult> => {
    setLoading(true);
    const result = await signInWithEmail(email, password);
    setLoading(false);
    return result;
  };

  const signUp = async (
    email: string,
    password: string,
    displayName?: string
  ): Promise<AuthResult> => {
    setLoading(true);
    const result = await registerWithEmail(email, password, displayName);
    setLoading(false);
    return result;
  };

  const logout = async (): Promise<AuthResult> => {
    setLoading(true);
    const result = await signOutUser();
    setLoading(false);
    return result;
  };

  const sendPasswordReset = async (email: string): Promise<AuthResult> => {
    return resetPassword(email);
  };

  const updateProfile = async (updates: {
    displayName?: string;
    photoURL?: string;
  }): Promise<AuthResult> => {
    if (!user) {
      return { success: false, error: 'No user logged in' };
    }
    return updateUserProfile(user, updates);
  };

  const getIdToken = async (): Promise<string | null> => {
    return getUserIdToken(user);
  };

  const value: AuthContextType = {
    user,
    loading,
    signIn,
    signUp,
    logout,
    sendPasswordReset,
    updateProfile,
    getIdToken,
    isAdmin: userRole === 'admin',
    userRole
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Export the context for direct access if needed
export { AuthContext };
