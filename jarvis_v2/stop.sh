#!/bin/bash

# JARVIS V2 - Stop All Services

echo "🛑 Stopping JARVIS V2..."
echo "=" | tr '=' '=' | head -c 60; echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to stop service by PID file
stop_service() {
    local pid_file=$1
    local name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -n "   Stopping $name (PID: $pid)..."
            kill $pid 2>/dev/null
            sleep 2
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi
            echo -e " ${GREEN}✓${NC}"
        else
            echo -e "   $name: ${RED}Not running${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "   $name: ${RED}PID file not found${NC}"
    fi
}

# Function to stop by port
stop_by_port() {
    local port=$1
    local name=$2
    
    local pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -n "   Stopping $name on port $port (PID: $pid)..."
        kill $pid 2>/dev/null
        sleep 1
        if lsof -ti :$port > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e "   $name: ${RED}Not running on port $port${NC}"
    fi
}

# Create .pids directory if not exists
mkdir -p .pids

# Stop services
echo ""
stop_service ".pids/frontend.pid" "Frontend"
stop_service ".pids/websocket.pid" "WebSocket Server"
stop_service ".pids/tools.pid" "Tool Server"
stop_service ".pids/ollama.pid" "Ollama"

# Fallback: stop by port
echo ""
echo "Checking ports..."
stop_by_port 5174 "Frontend"
stop_by_port 8001 "WebSocket"
stop_by_port 8002 "Tools"
stop_by_port 11434 "Ollama"

echo ""
echo "=" | tr '=' '=' | head -c 60; echo
echo -e "${GREEN}✅ All services stopped${NC}"
echo "=" | tr '=' '=' | head -c 60; echo
