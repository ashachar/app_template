# 🚀 Enhanced Debug Workflow with Custom Prefixes

## Overview

The enhanced debugging workflow uses **custom debug prefixes** to create a systematic, traceable debugging process. This allows you to:

1. Track issues across multiple modules (UI → API → DB → Lambda)
2. Filter logs by specific debug sessions
3. Automatically clean up debug logs when done
4. Visualize the flow of data through your system

## Step-by-Step Workflow

### 1. Start a Debug Session

```bash
# Create a new debug session with descriptive name
python debug_helpers/debug_session.py "auth-401-issue"

# Output:
# 🔍 DEBUG SESSION INITIALIZED
# Session ID: AUTH123
# Issue Type: auth-401-issue
```

### 2. Add Prefixed Debug Logs

Use the session ID in your debug logs across all modules:

#### Frontend (JavaScript/React)
```javascript
// LOG PRINT START
console.log('[DEBUG-AUTH123-UI-FLOW] Login form submitted');
console.log('[DEBUG-AUTH123-UI-DATA] Form data:', { email, hasPassword: !!password });
console.log('[DEBUG-AUTH123-UI-VALIDATE] Validation passed:', validationResult);
// LOG PRINT END

// After API call
// LOG PRINT START
console.log('[DEBUG-AUTH123-UI-ERROR] API returned 401:', error.response);
console.log('[DEBUG-AUTH123-UI-STATE] Auth state after error:', authContext.state);
// LOG PRINT END
```

#### API (Express/Node.js)
```javascript
// LOG PRINT START
console.log('[DEBUG-AUTH123-API-FLOW] POST /api/auth/login');
console.log('[DEBUG-AUTH123-API-DATA] Request body:', req.body);
console.log('[DEBUG-AUTH123-API-TIMING] Auth check started:', new Date().toISOString());
// LOG PRINT END

// In auth middleware
// LOG PRINT START
console.log('[DEBUG-AUTH123-API-AUTH] Token validation failed:', validateResult);
console.log('[DEBUG-AUTH123-API-ERROR] Returning 401 Unauthorized');
// LOG PRINT END
```

#### Database Queries
```javascript
// LOG PRINT START
console.log('[DEBUG-AUTH123-DB-FLOW] Querying user by email');
console.log('[DEBUG-AUTH123-DB-DATA] Query params:', { email });
console.log('[DEBUG-AUTH123-DB-TIMING] Query execution time:', endTime - startTime);
// LOG PRINT END
```

#### Lambda Functions (Python)
```python
# LOG PRINT START
print(f'[DEBUG-AUTH123-LAMBDA-FLOW] Processing auth validation')
print(f'[DEBUG-AUTH123-LAMBDA-DATA] Event payload: {json.dumps(event)}')
print(f'[DEBUG-AUTH123-LAMBDA-ERROR] Validation failed: {str(e)}')
# LOG PRINT END
```

### 3. Run Your Test/Reproduction

Execute your test with the debug logs in place:

```bash
# Run your test
node debug_test_auth.js

# Or run servers with logs
./restart-servers.sh
```

### 4. Analyze Logs by Session

```bash
# Analyze only logs from this debug session
python debug_helpers/analyze_logs.py --session AUTH123

# Output shows:
# 📌 Debug Session: AUTH123
# 
# 🔄 DEBUG FLOW ANALYSIS
# UI Module (5 entries):
#   [FLOW] Login form submitted
#   [DATA] Form data: { email: 'test@example.com', hasPassword: true }
#   [ERROR] API returned 401: { status: 401, message: 'Invalid credentials' }
# 
# API Module (4 entries):
#   [FLOW] POST /api/auth/login
#   [AUTH] Token validation failed: { reason: 'Token expired' }
#   [ERROR] Returning 401 Unauthorized
```

### 5. Clean Up Session Logs

```bash
# Remove all debug logs for this session
python debug_helpers/find_log_prints.py --clean --prefix DEBUG-AUTH123

# Output:
# Cleaning LOG PRINT blocks with prefix 'DEBUG-AUTH123' from the codebase...
# ✓ Cleaned 4 LOG PRINT block(s) with prefix 'DEBUG-AUTH123' from src/pages/LoginPage.tsx
# ✓ Cleaned 3 LOG PRINT block(s) with prefix 'DEBUG-AUTH123' from api/auth.js
# Total LOG PRINT blocks removed: 7
```

## Prefix Format Reference

```
[DEBUG-{SESSION}-{MODULE}-{CATEGORY}]
```

### Modules
- `UI` - Frontend/React components
- `API` - Express API endpoints
- `DB` - Database queries
- `LAMBDA` - Lambda functions
- `AUTH` - Authentication specific
- `MISC` - Other/general

### Categories
- `FLOW` - Execution flow tracking
- `DATA` - Data/payload logging
- `STATE` - State changes
- `ERROR` - Error conditions
- `TIMING` - Performance metrics
- `VALIDATE` - Validation results

## Real Example: Debugging Requisition Display Issue

```bash
# 1. Start session
python debug_helpers/debug_session.py "requisition-null"
# Session ID: REQN456

# 2. Add debug logs in React component
// LOG PRINT START
console.log('[DEBUG-REQN456-UI-FLOW] Rendering requisition list');
console.log('[DEBUG-REQN456-UI-STATE] Requisitions from state:', requisitions);
console.log('[DEBUG-REQN456-UI-DATA] Department lookup:', departmentId, lookupService.getDepartment(departmentId));
// LOG PRINT END

# 3. Add logs in API
// LOG PRINT START
console.log('[DEBUG-REQN456-API-FLOW] GET /api/requisitions');
console.log('[DEBUG-REQN456-API-DB] Query result:', rows.length, 'requisitions');
console.log('[DEBUG-REQN456-API-DATA] First requisition:', rows[0]);
// LOG PRINT END

# 4. Run and analyze
python debug_helpers/analyze_logs.py --session REQN456 --show-flow

# 5. Clean up
python debug_helpers/find_log_prints.py --clean --prefix DEBUG-REQN456
```

## Benefits Over Traditional Logging

1. **Focused Analysis**: Only see logs relevant to current issue
2. **Cross-Module Tracing**: Follow data flow across entire stack
3. **Clean Removal**: Remove all debug logs with one command
4. **No Noise**: Production logs remain unaffected
5. **Systematic Approach**: Consistent format across all modules
6. **Historical Record**: Session files track what was debugged

## Tips

1. Use descriptive session names: `"auth-401"`, `"null-department"`, `"slow-query"`
2. Add logs liberally during debugging - they're easy to remove
3. Use appropriate categories for better flow visualization
4. Check `.current_session` file to see active session
5. Session metadata stored in `debug_helpers/sessions/`

## Integration with VS Code

Add this snippet for quick debug log insertion:

```json
{
  "Debug Log with Session": {
    "prefix": "dlog",
    "body": [
      "// LOG PRINT START",
      "console.log('[DEBUG-${1:SESSION}-${2|UI,API,DB,LAMBDA|}-${3|FLOW,DATA,STATE,ERROR,TIMING,VALIDATE|}] ${4:message}');",
      "// LOG PRINT END"
    ]
  }
}
```

This enhanced workflow makes debugging more systematic, traceable, and clean!