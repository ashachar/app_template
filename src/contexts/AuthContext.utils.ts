// Utility functions for redirect URL handling

export const initializeRedirectUrl = (): string | null => {
  // Initialize from localStorage if available
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('auth_redirect_url');
    if (stored) return stored;
    
    // Check URL params for redirect_to
    const params = new URLSearchParams(window.location.search);
    const redirectTo = params.get('redirect_to');
    if (redirectTo) {
      // Preserve all query parameters from the redirect URL
      const redirectUrl = new URL(redirectTo, window.location.origin);
      params.forEach((value, key) => {
        if (key !== 'redirect_to') {
          redirectUrl.searchParams.append(key, value);
        }
      });
      const fullRedirectUrl = redirectUrl.pathname + redirectUrl.search;
      localStorage.setItem('auth_redirect_url', fullRedirectUrl);
      return fullRedirectUrl;
    }
  }
  return null;
};

export const persistRedirectUrl = (url: string | null) => {
  if (typeof window !== 'undefined') {
    if (url) {
      localStorage.setItem('auth_redirect_url', url);
    } else {
      localStorage.removeItem('auth_redirect_url');
    }
  }
};

export const getAuthCallbackUrl = (referralCode?: string): string => {
  // Always redirect to auth-callback to ensure proper session handling
  // In development, use the current origin. In production, use a consistent URL.
  const authCallbackUrl = import.meta.env.DEV 
    ? `${window.location.origin}/auth-callback`
    : `${import.meta.env.VITE_APP_URL || window.location.origin}/auth-callback`;
  
  // If referral code is provided, include it in the callback URL
  return referralCode 
    ? `${authCallbackUrl}?referral_code=${encodeURIComponent(referralCode)}`
    : authCallbackUrl;
};

export const shouldRedirectToAuthCallback = (): boolean => {
  if (typeof window !== 'undefined' && window.location.hash) {
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    const accessToken = hashParams.get('access_token');
    
    // If we have auth tokens in the hash and we're not on auth-callback, redirect there
    return !!(accessToken && window.location.pathname !== '/auth-callback');
  }
  return false;
};