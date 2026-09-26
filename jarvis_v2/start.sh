#!/bin/bash

# JARVIS V2 - Main Startup Script
# Starts all services in correct order

set -e

echo "🚀 Starting JARVIS V2..."
echo "=" | tr '=' '=' | head -c 60; echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "api/websocket_server_enhanced.py" ]; then
    echo -e "${RED}❌ Error: Must run from jarvis_v2 directory${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🟩 Activating virtual environment..."
    source .venv/bin/activate
fi

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to wait for service
wait_for_service() {
    local port=$1
    local name=$2
    local max_wait=30
    local count=0
    
    echo -n "   Waiting for $name (port $port)..."
    while [ $count -lt $max_wait ]; do
        if check_port $port; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    echo -e " ${RED}✗ Timeout${NC}"
    return 1
}

# 0. Start Ollama (if not running)
echo -e "\n${YELLOW}0️⃣ Starting Ollama LLM Server...${NC}"
if check_port 11434; then
    echo -e "   ${GREEN}✓ Already running on port 11434${NC}"
else
    ollama serve > logs/ollama.log 2>&1 &
    echo $! > .pids/ollama.pid
    wait_for_service 11434 "Ollama"
fi

# 1. Start Tool Server (Node.js)
echo -e "\n${YELLOW}1️⃣ Starting Tool Server...${NC}"
if check_port 8002; then
    echo -e "   ${GREEN}✓ Already running on port 8002${NC}"
else
    cd tools
    npm start > ../logs/tools.log 2>&1 &
    echo $! > ../.pids/tools.pid
    cd ..
    wait_for_service 8002 "Tool Server"
fi

# 2. Start WebSocket Server (Python)
echo -e "\n${YELLOW}2️⃣ Starting WebSocket Server...${NC}"
if check_port 8001; then
    echo -e "   ${GREEN}✓ Already running on port 8001${NC}"
else
    python3 api/websocket_server_enhanced.py > logs/websocket.log 2>&1 &
    echo $! > .pids/websocket.pid
    wait_for_service 8001 "WebSocket Server"
fi

# 3. Start Frontend (React + Vite)
echo -e "\n${YELLOW}3️⃣ Starting Frontend...${NC}"
if check_port 5174; then
    echo -e "   ${GREEN}✓ Already running on port 5174${NC}"
else
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../.pids/frontend.pid
    cd ..
    wait_for_service 5174 "Frontend"
fi

# Summary
echo ""
echo "=" | tr '=' '=' | head -c 60; echo
echo -e "${GREEN}✅ JARVIS V2 Started Successfully!${NC}"
echo ""
echo "🧠 AI Models:"
echo "   • Ollama Server:    http://localhost:11434"
echo "   • Mini Model:       llama3:latest (4.7 GB)"
echo "   • Coding Model:     codellama:latest (3.8 GB)"
echo ""
echo "📡 Services:"
echo "   • Tool Server:      http://localhost:8002"
echo "   • WebSocket Server: ws://localhost:8001/ws"
echo "   • Frontend UI:      http://localhost:5174"
echo ""
echo "📋 Logs:"
echo "   • Ollama:           logs/ollama.log"
echo "   • Tool Server:      logs/tools.log"
echo "   • WebSocket:        logs/websocket.log"
echo "   • Frontend:         logs/frontend.log"
echo ""
echo "🛑 To stop: ./stop.sh"
echo "📊 Status:  ./status.sh"
echo "=" | tr '=' '=' | head -c 60; echo
