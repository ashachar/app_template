# Deterministic Bug Detection Examples

This document shows how to use log prints and Playwright assertions for deterministic bug verification instead of subjective visual analysis.

## Example 1: Dual Toast Bug (Error + Success)

**Bug Description**: "When deleting items, both error and success toasts appear"

```javascript
// test_dual_toast_bug.js
const { chromium, expect } = require('@playwright/test');
const fs = require('fs');

async function testDualToastBug() {
  // LOG PRINT START - BUG REPRODUCTION
  console.log('[BUG_REPRO] Starting dual toast bug reproduction');
  console.log('[BUG_REPRO] Session ID:', `DUAL-TOAST-${Date.now()}`);
  console.log('[BUG_REPRO] Timestamp:', new Date().toISOString());
  // LOG PRINT END
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture ALL console logs from the browser
  const browserLogs = [];
  page.on('console', msg => {
    const logEntry = `[BROWSER_CONSOLE] ${msg.type()}: ${msg.text()}`;
    browserLogs.push(logEntry);
    // LOG PRINT START - BROWSER CONSOLE
    console.log(logEntry);
    // LOG PRINT END
  });
  
  try {
    // Navigate and perform actions
    await page.goto('http://localhost:3000/items');
    await page.click('button#delete-all');
    await page.click('button#confirm-delete');
    
    // Wait for toasts to appear
    await page.waitForTimeout(2000);
    
    // LOG PRINT START - TEST VERIFICATION
    console.log('[TEST] Starting dual toast verification...');
    
    // Deterministic checks with logging
    const errorToasts = page.locator('.toast.error, .destructive, [data-type="error"]');
    const successToasts = page.locator('.toast.success, [data-type="success"]');
    
    const errorCount = await errorToasts.count();
    const successCount = await successToasts.count();
    
    console.log('[TEST] Toast counts - Errors:', errorCount, 'Success:', successCount);
    
    // Get exact text content
    if (errorCount > 0) {
      const errorText = await errorToasts.first().textContent();
      console.log('[TEST] Error toast text:', errorText);
    }
    
    if (successCount > 0) {
      const successText = await successToasts.first().textContent();
      console.log('[TEST] Success toast text:', successText);
    }
    
    // DETERMINISTIC BUG DETECTION
    if (errorCount > 0 && successCount > 0) {
      console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
      console.log('[BUG_INDICATOR] Both error and success toasts are visible');
      console.log('[BUG_INDICATOR] This should not happen - only one toast type expected');
      // LOG PRINT END
      
      return false; // Test fails = bug exists
    }
    
    console.log('[TEST] ✅ Only one toast type visible (expected behavior)');
    return true; // Test passes = bug fixed
    
  } finally {
    await browser.close();
  }
}

// Run and save logs
testDualToastBug()
  .then(passed => {
    console.log('\n[RESULT] Test', passed ? 'PASSED' : 'FAILED');
    process.exit(passed ? 0 : 1);
  });
```

**Expected Log Output (Bug Present):**
```
[BUG_REPRO] Starting dual toast bug reproduction
[BUG_REPRO] Session ID: DUAL-TOAST-1234567890
[BUG_REPRO] Timestamp: 2024-01-15T10:30:00.000Z
[BROWSER_CONSOLE] log: Deleting items...
[TEST] Starting dual toast verification...
[TEST] Toast counts - Errors: 1 Success: 1
[TEST] Error toast text: An error occurred
[TEST] Success toast text: Items deleted successfully
[BUG_INDICATOR] *** BUG CONFIRMED ***
[BUG_INDICATOR] Both error and success toasts are visible
[BUG_INDICATOR] This should not happen - only one toast type expected
[RESULT] Test FAILED
```

## Example 2: Missing Required Element

**Bug Description**: "Submit button disappears after validation"

```javascript
async function testMissingButtonBug() {
  // LOG PRINT START - BUG REPRODUCTION
  console.log('[BUG_REPRO] Testing missing submit button bug');
  console.log('[BUG_REPRO] Expected: Button remains visible after validation');
  // LOG PRINT END
  
  // ... navigation code ...
  
  // Trigger validation
  await page.fill('#email', 'invalid-email');
  await page.click('#validate');
  
  // LOG PRINT START - ELEMENT STATE CHECK
  console.log('[TEST] Checking submit button visibility...');
  
  // Use Playwright's built-in assertions
  try {
    await expect(page.locator('button[type="submit"]')).toBeVisible({ timeout: 5000 });
    console.log('[TEST] ✅ Submit button is visible (no bug)');
    return true;
  } catch (e) {
    console.log('[TEST] ❌ Submit button is NOT visible');
    console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
    console.log('[BUG_INDICATOR] Submit button disappeared after validation');
    console.log('[BUG_INDICATOR] Expected: Button should remain visible');
    console.log('[BUG_INDICATOR] Actual: Button is missing from DOM');
    
    // Additional debugging info
    const buttonCount = await page.locator('button[type="submit"]').count();
    console.log('[DEBUG] Submit button count in DOM:', buttonCount);
    
    const allButtons = await page.locator('button').allTextContents();
    console.log('[DEBUG] All visible buttons:', allButtons);
    // LOG PRINT END
    
    return false;
  }
}
```

## Example 3: API Error Detection

**Bug Description**: "API returns success but UI shows error"

```javascript
async function testAPIResponseBug() {
  // LOG PRINT START - BUG REPRODUCTION
  console.log('[BUG_REPRO] Testing API response handling bug');
  // LOG PRINT END
  
  // Intercept API responses
  const apiResponses = [];
  await page.route('**/api/**', async route => {
    const response = await route.fetch();
    const responseData = {
      url: response.url(),
      status: response.status(),
      body: await response.text()
    };
    apiResponses.push(responseData);
    
    // LOG PRINT START - API RESPONSE
    console.log('[API_RESPONSE] URL:', responseData.url);
    console.log('[API_RESPONSE] Status:', responseData.status);
    console.log('[API_RESPONSE] Body:', responseData.body.substring(0, 200));
    // LOG PRINT END
    
    await route.fulfill({ response });
  });
  
  // Perform action
  await page.click('#save-button');
  await page.waitForTimeout(2000);
  
  // LOG PRINT START - VERIFICATION
  console.log('[TEST] Checking for API/UI mismatch...');
  
  // Check API response
  const saveResponse = apiResponses.find(r => r.url.includes('/save'));
  const apiSuccess = saveResponse && saveResponse.status === 200;
  
  // Check UI state
  const errorVisible = await page.locator('.error-message').isVisible();
  const successVisible = await page.locator('.success-message').isVisible();
  
  console.log('[TEST] API returned:', apiSuccess ? 'SUCCESS' : 'ERROR');
  console.log('[TEST] UI shows error:', errorVisible);
  console.log('[TEST] UI shows success:', successVisible);
  
  // Detect mismatch
  if (apiSuccess && errorVisible) {
    console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
    console.log('[BUG_INDICATOR] API returned success but UI shows error');
    console.log('[BUG_INDICATOR] This indicates incorrect error handling');
    // LOG PRINT END
    return false;
  }
  
  console.log('[TEST] ✅ API response and UI state match');
  return true;
}
```

## Example 4: Performance/Timing Issues

**Bug Description**: "Loading spinner never disappears"

```javascript
async function testInfiniteLoadingBug() {
  // LOG PRINT START - BUG REPRODUCTION
  console.log('[BUG_REPRO] Testing infinite loading spinner bug');
  // LOG PRINT END
  
  const loadingStates = [];
  const startTime = Date.now();
  
  // Monitor loading state changes
  const checkLoading = setInterval(async () => {
    const isLoading = await page.locator('.loading-spinner').isVisible().catch(() => false);
    const elapsed = Date.now() - startTime;
    
    loadingStates.push({ time: elapsed, loading: isLoading });
    
    // LOG PRINT START - STATE TRACKING
    console.log(`[LOADING_STATE] ${elapsed}ms - Loading: ${isLoading}`);
    // LOG PRINT END
  }, 500);
  
  // Perform action that triggers loading
  await page.click('#load-data');
  
  // Wait for reasonable time
  await page.waitForTimeout(10000);
  clearInterval(checkLoading);
  
  // LOG PRINT START - ANALYSIS
  console.log('[TEST] Analyzing loading states...');
  console.log('[TEST] Total measurements:', loadingStates.length);
  
  const stillLoading = loadingStates[loadingStates.length - 1].loading;
  const loadingDuration = loadingStates.filter(s => s.loading).length * 500;
  
  console.log('[TEST] Final loading state:', stillLoading);
  console.log('[TEST] Total loading duration:', loadingDuration, 'ms');
  
  if (stillLoading && loadingDuration > 5000) {
    console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
    console.log('[BUG_INDICATOR] Loading spinner stuck for over 5 seconds');
    console.log('[BUG_INDICATOR] Expected: Loading completes within 5s');
    console.log('[BUG_INDICATOR] Actual: Still loading after', loadingDuration, 'ms');
    // LOG PRINT END
    return false;
  }
  
  console.log('[TEST] ✅ Loading completed normally');
  return true;
}
```

## Log Analysis Script

```javascript
// analyze_bug_logs.js
const fs = require('fs');

function analyzeBugLogs(logFile) {
  const logs = fs.readFileSync(logFile, 'utf8');
  const lines = logs.split('\n');
  
  // Define bug indicators to search for
  const bugIndicators = {
    'DUAL_TOAST': '[BUG_INDICATOR] Both error and success toasts are visible',
    'MISSING_BUTTON': '[BUG_INDICATOR] Submit button disappeared',
    'API_MISMATCH': '[BUG_INDICATOR] API returned success but UI shows error',
    'INFINITE_LOADING': '[BUG_INDICATOR] Loading spinner stuck'
  };
  
  console.log('🔍 Analyzing logs for bug indicators...\n');
  
  const foundBugs = [];
  
  for (const [bugType, indicator] of Object.entries(bugIndicators)) {
    if (logs.includes(indicator)) {
      foundBugs.push(bugType);
      
      // Find context around the bug
      const bugLine = lines.findIndex(line => line.includes(indicator));
      const context = lines.slice(Math.max(0, bugLine - 3), bugLine + 3);
      
      console.log(`❌ BUG FOUND: ${bugType}`);
      console.log('Context:');
      context.forEach(line => console.log(`  ${line}`));
      console.log('');
    }
  }
  
  if (foundBugs.length === 0) {
    console.log('✅ No bugs detected in logs');
  } else {
    console.log(`\n📊 Summary: ${foundBugs.length} bug(s) found`);
    console.log('Bugs:', foundBugs.join(', '));
  }
  
  return foundBugs;
}

// Usage
if (process.argv[2]) {
  analyzeBugLogs(process.argv[2]);
} else {
  console.log('Usage: node analyze_bug_logs.js <logfile>');
}
```

## Best Practices

1. **Use Specific Log Prefixes**
   - `[BUG_REPRO]` - Bug reproduction metadata
   - `[TEST]` - Test execution steps
   - `[BUG_INDICATOR]` - Definitive bug confirmation
   - `[API_RESPONSE]` - API interaction logs
   - `[BROWSER_CONSOLE]` - Browser console output

2. **Make Bug Detection Binary**
   - Clear pass/fail conditions
   - No ambiguous states
   - Log exact values, not just "failed"

3. **Include Context**
   - What was expected
   - What actually happened
   - Relevant counts/values/timing

4. **Enable Automated Analysis**
   - Consistent log format
   - Searchable indicators
   - Machine-readable output

5. **Capture Everything**
   - Browser console logs
   - Network responses
   - Element states
   - Timing information

This approach ensures bugs are detected deterministically through logs rather than subjective visual interpretation.