# Log Indicators Guide - Deterministic Bug Detection

## 🔴 Critical Concept: Log Indicators

**Log indicators** are specific, searchable strings in logs that definitively prove a bug exists. They replace subjective visual analysis with objective, deterministic proof.

## Standard Log Prefixes

### Bug Reproduction Logs
- `[BUG_REPRO]` - Metadata about bug reproduction attempt
- `[TEST]` - Test execution and verification steps  
- `[BUG_INDICATOR]` - **CRITICAL** - Definitive proof bug exists
- `[BROWSER_CONSOLE]` - Browser console output
- `[API_RESPONSE]` - API calls and responses
- `[DEBUG]` - Additional debugging information

### Example Log Structure
```
[BUG_REPRO] Starting bug reproduction for: Dual toast issue
[BUG_REPRO] Session ID: DUAL-TOAST-1234567890
[TEST] Starting dual toast verification...
[TEST] Toast counts - Errors: 1 Success: 1
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] Both error and success toasts visible
```

## Common Bug Patterns and Their Indicators

### 1. Dual Toast Bug (Error + Success)

**Bug**: Both error and success toasts appear simultaneously

**Log Indicators**:
```
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] Both error and success toasts visible
[TEST] Toast counts - Errors: 1 Success: 1
```

**Test Code**:
```javascript
const errorCount = await page.locator('.error-toast').count();
const successCount = await page.locator('.success-toast').count();
console.log('[TEST] Toast counts - Errors:', errorCount, 'Success:', successCount);

if (errorCount > 0 && successCount > 0) {
  console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
  console.log('[BUG_INDICATOR] Both error and success toasts visible');
}
```

### 2. Missing Element Bug

**Bug**: Required element disappears unexpectedly

**Log Indicators**:
```
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] Required element missing: submit button
[TEST] Element count: 0 (expected: 1)
[DEBUG] Element selector: button[type="submit"]
```

**Test Code**:
```javascript
const elementCount = await page.locator('button[type="submit"]').count();
console.log('[TEST] Element count:', elementCount, '(expected: 1)');

if (elementCount === 0) {
  console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
  console.log('[BUG_INDICATOR] Required element missing: submit button');
  console.log('[DEBUG] Element selector: button[type="submit"]');
}
```

### 3. API/UI Mismatch

**Bug**: API returns success but UI shows error

**Log Indicators**:
```
[API_RESPONSE] Status: 200
[API_RESPONSE] Body: {"success": true}
[TEST] UI shows error: true
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] API success but UI shows error
```

**Test Code**:
```javascript
// In route interceptor
console.log('[API_RESPONSE] Status:', response.status());
console.log('[API_RESPONSE] Body:', responseBody);

// In UI check
const hasError = await page.locator('.error-message').isVisible();
console.log('[TEST] UI shows error:', hasError);

if (response.status() === 200 && hasError) {
  console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
  console.log('[BUG_INDICATOR] API success but UI shows error');
}
```

### 4. Performance/Timeout Issues

**Bug**: Operation takes too long or times out

**Log Indicators**:
```
[TEST] Operation started at: 1234567890
[TEST] Operation still running at: 1234577890 (10000ms elapsed)
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] Operation timeout: exceeded 10s limit
[BUG_INDICATOR] Expected duration: <5000ms, Actual: >10000ms
```

### 5. State Inconsistency

**Bug**: Application state doesn't match expected state

**Log Indicators**:
```
[TEST] Expected state: { loggedIn: true, role: "admin" }
[TEST] Actual state: { loggedIn: true, role: null }
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] State mismatch: role is null but should be "admin"
```

## How to Write Effective Bug Indicators

### 1. Be Specific and Searchable
```javascript
// ❌ BAD - Too generic
console.log('Error found');

// ✅ GOOD - Specific and searchable
console.log('[BUG_INDICATOR] Form validation bypassed - empty email accepted');
```

### 2. Include Actual vs Expected
```javascript
// ❌ BAD - No context
console.log('[BUG_INDICATOR] Wrong value');

// ✅ GOOD - Clear comparison
console.log('[BUG_INDICATOR] Price calculation wrong');
console.log('[BUG_INDICATOR] Expected: $100.00, Actual: $90.00');
```

### 3. Use Consistent Format
```javascript
// Always start with the marker
console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
// Then describe what's wrong
console.log('[BUG_INDICATOR] Description of the issue');
// Include relevant data
console.log('[BUG_INDICATOR] Key data points that prove the bug');
```

### 4. Make It Binary (Pass/Fail)
```javascript
// The presence of ANY [BUG_INDICATOR] means test failed
if (logs.includes('[BUG_INDICATOR]')) {
  return false; // Bug exists
}
return true; // No bug
```

## Analyzing Logs for Bug Indicators

### Manual Analysis
```bash
# Search for bug indicators in log file
grep "BUG_INDICATOR" bug_reproduction.log

# Count occurrences
grep -c "BUG_INDICATOR" bug_reproduction.log

# Show context
grep -B2 -A2 "BUG_INDICATOR" bug_reproduction.log
```

### Automated Analysis
```javascript
function analyzeBugLogs(logFile) {
  const logs = fs.readFileSync(logFile, 'utf8');
  const indicators = logs.split('\n')
    .filter(line => line.includes('[BUG_INDICATOR]'))
    .map(line => line.split('[BUG_INDICATOR]')[1].trim());
  
  if (indicators.length > 0) {
    console.log('❌ Bug Confirmed - Found indicators:');
    indicators.forEach(ind => console.log(`  - ${ind}`));
    return false; // Bug exists
  }
  
  console.log('✅ No bugs found');
  return true; // No bug
}
```

## Template for Bug Reproduction Test

```javascript
async function testBug() {
  // Start with metadata
  console.log('[BUG_REPRO] Testing: <bug description>');
  console.log('[BUG_REPRO] Session:', sessionId);
  
  // Perform test steps with logging
  console.log('[TEST] Step 1: Navigate to page');
  await page.goto(url);
  
  console.log('[TEST] Step 2: Perform action');
  await page.click(button);
  
  // Check for bug condition
  const bugCondition = await checkForBug(page);
  console.log('[TEST] Bug condition met:', bugCondition);
  
  if (bugCondition) {
    // ALWAYS use these three lines for confirmed bugs
    console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
    console.log('[BUG_INDICATOR] <specific description>');
    console.log('[BUG_INDICATOR] <key evidence>');
    return false; // Test fails
  }
  
  console.log('[TEST] ✅ Bug not found');
  return true; // Test passes
}
```

## Verification Checklist

Before proceeding with debugging, verify:

- [ ] Test outputs logs to a file
- [ ] Logs contain `[BUG_INDICATOR]` entries
- [ ] Bug indicators are specific and descriptive
- [ ] Test returns false (fails) when bug exists
- [ ] Log file is saved with session ID
- [ ] Evidence is recorded in bug_evidence.json

## Example: Complete Bug Verification

```bash
# Run test and capture logs
node test_bulk_delete_bug.js > bulk_delete_bug.log 2>&1

# Verify bug was found
grep "BUG_INDICATOR" bulk_delete_bug.log

# Expected output:
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] Both error and success toasts visible
[BUG_INDICATOR] Error count: 1, Success count: 1

# This proves the bug exists deterministically
```

## Summary

Log indicators transform bug detection from subjective ("looks wrong") to objective ("specific string found in logs"). This enables:

1. **Automated verification** - Scripts can check for bugs
2. **Consistent detection** - Same bug always produces same indicators  
3. **Clear success criteria** - Bug fixed when indicators disappear
4. **Historical tracking** - Can search past logs for patterns
5. **Team communication** - Everyone sees same evidence

Always use `[BUG_INDICATOR]` markers to make bugs searchable and verifiable!