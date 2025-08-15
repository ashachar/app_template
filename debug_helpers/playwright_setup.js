// Standard Playwright setup for debugging
//  ALWAYS use this configuration for consistency

const { chromium } = require('playwright');

async function setupBrowser() {
  // MANDATORY: Always use headless mode unless user explicitly says "show browser" or "not headless"
  const browser = await chromium.launch({ 
    headless: true,
    // Logs will be available in browser console if needed
    args: ['--enable-logging', '--v=1']
  });
  
  return browser;
}

async function setupContext(browser, testName) {
  const context = await browser.newContext({
    // Hebrew locale by default
    locale: 'he',
    // Video recording configuration
    recordVideo: {
      dir: 'tests/integration/videos/',
      size: { width: 1280, height: 720 }
    },
    // Capture browser console logs
    acceptDownloads: true
  });
  
  // Capture console logs
  context.on('console', msg => {
    console.log(`[BROWSER LOG] ${msg.type()}: ${msg.text()}`);
  });
  
  return context;
}

// Standard timeouts
const TIMEOUTS = { 
  navigation: 5000, 
  elementVisible: 3000,
  apiCall: 5000,
  formSubmit: 3000,
  buttonClick: 1000
};

// Test user credentials from .env
const getTestUsers = () => ({
  recruiter: {
    email: process.env.TEST_RECRUITER_EMAIL,
    password: process.env.TEST_RECRUITER_PASSWORD
  },
  candidate: {
    email: process.env.TEST_CANDIDATE_EMAIL,
    password: process.env.TEST_CANDIDATE_PASSWORD
  }
});

module.exports = { setupBrowser, setupContext, TIMEOUTS, getTestUsers };