#!/bin/bash

# Generic Application Restart Script (Synchronous)
# This script stops all running processes and restarts the application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - can be customized per project
FRONTEND_PORT=${FRONTEND_PORT:-3000}
BACKEND_PORT=${BACKEND_PORT:-3001}
APP_NAME=${APP_NAME:-"Application"}

echo -e "${YELLOW}🔄 Restarting ${APP_NAME}...${NC}"
echo ""

# Kill processes on frontend port
echo -e "${YELLOW}Checking port ${FRONTEND_PORT} (frontend)...${NC}"
FRONTEND_PID=$(lsof -ti :${FRONTEND_PORT})
if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "${RED}Killing process on port ${FRONTEND_PORT} (PID: $FRONTEND_PID)${NC}"
    kill -9 $FRONTEND_PID 2>/dev/null
    sleep 1
else
    echo -e "${GREEN}Port ${FRONTEND_PORT} is free${NC}"
fi

# Kill processes on backend port (if applicable)
if [ "$BACKEND_PORT" != "none" ]; then
    echo -e "${YELLOW}Checking port ${BACKEND_PORT} (backend)...${NC}"
    BACKEND_PID=$(lsof -ti :${BACKEND_PORT})
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${RED}Killing process on port ${BACKEND_PORT} (PID: $BACKEND_PID)${NC}"
        kill -9 $BACKEND_PID 2>/dev/null
        sleep 1
    else
        echo -e "${GREEN}Port ${BACKEND_PORT} is free${NC}"
    fi
fi

# Kill any nodemon processes
echo -e "${YELLOW}Checking for nodemon processes...${NC}"
pkill -f nodemon 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${RED}Killed nodemon processes${NC}"
    sleep 1
else
    echo -e "${GREEN}No nodemon processes found${NC}"
fi

# Kill any vite processes
echo -e "${YELLOW}Checking for vite processes...${NC}"
pkill -f vite 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${RED}Killed vite processes${NC}"
    sleep 1
else
    echo -e "${GREEN}No vite processes found${NC}"
fi

echo ""
echo -e "${GREEN}✅ All processes cleared!${NC}"
echo ""
echo -e "${YELLOW}Starting application...${NC}"
echo -e "${GREEN}Frontend: http://localhost:${FRONTEND_PORT}${NC}"
if [ "$BACKEND_PORT" != "none" ]; then
    echo -e "${GREEN}Backend:  http://localhost:${BACKEND_PORT}${NC}"
fi
echo ""

# Start the application
npm run dev