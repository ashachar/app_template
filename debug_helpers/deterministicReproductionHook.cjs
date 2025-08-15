/**
 * Deterministic Bug Reproduction Hook
 * Enforces log-based proof before debugging can proceed
 */

const fs = require('fs');
const path = require('path');

class DeterministicReproductionHook {
  constructor() {
    this.evidenceDir = path.join(__dirname, '..', 'bug_evidence');
    this.logsDir = path.join(__dirname, '..', 'bug_logs');
    
    // Create directories if they don't exist
    [this.evidenceDir, this.logsDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * Check if deterministic proof exists for this debugging session
   * @param {string} sessionId - Debug session ID
   * @returns {Object} Proof status and details
   */
  checkDeterministicProof(sessionId) {
    const evidenceFile = path.join(this.evidenceDir, `${sessionId}_evidence.json`);
    const logFile = path.join(this.logsDir, `${sessionId}_reproduction.log`);
    
    if (!fs.existsSync(evidenceFile) || !fs.existsSync(logFile)) {
      return { exists: false, reason: 'Missing evidence or log file' };
    }
    
    try {
      const evidence = JSON.parse(fs.readFileSync(evidenceFile, 'utf8'));
      const logs = fs.readFileSync(logFile, 'utf8');
      
      // Verify required fields
      const required = ['bugIndicators', 'testFailed', 'logFile'];
      for (const field of required) {
        if (!(field in evidence)) {
          return { exists: false, reason: `Missing field: ${field}` };
        }
      }
      
      // Verify test failed (bug exists)
      if (!evidence.testFailed) {
        return { exists: false, reason: 'Test passed - bug not reproduced' };
      }
      
      // Verify bug indicators are in logs
      const missingIndicators = [];
      for (const indicator of evidence.bugIndicators) {
        if (!logs.includes(indicator)) {
          missingIndicators.push(indicator);
        }
      }
      
      if (missingIndicators.length > 0) {
        return { 
          exists: false, 
          reason: 'Bug indicators not found in logs',
          missing: missingIndicators
        };
      }
      
      return { 
        exists: true, 
        evidence,
        logFile,
        indicators: evidence.bugIndicators
      };
      
    } catch (error) {
      return { exists: false, reason: `Error reading evidence: ${error.message}` };
    }
  }

  /**
   * Enforce deterministic reproduction before allowing debugging to proceed
   * @param {string} bugDescription - User's description of the bug
   * @param {string} sessionId - Current debug session ID
   * @throws {Error} If deterministic proof doesn't exist
   */
  enforceDeterministicReproduction(bugDescription, sessionId) {
    console.log('='.repeat(80));
    console.log('🔴 MANDATORY DETERMINISTIC BUG REPRODUCTION CHECK');
    console.log('='.repeat(80));
    
    const proof = this.checkDeterministicProof(sessionId);
    
    if (proof.exists) {
      console.log('✅ Deterministic proof found for this session');
      this.displayEvidence(proof);
      return true;
    }
    
    console.log('\n❌ NO DETERMINISTIC PROOF FOUND!');
    if (proof.reason) {
      console.log(`Reason: ${proof.reason}`);
    }
    if (proof.missing) {
      console.log('Missing indicators:', proof.missing);
    }
    
    console.log('\nYou MUST complete these steps before proceeding:\n');
    console.log('1. Create a test script that reproduces the bug');
    console.log('2. Add log prints with [BUG_INDICATOR] markers');
    console.log('3. Run the test and capture logs');
    console.log('4. Verify logs contain bug indicators');
    console.log('5. Save evidence using recordDeterministicProof()');
    
    console.log('\n📝 Example script to create:');
    this.printExampleScript(bugDescription);
    
    console.log('\n🛑 DEBUGGING BLOCKED until deterministic proof is provided!');
    console.log('='.repeat(80));
    
    // Block execution
    throw new Error(
      'Cannot proceed without deterministic proof of bug. ' +
      'Run bug reproduction script and capture logs first!'
    );
  }

  /**
   * Record deterministic proof of bug
   * @param {Object} params - Evidence parameters
   */
  recordDeterministicProof(params) {
    const {
      sessionId,
      bugIndicators,
      logFile,
      testResult,
      bugDescription,
      expectedBehavior,
      actualBehavior,
      additionalData = {}
    } = params;
    
    // Read the log file to verify indicators
    const logs = fs.readFileSync(logFile, 'utf8');
    
    // Verify all indicators are present
    const foundIndicators = [];
    const missingIndicators = [];
    
    for (const indicator of bugIndicators) {
      if (logs.includes(indicator)) {
        foundIndicators.push(indicator);
      } else {
        missingIndicators.push(indicator);
      }
    }
    
    if (missingIndicators.length > 0) {
      console.log('⚠️ WARNING: Some indicators not found in logs:', missingIndicators);
    }
    
    // Copy log file to evidence directory
    const evidenceLogFile = path.join(this.logsDir, `${sessionId}_reproduction.log`);
    fs.copyFileSync(logFile, evidenceLogFile);
    
    const evidence = {
      sessionId,
      timestamp: new Date().toISOString(),
      bugIndicators,
      foundIndicators,
      logFile: evidenceLogFile,
      testFailed: !testResult,  // Test should fail if bug exists
      bugConfirmed: !testResult && foundIndicators.length > 0,
      bugDescription,
      expectedBehavior,
      actualBehavior,
      ...additionalData
    };
    
    const evidenceFile = path.join(this.evidenceDir, `${sessionId}_evidence.json`);
    fs.writeFileSync(evidenceFile, JSON.stringify(evidence, null, 2));
    
    console.log(`\n✅ Deterministic proof recorded: ${evidenceFile}`);
    console.log(`📋 Log file saved: ${evidenceLogFile}`);
    
    if (evidence.bugConfirmed) {
      console.log('✅ Bug confirmed - all indicators found in logs');
      console.log('Found indicators:');
      foundIndicators.forEach(ind => console.log(`  - ${ind}`));
    } else {
      console.log('⚠️ WARNING: Bug not fully confirmed');
    }
  }

  /**
   * Display existing evidence
   * @param {Object} proof - Proof object from checkDeterministicProof
   */
  displayEvidence(proof) {
    console.log('\n📋 Deterministic Evidence Summary:');
    console.log(`  Log file: ${proof.logFile}`);
    console.log(`  Bug confirmed: ${proof.evidence.bugConfirmed ? 'YES' : 'NO'}`);
    console.log(`  Description: ${proof.evidence.bugDescription}`);
    console.log(`  Expected: ${proof.evidence.expectedBehavior}`);
    console.log(`  Actual: ${proof.evidence.actualBehavior}`);
    
    console.log('\n🔍 Bug Indicators Found:');
    proof.evidence.foundIndicators.forEach(indicator => {
      console.log(`  ✅ ${indicator}`);
    });
  }

  /**
   * Print example deterministic test script
   * @param {string} bugDescription - Bug description
   */
  printExampleScript(bugDescription) {
    console.log(`
// test_bug_deterministic.cjs
const { chromium } = require('playwright');
const fs = require('fs');
const { DeterministicReproductionHook } = require('./debug_helpers/deterministicReproductionHook.cjs');

async function reproduceBugDeterministically() {
  const hook = new DeterministicReproductionHook();
  const sessionId = 'BUG-' + Date.now();
  
  // LOG PRINT START - BUG REPRODUCTION
  console.log('[BUG_REPRO] Starting bug reproduction for: ${bugDescription}');
  console.log('[BUG_REPRO] Session ID:', sessionId);
  console.log('[BUG_REPRO] Timestamp:', new Date().toISOString());
  // LOG PRINT END
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture browser console
  page.on('console', msg => {
    // LOG PRINT START - BROWSER CONSOLE
    console.log(\`[BROWSER_CONSOLE] \${msg.type()}: \${msg.text()}\`);
    // LOG PRINT END
  });
  
  try {
    // Navigate and reproduce bug
    await page.goto('http://localhost:3000/path/to/bug');
    await page.click('button#trigger-bug');
    await page.waitForTimeout(2000);
    
    // LOG PRINT START - TEST VERIFICATION
    console.log('[TEST] Starting bug verification...');
    
    // Check for bug condition (example: dual toasts)
    const errorCount = await page.locator('.error-toast').count();
    const successCount = await page.locator('.success-toast').count();
    
    console.log('[TEST] Toast counts - Errors:', errorCount, 'Success:', successCount);
    
    if (errorCount > 0 && successCount > 0) {
      console.log('[BUG_INDICATOR] *** BUG CONFIRMED ***');
      console.log('[BUG_INDICATOR] Both error and success toasts visible');
      console.log('[BUG_INDICATOR] Expected: Only one toast type');
      // LOG PRINT END
      
      return false; // Test fails = bug exists
    }
    
    console.log('[TEST] ✅ Bug not found');
    return true;
    
  } finally {
    await browser.close();
  }
}

// Run test and save logs
const { spawn } = require('child_process');
const logFile = \`bug_logs/\${Date.now()}_reproduction.log\`;

const proc = spawn('node', [__filename], { 
  stdio: ['inherit', 'pipe', 'pipe'] 
});

let output = '';
proc.stdout.on('data', data => {
  output += data;
  process.stdout.write(data);
});
proc.stderr.on('data', data => {
  output += data;
  process.stderr.write(data);
});

proc.on('close', code => {
  // Save logs
  fs.writeFileSync(logFile, output);
  
  // Record evidence if bug was found
  if (code !== 0) {
    const hook = new DeterministicReproductionHook();
    hook.recordDeterministicProof({
      sessionId: 'BUG-' + Date.now(),
      bugIndicators: [
        '[BUG_INDICATOR] *** BUG CONFIRMED ***',
        '[BUG_INDICATOR] Both error and success toasts visible'
      ],
      logFile: logFile,
      testResult: false,
      bugDescription: '${bugDescription}',
      expectedBehavior: 'Only one toast type should appear',
      actualBehavior: 'Both error and success toasts appear'
    });
  }
});
`);
  }

  /**
   * Analyze logs for bug patterns
   * @param {string} logFile - Path to log file
   * @returns {Object} Analysis results
   */
  analyzeLogs(logFile) {
    const logs = fs.readFileSync(logFile, 'utf8');
    const lines = logs.split('\n');
    
    const analysis = {
      bugIndicators: [],
      testResults: [],
      errors: [],
      warnings: [],
      apiCalls: [],
      browserConsole: []
    };
    
    lines.forEach(line => {
      if (line.includes('[BUG_INDICATOR]')) {
        analysis.bugIndicators.push(line);
      }
      if (line.includes('[TEST]')) {
        analysis.testResults.push(line);
      }
      if (line.includes('[ERROR]') || line.includes('Error:')) {
        analysis.errors.push(line);
      }
      if (line.includes('[WARNING]') || line.includes('[WARN]')) {
        analysis.warnings.push(line);
      }
      if (line.includes('[API_RESPONSE]')) {
        analysis.apiCalls.push(line);
      }
      if (line.includes('[BROWSER_CONSOLE]')) {
        analysis.browserConsole.push(line);
      }
    });
    
    return analysis;
  }
}

// Export for use in tests
module.exports = { DeterministicReproductionHook };

// Example: Enforce deterministic proof from command line
if (require.main === module) {
  const hook = new DeterministicReproductionHook();
  const args = process.argv.slice(2);
  
  if (args[0] === 'analyze' && args[1]) {
    const analysis = hook.analyzeLogs(args[1]);
    console.log('\n📊 Log Analysis Results:');
    console.log('Bug Indicators:', analysis.bugIndicators.length);
    console.log('Test Results:', analysis.testResults.length);
    console.log('Errors:', analysis.errors.length);
    console.log('API Calls:', analysis.apiCalls.length);
    
    if (analysis.bugIndicators.length > 0) {
      console.log('\n🐛 Bug Indicators Found:');
      analysis.bugIndicators.forEach(ind => console.log(ind));
    }
  } else if (args.length < 2) {
    console.log('Usage:');
    console.log('  node deterministicReproductionHook.cjs <bug-description> <session-id>');
    console.log('  node deterministicReproductionHook.cjs analyze <log-file>');
    process.exit(1);
  } else {
    try {
      hook.enforceDeterministicReproduction(args[0], args[1]);
    } catch (error) {
      console.error(error.message);
      process.exit(1);
    }
  }
}