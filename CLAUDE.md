# CLAUDE.md

> **Purpose**: Guidance for Claude Code (claude.ai/code) when working with this repository. Read **once at the start of every session**.

---

## 🔴 CRITICAL: NEVER GUESS - ALWAYS ASK OR RESEARCH!

**⚠️ MANDATORY**: When you encounter ANY uncertainty about system behavior:

1. **STOP IMMEDIATELY** - Don't try multiple approaches blindly
2. **ASK THE USER** - "I need to understand [specific thing]. Can you help me research this?"
3. **USE AVAILABLE TOOLS** - Web search, documentation, or specialized agents
4. **NEVER WASTE TIME GUESSING** - One correct question saves hours of wrong attempts

**Examples**:
- ❌ WRONG: Trying 5 different workarounds for an error without understanding the root cause
- ✅ CORRECT: "I can't find the function definition. Can you help me examine this function?"
- ❌ WRONG: Guessing how the framework handles parameters
- ✅ CORRECT: "How does Supabase handle empty arrays in RPC calls? Can you research this for me?"

### 🔴 ASK CLARIFICATION QUESTIONS BEFORE STARTING WORK

**⚠️ MANDATORY**: Before implementing ANY task or command:

1. **REVIEW THE REQUEST** - Identify any ambiguities or unclear requirements
2. **ASK CLARIFICATION QUESTIONS** - If anything is not 100% clear, ask the user before proceeding
3. **CONFIRM UNDERSTANDING** - Summarize your understanding and get confirmation
4. **THEN PROCEED** - Only start implementation after all questions are answered

**Example**:
```
User: "Fix the filter"
AI: "Before I begin, I need to clarify:
1. What specific issue are you experiencing with the filter?
2. Is this in a specific page or component?
3. What behavior are you expecting vs what's happening?
Please provide these details so I can fix the right issue."
```

---

## Project Overview

[PROJECT_NAME] is a web application built with React, TypeScript, Vite, and Supabase. This template provides a solid foundation with authentication, logging, and common UI components.

## Architecture

### Directory Structure
```
app_template/
├── src/
│   ├── api/           # API client functions
│   ├── components/    # React components
│   │   ├── auth/     # Authentication components
│   │   ├── common/   # Reusable UI components
│   │   ├── landing/  # Landing page components
│   │   └── layout/   # Layout components
│   ├── contexts/     # React contexts
│   ├── hooks/        # Custom React hooks
│   ├── lib/          # External library configurations
│   ├── locales/      # Internationalization files
│   ├── pages/        # Page components
│   ├── utils/        # Utility functions
│   └── main.tsx      # Application entry point
├── scripts/          # Build and utility scripts
├── debug_helpers/    # Debug utilities and scripts
└── consolidated_logs/ # Application logs
```

### Tech Stack
- **Frontend**: React 19 + TypeScript + Vite
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth with JWT
- **Styling**: Tailwind CSS
- **State Management**: React Context API

## Important Notes for Claude Code

### Database Configuration
The application uses Supabase for all database operations. Configure the connection in `.env`:
```env
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-key
```

### UI/UX Guidelines
**NO EMOJIS in the application UI** - Use only icon libraries like FontAwesome. This ensures consistent rendering across all platforms.

**Component Class Names** - Every React component should have a CSS class name matching its component name (in kebab-case) on its root element:
- `AuthPage.tsx` → class `auth-page`
- `LandingPage.tsx` → class `landing-page`
- `UserProfile.tsx` → class `user-profile`

### Code Quality Guidelines

#### 🔴 CRITICAL: File Size Limit - 200 Lines Maximum

**⚠️ MANDATORY COMPLIANCE**: Every code file MUST be kept under 200 lines. This is NON-NEGOTIABLE.

**FILE SIZE RULES**:
1. **HARD LIMIT**: No code file should exceed 200 lines
2. **CHECK BEFORE ADDING**: Before adding any new feature, check the current file size
3. **BREAK UP LARGE FILES**: If a new feature would push a file over 200 lines, refactor first
4. **RISK-FREE REFACTORING**: When breaking up files:
   - Extract logical components/functions into separate files
   - Group related functionality together
   - Maintain clear imports/exports
   - Preserve all existing functionality
   - Test thoroughly after refactoring

**HOW TO BREAK UP LARGE FILES**:

1. **Identify Logical Boundaries**:
   - Separate data models from business logic
   - Extract utility functions to helper files
   - Move constants and configurations to dedicated files
   - Split large components into smaller sub-components

2. **Common Refactoring Patterns**:
   ```javascript
   // Before: Everything in one file
   // After: Split into multiple files
   // - component.tsx (main component, <100 lines)
   // - component.hooks.ts (custom hooks)
   // - component.utils.ts (utility functions)
   // - component.types.ts (TypeScript interfaces)
   // - component.constants.ts (constants)
   ```

**🚨 ENFORCEMENT**: Check file size with `wc -l filename` before and after changes

#### 🔴 CRITICAL: NO EMOJIS IN CODE FILES

**⚠️ MANDATORY**: NEVER use emojis in any code files (*.js, *.ts, *.tsx, *.py, *.sql, etc.)

1. **NO** emojis in comments, strings, or variable names
2. **NO** emojis in console.log statements or debug messages
3. **ONLY** use standard ASCII characters in code
4. Emojis make code less portable and can cause encoding issues

**🌍 EXCEPTION: Flag emojis ARE allowed in language configuration files**
- Flag emojis (🇺🇸, 🇮🇱, 🇫🇷, etc.) are permitted ONLY in language/locale configuration
- Specifically allowed in: language constants and language toggle components
- This exception exists because flag emojis are universally supported for country representation

**❌ WRONG**: 
```javascript
console.log("✅ Success!");
console.log("🔴 Error occurred");
```

**✅ CORRECT**:
```javascript
console.log("Success!");
console.log("Error occurred");
```

## Consolidated Logging System

The application includes a consolidated logging system that captures both frontend and backend logs.

### How It Works
1. **Frontend**: Browser console methods are intercepted and sent to the backend
2. **Backend**: All console outputs are captured automatically
3. **Storage**: Logs are stored in `consolidated_logs/recent.log`

### Viewing Logs
```bash
# Direct file access (preferred for Claude Code)
cat consolidated_logs/recent.log

# Or use the helper script
./get_prefixed_logs.sh '[PREFIX]'
```

### Log Format
```
[TIMESTAMP] [SOURCE] [LEVEL] MESSAGE
```
- **SOURCE**: CLIENT (frontend) or SERVER (backend)
- **LEVEL**: INFO, WARN, ERROR

### Debug Logging Best Practices

#### 🔴 CRITICAL: NEVER REMOVE LOG PRINTS

**⚠️ MANDATORY**: NEVER remove any log print statements unless the user explicitly asks you to do so. This is NON-NEGOTIABLE.

**Why this is critical:**
- Log statements are essential for debugging and monitoring
- Removing logs can hide important system behavior
- Users may rely on specific logs for their workflows
- Logs provide audit trails and help track issues

**Rule**: If you see any log statement (console.log, print, logger.*, etc.), leave it untouched unless specifically instructed to remove it.

#### 🔴 MANDATORY: @LOGMARK Marker for Easy Removal

**CRITICAL: Every debug log line MUST end with `// @LOGMARK` comment.** This allows instant removal of all debug logs using the cleanup script:

```javascript
// ❌ WRONG - Missing @LOGMARK on object lines
console.log('[DEBUG-BUG123] Data:', { // @LOGMARK
  userId: data.userId,
  items: data.items,
  timestamp: data.timestamp
}); // @LOGMARK

// ✅ CORRECT - @LOGMARK on EVERY line including object content
console.log('[DEBUG-BUG123] Data:', { // @LOGMARK
  userId: data.userId, // @LOGMARK
  items: data.items, // @LOGMARK
  timestamp: data.timestamp // @LOGMARK
}); // @LOGMARK

// ✅ CORRECT Alternative - Split into multiple console.logs
console.log('[DEBUG-BUG123] Full state: {'); // @LOGMARK
console.log(`  userId: ${data.userId},`); // @LOGMARK
console.log(`  items: [${data.items.join(', ')}],`); // @LOGMARK
console.log(`  timestamp: ${data.timestamp}`); // @LOGMARK
console.log('}'); // @LOGMARK
```

**Python debug logs:**
```python
print(f"[DEBUG-BUG123] Processing request")  # @LOGMARK
print(f"  User ID: {user_id}")  # @LOGMARK
print(f"  Status: {status}")  # @LOGMARK
```

#### Prefix Pattern for Context

**ALWAYS use prefixed console.log statements** with `[PREFIX]` pattern where PREFIX describes the component or function.

**CRITICAL: Use a SINGLE debug prefix for each debugging session.** Never split debugging into multiple prefixes. This ensures all related logs can be retrieved with one command.

```javascript
// ✅ CORRECT - Single prefix for entire debugging session
console.log('[DEBUG-BUG456] Loading project:', projectId); // @LOGMARK
console.log('[DEBUG-BUG456] Canvas dimensions:', width, height); // @LOGMARK
console.log('[DEBUG-BUG456] Saving objects'); // @LOGMARK

// ❌ WRONG - Multiple prefixes for same debugging session
console.log('[Editor] Loading project'); // @LOGMARK
console.log('[Canvas] Setting dimensions'); // @LOGMARK
```

**Common Prefixes (only when NOT debugging):**
- `[ComponentName]` - For React components
- `[API]` - For API calls
- `[Auth]` - For authentication
- `[DB]` - For database operations

### Removing Debug Logs

```bash
# Find all debug logs
python debug_helpers/find_log_prints.py

# Remove all debug logs with @LOGMARK
python debug_helpers/find_log_prints.py --clean
```

## Essential Commands

### Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Run type checking
npm run typecheck
```

### Logging
```bash
# View recent logs
cat consolidated_logs/recent.log

# Get logs with specific prefix
./get_prefixed_logs.sh '[Auth]'

# Find all debug logs
python debug_helpers/find_log_prints.py
```

## Authentication Flow

The template includes a complete authentication system:

1. **Email/Password Auth**: Using Supabase Auth
2. **Google OAuth**: Optional integration
3. **Protected Routes**: Components in `src/components/auth/`
4. **Auth Context**: Available throughout the app via `AuthContext`

### Setting Up Authentication

1. Configure Supabase project
2. Add environment variables
3. Use `AuthContext` in components:

```typescript
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, signIn, signOut } = useAuth();
  // ...
}
```

## Common Development Tasks

### Add a new page
1. Create component in `src/pages/`
2. Add route in `App.tsx`
3. Update navigation if needed

### Add API endpoint
1. Create function in `src/api/`
2. Use Supabase client from `src/lib/supabase.ts`

### Add new component
1. Create in appropriate `src/components/` subdirectory
2. Follow naming conventions
3. Keep under 200 lines

### Debug an issue
1. Add prefixed console.log with @LOGMARK
2. Check `consolidated_logs/recent.log`
3. Use `./get_prefixed_logs.sh` to filter
4. Remove debug logs when done

## Environment Variables

Required in `.env`:
```env
# Supabase
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-key

# Optional: Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## Database Schema

The template expects these base tables in Supabase:
- `profiles`: User profiles linked to auth.users
- `user_preferences`: User settings and preferences

Additional tables can be added as needed for your application.

## Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test:watch

# Run e2e tests
npm run test:e2e
```

## Deployment

The application can be deployed to:
- Vercel (recommended)
- Netlify
- Any static hosting service

Build command: `npm run build`
Output directory: `dist`

## Troubleshooting

### Logs not appearing
- Ensure the app is running
- Check browser console for errors
- Verify `consoleCapture.ts` is imported in `main.tsx`

### Authentication issues
- Verify Supabase credentials in `.env`
- Check Supabase dashboard for auth settings
- Ensure redirect URLs are configured

### Build errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run typecheck`
- Verify all imports are correct

## Best Practices

1. **Component Organization**: Keep components focused and under 200 lines
2. **State Management**: Use Context API for global state
3. **Error Handling**: Always handle API errors gracefully
4. **Logging**: Use prefixed console.log with @LOGMARK
5. **Type Safety**: Leverage TypeScript for all components
6. **Code Splitting**: Use dynamic imports for large components
7. **Performance**: Use React.memo and useMemo where appropriate

## Component CSS Class Naming Convention

### 🔴 CRITICAL: Component Identification Classes

**⚠️ MANDATORY**: All React components MUST include component-specific CSS classes for debugging and testing.

### Required Naming Pattern

**ALWAYS add component identification classes to main container elements:**

```tsx
// ✅ CORRECT - Component name + purpose
<div className="jobcards-container flex-1 overflow-y-auto min-h-0">
<div className="candidatecard-item bg-white border rounded-lg">
<div className="searchfilters-wrapper flex flex-col">

// ❌ WRONG - Generic classes only
<div className="flex-1 overflow-y-auto min-h-0">
<div className="bg-white border rounded-lg">
<div className="flex flex-col">
```

### Class Name Format

**Component Name → CSS Class:**
- Convert PascalCase to kebab-case
- Add descriptive suffix for purpose
- Always combine with existing utility classes

**Examples:**
- `JobCards.tsx` → `jobcards-container`
- `CandidateCard.tsx` → `candidatecard-item`
- `SearchFilters.tsx` → `searchfilters-wrapper`

### Suffix Conventions

| Suffix | Purpose | Example |
|--------|---------|---------|
| `-wrapper` | Outermost container | `jobcards-wrapper` |
| `-container` | Main content area | `jobcards-container` |
| `-header` | Top section | `jobcards-header` |
| `-footer` | Bottom section | `jobcards-footer` |
| `-item` | Individual list items | `candidatecard-item` |
| `-modal` | Modal/dialog containers | `filterdropdown-modal` |
| `-sidebar` | Side panel containers | `navigation-sidebar` |

### Implementation Requirements

1. **New Components**: MUST include component-specific classes from creation
2. **Existing Components**: Add classes during any modification
3. **Multiple Containers**: Use descriptive suffixes for each section
4. **Always Combine**: Component classes + utility classes together

## Testing & Debugging

### JavaScript Analysis Scripts

When creating diagnostic scripts for browser console:
- **NEVER include React references** - React is not available in global scope
- **Use vanilla JavaScript only** - simplest syntax that achieves the goal
- **Avoid framework-specific code** - stick to DOM APIs and basic JavaScript
- **Test for existence** before using any global objects
- **Always use IIFE pattern** - `(() => { /* code */ })()`

### Restarting the Application

**If your application supports hot restart:**
```bash
# Use the restart command if available
npm run restart

# This command should:
# - Start the app in the background
# - Return control immediately (non-blocking)
# - Allow you to continue with other tasks
```

## Getting Help

- Check existing components for patterns
- Review debug logs for issues
- Follow the established conventions
- Keep code modular and testable

## Important Reminders

### 🔴 Do What's Asked - Nothing More, Nothing Less

1. **NEVER create files** unless they're absolutely necessary for achieving your goal
2. **ALWAYS prefer editing** an existing file to creating a new one
3. **NEVER proactively create** documentation files (*.md) or README files
4. **Only create documentation** if explicitly requested by the User

### 🔴 Backward Compatibility

1. **NEVER** add backward compatibility features unless explicitly requested
2. **NO** redirect routes for old URLs
3. **NO** support for deprecated APIs or patterns
4. **ALWAYS** use the current, canonical approach
5. Breaking changes are acceptable - focus on clean, modern code

### 🔴 Version Control

- The agent must **NEVER run `git commit` or `git push`**
- When asked, show `git status`, `git diff`, and propose clear commit/PR messages
- Let the user handle all version control operations