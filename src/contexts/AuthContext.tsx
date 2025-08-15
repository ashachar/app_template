import { createContext, useEffect, useState } from 'react';
import { Session, User } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';
import { authService } from './AuthContext.services';
import { 
  initializeRedirectUrl, 
  persistRedirectUrl, 
  shouldRedirectToAuthCallback 
} from './AuthContext.utils';
import { AuthContextType } from './AuthContext.types';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [phoneVerificationRequired, setPhoneVerificationRequired] = useState(false);
  const [redirectUrl, setRedirectUrl] = useState<string | null>(() => initializeRedirectUrl());
  const setRedirectUrlWithLogging = (url: string | null) => {
    setRedirectUrl(url);
    persistRedirectUrl(url);
  };

  const setSourcePath = (path: string) => {
    // Set the source path as a relative path for proper routing
    setRedirectUrlWithLogging(path);
  };

  const clearRedirectUrl = () => {
    setRedirectUrlWithLogging(null);
  };

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
      
      // Force session refresh if we detect a sign in event
      if (event === 'SIGNED_IN') {
        supabase.auth.getSession().then(({ data: { session: refreshedSession } }) => {
          if (refreshedSession) {
            setSession(refreshedSession);
            setUser(refreshedSession.user);
            setLoading(false);
          }
        });
      }
    });

    // Hash parameter handling is now done in AuthNavigationHandler
    // to properly use React Router navigation
    
    // Give Supabase a moment to process the hash parameters if present
    if (typeof window !== 'undefined' && window.location.hash) {
      setTimeout(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
          if (session) {
            setSession(session);
            setUser(session.user);
            setLoading(false);
          }
        });
      }, 100);
    }

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const signUp = async (email: string, password: string, metadata?: { full_name?: string; referral_code?: string }) => {
    return authService.signUp(email, password, metadata);
  };

  const signIn = async (email: string, password: string) => {
    return authService.signIn(email, password);
  };

  const signInWithGoogle = async (referralCode?: string) => {
    return authService.signInWithGoogle(referralCode);
  };

  const signOut = async () => {
    await authService.signOut();
    clearRedirectUrl(); // Clear redirect URL on sign out
  };

  const resendConfirmationEmail = async (email: string) => {
    return authService.resendConfirmationEmail(email);
  };

  const checkPhoneVerification = async (userId: string): Promise<boolean> => {
    const result = await authService.checkPhoneVerification(userId);
    setPhoneVerificationRequired(result);
    return result;
  };

  const setPhoneVerified = () => {
    setPhoneVerificationRequired(false);
  };

  const value = {
    session,
    user,
    loading,
    redirectUrl,
    phoneVerificationRequired,
    setRedirectUrl: setRedirectUrlWithLogging,
    setSourcePath,
    clearRedirectUrl,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
    resendConfirmationEmail,
    checkPhoneVerification,
    setPhoneVerified
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Re-export for backward compatibility
export { useAuth } from './AuthContext.hooks'; 