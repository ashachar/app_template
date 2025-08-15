# Visual Bug Detection Examples

This document provides practical examples of how to use visual bug detection for common UI issues.

## Example 1: Error Toast Detection

**Bug Description**: "An error toast appears when saving a job, but the save is actually successful"

```javascript
// test_error_toast_bug.cjs
const { chromium } = require('playwright');
const { VisualReproductionHook } = require('./debug_helpers/visualReproductionHook.cjs');

async function testErrorToastBug() {
  const hook = new VisualReproductionHook();
  const sessionId = `ERROR-TOAST-${Date.now()}`;
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate and login
    await page.goto('http://localhost:3000/recruiter/jobs');
    // ... perform login ...
    
    // Reproduce the bug
    await page.click('button:has-text("Save")');
    await page.waitForTimeout(2000); // Wait for toast to appear
    
    // Take screenshot
    const screenshot = `bug_evidence/error_toast_${Date.now()}.png`;
    await page.screenshot({ path: screenshot, fullPage: true });
    
    // Visual verification
    const errorToastVisible = await page.locator('.destructive, [class*="error"]').count() > 0;
    const successToastVisible = await page.locator('[class*="success"]').count() > 0;
    
    // Bug exists if BOTH toasts appear
    const bugExists = errorToastVisible && successToastVisible;
    
    // Record evidence
    hook.recordVisualProof({
      sessionId,
      screenshotPath: screenshot,
      visualTestPath: __filename,
      testResult: !bugExists,  // false = bug exists
      bugDescription: 'Error toast appears alongside success toast',
      expectedBehavior: 'Only success toast should appear',
      actualBehavior: 'Both error and success toasts appear',
      visualElements: {
        errorToastCount: await page.locator('.destructive').count(),
        successToastCount: await page.locator('[class*="success"]').count(),
        errorMessage: errorToastVisible ? await page.locator('.destructive').textContent() : 'N/A'
      }
    });
    
    return !bugExists; // Return false if bug exists
    
  } finally {
    await browser.close();
  }
}
```

## Example 2: Missing UI Element

**Bug Description**: "The submit button disappears after form validation"

```javascript
async function testMissingButtonBug() {
  const hook = new VisualReproductionHook();
  const sessionId = `MISSING-BUTTON-${Date.now()}`;
  
  // ... browser setup ...
  
  // Fill form with invalid data to trigger validation
  await page.fill('#email', 'invalid-email');
  await page.click('#validate');
  await page.waitForTimeout(1000);
  
  // Take screenshot
  const screenshot = `bug_evidence/missing_button_${Date.now()}.png`;
  await page.screenshot({ path: screenshot, fullPage: true });
  
  // Check if button is missing
  const submitButtonVisible = await page.locator('button[type="submit"]').isVisible();
  const bugExists = !submitButtonVisible;
  
  hook.recordVisualProof({
    sessionId,
    screenshotPath: screenshot,
    visualTestPath: __filename,
    testResult: !bugExists,
    bugDescription: 'Submit button disappears after validation',
    expectedBehavior: 'Submit button should remain visible',
    actualBehavior: 'Submit button is not visible after validation',
    visualElements: {
      submitButtonVisible,
      validationErrorsCount: await page.locator('.field-error').count()
    }
  });
}
```

## Example 3: Layout/Styling Issues

**Bug Description**: "The sidebar overlaps the main content on certain screen sizes"

```javascript
async function testLayoutBug() {
  const hook = new VisualReproductionHook();
  const sessionId = `LAYOUT-BUG-${Date.now()}`;
  
  // Set specific viewport size where bug occurs
  await page.setViewportSize({ width: 1024, height: 768 });
  
  // Navigate to affected page
  await page.goto('http://localhost:3000/dashboard');
  
  // Take screenshot
  const screenshot = `bug_evidence/layout_overlap_${Date.now()}.png`;
  await page.screenshot({ path: screenshot, fullPage: true });
  
  // Check for overlap using bounding boxes
  const sidebar = await page.locator('.sidebar').boundingBox();
  const mainContent = await page.locator('.main-content').boundingBox();
  
  const hasOverlap = sidebar && mainContent && 
    (sidebar.x + sidebar.width > mainContent.x);
  
  hook.recordVisualProof({
    sessionId,
    screenshotPath: screenshot,
    visualTestPath: __filename,
    testResult: !hasOverlap,
    bugDescription: 'Sidebar overlaps main content',
    expectedBehavior: 'Sidebar and main content should not overlap',
    actualBehavior: 'Sidebar overlaps main content by ' + 
      (hasOverlap ? (sidebar.x + sidebar.width - mainContent.x) + 'px' : '0px'),
    visualElements: {
      sidebarPosition: sidebar,
      mainContentPosition: mainContent,
      overlapAmount: hasOverlap ? sidebar.x + sidebar.width - mainContent.x : 0
    }
  });
}
```

## Example 4: Text/Content Issues

**Bug Description**: "Wrong error message appears in validation"

```javascript
async function testWrongErrorMessage() {
  // Use Python integration for advanced text extraction
  const { execSync } = require('child_process');
  
  // Take screenshot first
  const screenshot = `bug_evidence/wrong_message_${Date.now()}.png`;
  await page.screenshot({ path: screenshot, fullPage: true });
  
  // Use OCR to extract text from error region
  const extractedText = execSync(
    `python -c "
from debug_helpers.visual_bug_detector import VisualBugDetector
detector = VisualBugDetector()
text = detector.extract_text_from_region('${screenshot}', (100, 200, 500, 300))
print(text)
"`
  ).toString().trim();
  
  const bugExists = extractedText.includes('Undefined error');
  
  hook.recordVisualProof({
    sessionId,
    screenshotPath: screenshot,
    visualTestPath: __filename,
    testResult: !bugExists,
    bugDescription: 'Generic error message instead of specific validation error',
    expectedBehavior: 'Should show "Email format is invalid"',
    actualBehavior: `Shows "${extractedText}"`,
    visualElements: {
      extractedErrorText: extractedText,
      expectedText: 'Email format is invalid'
    }
  });
}
```

## Example 5: Color/Theme Issues

**Bug Description**: "Dark mode shows light-colored text on light background"

```javascript
async function testDarkModeContrast() {
  // Enable dark mode
  await page.click('#theme-toggle');
  await page.waitForTimeout(500);
  
  const screenshot = `bug_evidence/dark_mode_contrast_${Date.now()}.png`;
  await page.screenshot({ path: screenshot, fullPage: true });
  
  // Use Python for color analysis
  const colorAnalysis = execSync(
    `python -c "
from debug_helpers.visual_bug_detector import VisualBugDetector
detector = VisualBugDetector()
# Count light pixels in text area
light_pixels = detector.count_color_pixels('${screenshot}', {
    'red': (200, 255),
    'green': (200, 255),
    'blue': (200, 255)
})
print(light_pixels)
"`
  ).toString().trim();
  
  const tooManyLightPixels = parseInt(colorAnalysis) > 10000;
  
  hook.recordVisualProof({
    sessionId,
    screenshotPath: screenshot,
    visualTestPath: __filename,
    testResult: !tooManyLightPixels,
    bugDescription: 'Poor contrast in dark mode',
    expectedBehavior: 'Dark background with light text',
    actualBehavior: 'Light text on light background',
    visualElements: {
      lightPixelCount: colorAnalysis,
      thresholdExceeded: tooManyLightPixels
    }
  });
}
```

## Integration with Debug Workflow

Once visual proof is recorded, the main debug workflow can proceed:

```javascript
// In your main debug script
const { VisualReproductionHook } = require('./debug_helpers/visualReproductionHook.cjs');

async function debugBug(bugDescription, sessionId) {
  const hook = new VisualReproductionHook();
  
  // This will throw if visual proof doesn't exist
  try {
    hook.enforceVisualReproduction(bugDescription, sessionId);
  } catch (error) {
    console.error('❌ Must create visual proof first!');
    // Run the appropriate visual test from examples above
    return;
  }
  
  // If we get here, visual proof exists
  console.log('✅ Visual proof verified, proceeding with debug...');
  
  // Now you can:
  // 1. Read the code
  // 2. Analyze the issue
  // 3. Implement fixes
  // 4. Re-run the visual test to verify the fix
}
```

## Best Practices

1. **Always capture the bug state first** - Don't try to understand why, just prove it exists
2. **Make tests specific** - Check for the exact visual issue reported
3. **Use appropriate verification method**:
   - Text content: Use Playwright selectors
   - Visual layout: Use bounding boxes
   - Colors/images: Use Python CV integration
   - Complex patterns: Use template matching
4. **Record comprehensive evidence** - Include all relevant visual elements
5. **Test must fail initially** - If it passes, you haven't reproduced the bug