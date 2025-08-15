# XML Log Integration Script

## Overview

The `get_logs_silent.sh` script has been updated to work with the new XML-based debugging workflow. Instead of using a prefix file, it now:

1. Finds the most recent `bug_report_*.xml` file in `debug_artifacts/`
2. Extracts the `issue_id` from the XML
3. Searches for logs with prefix `[DEBUG-<issue_id>]`
4. Injects the logs and JS script results directly into the XML
5. Copies the updated XML to clipboard

## How It Works

### 1. Finding the Latest XML
```bash
LATEST_XML=$(ls -t "$DEBUG_DIR"/bug_report_*.xml 2>/dev/null | head -1)
```

### 2. Extracting Issue ID
```bash
ISSUE_ID=$(grep -oP '(?<=<issue_id>)[^<]+' "$LATEST_XML")
```

### 3. Log Collection
- Uses the existing `get_prefixed_logs.sh` script
- Searches for logs with pattern `[DEBUG-<issue_id>]`

### 4. JS Script Results
- Looks for JSON files in `~/Downloads` created in the last 10 minutes
- Takes the most recent one as the JS script results

### 5. XML Update
The script injects:
- Individual log results into `<log>/<result>` tags (placeholder for now)
- JS script output into `<js_script>/<result>` tag
- All logs into a `<log_results>` section for consolidated view

### 6. Output
- Updates the original XML file in place
- Copies the updated XML to clipboard
- Auto-pastes with Cmd+V

## Usage

1. Run `/bug_hypothesis` command to add logs to your code
2. Reproduce the bug
3. Run the JS diagnostic script in browser console
4. Save the JS output as JSON in Downloads folder
5. Press your keyboard shortcut to run this script
6. The updated XML is automatically pasted

## XML Structure After Update

```xml
<bug_report>
  <issue_id>COMP-FILTER-001</issue_id>
  <issue_to_fix>...</issue_to_fix>
  <files_relevant_to_issue>
    <file>
      <logs>
        <log>
          <message>console.log(...)</message>
          <reason>...</reason>
          <result>Log output collected - see consolidated results</result>
        </log>
      </logs>
    </file>
  </files_relevant_to_issue>
  <js_script>
    <script>...</script>
    <reason>...</reason>
    <result>{ JSON output from browser console }</result>
  </js_script>
  <log_results>
    [All collected log entries with DEBUG-ISSUE_ID prefix]
  </log_results>
</bug_report>
```

## Migration Notes

- No longer uses `debug_prefix.txt` file
- No longer uses `debug_header_message.txt` file
- Works automatically with the most recent bug report XML
- Integrated with the three-command debugging workflow