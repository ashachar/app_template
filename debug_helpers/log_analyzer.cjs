/**
 * JavaScript Log Analyzer for integration with Playwright tests
 * Provides real-time log analysis during test execution
 */

const fs = require('fs');
const path = require('path');

class LogAnalyzer {
  constructor() {
    this.patterns = this.loadPatterns();
    this.findings = [];
    this.consoleLogs = [];
    this.networkErrors = [];
    this.performanceMetrics = {};
  }

  loadPatterns() {
    const patternsPath = path.join(__dirname, 'patterns', 'error_patterns.json');
    try {
      return JSON.parse(fs.readFileSync(patternsPath, 'utf8'));
    } catch (error) {
      console.warn('Could not load error patterns, using defaults');
      return this.getDefaultPatterns();
    }
  }

  getDefaultPatterns() {
    return {
      "api_errors": {
        "patterns": ["40[134]", "500", "ECONNREFUSED"],
        "category": "API",
        "severity": "high"
      },
      "null_errors": {
        "patterns": ["Cannot read property.*of (null|undefined)"],
        "category": "Null Reference",
        "severity": "medium"
      }
    };
  }

  /**
   * Attach to Playwright context to capture browser logs
   */
  attachToContext(context) {
    // Capture console logs
    context.on('console', async (msg) => {
      const logEntry = {
        type: msg.type(),
        text: msg.text(),
        timestamp: new Date().toISOString(),
        location: msg.location()
      };
      
      this.consoleLogs.push(logEntry);
      
      // Analyze log in real-time
      if (msg.type() === 'error' || msg.type() === 'warning') {
        this.analyzeLogEntry(logEntry);
      }
    });

    // Capture network failures
    context.on('requestfailed', (request) => {
      const error = {
        url: request.url(),
        method: request.method(),
        failure: request.failure(),
        timestamp: new Date().toISOString()
      };
      
      this.networkErrors.push(error);
      this.analyzeNetworkError(error);
    });

    // Capture page errors
    context.on('pageerror', (error) => {
      this.analyzeLogEntry({
        type: 'pageerror',
        text: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });
    });
  }

  /**
   * Analyze a single log entry against patterns
   */
  analyzeLogEntry(logEntry) {
    const text = logEntry.text || '';
    
    for (const [patternName, patternInfo] of Object.entries(this.patterns)) {
      for (const pattern of patternInfo.patterns) {
        const regex = new RegExp(pattern, 'i');
        if (regex.test(text)) {
          this.findings.push({
            timestamp: logEntry.timestamp,
            category: patternInfo.category,
            severity: patternInfo.severity,
            message: text,
            pattern: patternName,
            type: logEntry.type,
            suggestions: patternInfo.suggestions || []
          });
          break;
        }
      }
    }
  }

  /**
   * Analyze network errors
   */
  analyzeNetworkError(error) {
    const finding = {
      timestamp: error.timestamp,
      category: 'Network',
      severity: 'high',
      message: `${error.method} ${error.url} failed: ${error.failure}`,
      type: 'network',
      suggestions: []
    };

    // Add specific suggestions based on error type
    if (error.failure && error.failure.includes('net::ERR_CONNECTION_REFUSED')) {
      finding.suggestions.push('Check if API server is running');
      finding.suggestions.push('Verify API URL in environment variables');
    } else if (error.url.includes('/api/') && error.failure) {
      finding.suggestions.push('Check API endpoint implementation');
      finding.suggestions.push('Verify API route exists');
    }

    this.findings.push(finding);
  }

  /**
   * Analyze server logs from file
   */
  async analyzeServerLogs(logPath = 'consolidated_logs/latest.log') {
    if (!fs.existsSync(logPath)) {
      return { error: `Log file not found: ${logPath}` };
    }

    const content = fs.readFileSync(logPath, 'utf8');
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      if (line.trim()) {
        this.analyzeLogEntry({
          type: 'server',
          text: line,
          timestamp: new Date().toISOString(),
          lineNumber: index + 1
        });
      }
    });

    return { analyzed: lines.length, findings: this.findings.length };
  }

  /**
   * Track performance metrics
   */
  trackPerformance(metricName, value) {
    if (!this.performanceMetrics[metricName]) {
      this.performanceMetrics[metricName] = [];
    }
    this.performanceMetrics[metricName].push({
      value,
      timestamp: new Date().toISOString()
    });

    // Analyze for performance issues
    if (metricName === 'apiResponseTime' && value > 5000) {
      this.findings.push({
        timestamp: new Date().toISOString(),
        category: 'Performance',
        severity: 'medium',
        message: `Slow API response: ${value}ms`,
        type: 'performance',
        suggestions: ['Check server load', 'Optimize database queries', 'Add caching']
      });
    }
  }

  /**
   * Get summary of findings
   */
  getSummary() {
    const summary = {
      totalFindings: this.findings.length,
      byCategory: {},
      bySeverity: {},
      criticalFindings: [],
      suggestions: new Set()
    };

    this.findings.forEach(finding => {
      // Count by category
      summary.byCategory[finding.category] = (summary.byCategory[finding.category] || 0) + 1;
      
      // Count by severity
      summary.bySeverity[finding.severity] = (summary.bySeverity[finding.severity] || 0) + 1;
      
      // Collect critical findings
      if (finding.severity === 'high') {
        summary.criticalFindings.push({
          category: finding.category,
          message: finding.message.substring(0, 100) + '...'
        });
      }
      
      // Collect unique suggestions
      finding.suggestions.forEach(s => summary.suggestions.add(s));
    });

    summary.suggestions = Array.from(summary.suggestions);
    return summary;
  }

  /**
   * Generate HTML report
   */
  generateHTMLReport() {
    const summary = this.getSummary();
    
    return `
<!DOCTYPE html>
<html>
<head>
  <title>Log Analysis Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; }
    .critical { color: #d32f2f; }
    .warning { color: #f57c00; }
    .info { color: #0288d1; }
    .finding { margin: 10px 0; padding: 10px; border-left: 3px solid #ccc; }
    .high { border-color: #d32f2f; }
    .medium { border-color: #f57c00; }
    .low { border-color: #0288d1; }
  </style>
</head>
<body>
  <h1>🔍 Log Analysis Report</h1>
  
  <div class="summary">
    <h2>Summary</h2>
    <p>Total Findings: ${summary.totalFindings}</p>
    <p>Critical Issues: ${summary.bySeverity.high || 0}</p>
    <p>Warnings: ${summary.bySeverity.medium || 0}</p>
  </div>
  
  <h2>Findings by Category</h2>
  <ul>
    ${Object.entries(summary.byCategory)
      .map(([cat, count]) => `<li>${cat}: ${count}</li>`)
      .join('')}
  </ul>
  
  <h2>Critical Findings</h2>
  ${summary.criticalFindings
    .map(f => `<div class="finding high"><strong>${f.category}:</strong> ${f.message}</div>`)
    .join('')}
  
  <h2>Suggested Actions</h2>
  <ol>
    ${summary.suggestions.map(s => `<li>${s}</li>`).join('')}
  </ol>
  
  <h2>Detailed Findings</h2>
  ${this.findings
    .slice(0, 50) // Limit to first 50
    .map(f => `
      <div class="finding ${f.severity}">
        <strong>[${f.timestamp}] ${f.category}</strong><br>
        ${f.message}<br>
        <small>Pattern: ${f.pattern}</small>
      </div>
    `)
    .join('')}
</body>
</html>
    `;
  }

  /**
   * Clear all collected data
   */
  clear() {
    this.findings = [];
    this.consoleLogs = [];
    this.networkErrors = [];
    this.performanceMetrics = {};
  }

  /**
   * Export findings to JSON
   */
  exportToJSON(filePath) {
    const data = {
      timestamp: new Date().toISOString(),
      summary: this.getSummary(),
      findings: this.findings,
      consoleLogs: this.consoleLogs.slice(-100), // Last 100 logs
      networkErrors: this.networkErrors,
      performanceMetrics: this.performanceMetrics
    };
    
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    return filePath;
  }
}

// Helper function for use in tests
async function withLogAnalysis(testFn, options = {}) {
  const analyzer = new LogAnalyzer();
  
  try {
    // Run the test with analyzer
    const result = await testFn(analyzer);
    
    // Generate report
    const summary = analyzer.getSummary();
    
    if (summary.totalFindings > 0) {
      console.log('\n📊 Log Analysis Summary:');
      console.log(`   Total issues found: ${summary.totalFindings}`);
      console.log(`   Critical issues: ${summary.bySeverity.high || 0}`);
      
      if (summary.criticalFindings.length > 0) {
        console.log('\n🚨 Critical Findings:');
        summary.criticalFindings.forEach((f, i) => {
          console.log(`   ${i + 1}. [${f.category}] ${f.message}`);
        });
      }
      
      if (summary.suggestions.length > 0) {
        console.log('\n💡 Suggestions:');
        summary.suggestions.forEach((s, i) => {
          console.log(`   ${i + 1}. ${s}`);
        });
      }
    } else {
      console.log('\n✅ No issues found in logs!');
    }
    
    // Save report if requested
    if (options.saveReport) {
      const reportPath = analyzer.exportToJSON(
        options.reportPath || `log_analysis_${Date.now()}.json`
      );
      console.log(`\n📄 Detailed report saved to: ${reportPath}`);
    }
    
    return result;
  } finally {
    analyzer.clear();
  }
}

module.exports = {
  LogAnalyzer,
  withLogAnalysis
};