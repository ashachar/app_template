import { Session, User, AuthError, OAuthResponse } from '@supabase/supabase-js';

export type AuthContextType = {
  session: Session | null;
  user: User | null;
  loading: boolean;
  redirectUrl: string | null;
  phoneVerificationRequired: boolean;
  setRedirectUrl: (url: string | null) => void;
  setSourcePath: (path: string) => void;
  clearRedirectUrl: () => void;
  signUp: (email: string, password: string, metadata?: { full_name?: string; referral_code?: string }) => Promise<{
    error: Error | null;
    data: { user: User | null; session: Session | null } | null;
  }>;
  signIn: (email: string, password: string) => Promise<{
    error: Error | null;
    data: { user: User | null; session: Session | null } | null;
  }>;
  signInWithGoogle: (referralCode?: string) => Promise<OAuthResponse>;
  signOut: () => Promise<void>;
  resendConfirmationEmail: (email: string) => Promise<{
    error: Error | null;
    data: {} | null;
  }>;
  checkPhoneVerification: (userId: string) => Promise<boolean>;
  setPhoneVerified: () => void;
};

export type SignUpMetadata = {
  full_name?: string;
  referral_code?: string;
  is_recruiter?: boolean;
};