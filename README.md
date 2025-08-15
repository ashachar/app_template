# App Template

A comprehensive boilerplate for building modern web applications with React, TypeScript, Vite, and Supabase. This template includes authentication, logging infrastructure, and common UI components to jumpstart your next project.

## Features

### Core Infrastructure
- **React 19 + TypeScript + Vite** - Modern, fast development experience
- **Supabase Integration** - Complete authentication and database setup
- **Tailwind CSS** - Utility-first CSS framework
- **ESLint + Prettier** - Code quality and formatting

### Authentication System
- Email/password authentication
- Google OAuth integration (optional)
- Protected routes
- Auth context with hooks
- Session management

### Logging & Debugging
- **Consolidated Logging System** - Frontend and backend logs in one place
- **Debug Helpers** - Scripts for finding and removing debug logs
- **Prefixed Logging** - Easy filtering by component/feature
- **@LOGMARK System** - Clean removal of debug statements

### Development Tools
- **Claude Code Integration** - CLAUDE.md with best practices
- **.claude Commands** - Quick access to common tasks
- **Setup Scripts** - Automated project initialization
- **Hot Module Replacement** - Fast development cycle

## Quick Start

### Using the Setup Script (Recommended)

1. Clone this template:
```bash
git clone [template-repo-url] app_template
cd app_template
```

2. Create a new project:
```bash
./scripts/setup-new-project.sh my-awesome-app
```

3. Navigate to your new project:
```bash
cd ../../my-awesome-app
```

4. Configure environment:
```bash
# Edit .env with your Supabase credentials
vim .env
```

5. Start developing:
```bash
npm run dev
```

### Manual Setup

1. Copy the template to your project location:
```bash
cp -r app_template /path/to/your-project
cd /path/to/your-project
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Start the development server:
```bash
npm run dev
```

## Project Structure

```
app_template/
├── src/
│   ├── api/              # API client functions
│   ├── components/       # React components
│   │   ├── auth/        # Authentication components
│   │   ├── common/      # Reusable UI components
│   │   ├── landing/     # Landing page components
│   │   └── layout/      # Layout components
│   ├── contexts/        # React contexts (Auth, etc.)
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # External library configs
│   ├── locales/         # i18n translation files
│   ├── pages/           # Page components
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── scripts/             # Build and utility scripts
├── debug_helpers/       # Debug utilities
├── consolidated_logs/   # Application logs
├── .claude/            # Claude Code commands
├── CLAUDE.md           # Claude Code guidance
└── README.md           # This file
```

## Key Components

### Authentication

The template includes a complete authentication system using Supabase:

```typescript
// Using auth in components
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, signIn, signOut, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Please sign in</div>;
  
  return <div>Welcome {user.email}!</div>;
}
```

### Protected Routes

```typescript
// Protecting routes
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  } 
/>
```

### Logging System

The template includes a sophisticated logging system:

```javascript
// Always use prefixed logs with @LOGMARK
console.log('[ComponentName] Action happened:', data); // @LOGMARK

// View logs
cat consolidated_logs/recent.log

// Filter logs by prefix
./get_prefixed_logs.sh '[Auth]'

// Find all debug logs
python debug_helpers/find_log_prints.py

// Remove all debug logs
python debug_helpers/find_log_prints.py --clean
```

## Available Scripts

### Development
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run typecheck` - Check TypeScript types

### Logging & Debug
- `./get_prefixed_logs.sh '[PREFIX]'` - Get logs with specific prefix
- `python debug_helpers/find_log_prints.py` - Find all debug logs
- `python debug_helpers/find_log_prints.py --clean` - Remove all @LOGMARK logs

## Environment Variables

Create a `.env` file with:

```env
# Supabase (Required)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Google OAuth (Optional)
VITE_GOOGLE_CLIENT_ID=your-google-client-id

# API Configuration
VITE_API_URL=http://localhost:3000/api

# Environment
NODE_ENV=development
```

## Supabase Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)

2. Create required tables:
```sql
-- User profiles
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- User preferences
CREATE TABLE user_preferences (
  user_id UUID REFERENCES auth.users PRIMARY KEY,
  theme TEXT DEFAULT 'light',
  language TEXT DEFAULT 'en',
  notifications BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

3. Enable Row Level Security (RLS) on tables

4. Add your Supabase credentials to `.env`

## Best Practices

### Component Development
- Keep components under 200 lines
- Use TypeScript for all components
- Follow the naming convention for CSS classes
- Create reusable components in `src/components/common/`

### State Management
- Use React Context for global state
- Keep component state local when possible
- Use custom hooks for complex logic

### Logging & Debugging
- Always prefix console.log statements
- Add `// @LOGMARK` to debug logs
- Remove debug logs before committing
- Check `consolidated_logs/recent.log` for issues

### Code Quality
- Run `npm run lint` before committing
- Fix TypeScript errors with `npm run typecheck`
- Follow the established file structure
- Write clean, self-documenting code

## Common Tasks

### Add a New Page

1. Create component in `src/pages/`:
```typescript
// src/pages/About.tsx
export default function About() {
  return (
    <div className="about">
      <h1>About Page</h1>
    </div>
  );
}
```

2. Add route in `App.tsx`:
```typescript
<Route path="/about" element={<About />} />
```

### Add API Endpoint

1. Create function in `src/api/`:
```typescript
// src/api/users.ts
import { supabase } from '@/lib/supabase';

export async function getUsers() {
  const { data, error } = await supabase
    .from('profiles')
    .select('*');
    
  if (error) throw error;
  return data;
}
```

### Add Protected Feature

```typescript
import { useAuth } from '@/contexts/AuthContext';

function ProtectedFeature() {
  const { user } = useAuth();
  
  if (!user) {
    return <div>Please sign in to access this feature</div>;
  }
  
  return <div>Protected content here</div>;
}
```

## Deployment

### Vercel (Recommended)
1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Netlify
1. Push to GitHub
2. Create new site from Git
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add environment variables

### Manual Deployment
```bash
npm run build
# Upload contents of dist/ to your hosting service
```

## Troubleshooting

### Logs Not Appearing
- Ensure `consoleCapture.ts` is imported in `main.tsx`
- Check browser console for errors
- Verify the app is running

### Authentication Issues
- Verify Supabase credentials in `.env`
- Check Supabase dashboard for auth settings
- Ensure redirect URLs are configured in Supabase

### Build Errors
```bash
# Clear and reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check TypeScript errors
npm run typecheck

# Check lint errors
npm run lint
```

## Claude Code Integration

This template is optimized for use with Claude Code. The `CLAUDE.md` file provides:
- Project structure overview
- Coding conventions
- Debug logging guidelines
- Common task instructions

Use `.claude` commands for quick access to common tasks.

## Contributing

When contributing to the template:
1. Follow the established patterns
2. Keep the template generic and reusable
3. Document new features in README
4. Update CLAUDE.md if adding new conventions
5. Test the setup script with new changes

## License

MIT - Use this template for any project!

## Support

For issues or questions:
- Check the troubleshooting section
- Review CLAUDE.md for detailed guidance
- Create an issue in the repository

---

Happy coding! 🚀