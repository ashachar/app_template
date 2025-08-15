# Debugging the Keyboard Shortcut

## Step 1: Update Automator to use debug script

1. Open Automator
2. Go to File → Open Recent → "Get Debug Logs"
3. Change the shell script path from:
   ```
   /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/get_logs_silent.sh
   ```
   To:
   ```
   /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/get_logs_debug.sh
   ```
4. Save (⌘S)

## Step 2: Test the shortcut

1. Press `⌘⌃⇧S`
2. Enter a prefix (or use default)
3. Click "Search"
4. You'll see an alert telling you where the debug log is saved

## Step 3: Check the debug log

In Terminal, run:
```bash
cat /tmp/get_logs_debug.log
```

This will show:
- Whether the script ran
- What directory it's in
- Whether it found the log files
- What happened with the clipboard
- Any errors

## Step 4: Manual test

Let's also test the script manually to ensure it works:

```bash
cd /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app
./debug_helpers/get_logs_silent.sh
```

Enter a prefix and see if it works when run directly.

## Common Issues and Fixes

### Issue 1: "consolidated_logs directory NOT found"
The script is running from the wrong directory. Make sure the Automator workflow has the full path.

### Issue 2: No clipboard update
The get_prefixed_logs.sh might not be copying to clipboard properly. Check if you see "✓ Logs copied to clipboard" in the output.

### Issue 3: Permission denied
Make sure all scripts are executable:
```bash
chmod +x /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/get_prefixed_logs.sh
chmod +x /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/get_logs_silent.sh
chmod +x /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/get_logs_debug.sh
```

## After debugging

Once we fix the issue, remember to:
1. Change Automator back to use `get_logs_silent.sh`
2. Save the workflow

Share the contents of `/tmp/get_logs_debug.log` and I'll help fix the issue!