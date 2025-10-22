/**
 * useAuth Hook
 * Manages authentication state and synchronizes with API client
 */

import { useEffect, useState, useCallback } from 'react';
import { useSupabaseClient, useSession } from '@supabase/auth-helpers-react';
import { apiClient } from '@/lib/api-client';
import { AuthSession } from '@supabase/supabase-js';

interface AuthState {
  session: AuthSession | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

interface UseAuthReturn extends AuthState {
  signUp: (email: string, password: string, name?: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updatePassword: (newPassword: string) => Promise<void>;
}

/**
 * useAuth hook
 * Provides authentication functionality and manages session
 */
export function useAuth(): UseAuthReturn {
  const supabase = useSupabaseClient();
  const session = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync session with API client whenever it changes
  useEffect(() => {
    if (session) {
      apiClient.setSession(session);
      console.log('✓ API client session updated');
    } else {
      apiClient.setSession(null);
    }
  }, [session]);

  // Listen for unauthorized events
  useEffect(() => {
    const handleUnauthorized = async () => {
      console.warn('Unauthorized access detected, signing out...');
      await supabase.auth.signOut();
      setError('Your session has expired. Please sign in again.');
      window.location.href = '/auth/login';
    };

    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, [supabase]);

  /**
   * Sign up with email and password
   */
  const signUp = useCallback(
    async (email: string, password: string, name?: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const { error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              full_name: name || email.split('@')[0],
            },
            emailRedirectTo: `${window.location.origin}/auth/callback`,
          },
        });

        if (signUpError) {
          throw new Error(signUpError.message);
        }

        // Success - user will receive confirmation email
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Sign up failed';
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [supabase]
  );

  /**
   * Sign in with email and password
   */
  const signIn = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (signInError) {
          throw new Error(signInError.message);
        }

        // Success - session will be updated and API client will be synced
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Sign in failed';
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [supabase]
  );

  /**
   * Sign out
   */
  const signOut = useCallback(async () => {
    setIsLoading(true);
    try {
      const { error: signOutError } = await supabase.auth.signOut();
      if (signOutError) {
        throw new Error(signOutError.message);
      }
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Sign out failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [supabase]);

  /**
   * Reset password (send reset email)
   */
  const resetPassword = useCallback(
    async (email: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/auth/reset-password`,
        });

        if (resetError) {
          throw new Error(resetError.message);
        }

        // Success - user will receive reset email
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Password reset failed';
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [supabase]
  );

  /**
   * Update password (requires current session)
   */
  const updatePassword = useCallback(
    async (newPassword: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const { error: updateError } = await supabase.auth.updateUser({
          password: newPassword,
        });

        if (updateError) {
          throw new Error(updateError.message);
        }

        // Success - password updated
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Password update failed';
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [supabase]
  );

  return {
    session,
    isLoading,
    error,
    isAuthenticated: !!session,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword,
  };
}

/**
 * Hook to get current user from session
 */
export function useCurrentUser() {
  const session = useSession();

  return {
    user: session?.user || null,
    id: session?.user?.id,
    email: session?.user?.email,
    isLoading: !session,
  };
}

/**
 * Hook to check if user is authenticated
 */
export function useIsAuthenticated(): boolean {
  const session = useSession();
  return !!session;
}

/**
 * Hook to get access token
 */
export function useAccessToken(): string | null {
  const session = useSession();
  return session?.access_token || null;
}
