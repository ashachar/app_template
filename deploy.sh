#!/bin/bash

# Deployment script for app_template
# This script adds, commits, and pushes all changes to GitHub

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting deployment process...${NC}"
echo "📅 Timestamp: $(date)"

# Function to handle errors
handle_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    exit 1
}

# Check if we're in a git repository
if [ ! -d .git ]; then
    handle_error "Not a git repository. Please initialize git first with: git init"
fi

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
if [ -z "$BRANCH" ]; then
    BRANCH="main"
    git checkout -b main || handle_error "Failed to create main branch"
fi

echo -e "${YELLOW}📍 Current branch: $BRANCH${NC}"

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}ℹ️  No changes to deploy${NC}"
    exit 0
fi

# Show status
echo -e "${BLUE}📝 Changes to be deployed:${NC}"
git status --short

# Add all changes
echo -e "${BLUE}➕ Adding all changes...${NC}"
git add -A || handle_error "Failed to add changes"

# Generate commit message
echo -e "${BLUE}🔍 Analyzing changes for commit message...${NC}"

# Count changes
FILES_CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
ADDITIONS=$(git diff --cached --numstat | awk '{s+=$1} END {print s}')
DELETIONS=$(git diff --cached --numstat | awk '{s+=$2} END {print s}')

# Analyze file types for commit message
MESSAGE_PARTS=()
STAGED_FILES=$(git diff --cached --name-only)

if echo "$STAGED_FILES" | grep -q "\.tsx\?$\|\.jsx\?$"; then
    MESSAGE_PARTS+=("update React components")
fi

if echo "$STAGED_FILES" | grep -q "\.css$\|\.scss$\|tailwind\.config"; then
    MESSAGE_PARTS+=("update styles")
fi

if echo "$STAGED_FILES" | grep -q "package\.json"; then
    MESSAGE_PARTS+=("update dependencies")
fi

if echo "$STAGED_FILES" | grep -q "\.md$\|README\|CLAUDE"; then
    MESSAGE_PARTS+=("update documentation")
fi

if echo "$STAGED_FILES" | grep -q "supabase\|\.sql$\|\.ts$.*supabase"; then
    MESSAGE_PARTS+=("update database configuration")
fi

if echo "$STAGED_FILES" | grep -q "\.sh$"; then
    MESSAGE_PARTS+=("update scripts")
fi

if echo "$STAGED_FILES" | grep -q "\.env\|\.config\|vite\.config"; then
    MESSAGE_PARTS+=("update configuration")
fi

# Check for new files
NEW_FILES=$(git diff --cached --name-status | grep "^A" 2>/dev/null | wc -l | tr -d ' ')
if [ "$NEW_FILES" -gt 0 ]; then
    MESSAGE_PARTS+=("add $NEW_FILES new file$([ $NEW_FILES -ne 1 ] && echo 's')")
fi

# Check for deleted files  
DELETED_FILES=$(git diff --cached --name-status | grep "^D" 2>/dev/null | wc -l | tr -d ' ')
if [ "$DELETED_FILES" -gt 0 ]; then
    MESSAGE_PARTS+=("remove $DELETED_FILES file$([ $DELETED_FILES -ne 1 ] && echo 's')")
fi

# Build commit message
if [ ${#MESSAGE_PARTS[@]} -gt 0 ]; then
    IFS=", "
    CHANGES="${MESSAGE_PARTS[*]}"
    # Capitalize first letter
    CHANGES="$(echo "$CHANGES" | sed 's/^./\U&/')"
    COMMIT_MSG="$CHANGES"
else
    COMMIT_MSG="Update $FILES_CHANGED file$([ $FILES_CHANGED -ne 1 ] && echo 's')"
fi

# Add statistics
COMMIT_MSG="$COMMIT_MSG (+${ADDITIONS:-0}/-${DELETIONS:-0})"

echo -e "${GREEN}💬 Commit message: $COMMIT_MSG${NC}"

# Create commit
echo -e "${BLUE}📦 Creating commit...${NC}"
git commit -m "$COMMIT_MSG" || handle_error "Failed to commit changes"
echo -e "${GREEN}✅ Changes committed${NC}"

# Check if remote exists
if ! git remote get-url origin &>/dev/null; then
    echo -e "${YELLOW}⚠️  No remote origin configured${NC}"
    echo "Please add a remote repository:"
    echo "  git remote add origin <repository-url>"
    echo ""
    echo "Then run this script again to push your changes."
    exit 0
fi

# Push to remote
echo -e "${BLUE}🔄 Pushing to origin/$BRANCH...${NC}"
git push origin "$BRANCH" 2>/dev/null || {
    echo -e "${YELLOW}📤 Setting upstream and pushing...${NC}"
    git push -u origin "$BRANCH" || handle_error "Failed to push to remote"
}

echo -e "${GREEN}✅ Successfully deployed to GitHub${NC}"
echo "📅 Deployment completed at $(date)"

# Show latest commit
echo ""
echo -e "${BLUE}📋 Latest commit:${NC}"
git log -1 --oneline --color=always

# Show remote URL
REMOTE_URL=$(git config --get remote.origin.url)
if [ -n "$REMOTE_URL" ]; then
    # Convert SSH to HTTPS URL for GitHub
    if [[ "$REMOTE_URL" == git@github.com:* ]]; then
        REPO_PATH=${REMOTE_URL#git@github.com:}
        REPO_PATH=${REPO_PATH%.git}
        WEB_URL="https://github.com/$REPO_PATH"
    elif [[ "$REMOTE_URL" == https://github.com/* ]]; then
        WEB_URL=${REMOTE_URL%.git}
    else
        WEB_URL="$REMOTE_URL"
    fi
    echo -e "${BLUE}🌐 Repository: $WEB_URL${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All done!${NC}"