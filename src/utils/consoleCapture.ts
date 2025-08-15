// Console capture utility to forward browser logs to consolidated logger
// This captures ALL console.log, console.warn, and console.error calls and sends them to the server

const BATCH_INTERVAL = 1000; // Send logs every 1 second
const LOG_ENDPOINT = '/api/debug-logs';

class ConsoleCapture {
  private originalConsole: {
    log: typeof console.log;
    warn: typeof console.warn;
    error: typeof console.error;
  };
  private logBuffer: Array<{
    type: string;
    message: string;
    timestamp: string;
    url: string;
  }> = [];
  private batchTimer: NodeJS.Timeout | null = null;

  constructor() {
    // Store original console methods
    this.originalConsole = {
      log: console.log.bind(console),
      warn: console.warn.bind(console),
      error: console.error.bind(console)
    };
  }

  start() {
    // Override console methods
    console.log = this.captureLog.bind(this, 'log');
    console.warn = this.captureLog.bind(this, 'warn');
    console.error = this.captureLog.bind(this, 'error');
  }

  private captureLog(type: string, ...args: any[]) {
    // Always call original console method
    this.originalConsole[type as keyof typeof this.originalConsole](...args);

    // Capture ALL console logs - no filtering
    // Format the message
    const message = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ');

    // Add to buffer
    this.logBuffer.push({
      type,
      message,
      timestamp: new Date().toISOString(),
      url: window.location.href
    });

    // Schedule batch send
    this.scheduleBatchSend();
  }

  private scheduleBatchSend() {
    if (this.batchTimer) return;

    this.batchTimer = setTimeout(() => {
      this.sendLogs();
      this.batchTimer = null;
    }, BATCH_INTERVAL);
  }

  private async sendLogs() {
    if (this.logBuffer.length === 0) return;

    const logs = [...this.logBuffer];
    this.logBuffer = [];

    try {
      await fetch(LOG_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ logs })
      });
    } catch (error) {
      // If sending fails, log to original console
      this.originalConsole.error('Failed to send logs to server:', error);
      // Re-add logs to buffer for retry
      this.logBuffer.unshift(...logs);
    }
  }

  stop() {
    // Restore original console methods
    console.log = this.originalConsole.log;
    console.warn = this.originalConsole.warn;
    console.error = this.originalConsole.error;

    // Send any remaining logs
    this.sendLogs();

    // Clear timer
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }
  }
}

// Create and export singleton instance
export const consoleCapture = new ConsoleCapture();