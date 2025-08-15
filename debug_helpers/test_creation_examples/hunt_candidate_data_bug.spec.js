import { test, expect } from '@playwright/test';
import fs from 'fs';
import dotenv from 'dotenv';

/*
 MANDATORY TEST FLOW PLAN - WRITE THIS FIRST!

TEST: Hunt Page Candidate Data Display Bug
PURPOSE: Verify that Hunt page shows only minimal candidate data (name only)

FLOW TODO LIST:
[x] Step 1: Navigate to login page
    - Expected: Login form visible
    - Screenshot: debug-step1-navigation.png
    - Selectors needed: email and password fields

[x] Step 2: Login as test recruiter
    - Locate: Email and password fields
    - Action: Fill credentials and submit
    - Screenshot: debug-step2-after-login.png
    - Expected: Redirect to dashboard

[x] Step 3: Navigate to Hunt page
    - Locate: Hunt button
    - Action: Click
    - Screenshot: debug-step3-hunt-page.png
    - Expected: Hunt page loads with candidates

[x] Step 4: Verify candidate data display
    - Check: What candidate data is visible
    - Screenshot: debug-step4-candidate-data.png
    - Success criteria: Identify missing data fields

DATA NEEDED:
- Test user credentials: From .env file
- Mock data: Already created with requisition ID da30bcd5-56bd-4af4-a1d5-cc9333186a93
- Translation keys: From src/locales/he.js
*/

test('Hunt page shows minimal candidate data - BUG REPRODUCTION', async ({ page }) => {
  // Load environment variables
  dotenv.config();
  
  const SESSION_ID = 'HUNT168';
  
  // Test credentials
  const testEmail = process.env.TEST_RECRUITER_EMAIL;
  const testPassword = process.env.TEST_RECRUITER_PASSWORD;
  
  // Load mock data info
  const mockDataInfo = JSON.parse(fs.readFileSync('mock_hunt_test_ids.json', 'utf8'));
  const requisitionId = mockDataInfo.requisition_ids[0];
  
  console.log(`[DEBUG-${SESSION_ID}] Starting bug reproduction test`);
  console.log(`[DEBUG-${SESSION_ID}] Requisition ID: ${requisitionId}`);
  
  // Configure browser
  const browser = await page.context().browser();
  
  // Step 1: Navigate to login page
  console.log(`[DEBUG-${SESSION_ID}] Step 1: Navigate to login`);
  await page.goto('http://localhost:3000/login');
  await page.screenshot({ path: 'debug_artifacts/debug-step1-navigation.png' });
  
  // Step 2: Login
  console.log(`[DEBUG-${SESSION_ID}] Step 2: Logging in as test recruiter`);
  await page.getByRole('textbox', { name: 'כתובת אימייל' }).click();
  await page.getByRole('textbox', { name: 'כתובת אימייל' }).fill(testEmail);
  await page.getByRole('textbox', { name: 'סיסמה' }).fill(testPassword);
  await page.getByRole('button', { name: 'התחבר/י עם אימייל' }).click();
  
  // Wait for navigation
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'debug_artifacts/debug-step2-after-login.png' });
  
  // Step 3: Navigate to Hunt page
  console.log(`[DEBUG-${SESSION_ID}] Step 3: Navigate to Hunt page`);
  await page.getByRole('button', { name: 'ציד' }).click();
  
  // Wait for Hunt page to load
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'debug_artifacts/debug-step3-hunt-page.png' });
  
  // Step 4: Analyze what candidate data is visible
  console.log(`[DEBUG-${SESSION_ID}] Step 4: Checking visible candidate data`);
  
  // Save page HTML for analysis
  const htmlContent = await page.content();
  fs.writeFileSync('debug_artifacts/hunt-page-content.html', htmlContent);
  
  // Check for candidate data elements
  const candidateName = await page.locator('h2').first().textContent();
  console.log(`[DEBUG-${SESSION_ID}] Candidate name visible: ${candidateName}`);
  
  // Check for other data fields
  const dataChecks = {
    email: await page.locator('text=@').count() > 0,
    skills: await page.getByText(/React|Node\.js|TypeScript/).count() > 0,
    education: await page.getByText(/B\.Sc\.|Computer Science|University/).count() > 0,
    experience: await page.getByText(/years|Senior|Developer/).count() > 0,
    location: await page.getByText(/Tel Aviv|Herzliya|Israel/).count() > 0,
    linkedin: await page.locator('a[href*="linkedin.com"]').count() > 0
  };
  
    // Count how many fields are missing
  const missingFields = Object.values(dataChecks).filter(v => !v).length;
  
  if (missingFields >= 4) {
    console.log(`[BUG_INDICATOR] *** BUG REPRODUCED ***`);
    console.log(`[DEBUG-${SESSION_ID}]  Hunt page shows minimal data - only ${Object.values(dataChecks).filter(v => v).length} of 6 fields visible`);
  } else {
    console.log(`[DEBUG-${SESSION_ID}]  Hunt page shows ${Object.values(dataChecks).filter(v => v).length} of 6 data fields`);
  }
  
  // Take final screenshot showing the issue
  await page.screenshot({ path: 'debug_artifacts/debug-step4-candidate-data.png', fullPage: true });
  
  // Additional check: Look for specific UI elements
  const matchScore = await page.locator('.text-2xl.font-bold.text-purple-700').textContent();
  console.log(`[DEBUG-${SESSION_ID}] Match score visible: ${matchScore || 'NOT FOUND'}`);
  
  const skillBadges = await page.locator('.badge').count();
  console.log(`[DEBUG-${SESSION_ID}] Skill badges found: ${skillBadges}`);
  
  // Close browser
  await browser.close();
});