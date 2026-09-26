#!/bin/bash

# JARVIS Watchdog Starter - Phase 0
# Starts the watchdog manager which monitors all services

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 JARVIS Watchdog Manager${NC}"
echo "================================"

# Check if already running
if [ -f ".pids/watchdog.pid" ]; then
    PID=$(cat .pids/watchdog.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Watchdog already running (PID: $PID)${NC}"
        echo "Use './stop_watchdog.sh' to stop it first"
        exit 1
    fi
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check required packages
echo "Checking dependencies..."
python3 -c "import psutil, watchdog" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Installing required packages...${NC}"
    pip3 install psutil watchdog
fi

echo -e "${GREEN}✓ Dependencies OK${NC}"

# Create directories
mkdir -p .pids logs core

# Start watchdog in background
echo "Starting watchdog manager..."
nohup python3 core/watchdog_manager.py > logs/watchdog.log 2>&1 &
WATCHDOG_PID=$!

# Save PID
echo $WATCHDOG_PID > .pids/watchdog.pid

# Wait a bit and check if it's running
sleep 2

if ps -p $WATCHDOG_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Watchdog started (PID: $WATCHDOG_PID)${NC}"
    echo ""
    echo "Services will be monitored and auto-restarted if they crash"
    echo ""
    echo "Commands:"
    echo "  - View logs: tail -f logs/watchdog.log"
    echo "  - Stop: ./stop_watchdog.sh"
    echo "  - Status: ./status.sh"
else
    echo -e "${RED}✗ Failed to start watchdog${NC}"
    echo "Check logs/watchdog.log for details"
    exit 1
fi
