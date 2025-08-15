# Bug Report XML Updater

A reusable Python script for safely updating bug report XML files during the debugging hypothesis generation process.

## Overview

The `bug_report_xml_updater.py` script replaces the manual XML manipulation that was previously done in individual debugging sessions. It provides a consistent, safe way to:

- Move current hypotheses to past hypotheses automatically  
- Add new hypotheses with proper formatting
- Annotate files that had debug logs added
- Reference diagnostic JavaScript scripts
- Add metadata timestamps for tracking

## What It Replaces

**Before**: Each debugging session required custom XML manipulation code like:

```python
# Custom XML manipulation (error-prone, repetitive)
import xml.etree.ElementTree as ET
xml_content = '''entire XML hardcoded here...'''
# ... manual parsing and updating
```

**After**: Simple command-line usage:

```bash
python debug_helpers/bug_report_xml_updater.py \
    --xml-file debug_artifacts/bug_report_ISSUE-123.xml \
    --hypothesis "Your hypothesis here" \
    --logged-files "file1.ts,file2.tsx" \
    --analysis-script "$(cat diagnostic_script_ISSUE-123.js)"
```

## Features

### 🔄 Hypothesis History Management
- Automatically moves existing `current_hypothesis` to `past_hypotheses`
- Adds timestamps to failed hypotheses for tracking
- Prevents loss of previous debugging work

### 🛡️ Safe XML Processing
- Parses existing XML without corruption
- Preserves all existing content and structure
- Handles malformed XML gracefully with error messages
- Creates backups of original structure

### 📝 Log File Annotation
- Marks specific files that had debug logs added
- Timestamps when logs were added
- Helps track which files have debugging instrumentation

### 🎯 Analysis Script Integration
- Embeds JavaScript diagnostic code directly in XML
- Self-contained debugging artifacts in `<analysis_script><code>` tag
- Results automatically populated in `<analysis_script><results>` by get_logs_silent.sh

### 📊 Metadata Tracking
- Adds `last_updated` timestamps
- Tracks when XML was modified
- Enables debugging session history

## Usage Examples

### Basic Hypothesis Update
```bash
python debug_helpers/bug_report_xml_updater.py \
    --xml-file debug_artifacts/bug_report_AUTH-404.xml \
    --hypothesis "User authentication fails due to missing CSRF token validation"
```

### Full Debugging Session Update
```bash
python debug_helpers/bug_report_xml_updater.py \
    --xml-file debug_artifacts/bug_report_COMP-FILTER-001.xml \
    --hypothesis "HYPOTHESIS: Missing Data Propagation Chain

The company filter shows all companies because filteredCompanyOptions from useCompanySearch is not passed through the props hierarchy.

ROOT CAUSE: Missing links in data flow chain:
1. useExploreProps missing filteredCompanies parameter
2. filterBarProps.ts interface missing filteredCompanies property
3. SearchableFilterDropdown falls back to maxDisplayOptions=10" \
    --logged-files "useSearchOrchestrator.ts,useExploreProps.ts,filterBarProps.ts" \
    --analysis-script "$(cat diagnostic_script_COMP-FILTER-001.js)" \
    --issue-id "COMP-FILTER-001"
```

### Update Only Analysis Script
```bash
python debug_helpers/bug_report_xml_updater.py \
    --xml-file debug_artifacts/bug_report_DB-502.xml \
    --analysis-script "$(cat diagnostic_script_DB-502.js)"
```

## Integration with `/bug_hypothesis` Command

The script is integrated into the `/bug_hypothesis` command workflow:

1. **STEP 7** of bug hypothesis generation uses this script
2. Replaces manual XML manipulation in `.claude/commands/bug_hypothesis.md`
3. Ensures consistent XML updates across all debugging sessions
4. Reduces errors from manual XML editing

## Command-Line Options

| Option | Required | Description | Example |
|--------|----------|-------------|---------|
| `--xml-file` | ✅ | Path to bug report XML | `debug_artifacts/bug_report_ISSUE-123.xml` |
| `--hypothesis` | ❌ | New hypothesis text (multi-line supported) | `"Missing data in props chain"` |
| `--logged-files` | ❌ | Comma-separated files with logs added | `"file1.ts,file2.tsx,file3.py"` |
| `--analysis-script` | ❌ | Complete diagnostic script code | `"$(cat script.js)"` |
| `--issue-id` | ❌ | Issue ID for validation | `"ISSUE-123"` |
| `--output` | ❌ | Output file path (defaults to input) | `debug_artifacts/updated_report.xml` |

## Error Handling

The script provides clear error messages for common issues:

- **File not found**: Clear path to missing XML file
- **XML parsing errors**: Details about malformed XML
- **Permission errors**: File write permission issues
- **Invalid arguments**: Missing required parameters

## Output

Success output example:
```
✅ Loaded existing XML: debug_artifacts/bug_report_COMP-FILTER-001.xml
📋 Moved current hypothesis to past_hypotheses
✅ Updated current hypothesis
✅ Added log annotations to 3 files
✅ Added JS script reference: diagnostic_script_COMP-FILTER-001.js
✅ Updated metadata timestamp

✅ Bug report XML updated successfully!
📁 Location: debug_artifacts/bug_report_COMP-FILTER-001.xml
```

## Benefits

### For Individual Sessions
- ✅ No need to write custom XML manipulation code
- ✅ Consistent XML structure and formatting
- ✅ Safe handling of existing content
- ✅ Automatic hypothesis history tracking

### For Team Collaboration  
- ✅ Standardized XML update process
- ✅ Preserves debugging history across team members
- ✅ Consistent file structure for sharing bug reports
- ✅ Reduces onboarding time for new debugging workflows

### For Long-term Maintenance
- ✅ Central place to improve XML handling
- ✅ Easy to add new features to all debugging sessions
- ✅ Consistent error handling and validation
- ✅ Audit trail of all XML modifications

## Future Enhancements

Potential improvements to the script:

- **Validation**: Verify hypothesis format and completeness
- **Templates**: Pre-defined hypothesis templates for common bug types
- **Analytics**: Generate statistics on debugging success rates
- **Integration**: Direct integration with issue tracking systems
- **Backup**: Automatic backup of XML files before modification

---

**Used by**: `.claude/commands/bug_hypothesis.md` → STEP 7: UPDATE XML AND SAVE