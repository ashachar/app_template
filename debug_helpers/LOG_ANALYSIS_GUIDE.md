# 🤖 Automated Log Analysis Quick Reference

## Quick Start

### Python (Standalone Analysis)
```bash
# Analyze all logs immediately
python debug_helpers/analyze_logs.py

# This will:
# - Scan consolidated_logs/latest.log
# - Check all logs in logs/ directory
# - Analyze backend/api error logs
# - Generate a comprehensive report
```

### JavaScript (In Tests)
```javascript
const { LogAnalyzer } = require('./debug_helpers/log_analyzer.cjs');
const analyzer = new LogAnalyzer();

// Attach to Playwright for real-time monitoring
analyzer.attachToContext(context);

// Get results
const summary = analyzer.getSummary();
```

## Understanding the Report

### Severity Levels
- 🔴 **High**: Critical issues requiring immediate attention (Database, API, Lambda, React errors)
- 🟡 **Medium**: Important but not blocking (Timeouts, null references, performance)
- 🟢 **Low**: Informational or minor issues

### Error Categories

| Category | Common Issues | Priority |
|----------|--------------|----------|
| **Database** | Missing tables, column errors, connection issues | 🔴 High |
| **API** | 401/403/404/500 errors, CORS, connection refused | 🔴 High |
| **Lambda** | Deployment failures, timeouts, permissions | 🔴 High |
| **React** | Hook violations, render loops, state updates | 🔴 High |
| **Lookup Table** | String vs integer mismatches, invalid enums | 🟡 Medium |
| **Null Reference** | Undefined properties, missing data | 🟡 Medium |
| **Timeout** | Slow responses, element not found | 🟡 Medium |
| **File System** | Missing files, permission denied | 🔴 High |
| **Authentication** | JWT expired, invalid credentials | 🔴 High |

## Common Patterns & Solutions

### 1. Lookup Table Errors
**Pattern**: `"Invalid enum value"` or `"Expected integer, got string"`
**Solution**: 
- Check `api_agreements.md` for correct format
- Ensure using integer indexes, not string values
- Verify `lookupService.ts` is properly initialized

### 2. Null Reference Errors
**Pattern**: `"Cannot read property 'X' of null/undefined"`
**Solution**:
- Add null checks: `data?.field?.value`
- Initialize state with proper defaults
- Verify API response structure

### 3. API Errors
**Pattern**: `401`, `403`, `404`, `500` status codes
**Solution**:
- Check authentication headers
- Verify endpoint exists in `api/routes/`
- Check CORS configuration
- Ensure API server is running

### 4. Database Errors
**Pattern**: `"relation does not exist"`, `"column not found"`
**Solution**:
- Run migrations: `cd schema && ./run_migration.sh`
- Check schema files in `schema/sql/structured/`
- Verify RLS policies

## Integration Examples

### Basic Test with Analysis
```javascript
const { withLogAnalysis } = require('./debug_helpers/log_analyzer.cjs');

await withLogAnalysis(async (analyzer) => {
  // Your test code here
  const browser = await chromium.launch();
  const context = await browser.newContext();
  
  // Attach analyzer
  analyzer.attachToContext(context);
  
  // Run your test...
  
  await browser.close();
}, {
  saveReport: true,
  reportPath: 'test_analysis.json'
});
```

### Manual Analysis in Debug Script
```javascript
const analyzer = new LogAnalyzer();

// Analyze server logs
await analyzer.analyzeServerLogs('consolidated_logs/latest.log');

// Run your debug code...

// Check for issues
const summary = analyzer.getSummary();
if (summary.criticalFindings.length > 0) {
  console.log('🚨 Critical issues found!');
  summary.criticalFindings.forEach(f => console.log(f));
}
```

### Performance Tracking
```javascript
// Track custom metrics
analyzer.trackPerformance('apiCallTime', responseTime);
analyzer.trackPerformance('renderTime', renderDuration);

// Automatic alerts for slow operations (>5000ms)
```

## Interpreting Results

### No Issues Found
```
✅ Great! No issues detected in logs.
```
**Action**: Proceed with confidence, logs are clean.

### Critical Issues Found
```
🚨 Critical Findings:
1. [Database] relation "requisitions" does not exist
2. [API] POST /api/candidates 500 Internal Server Error
```
**Action**: Address these immediately before proceeding.

### Multiple Categories
```
📈 Issues by Category:
   Database     ████████████ (6)
   API          ████████ (4)
   Null Reference ████ (2)
```
**Action**: Start with the highest count category.

### Suggested Actions
```
💡 Recommended Actions:
1. Check if migrations have been run: cd schema && ./run_migration.sh
2. Verify API server is running: check consolidated_logs/latest.log
3. Add null checks before accessing properties
```
**Action**: Follow suggestions in order.

## Advanced Features

### Custom Pattern Addition
Add patterns to `debug_helpers/patterns/error_patterns.json`:
```json
{
  "custom_errors": {
    "patterns": ["Your.*custom.*pattern"],
    "category": "Custom",
    "severity": "high",
    "suggestions": ["Your custom fix suggestion"]
  }
}
```

### Export Formats
- **JSON**: Detailed data for further analysis
- **HTML**: Visual report for sharing
- **Console**: Quick summary during debugging

### Real-time Monitoring
The analyzer captures:
- Console logs (errors, warnings)
- Network failures
- Page errors
- Performance metrics

## Tips for Effective Use

1. **Run Early and Often**: Analyze logs at the start of debugging
2. **Use Categories**: Focus on one category at a time
3. **Follow Suggestions**: They're based on common solutions
4. **Track Progress**: Save reports to see improvement
5. **Combine with Tests**: Use in integration tests for regression prevention

## Troubleshooting

### Analyzer Not Finding Patterns
- Check if log file paths are correct
- Verify error patterns match actual log format
- Ensure proper encoding (UTF-8)

### Too Many False Positives
- Adjust patterns in `error_patterns.json`
- Use more specific regex patterns
- Consider severity levels

### Performance Impact
- Analyze logs asynchronously
- Limit real-time analysis to critical paths
- Use sampling for high-volume logs