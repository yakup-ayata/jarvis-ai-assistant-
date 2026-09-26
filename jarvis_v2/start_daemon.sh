#!/bin/bash

# JARVIS Daemon Agent Starter - Phase 1

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧠 JARVIS Core Daemon Agent${NC}"
echo "================================"

# Check if already running
if [ -f ".pids/daemon.pid" ]; then
    PID=$(cat .pids/daemon.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Daemon already running (PID: $PID)${NC}"
        echo "Use './stop_daemon.sh' to stop it first"
        exit 1
    fi
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
fi

# Create directories
mkdir -p .pids logs core

# Start daemon in background
echo "Starting daemon agent..."
cd core
nohup python3 daemon_agent.py > ../logs/daemon.log 2>&1 &
DAEMON_PID=$!
cd ..

# Save PID
echo $DAEMON_PID > .pids/daemon.pid

# Wait and check
sleep 2

if ps -p $DAEMON_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Daemon started (PID: $DAEMON_PID)${NC}"
    echo ""
    echo "The daemon is now running with:"
    echo "  - Tiered Intelligence (Rule/Mini/Full)"
    echo "  - Environment Monitoring"
    echo "  - Event-driven Architecture"
    echo ""
    echo "Commands:"
    echo "  - View logs: tail -f logs/daemon.log"
    echo "  - Check state: cat logs/daemon_state.json"
    echo "  - Stop: ./stop_daemon.sh"
else
    echo -e "${RED}✗ Failed to start daemon${NC}"
    echo "Check logs/daemon.log for details"
    exit 1
fi
