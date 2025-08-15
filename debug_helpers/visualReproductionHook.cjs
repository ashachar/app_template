/**
 * Visual Bug Reproduction Hook - JavaScript version
 * Enforces visual proof before debugging can proceed
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class VisualReproductionHook {
  constructor() {
    this.evidenceDir = path.join(__dirname, '..', 'bug_evidence');
    if (!fs.existsSync(this.evidenceDir)) {
      fs.mkdirSync(this.evidenceDir, { recursive: true });
    }
  }

  /**
   * Check if visual proof exists for this debugging session
   * @param {string} sessionId - Debug session ID
   * @returns {boolean} True if visual proof exists
   */
  checkVisualProofExists(sessionId) {
    const evidenceFile = path.join(this.evidenceDir, `${sessionId}_evidence.json`);
    
    if (!fs.existsSync(evidenceFile)) {
      return false;
    }
    
    try {
      const evidence = JSON.parse(fs.readFileSync(evidenceFile, 'utf8'));
      
      // Verify required fields
      const required = ['screenshot_path', 'bug_confirmed', 'visual_test_path', 'test_failed'];
      for (const field of required) {
        if (!(field in evidence)) {
          return false;
        }
      }
      
      // Verify screenshot exists
      if (!fs.existsSync(evidence.screenshot_path)) {
        console.log('❌ Screenshot file not found:', evidence.screenshot_path);
        return false;
      }
      
      // Verify test failed (bug exists)
      if (!evidence.test_failed) {
        console.log('⚠️ WARNING: Visual test passed - bug may not exist!');
        return false;
      }
      
      return true;
      
    } catch (error) {
      console.error('❌ Error reading evidence:', error);
      return false;
    }
  }

  /**
   * Enforce visual reproduction before allowing debugging to proceed
   * @param {string} bugDescription - User's description of the bug
   * @param {string} sessionId - Current debug session ID
   * @throws {Error} If visual proof doesn't exist
   */
  enforceVisualReproduction(bugDescription, sessionId) {
    console.log('='.repeat(80));
    console.log('🔴 MANDATORY VISUAL BUG REPRODUCTION CHECK');
    console.log('='.repeat(80));
    
    if (this.checkVisualProofExists(sessionId)) {
      console.log('✅ Visual proof found for this session');
      this.displayEvidence(sessionId);
      return true;
    }
    
    console.log('\n❌ NO VISUAL PROOF FOUND!');
    console.log('\nYou MUST complete these steps before proceeding:\n');
    console.log('1. Create a test script that reproduces the bug visually');
    console.log('2. Take a screenshot showing the bug');
    console.log('3. Create a visual verification test that FAILS');
    console.log('4. Save the evidence using recordVisualProof()');
    
    console.log('\n📝 Example script to create:');
    this.printExampleScript(bugDescription);
    
    console.log('\n🛑 DEBUGGING BLOCKED until visual proof is provided!');
    console.log('='.repeat(80));
    
    // Block execution
    throw new Error(
      'Cannot proceed without visual proof of bug. ' +
      'Run visual reproduction script first!'
    );
  }

  /**
   * Record visual proof of bug for the debugging session
   * @param {Object} params - Evidence parameters
   */
  recordVisualProof(params) {
    const {
      sessionId,
      screenshotPath,
      visualTestPath,
      testResult,
      bugDescription,
      expectedBehavior,
      actualBehavior,
      visualElements = {}
    } = params;
    
    const evidence = {
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      screenshot_path: screenshotPath,
      visual_test_path: visualTestPath,
      test_failed: !testResult,  // Test should fail if bug exists
      bug_confirmed: !testResult,
      bug_description: bugDescription,
      expected_behavior: expectedBehavior,
      actual_behavior: actualBehavior,
      visual_elements: visualElements
    };
    
    const evidenceFile = path.join(this.evidenceDir, `${sessionId}_evidence.json`);
    fs.writeFileSync(evidenceFile, JSON.stringify(evidence, null, 2));
    
    console.log(`\n✅ Visual proof recorded: ${evidenceFile}`);
    
    if (!testResult) {
      console.log('✅ Bug confirmed - visual test failed as expected');
    } else {
      console.log('⚠️ WARNING: Visual test passed - are you sure the bug exists?');
    }
    
    // Open screenshot for verification
    try {
      execSync(`open "${screenshotPath}"`);
      console.log('📸 Screenshot opened for verification');
    } catch (e) {
      console.log('📸 Please manually verify screenshot:', screenshotPath);
    }
  }

  /**
   * Display existing evidence for the session
   * @param {string} sessionId - Debug session ID
   */
  displayEvidence(sessionId) {
    const evidenceFile = path.join(this.evidenceDir, `${sessionId}_evidence.json`);
    const evidence = JSON.parse(fs.readFileSync(evidenceFile, 'utf8'));
    
    console.log('\n📸 Visual Evidence Summary:');
    console.log(`  Screenshot: ${evidence.screenshot_path}`);
    console.log(`  Visual Test: ${evidence.visual_test_path}`);
    console.log(`  Bug Confirmed: ${evidence.bug_confirmed ? 'YES' : 'NO'}`);
    console.log(`  Description: ${evidence.bug_description}`);
    console.log(`  Expected: ${evidence.expected_behavior}`);
    console.log(`  Actual: ${evidence.actual_behavior}`);
    
    if (evidence.visual_elements) {
      console.log('\n🔍 Visual Elements Detected:');
      Object.entries(evidence.visual_elements).forEach(([key, value]) => {
        console.log(`  ${key}: ${value}`);
      });
    }
  }

  /**
   * Print example visual reproduction script
   * @param {string} bugDescription - Bug description
   */
  printExampleScript(bugDescription) {
    console.log(`
// visual_bug_reproduction.cjs
const { chromium } = require('playwright');
const fs = require('fs');
const { VisualReproductionHook } = require('./debug_helpers/visualReproductionHook.cjs');

async function reproduceAndVerifyBug() {
  const hook = new VisualReproductionHook();
  const sessionId = 'DEBUG-' + Date.now();
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // 1. Navigate to the problem area
    await page.goto('http://localhost:3000/path/to/bug');
    
    // 2. Reproduce the bug
    await page.click('button#trigger-bug');
    await page.waitForTimeout(2000);
    
    // 3. Take screenshot
    const screenshot = \`bug_evidence/BUG_VISIBLE_\${Date.now()}.png\`;
    await page.screenshot({ path: screenshot, fullPage: true });
    console.log(\`📸 Bug screenshot saved: \${screenshot}\`);
    
    // 4. Visual verification test
    const testResult = await verifyBugVisually(page);
    
    if (testResult) {
      throw new Error('Bug not reproduced! Test must fail initially!');
    }
    
    // 5. Record the evidence
    hook.recordVisualProof({
      sessionId: sessionId,
      screenshotPath: screenshot,
      visualTestPath: __filename,
      testResult: testResult,  // Should be false (test failed = bug exists)
      bugDescription: '${bugDescription}',
      expectedBehavior: 'No error should appear',
      actualBehavior: 'Error toast appears',
      visualElements: {
        errorToastVisible: true,
        errorMessage: await page.locator('.error-toast').textContent()
      }
    });
    
    console.log('✅ Bug reproduced and evidence recorded!');
    console.log(\`📝 Session ID: \${sessionId}\`);
    console.log('You can now proceed with debugging using this session ID.');
    
  } finally {
    await browser.close();
  }
}

async function verifyBugVisually(page) {
  // This function should return false if bug exists (test fails)
  // Return true if bug is fixed (test passes)
  
  // Example: Check for error toast
  const errorToast = await page.locator('.error-toast').count();
  if (errorToast > 0) {
    console.log('❌ Bug detected: Error toast is visible');
    return false;  // Test fails = bug exists
  }
  
  return true;  // Test passes = bug is fixed
}

reproduceAndVerifyBug().catch(console.error);
`);
  }

  /**
   * Create a visual assertion helper
   * @param {Object} page - Playwright page object
   * @returns {Object} Visual assertion methods
   */
  createVisualAssertions(page) {
    return {
      // Check if element with specific text exists
      async assertTextNotVisible(text, selector = 'body') {
        const element = page.locator(selector);
        const content = await element.textContent();
        if (content && content.includes(text)) {
          throw new Error(`Unexpected text found: "${text}"`);
        }
      },
      
      // Check if element exists
      async assertElementNotVisible(selector) {
        const count = await page.locator(selector).count();
        if (count > 0) {
          throw new Error(`Unexpected element found: ${selector}`);
        }
      },
      
      // Check color presence (requires screenshot analysis)
      async assertNoErrorColors(screenshotPath) {
        // This would integrate with visual_bug_detector.py
        console.log('Color analysis would be performed on:', screenshotPath);
      },
      
      // Compare with expected screenshot
      async assertScreenshotMatches(expectedPath, actualPath, threshold = 0.95) {
        // This would integrate with visual comparison
        console.log(`Comparing ${actualPath} with ${expectedPath}`);
      }
    };
  }
}

// Export for use in tests
module.exports = { VisualReproductionHook };

// Example: Enforce visual proof from command line
if (require.main === module) {
  const hook = new VisualReproductionHook();
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('Usage: node visualReproductionHook.cjs <bug-description> <session-id>');
    process.exit(1);
  }
  
  try {
    hook.enforceVisualReproduction(args[0], args[1]);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}