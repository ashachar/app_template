# Setting Up Keyboard Shortcut for Get Logs (⌘⌃⇧S)

This guide will help you set up a keyboard shortcut (Command + Control + Shift + S) to quickly search and copy logs to your clipboard.

## Method 1: Using Automator (Recommended)

1. **Open Automator**
   - Press `⌘ + Space` and search for "Automator"
   - Click "New Document"
   - Choose "Quick Action" (or "Service" on older macOS)

2. **Configure the Quick Action**
   - Set "Workflow receives" to: **no input**
   - Set "in" to: **any application**

3. **Add a Shell Script Action**
   - In the actions library (left side), search for "Run Shell Script"
   - Drag "Run Shell Script" to the workflow area
   - Set Shell to: `/bin/bash`
   - Replace the script content with:
   ```bash
   /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/get_logs_silent.sh
   ```

4. **Save the Quick Action**
   - Press `⌘ + S`
   - Name it: "Get Debug Logs"
   - It will be saved to `~/Library/Services/`

5. **Assign the Keyboard Shortcut**
   - Open System Preferences → Keyboard → Shortcuts
   - Click "Services" in the left sidebar
   - Find "Get Debug Logs" under "General"
   - Click "Add Shortcut" and press: `⌘⌃⇧S`

## Method 2: Using Shortcuts App (macOS Monterey or later)

1. **Open Shortcuts app**
   - Press `⌘ + Space` and search for "Shortcuts"

2. **Create New Shortcut**
   - Click the "+" button
   - Add action: "Run Shell Script"
   - Enter the script path:
   ```bash
   /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app/debug_helpers/get_logs_silent.sh
   ```

3. **Configure the Shortcut**
   - Click shortcut settings (three dots)
   - Enable "Use with: Global"
   - Add keyboard shortcut: `⌘⌃⇧S`

## How It Works

When you press `⌘⌃⇧S`:
1. A dialog box appears asking for the log prefix
2. Default prefix is "[DEBUG-" (you can type to change it)
3. Press Enter or click "Search"
4. The script searches for logs with that prefix
5. Results are automatically copied to your clipboard
6. You'll see a notification with the result

## Troubleshooting

- **If the shortcut doesn't work:** Check System Preferences → Security & Privacy → Privacy → Accessibility and ensure Automator/Shortcuts has permission
- **If you get "command not found":** Make sure the full path to the script is correct
- **If logs aren't found:** Ensure your servers are running and logs exist in `consolidated_logs/latest.log`

## Testing

1. Make sure your servers are running: `npm run dev:all`
2. Add some test logs to trigger
3. Press `⌘⌃⇧S`
4. Enter a prefix like "[DEBUG-" or "ERROR"
5. Check your clipboard (⌘V to paste somewhere)

## Alternative: Terminal Alias

If you prefer using Terminal, add this to your `~/.zshrc` or `~/.bash_profile`:

```bash
alias getlogs='cd /Users/amirshachar/Desktop/Amir/Projects/Personal/swifit/app && ./get_prefixed_logs.sh'
```

Then you can just type `getlogs '[DEBUG-123]'` in Terminal.