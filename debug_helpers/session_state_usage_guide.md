# Debug Session State Management Usage Guide

## Overview

The debug session state management system provides persistent storage for debugging sessions, allowing you to:
- Save and restore debugging progress
- Cache test data and API responses
- Track failed attempts and findings
- Resume interrupted debugging sessions

## Quick Start

### 1. Initialize Session State

```python
from debug_helpers.debug_session import DebugSession
from debug_helpers.debug_session_state import DebugSessionState

# Create debug session (for prefix management)
debug_session = DebugSession("issue-type")
session_id = debug_session.session_id

# Create state manager
state = DebugSessionState(session_id)
```

### 2. Basic Usage in Debug Scripts

```python
# Set current debugging step
state.set_current_step("login", "Testing user authentication")

# Save reusable test data
state.save_test_data("job_id", job_id, category="ids")
state.save_test_data("auth_token", token, category="auth")

# Retrieve saved data (increments usage count)
saved_job_id = state.get_test_data("job_id", "ids")

# Create checkpoint after successful step
state.create_checkpoint("after_login", "User authenticated successfully")
state.complete_current_step()

# Cache API responses
state.cache_api_response("GET", "/api/jobs", response_data, 200)

# Retrieve cached response (increments hit count)
cached = state.get_cached_response("GET", "/api/jobs")
if cached:
    data = cached["response"]
```

### 3. Handling Failures

```python
# Record failed attempts
try:
    # Some operation that might fail
    await page.click('button[type="submit"]')
except Exception as e:
    state.record_failed_attempt(
        "Submit button click failed",
        str(e),
        context={"selector": 'button[type="submit"]', "url": page.url()},
        notes="Button might be disabled or not visible"
    )

# Document findings
state.add_finding(
    "root_cause",
    "Submit button disabled due to missing validation",
    evidence="Button has disabled attribute when required fields are empty",
    fix_suggestion="Add client-side validation for required fields",
    related_files=["src/components/JobForm.tsx"]
)
```

### 4. Resume Interrupted Sessions

```python
# List available sessions
from debug_helpers.debug_session_state import list_sessions
sessions = list_sessions()
for session in sessions:
    print(f"{session['session_id']}: {session['checkpoints']} checkpoints")

# Load existing session
from debug_helpers.debug_session_state import load_session
state = load_session("AUTH-123")

# Get session summary
state.print_summary()

# Get suggestions for next steps
suggestions = state.suggest_next_steps()

# Restore from checkpoint
state.restore_checkpoint("after_login")
```

### 5. Integration with Playwright Tests

```javascript
// In your Playwright test with Python
async def debug_job_creation():
    # Initialize state management
    debug_session = DebugSession("job-creation")
    state = DebugSessionState(debug_session.session_id)
    
    # Start browser
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Step 1: Login
        state.set_current_step("login", "User authentication")
        
        await page.goto("http://localhost:3000/login")
        await page.fill('input[type="email"]', email)
        await page.fill('input[type="password"]', password)
        
        # LOG PRINT START
        await page.evaluate(f'''console.log("{debug_session.get_prefix('UI', 'FLOW')} Submitting login form")''')
        # LOG PRINT END
        
        await page.click('button[type="submit"]')
        
        # Save auth data for reuse
        auth_token = await page.evaluate("localStorage.getItem('authToken')")
        state.save_test_data("auth_token", auth_token, "auth")
        
        # Create checkpoint
        state.create_checkpoint("login_complete", "User authenticated")
        state.complete_current_step()
        
        # Step 2: Create job (can resume from here if needed)
        state.set_current_step("create_job", "Job creation flow")
        
        # ... rest of test
        
    except Exception as e:
        # Record failure
        state.record_failed_attempt(
            "Test failed",
            str(e),
            {"step": state.current_step, "url": page.url()}
        )
        
        # Take screenshot and save as artifact
        screenshot = await page.screenshot()
        state.save_artifact(
            f"failure_{int(time.time())}.png",
            content=screenshot,
            artifact_type="screenshots"
        )
        raise
    
    finally:
        await browser.close()
        debug_session.close_session()
```

## Key Features

### 1. Checkpoints
- Save progress at key milestones
- Include custom data with each checkpoint
- Restore to any previous checkpoint
- Automatically tracks test data snapshot

### 2. Test Data Management
- Organize data by categories (ids, auth, etc.)
- Track usage count for each data item
- Persist across session reloads
- Easy retrieval with automatic usage tracking

### 3. API Response Caching
- Cache successful API responses
- Large responses automatically saved to files
- Track cache hits
- Reduce redundant API calls in tests

### 4. Failed Attempts Tracking
- Document what didn't work
- Include error messages and context
- Learn from previous attempts
- Helps avoid repeating failed approaches

### 5. Findings Documentation
- Types: root_cause, observation, hypothesis, solution
- Include evidence and fix suggestions
- Link to related files
- Query findings by type

### 6. Session Management
- List all debugging sessions
- Clean up old sessions
- Load and resume any session
- Get intelligent next-step suggestions

## Best Practices

1. **Create Checkpoints Frequently**
   - After each successful major step
   - Before attempting risky operations
   - Include descriptive messages

2. **Use Meaningful Categories**
   - "ids" for entity IDs (job_id, user_id)
   - "auth" for tokens and credentials
   - "config" for configuration values
   - Create custom categories as needed

3. **Document Failures Thoroughly**
   - Include full error messages
   - Add relevant context (URLs, selectors, etc.)
   - Write notes about why it might have failed

4. **Cache Expensive Operations**
   - API responses that don't change
   - Database query results
   - File contents or configurations

5. **Clean Up Completed Sessions**
   ```python
   from debug_helpers.debug_session_state import cleanup_old_sessions
   cleaned = cleanup_old_sessions(days=7)  # Remove sessions older than 7 days
   ```

## Command Line Usage

```bash
# List all sessions
python debug_helpers/debug_session_state.py --list

# Resume a specific session
python debug_helpers/debug_session_state.py --resume SESSION_ID

# Clean up old sessions
python -c "from debug_helpers.debug_session_state import cleanup_old_sessions; print(f'Cleaned {cleanup_old_sessions(30)} sessions')"
```

## Integration with Log Analysis

The session state management integrates seamlessly with the log analysis tools:

```bash
# Analyze logs for a specific session
python debug_helpers/analyze_logs.py --session JOB-123

# Clean up logs for a session
python debug_helpers/find_log_prints.py --clean --prefix 'DEBUG-JOB-123'
```

## Example: Complete Debug Flow

```python
# 1. Start debugging session
debug_session = DebugSession("auth-401-error")
state = DebugSessionState(debug_session.session_id)

# 2. Run debug script with state tracking
# ... (your debug code with checkpoints and data saving)

# 3. If interrupted, resume later:
state = load_session("AUTH-401")
state.print_summary()

# Get saved data
auth_token = state.get_test_data("auth_token", "auth")
last_api_response = state.get_cached_response("GET", "/api/user")

# Continue from checkpoint
state.restore_checkpoint("after_login")

# 4. Analyze logs when done
os.system(f"python debug_helpers/analyze_logs.py --session {state.session_id}")

# 5. Clean up
debug_session.close_session()
os.system(debug_session.get_cleanup_command())
```

## Benefits

1. **Never Lose Progress**: Checkpoints ensure you can always resume
2. **Faster Debugging**: Cached data and API responses speed up iterations
3. **Better Documentation**: Failed attempts and findings create a knowledge base
4. **Reduced Frustration**: Skip already-completed steps when resuming
5. **Team Collaboration**: Share session IDs to hand off debugging tasks
6. **Historical Analysis**: Review past debugging sessions to learn patterns