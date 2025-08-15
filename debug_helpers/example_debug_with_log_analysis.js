#!/usr/bin/env node
/**
 * Example: Using Automated Log Analysis in Debug Scripts
 * This shows how to integrate the log analyzer with Playwright tests
 */

const { chromium } = require('playwright');
const { LogAnalyzer, withLogAnalysis } = require('./log_analyzer.cjs');
const path = require('path');
require('dotenv').config();

async function debugWithAutomatedAnalysis() {
  console.log(' Starting debug session with automated log analysis...\n');
  
  // Create log analyzer instance
  const analyzer = new LogAnalyzer();
  
  // First, analyze existing server logs
  console.log(' Analyzing server logs...');
  const serverAnalysis = await analyzer.analyzeServerLogs(
    path.join(__dirname, '..', 'consolidated_logs', 'latest.log')
  );
  
  if (serverAnalysis.error) {
    console.log(`  ${serverAnalysis.error}`);
  } else {
    console.log(` Analyzed ${serverAnalysis.analyzed} lines, found ${serverAnalysis.findings} issues`);
  }
  
  // Now run browser test with real-time analysis
  console.log('\n Starting browser test with real-time log monitoring...');
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox']
  });
  
  const context = await browser.newContext({
    locale: 'he',
    ignoreHTTPSErrors: true,
    recordVideo: {
      dir: path.join(__dirname, '..', 'tests', 'integration', 'videos')
    }
  });
  
  // Attach analyzer to capture browser logs
  analyzer.attachToContext(context);
  
  const page = await context.newPage();
  
  try {
    // Example: Navigate to a page that might have errors
    console.log('\n Navigating to recruiter dashboard...');
    
    // Track performance
    const startTime = Date.now();
    
    await page.goto('http://localhost:5173/recruiter/dashboard');
    
    const loadTime = Date.now() - startTime;
    analyzer.trackPerformance('pageLoadTime', loadTime);
    console.log(` Page loaded in ${loadTime}ms`);
    
    // Wait for potential API calls
    console.log('\n Waiting for API responses...');
    
    try {
      const apiResponse = await page.waitForResponse(
        response => response.url().includes('/api/') && response.status() !== 304,
        { timeout: 5000 }
      );
      
      const responseTime = Date.now() - startTime;
      analyzer.trackPerformance('apiResponseTime', responseTime);
      
      console.log(` API response received: ${apiResponse.status()} in ${responseTime}ms`);
      
      if (!apiResponse.ok()) {
        console.log(`  API error: ${apiResponse.status()} ${apiResponse.statusText()}`);
      }
    } catch (e) {
      console.log('  No API calls detected or timeout reached');
    }
    
    // Check for specific elements
    console.log('\n Checking page elements...');
    
    const checks = [
      { selector: '[data-testid="requisitions-list"]', name: 'Requisitions List' },
      { selector: '[data-testid="create-requisition-btn"]', name: 'Create Button' },
      { selector: '.error-message', name: 'Error Messages', expectMissing: true }
    ];
    
    for (const check of checks) {
      try {
        if (check.expectMissing) {
          await page.waitForSelector(check.selector, { state: 'hidden', timeout: 1000 });
          console.log(` ${check.name}: Not present (as expected)`);
        } else {
          await page.waitForSelector(check.selector, { timeout: 3000 });
          console.log(` ${check.name}: Found`);
        }
      } catch (e) {
        console.log(` ${check.name}: ${check.expectMissing ? 'Present (unexpected)' : 'Not found'}`);
      }
    }
    
    // Take screenshot for evidence
    await page.screenshot({ 
      path: path.join(__dirname, 'debug_screenshot.png'),
      fullPage: true 
    });
    console.log('\n Screenshot saved: debug_screenshot.png');
    
  } catch (error) {
    console.error('\n Test error:', error.message);
  } finally {
    await context.close();
    await browser.close();
  }
  
  // Generate analysis report
  console.log('\n' + '='.repeat(80));
  console.log(' AUTOMATED LOG ANALYSIS RESULTS');
  console.log('='.repeat(80));
  
  const summary = analyzer.getSummary();
  
  if (summary.totalFindings === 0) {
    console.log('\n Great! No issues detected in logs.\n');
  } else {
    console.log(`\n Total Issues Found: ${summary.totalFindings}`);
    
    // Show breakdown by category
    console.log('\n Issues by Category:');
    Object.entries(summary.byCategory)
      .sort(([,a], [,b]) => b - a)
      .forEach(([category, count]) => {
        const bar = ''.repeat(Math.min(count * 2, 40));
        console.log(`   ${category.padEnd(20)} ${bar} (${count})`);
      });
    
    // Show severity breakdown
    console.log('\n  Issues by Severity:');
    console.log(`    High:   ${summary.bySeverity.high || 0}`);
    console.log(`    Medium: ${summary.bySeverity.medium || 0}`);
    console.log(`    Low:    ${summary.bySeverity.low || 0}`);
    
    // Show critical findings
    if (summary.criticalFindings.length > 0) {
      console.log('\n Critical Findings:');
      summary.criticalFindings.slice(0, 5).forEach((finding, i) => {
        console.log(`\n   ${i + 1}. [${finding.category}]`);
        console.log(`      ${finding.message}`);
      });
      
      if (summary.criticalFindings.length > 5) {
        console.log(`\n   ... and ${summary.criticalFindings.length - 5} more critical issues`);
      }
    }
    
    // Show suggestions
    if (summary.suggestions.length > 0) {
      console.log('\n Recommended Actions:');
      summary.suggestions.slice(0, 5).forEach((suggestion, i) => {
        console.log(`   ${i + 1}. ${suggestion}`);
      });
    }
  }
  
  // Save detailed report
  const reportPath = analyzer.exportToJSON(
    path.join(__dirname, `log_analysis_${Date.now()}.json`)
  );
  console.log(`\n Detailed report saved to: ${reportPath}`);
  
  // Save HTML report
  const htmlReport = analyzer.generateHTMLReport();
  const htmlPath = path.join(__dirname, `log_analysis_${Date.now()}.html`);
  require('fs').writeFileSync(htmlPath, htmlReport);
  console.log(` HTML report saved to: ${htmlPath}`);
  
  console.log('\n' + '='.repeat(80));
  console.log(' Debug session with automated analysis complete!\n');
}

// Alternative: Use the withLogAnalysis wrapper
async function debugWithWrapper() {
  await withLogAnalysis(async (analyzer) => {
    // Your test code here
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    
    // Attach analyzer
    analyzer.attachToContext(context);
    
    const page = await context.newPage();
    
    // Run your test...
    await page.goto('http://localhost:5173');
    
    // Clean up
    await browser.close();
  }, {
    saveReport: true,
    reportPath: 'debug_analysis.json'
  });
}

// Run the example
if (require.main === module) {
  debugWithAutomatedAnalysis().catch(console.error);
}