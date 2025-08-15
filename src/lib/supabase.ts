import { createClient } from '@supabase/supabase-js';

// Get environment variables from Vite
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Validate required environment variables
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('[supabase] Missing required Supabase credentials!');
  console.error('[supabase] Please check your .env file contains:');
  console.error('[supabase] - VITE_SUPABASE_URL');
  console.error('[supabase] - VITE_SUPABASE_ANON_KEY');
  throw new Error('Missing required Supabase environment variables');
}

// Supabase client created with configured URL
export const supabase = createClient(
  supabaseUrl, 
  supabaseAnonKey,
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      // FOR DEVELOPMENT ONLY: This will log email links to console instead of sending emails
      debug: false,
      detectSessionInUrl: true,
      flowType: 'pkce'
    },
    global: {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
      }
    },
    db: {
      schema: 'public'
    }
  }
);

// Add auth state change listener with comprehensive logging
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN' && session) {
    // Set the flag in localStorage
    localStorage.setItem('auth_session_ready', 'true');
    // Dispatch custom event
    window.dispatchEvent(new Event('auth-session-ready'));
  } else if (event === 'SIGNED_OUT') {
    // Remove the flag on sign out
    localStorage.removeItem('auth_session_ready');
  }
});

// Add email confirmation debugging
// Intercept auth operations for logging
const originalAuth = supabase.auth;
const originalSignUp = originalAuth.signUp;

supabase.auth.signUp = async function(credentials) {
      const startTime = performance.now();
  
  try {
        const result = await originalSignUp.apply(originalAuth, arguments);
    
    const endTime = performance.now();
                    if (result?.error) {
          }
    
    if (result?.data?.user) {
          }
    
    return result;
  } catch (error) {
    const endTime = performance.now();
    console.error('[EMAIL_CONFIRM] === AUTH.SIGNUP EXCEPTION ===');
    console.error('[EMAIL_CONFIRM] Exception after:', endTime - startTime, 'ms');
    console.error('[EMAIL_CONFIRM] Exception type:', error?.constructor?.name);
    console.error('[EMAIL_CONFIRM] Exception message:', error?.message);
    console.error('[EMAIL_CONFIRM] Exception:', error);
    throw error;
  }
};

// Add debugging for requests
if (typeof window !== 'undefined') {
  // Only add debugging in browser environment
  const originalFrom = supabase.from;
  supabase.from = function(table: string) {
    const query = originalFrom.call(this, table);
    
    // Override select to add debugging
    const originalSelect = query.select;
    query.select = function(...args) {
      const result = originalSelect.apply(this, args);
      
      // Track if this is a companies query with ilike
      let isCompanyIlikeQuery = false;
      let queryDetails = { table, args: args[0] };
      
      // Override ilike to detect company queries
      const originalIlike = result.ilike;
      if (originalIlike) {
        result.ilike = function(column, value) {
          if (table === 'companies' && column === 'company_name') {
            isCompanyIlikeQuery = true;
                      }
          return originalIlike.apply(this, arguments);
        };
      }
      
      // Override the promise to log results
      const originalThen = result.then;
      result.then = function(onFulfilled, onRejected) {
        return originalThen.call(this, (value) => {
          if (isCompanyIlikeQuery && value?.error?.code === '406') {
            console.error('[SUPABASE_406_TRACE] 406 Error caught:', {
              table,
              error: value.error,
              errorCode: value.error.code,
              errorMessage: value.error.message,
              errorHint: value.error.hint,
              timestamp: new Date().toISOString()
            });
          }
          return onFulfilled ? onFulfilled(value) : value;
        }, (error) => {
          if (table === 'companies') {
            console.error('[SUPABASE_406_TRACE] Companies query error:', {
              table,
              error,
              errorType: error?.constructor?.name,
              errorMessage: error?.message,
              timestamp: new Date().toISOString()
            });
          }
          console.error('[supabase] Query error for', table, ':', error);
          return onRejected ? onRejected(error) : Promise.reject(error);
        });
      };
      
      return result;
    };
    
    return query;
  };
}

// Only create admin client in server environment (not in browser)
// The admin client should only be used in server-side code (API routes)
export const supabaseAdmin = null;

// Note: If you need an admin client, create it in your server-side API files
// This prevents the "Multiple GoTrueClient instances" warning in the browser
