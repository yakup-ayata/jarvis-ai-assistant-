#!/bin/bash

# JARVIS Tool Server Stopper - Phase 2

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🛑 Stopping JARVIS Tool Server..."

if [ ! -f ".pids/tools.pid" ]; then
    echo -e "${YELLOW}⚠️  Tool server not running${NC}"
    exit 0
fi

PID=$(cat .pids/tools.pid)

if ! ps -p $PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Tool server not running (stale PID)${NC}"
    rm .pids/tools.pid
    exit 0
fi

echo "Sending shutdown signal (PID: $PID)..."
kill -TERM $PID

for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Tool server stopped${NC}"
        rm .pids/tools.pid
        exit 0
    fi
    sleep 1
done

echo -e "${YELLOW}⚠️  Force killing...${NC}"
kill -9 $PID 2>/dev/null || true
rm .pids/tools.pid

echo -e "${GREEN}✓ Tool server stopped (forced)${NC}"
