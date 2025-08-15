# Debug Workflow File Paths

## Command Files
- `/explore <description> <issue_id>` → `.claude/commands/explore.md`
- `/bug_hypothesis` → `.claude/commands/bug_hypothesis.md`
- `/bug_fix` → `.claude/commands/bug_fix.md`

## How Commands Work

### 1. `/explore` Command
- **Input**: Issue description and issue_id as arguments
- **Output**: Creates XML with `<issue_id>` tag
- **File**: Creates `debug_artifacts/bug_report_<issue_id>.xml`
- **Action**: Copies XML to clipboard

### 2. `/bug_hypothesis` Command  
- **Input**: User pastes the XML (from clipboard)
- **Process**: Extracts issue_id from the `<issue_id>` tag in XML
- **Output**: Enhanced XML with logs and JS script
- **File**: Updates same file `debug_artifacts/bug_report_<issue_id>.xml`
- **Action**: Copies enhanced XML to clipboard

### 3. `/bug_fix` Command
- **Input**: User pastes the enriched XML (with log results)
- **Process**: Extracts issue_id from the `<issue_id>` tag in XML
- **Output**: Final XML with fix details and insights
- **File**: Updates same file `debug_artifacts/bug_report_<issue_id>.xml`
- **Action**: Copies final XML to clipboard

## XML Structure with issue_id Tag

```xml
<bug_report>
  <issue_id>COMP-FILTER-001</issue_id>  <!-- This tag is key! -->
  <issue_to_fix>Description...</issue_to_fix>
  <!-- ... rest of XML ... -->
</bug_report>
```

## Directory Structure
```
app/
├── .claude/
│   └── commands/
│       ├── explore.md          # Creates initial XML
│       ├── bug_hypothesis.md   # Adds logs and JS script
│       └── bug_fix.md          # Implements fix
├── debug_artifacts/            # All XML files go here
│   ├── bug_report_*.xml
│   ├── bug_report_*_hypothesis.xml
│   └── bug_report_*_fixed.xml
└── bug_reports/
    └── README.md               # Documentation

```

## Workflow Summary

1. **User runs**: `/explore "Company filter broken" COMP-001`
   - Creates: `debug_artifacts/bug_report_COMP-001.xml` with `<issue_id>COMP-001</issue_id>`
   - Copies XML to clipboard

2. **User runs**: `/bug_hypothesis` and pastes XML
   - Reads issue_id from `<issue_id>` tag
   - Updates: `debug_artifacts/bug_report_COMP-001.xml` (same file)
   - Adds logs to code files
   - Copies enhanced XML to clipboard

3. **User manually**:
   - Reproduces bug
   - Collects logs
   - Enriches XML with results

4. **User runs**: `/bug_fix` and pastes enriched XML
   - Reads issue_id from `<issue_id>` tag
   - Updates: `debug_artifacts/bug_report_COMP-001.xml` (same file)
   - Implements the fix
   - Copies final XML to clipboard

## Key Implementation Details

- **XML Communication**: Commands communicate via clipboard-pasted XML
- **issue_id Storage**: Stored in `<issue_id>` tag within the XML
- **Directory creation**: `mkdir -p debug_artifacts` ensures directory exists
- **Clipboard integration**: Each command ends with `cat <file> | pbcopy`
- **Log format**: `[DEBUG-<ACTUAL_ISSUE_ID>]` (replace placeholder with real ID)
- **JS script**: Uses `[ISSUE_ID]` placeholder to be replaced with actual ID