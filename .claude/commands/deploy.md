# deploy

Deploy changes to GitHub with automatic commit message generation.

## Usage
```
/deploy
```

## What this command does

1. **Check git status** to see what changes are pending
2. **Analyze changes** to generate a meaningful commit message
3. **Stage all changes** that are not ignored by .gitignore  
4. **Create a commit** with an auto-generated descriptive message
5. **Push to remote** repository on the current branch

## Steps to execute

### 1. Check current status

```bash
# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "Error: Not a git repository. Initialize with: git init"
    exit 1
fi

# Check current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
echo "Current branch: $BRANCH"

# Check for changes
git status --short
```

### 2. Analyze and stage changes

```bash
# Add all changes
git add -A

# Count changes for commit message
FILES_CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
ADDITIONS=$(git diff --cached --numstat | awk '{s+=$1} END {print s}')
DELETIONS=$(git diff --cached --numstat | awk '{s+=$2} END {print s}')
```

### 3. Generate intelligent commit message

```bash
# Analyze file types changed
STAGED_FILES=$(git diff --cached --name-only)
MESSAGE_PARTS=()

# Detect React/TypeScript changes
if echo "$STAGED_FILES" | grep -q "\.tsx\?$\|\.jsx\?$"; then
    MESSAGE_PARTS+=("update React components")
fi

# Detect style changes
if echo "$STAGED_FILES" | grep -q "\.css$\|tailwind\.config"; then
    MESSAGE_PARTS+=("update styles")
fi

# Detect dependency changes
if echo "$STAGED_FILES" | grep -q "package\.json"; then
    MESSAGE_PARTS+=("update dependencies")
fi

# Detect documentation changes
if echo "$STAGED_FILES" | grep -q "\.md$\|CLAUDE"; then
    MESSAGE_PARTS+=("update documentation")
fi

# Detect database/Supabase changes
if echo "$STAGED_FILES" | grep -q "supabase\|\.sql$"; then
    MESSAGE_PARTS+=("update database configuration")
fi

# Detect new files
NEW_FILES=$(git diff --cached --name-status | grep "^A" | wc -l | tr -d ' ')
if [ "$NEW_FILES" -gt 0 ]; then
    MESSAGE_PARTS+=("add $NEW_FILES new file$([ $NEW_FILES -ne 1 ] && echo 's')")
fi

# Detect deleted files
DELETED_FILES=$(git diff --cached --name-status | grep "^D" | wc -l | tr -d ' ')
if [ "$DELETED_FILES" -gt 0 ]; then
    MESSAGE_PARTS+=("remove $DELETED_FILES file$([ $DELETED_FILES -ne 1 ] && echo 's')")
fi

# Build commit message
if [ ${#MESSAGE_PARTS[@]} -gt 0 ]; then
    IFS=", "
    COMMIT_MSG="${MESSAGE_PARTS[*]}"
    # Capitalize first letter
    COMMIT_MSG="$(echo "$COMMIT_MSG" | sed 's/^./\U&/')"
else
    COMMIT_MSG="Update $FILES_CHANGED file$([ $FILES_CHANGED -ne 1 ] && echo 's')"
fi

# Add statistics
COMMIT_MSG="$COMMIT_MSG (+${ADDITIONS:-0}/-${DELETIONS:-0})"
```

### 4. Commit and push

```bash
# Create commit
git commit -m "$COMMIT_MSG"

# Push to remote (with upstream setup if needed)
git push origin "$BRANCH" 2>/dev/null || git push -u origin "$BRANCH"
```

## Full deployment script

```bash
#!/bin/bash

# Check git repository
[ ! -d .git ] && { echo "Not a git repository"; exit 1; }

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
[ -z "$BRANCH" ] && { git checkout -b main; BRANCH="main"; }

# Check for changes
[ -z "$(git status --porcelain)" ] && { echo "No changes to deploy"; exit 0; }

# Show changes
echo "Changes to deploy:"
git status --short

# Add all changes
git add -A

# Generate commit message
FILES_CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
ADDITIONS=$(git diff --cached --numstat | awk '{s+=$1} END {print s}')
DELETIONS=$(git diff --cached --numstat | awk '{s+=$2} END {print s}')
STAGED_FILES=$(git diff --cached --name-only)

MESSAGE_PARTS=()
echo "$STAGED_FILES" | grep -q "\.tsx\?$\|\.jsx\?$" && MESSAGE_PARTS+=("update React components")
echo "$STAGED_FILES" | grep -q "\.css$\|tailwind" && MESSAGE_PARTS+=("update styles")
echo "$STAGED_FILES" | grep -q "package\.json" && MESSAGE_PARTS+=("update dependencies")
echo "$STAGED_FILES" | grep -q "\.md$" && MESSAGE_PARTS+=("update documentation")
echo "$STAGED_FILES" | grep -q "supabase\|\.sql$" && MESSAGE_PARTS+=("update database")

NEW_FILES=$(git diff --cached --name-status | grep "^A" 2>/dev/null | wc -l | tr -d ' ')
[ "$NEW_FILES" -gt 0 ] && MESSAGE_PARTS+=("add $NEW_FILES new file$([ $NEW_FILES -ne 1 ] && echo 's')")

DELETED_FILES=$(git diff --cached --name-status | grep "^D" 2>/dev/null | wc -l | tr -d ' ')
[ "$DELETED_FILES" -gt 0 ] && MESSAGE_PARTS+=("remove $DELETED_FILES file$([ $DELETED_FILES -ne 1 ] && echo 's')")

if [ ${#MESSAGE_PARTS[@]} -gt 0 ]; then
    IFS=", "
    COMMIT_MSG="${MESSAGE_PARTS[*]}"
    COMMIT_MSG="$(echo "$COMMIT_MSG" | sed 's/^./\U&/')"
else
    COMMIT_MSG="Update $FILES_CHANGED file$([ $FILES_CHANGED -ne 1 ] && echo 's')"
fi

COMMIT_MSG="$COMMIT_MSG (+${ADDITIONS:-0}/-${DELETIONS:-0})"

# Commit and push
echo "Commit message: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"
git push origin "$BRANCH" 2>/dev/null || git push -u origin "$BRANCH"

echo "Successfully deployed to GitHub"
git log -1 --oneline
```

## Example commit messages

Based on the changes detected, the system generates messages like:

- `Update React components, add 2 new files (+120/-45)`
- `Update styles, update documentation (+34/-12)`
- `Update dependencies, remove 1 file (+89/-5)`
- `Add 3 new files, update database (+234/-10)`
- `Update React components, update styles, update dependencies (+445/-123)`

## Files automatically handled

**Excluded (via .gitignore):**
- `node_modules/` (dependencies)
- `.env*` (environment variables)
- `*.log` (logs)
- `consolidated_logs/` (application logs)
- `dist/`, `build/` (build outputs)

**Included:**
- Source code (`.ts`, `.tsx`, `.js`, `.jsx`)
- Configuration files (`package.json`, `vite.config.ts`, etc.)
- Documentation (`.md` files)
- Styles (`.css`, `.scss`)
- Database schemas (`.sql`)

## Troubleshooting

### No remote configured
```bash
# Add remote repository
git remote add origin <repository-url>
```

### Push rejected
```bash
# Pull latest changes first
git pull origin main --rebase
git push origin main
```

### Review what will be committed
```bash
git diff --cached
```

### Undo last commit (before push)
```bash
git reset --soft HEAD~1
```