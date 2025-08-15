# Clean Logs Command

Clean ALL debug log statements from the codebase using the `@LOGMARK` marker system.

## Usage

```bash
/clean_logs
```

## Implementation

```bash
# Simply run the marker-based cleaner
python debug_helpers/find_log_prints.py --clean
```
