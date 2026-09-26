#!/bin/bash

# JARVIS Daemon Stopper - Phase 1

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🛑 Stopping JARVIS Daemon Agent..."

# Check if daemon is running
if [ ! -f ".pids/daemon.pid" ]; then
    echo -e "${YELLOW}⚠️  Daemon not running${NC}"
    exit 0
fi

PID=$(cat .pids/daemon.pid)

if ! ps -p $PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Daemon not running (stale PID file)${NC}"
    rm .pids/daemon.pid
    exit 0
fi

# Send SIGTERM for graceful shutdown
echo "Sending shutdown signal to daemon (PID: $PID)..."
kill -TERM $PID

# Wait for it to stop
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Daemon stopped${NC}"
        rm .pids/daemon.pid
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo -e "${YELLOW}⚠️  Force killing daemon...${NC}"
kill -9 $PID 2>/dev/null || true
rm .pids/daemon.pid

echo -e "${GREEN}✓ Daemon stopped (forced)${NC}"
