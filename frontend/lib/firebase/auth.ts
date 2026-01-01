/**
 * Firebase Authentication Helper Functions
 *
 * Provides utility functions for authentication operations
 */

import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  sendPasswordResetEmail,
  sendEmailVerification,
  updateProfile,
  updateEmail,
  updatePassword,
  deleteUser,
  User,
  UserCredential,
  AuthError
} from 'firebase/auth';
import { auth } from './config';

export interface AuthResult {
  success: boolean;
  user?: User;
  error?: string;
}

/**
 * Register a new user with email and password
 */
export async function registerWithEmail(
  email: string,
  password: string,
  displayName?: string
): Promise<AuthResult> {
  try {
    const userCredential: UserCredential = await createUserWithEmailAndPassword(
      auth,
      email,
      password
    );

    // Update display name if provided
    if (displayName && userCredential.user) {
      await updateProfile(userCredential.user, { displayName });
    }

    // Send email verification
    if (userCredential.user) {
      await sendEmailVerification(userCredential.user);
    }

    return {
      success: true,
      user: userCredential.user
    };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Sign in with email and password
 */
export async function signInWithEmail(
  email: string,
  password: string
): Promise<AuthResult> {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return {
      success: true,
      user: userCredential.user
    };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Sign out the current user
 */
export async function signOutUser(): Promise<AuthResult> {
  try {
    await signOut(auth);
    return { success: true };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Send password reset email
 */
export async function resetPassword(email: string): Promise<AuthResult> {
  try {
    await sendPasswordResetEmail(auth, email);
    return { success: true };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Update user profile
 */
export async function updateUserProfile(
  user: User,
  updates: { displayName?: string; photoURL?: string }
): Promise<AuthResult> {
  try {
    await updateProfile(user, updates);
    return { success: true, user };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Update user email
 */
export async function updateUserEmail(
  user: User,
  newEmail: string
): Promise<AuthResult> {
  try {
    await updateEmail(user, newEmail);
    return { success: true, user };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Update user password
 */
export async function updateUserPassword(
  user: User,
  newPassword: string
): Promise<AuthResult> {
  try {
    await updatePassword(user, newPassword);
    return { success: true, user };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Delete user account
 */
export async function deleteUserAccount(user: User): Promise<AuthResult> {
  try {
    await deleteUser(user);
    return { success: true };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}

/**
 * Get user-friendly error messages
 */
function getAuthErrorMessage(error: AuthError): string {
  switch (error.code) {
    case 'auth/email-already-in-use':
      return 'This email is already registered. Please sign in instead.';
    case 'auth/invalid-email':
      return 'Invalid email address format.';
    case 'auth/operation-not-allowed':
      return 'Email/password accounts are not enabled. Please contact support.';
    case 'auth/weak-password':
      return 'Password is too weak. Please use at least 6 characters.';
    case 'auth/user-disabled':
      return 'This account has been disabled. Please contact support.';
    case 'auth/user-not-found':
      return 'No account found with this email.';
    case 'auth/wrong-password':
      return 'Incorrect password. Please try again.';
    case 'auth/invalid-credential':
      return 'Invalid credentials. Please check your email and password.';
    case 'auth/too-many-requests':
      return 'Too many failed attempts. Please try again later.';
    case 'auth/requires-recent-login':
      return 'This operation requires recent login. Please sign in again.';
    default:
      return error.message || 'An authentication error occurred. Please try again.';
  }
}

/**
 * Get current user's ID token
 */
export async function getUserIdToken(user: User | null): Promise<string | null> {
  if (!user) return null;
  try {
    const token = await user.getIdToken();
    return token;
  } catch (error) {
    console.error('Error getting ID token:', error);
    return null;
  }
}

/**
 * Check if user email is verified
 */
export function isEmailVerified(user: User | null): boolean {
  return user?.emailVerified ?? false;
}

/**
 * Resend verification email
 */
export async function resendVerificationEmail(user: User): Promise<AuthResult> {
  try {
    await sendEmailVerification(user);
    return { success: true };
  } catch (error) {
    const authError = error as AuthError;
    return {
      success: false,
      error: getAuthErrorMessage(authError)
    };
  }
}
