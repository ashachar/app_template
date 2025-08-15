// Log management helpers for debugging

const fs = require('fs');
const path = require('path');

// Log file locations
const LOG_LOCATIONS = {
  consolidated: 'consolidated_logs/latest.log',
  playwright: 'playwright_debug.log',
  apiErrors: 'api/logs/error.log',
  lambdaLogs: 'Check CloudWatch logs for Lambda functions'
};

function addDebugLog(message, data = null) {
  const log = data ? `[DEBUG] ${message}: ${JSON.stringify(data, null, 2)}` : `[DEBUG] ${message}`;
  
  // Always wrap debug logs
  console.log('');
}

function checkServerLogs() {
  console.log('\n Checking server logs...');
  
  if (fs.existsSync(LOG_LOCATIONS.consolidated)) {
    const logs = fs.readFileSync(LOG_LOCATIONS.consolidated, 'utf8');
    const lines = logs.split('\n');
    const recentErrors = lines.slice(-50).filter(line => 
      line.includes('ERROR') || 
      line.includes('FAILED') || 
      line.includes('Error:') ||
      line.includes('[error]')
    );
    
    if (recentErrors.length > 0) {
      console.log(' Recent errors found in server logs:');
      recentErrors.forEach(error => console.log(`  ${error}`));
    } else {
      console.log(' No recent errors in server logs');
    }
  } else {
    console.log('  Server log file not found');
  }
}

function checkBrowserConsole(consoleMessages) {
  console.log('\n Checking browser console logs...');
  
  const errors = consoleMessages.filter(msg => msg.type === 'error');
  const warnings = consoleMessages.filter(msg => msg.type === 'warning');
  
  if (errors.length > 0) {
    console.log(' Browser errors found:');
    errors.forEach(err => console.log(`  ${err.text}`));
  }
  
  if (warnings.length > 0) {
    console.log('  Browser warnings found:');
    warnings.forEach(warn => console.log(`  ${warn.text}`));
  }
  
  if (errors.length === 0 && warnings.length === 0) {
    console.log(' No browser console errors or warnings');
  }
}

function printLogLocations() {
  console.log('\n Log file locations:');
  Object.entries(LOG_LOCATIONS).forEach(([name, location]) => {
    console.log(`  ${name}: ${location}`);
  });
}

module.exports = { 
  LOG_LOCATIONS,
  addDebugLog,
  checkServerLogs,
  checkBrowserConsole,
  printLogLocations
};