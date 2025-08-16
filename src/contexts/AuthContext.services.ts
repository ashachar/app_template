import { supabase } from '@/lib/supabase';
import { getAuthCallbackUrl } from './AuthContext.utils';
import { SignUpMetadata } from './AuthContext.types';

export const authService = {
  async signUp(email: string, password: string, metadata?: SignUpMetadata) {
    try {
      const emailRedirectUrl = getAuthCallbackUrl(metadata?.referral_code);
      
      // Simplify the metadata to avoid database errors
      const signUpOptions = {
        email,
        password,
        options: {
          data: {
            full_name: metadata?.full_name || '',
            app_origin: window.location.origin,
            signup_method: 'email' // Add this to distinguish from Google signup
          },
          emailRedirectTo: emailRedirectUrl
        }
      };
      
      const response = await supabase.auth.signUp(signUpOptions);
      
      // If there's an error and it's about the email already being in use
      if (response.error && response.error.message.includes('email') && 
          response.error.message.toLowerCase().includes('already') && 
          response.error.message.toLowerCase().includes('registered')) {
        return {
          error: {
            message: 'This email is already registered. Please use a different email or try logging in.'
          },
          data: null
        };
      }
      
      return response;
    } catch (error: any) {
      console.error('[EMAIL_CONFIRM] === SIGNUP EXCEPTION ===');
      console.error('[EMAIL_CONFIRM] Exception caught:', error);
      console.error('[EMAIL_CONFIRM] Error stack:', error.stack);
      return {
        error,
        data: null
      };
    }
  },

  async signIn(email: string, password: string) {
    const response = await supabase.auth.signInWithPassword({
      email,
      password
    });
    return response;
  },

  async signInWithGoogle(referralCode?: string) {
    const redirectUrl = getAuthCallbackUrl(referralCode);
    const response = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: redirectUrl,
        queryParams: {
          app_origin: window.location.origin,
          signup_method: 'google' // Add this to distinguish from email signup
        }
      }
    });
    return response;
  },

  async signOut() {
    await supabase.auth.signOut();
  },

  async resendConfirmationEmail(email: string) {
    try {
      const authCallbackUrl = getAuthCallbackUrl();
      
      const resendOptions = {
        type: 'signup' as const,
        email: email,
        options: {
          emailRedirectTo: authCallbackUrl
        }
      };
      
      const { error } = await supabase.auth.resend(resendOptions);
      
      if (error) {
        console.error('[EMAIL_CONFIRM] Resend error:', error);
        console.error('[EMAIL_CONFIRM] Error details:', {
          message: error.message,
          status: error.status,
          code: error.code
        });
        
        // Check for rate limiting
        if (error.status === 429 || error.code === 'over_email_send_rate_limit') {
          return {
            error: {
              message: 'Too many requests. Please wait a few minutes before trying again.'
            },
            data: null
          };
        }
        
        return { error, data: null };
      }
      
      return { error: null, data: {} };
    } catch (error: any) {
      console.error('[EMAIL_CONFIRM] Exception resending email:', error);
      return { error, data: null };
    }
  },

  async checkPhoneVerification(userId: string): Promise<boolean> {
    // Phone verification is optional - can be implemented later
    // For now, return false to skip phone verification
    return false;
  }
};