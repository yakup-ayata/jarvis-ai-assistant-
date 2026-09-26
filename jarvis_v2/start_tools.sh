#!/bin/bash

# JARVIS Tool Server Starter - Phase 2

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔧 JARVIS Tool Server${NC}"
echo "================================"

# Check if already running
if [ -f ".pids/tools.pid" ]; then
    PID=$(cat .pids/tools.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Tool server already running (PID: $PID)${NC}"
        exit 1
    fi
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Install dependencies if needed
if [ ! -d "tools/node_modules" ]; then
    echo "Installing dependencies..."
    cd tools
    npm install
    cd ..
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Create directories
mkdir -p .pids logs

# Start tool server
echo "Starting tool server..."
cd tools
nohup node server.js > ../logs/tools.log 2>&1 &
TOOLS_PID=$!
cd ..

# Save PID
echo $TOOLS_PID > .pids/tools.pid

# Wait and check
sleep 2

if ps -p $TOOLS_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Tool server started (PID: $TOOLS_PID)${NC}"
    echo ""
    echo "Server running on http://localhost:8002"
    echo ""
    echo "Available actions:"
    echo "  - open_app, close_app"
    echo "  - set_volume, get_volume"
    echo "  - open_url, web_search"
    echo "  - execute_command (sandboxed)"
    echo "  - take_screenshot"
    echo "  - get_system_info"
    echo ""
    echo "Commands:"
    echo "  - View logs: tail -f logs/tools.log"
    echo "  - Test: cd tools && npm test"
    echo "  - Stop: ./stop_tools.sh"
else
    echo -e "${RED}✗ Failed to start tool server${NC}"
    echo "Check logs/tools.log for details"
    exit 1
fi
