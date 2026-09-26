#!/bin/bash

# JARVIS Watchdog Stopper - Phase 0

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🛑 Stopping JARVIS Watchdog..."

# Check if watchdog is running
if [ ! -f ".pids/watchdog.pid" ]; then
    echo -e "${YELLOW}⚠️  Watchdog not running${NC}"
    exit 0
fi

PID=$(cat .pids/watchdog.pid)

if ! ps -p $PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Watchdog not running (stale PID file)${NC}"
    rm .pids/watchdog.pid
    exit 0
fi

# Send SIGTERM for graceful shutdown
echo "Sending shutdown signal to watchdog (PID: $PID)..."
kill -TERM $PID

# Wait for it to stop
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Watchdog stopped${NC}"
        rm .pids/watchdog.pid
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo -e "${YELLOW}⚠️  Force killing watchdog...${NC}"
kill -9 $PID 2>/dev/null || true
rm .pids/watchdog.pid

echo -e "${GREEN}✓ Watchdog stopped (forced)${NC}"
