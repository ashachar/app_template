# Fixing "Operation not permitted" Error

## Solution 1: Remove Quarantine Attribute (Most Likely Fix)

The script might have a quarantine attribute. Run this in Terminal:

```bash
xattr -d com.apple.quarantine /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/get_logs_silent.sh
xattr -d com.apple.quarantine /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/get_prefixed_logs.sh
```

If you get "No such xattr", that's fine - move to Solution 2.

## Solution 2: Grant Full Disk Access to Automator

1. **System Preferences → Security & Privacy → Privacy**
2. Click the lock to make changes
3. Select **Full Disk Access** in the left sidebar
4. Click the **+** button
5. Navigate to `/System/Library/CoreServices/`
6. Add **Automator.app**
7. Also add **Terminal.app** from `/Applications/Utilities/`

## Solution 3: Use a Wrapper Script

Create a new script that Automator can definitely run:

```bash
#!/bin/bash
cd /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app
./debug_helpers/get_logs_silent.sh
```

Save this as `/tmp/run_get_logs.sh` and use that path in Automator instead.

## Solution 4: Reset Permissions on the Entire Directory

```bash
# Reset permissions on the debug_helpers directory
chmod -R 755 /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/
chmod -R 755 /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/*.sh

# Clear extended attributes
xattr -cr /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/
```

## Quick Test

After trying any solution above, test in Finder with ⌃⌘⇧S again.