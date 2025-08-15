#!/bin/bash

# Setup script for new projects based on app_template
# Usage: ./scripts/setup-new-project.sh <project-name>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if project name is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide a project name${NC}"
    echo "Usage: ./scripts/setup-new-project.sh <project-name>"
    exit 1
fi

PROJECT_NAME=$1
PROJECT_DIR="../../$PROJECT_NAME"

echo -e "${BLUE}Setting up new project: $PROJECT_NAME${NC}"

# Check if project directory already exists
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Directory $PROJECT_DIR already exists${NC}"
    exit 1
fi

# Create project directory
echo -e "${GREEN}Creating project directory...${NC}"
mkdir -p "$PROJECT_DIR"

# Copy template files
echo -e "${GREEN}Copying template files...${NC}"
cp -r . "$PROJECT_DIR"

# Remove this setup script from the new project
rm "$PROJECT_DIR/scripts/setup-new-project.sh"

# Navigate to project directory
cd "$PROJECT_DIR"

# Update CLAUDE.md with project name
echo -e "${GREEN}Updating CLAUDE.md with project name...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" CLAUDE.md
else
    # Linux
    sed -i "s/\[PROJECT_NAME\]/$PROJECT_NAME/g" CLAUDE.md
fi

# Create .env file
echo -e "${GREEN}Creating .env file...${NC}"
cat > .env << EOF
# Supabase Configuration
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-key

# Optional: Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id

# API Configuration
VITE_API_URL=http://localhost:3000/api

# Environment
NODE_ENV=development
EOF

# Create .env.example
cp .env .env.example

# Create initial App.tsx if it doesn't exist
if [ ! -f "src/App.tsx" ]; then
    echo -e "${GREEN}Creating App.tsx...${NC}"
    cat > src/App.tsx << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LandingPage from './components/landing/LandingPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            {/* Add more routes here */}
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
EOF
fi

# Create main.tsx if it doesn't exist
if [ ! -f "src/main.tsx" ]; then
    echo -e "${GREEN}Creating main.tsx...${NC}"
    cat > src/main.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import './utils/consoleCapture';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF
fi

# Create index.html if it doesn't exist
if [ ! -f "index.html" ]; then
    echo -e "${GREEN}Creating index.html...${NC}"
    cat > index.html << EOF
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>$PROJECT_NAME</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
fi

# Create index.css if it doesn't exist
if [ ! -f "src/index.css" ]; then
    echo -e "${GREEN}Creating index.css...${NC}"
    cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

@media (prefers-color-scheme: light) {
  :root {
    color: #213547;
    background-color: #ffffff;
  }
}
EOF
fi

# Make scripts executable
chmod +x get_prefixed_logs.sh
chmod +x debug_helpers/*.py 2>/dev/null || true

# Initialize git repository
echo -e "${GREEN}Initializing git repository...${NC}"
git init

# Create .gitignore
echo -e "${GREEN}Creating .gitignore...${NC}"
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
dist/
build/

# Misc
.DS_Store
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*
consolidated_logs/*.log

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
EOF

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
npm install

# Success message
echo -e "${GREEN}✓ Project $PROJECT_NAME created successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. cd $PROJECT_DIR"
echo "2. Update .env with your Supabase credentials"
echo "3. npm run dev to start development server"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  npm run dev         - Start development server"
echo "  npm run build       - Build for production"
echo "  npm run lint        - Run linting"
echo "  npm run typecheck   - Run type checking"
echo ""
echo -e "${BLUE}Logging commands:${NC}"
echo "  cat consolidated_logs/recent.log              - View recent logs"
echo "  ./get_prefixed_logs.sh '[ComponentName]'      - Filter logs by prefix"
echo "  python debug_helpers/find_log_prints.py       - Find all debug logs"
echo ""