#!/bin/bash

# Generic Application Async Restart Script
# This script restarts the app in the background and returns immediately

# Configuration - can be customized per project
FRONTEND_PORT=${FRONTEND_PORT:-3000}
BACKEND_PORT=${BACKEND_PORT:-3001}
APP_NAME=${APP_NAME:-"Application"}
LOG_DIR=${LOG_DIR:-"consolidated_logs"}

echo "🔄 Restarting ${APP_NAME} (async)..."

# Kill existing processes
echo "Stopping existing processes..."

# Kill processes on specific ports
lsof -ti:${FRONTEND_PORT} | xargs kill -9 2>/dev/null
if [ "$BACKEND_PORT" != "none" ]; then
    lsof -ti:${BACKEND_PORT} | xargs kill -9 2>/dev/null
fi

# Kill any nodemon or vite processes
pkill -f nodemon 2>/dev/null
pkill -f vite 2>/dev/null

# Small delay to ensure processes are killed
sleep 1

# Start the application in the background
echo "Starting application in background..."

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Create a log file for nohup output
# Use tr for lowercase conversion for better compatibility
APP_NAME_LOWER=$(echo "$APP_NAME" | tr '[:upper:]' '[:lower:]')
NOHUP_LOG="/tmp/${APP_NAME_LOWER}-nohup.log"

# Check if dev-with-logging.js exists, otherwise use npm run dev directly
if [ -f "dev-with-logging.js" ]; then
    # Use the logging wrapper if available
    nohup node dev-with-logging.js > "$NOHUP_LOG" 2>&1 &
else
    # Fallback to direct npm run dev
    nohup npm run dev > "$NOHUP_LOG" 2>&1 &
fi

# Get the PID of the background process
PID=$!

echo "✅ Application restarted in background (PID: $PID)"
if [ -d "$LOG_DIR" ]; then
    echo "📝 Logs available at: ${LOG_DIR}/recent.log"
fi
echo "🌐 Frontend: http://localhost:${FRONTEND_PORT}"
if [ "$BACKEND_PORT" != "none" ]; then
    echo "🔧 Backend:  http://localhost:${BACKEND_PORT}"
fi
echo ""
echo "Use 'npm run logs' to view logs (if configured)"

# Exit immediately without waiting
exit 0