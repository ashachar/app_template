# Test Creation Examples

This directory contains proven examples of how to create integration tests from user reference tests.

## Hunt Page Bug Example

This example shows how we successfully created an integration test from a simple user test.

### User's Reference Test (Unit Test)
File: `tests/unit/ui/hunt_candidates.spec.ts`
```typescript
import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.getByRole('textbox', { name: 'כתובת אימייל' }).click();
  await page.getByRole('textbox', { name: 'כתובת אימייל' }).fill('amir.shachar.auto@gmail.com');
  await page.getByRole('textbox', { name: 'כתובת אימייל' }).press('Tab');
  await page.getByRole('link', { name: 'שכחת סיסמה?' }).press('Tab');
  await page.getByRole('textbox', { name: 'סיסמה' }).fill('Swifit2025');
  await page.getByRole('textbox', { name: 'סיסמה' }).press('Enter');
  await page.getByRole('button', { name: 'התחבר/י עם אימייל' }).click();
  await page.getByRole('button', { name: 'ציד' }).click();
});
```

### Final Integration Test Created
File: `tests/integration/hunt_candidate_data_bug.spec.js`

Key differences and improvements:
1. **ES Module syntax** - Required for the app's module system
2. **Proper file location** - In tests/integration/ directory
3. **Mock data setup** - Loads created mock data IDs
4. **Bug verification logic** - Checks what data is visible
5. **Diagnostic output** - Logs to confirm bug reproduction
6. **Screenshots** - Captures evidence at each step

## Lessons Learned

1. **File Location Matters**: Playwright only finds tests in the configured testDir (./tests)
2. **ES Modules Required**: The app uses "type": "module" so we must use import syntax
3. **Extension Must Be .spec.js**: Playwright filters for this pattern
4. **Environment Variables**: Use dotenv.config() to load test credentials
5. **Mock Data Reference**: Save mock IDs to JSON and load in test

## Quick Start Template

```javascript
import { test, expect } from '@playwright/test';
import fs from 'fs';
import dotenv from 'dotenv';

test('Your bug description - BUG REPRODUCTION', async ({ page }) => {
  // Load environment variables
  dotenv.config();
  
  const SESSION_ID = 'YOUR_SESSION_ID';
  
  // Test credentials
  const testEmail = process.env.TEST_RECRUITER_EMAIL;
  const testPassword = process.env.TEST_RECRUITER_PASSWORD;
  
  // Load mock data if created
  const mockDataInfo = JSON.parse(fs.readFileSync('mock_data_ids.json', 'utf8'));
  
  // Your test steps here...
  
  // Bug verification
  if (bugConditionMet) {
    console.log('[BUG_INDICATOR] *** BUG REPRODUCED ***');
  }
});
```

Save this template and modify as needed for your specific bug reproduction needs!