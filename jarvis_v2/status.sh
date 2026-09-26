#!/bin/bash

# JARVIS V2 Status Checker

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📊 JARVIS V2 System Status${NC}"
echo "================================"

# Check services
echo -e "\n${BLUE}Services:${NC}"

check_service() {
    local name=$1
    local port=$2
    local pid_file=".pids/${name}.pid"
    
    if lsof -i :$port > /dev/null 2>&1; then
        if [ -f "$pid_file" ]; then
            PID=$(cat $pid_file)
            echo -e "  ${GREEN}✓ $name (PID: $PID, Port: $port)${NC}"
        else
            echo -e "  ${GREEN}✓ $name (Port: $port)${NC}"
        fi
    else
        echo -e "  ${RED}✗ $name (Port: $port not listening)${NC}"
    fi
}

check_service "Ollama" 11434
check_service "Tool Server" 8002
check_service "WebSocket" 8001
check_service "Frontend" 5174

# Check Ollama models
echo -e "\n${BLUE}Ollama Models:${NC}"
if lsof -i :11434 > /dev/null 2>&1; then
    ollama list 2>/dev/null | tail -n +2 | while read line; do
        echo -e "  ${GREEN}✓${NC} $line"
    done
else
    echo -e "  ${RED}✗ Ollama not running${NC}"
fi

# System resources
echo -e "\n${BLUE}System Resources:${NC}"
python3 -c "
import psutil
cpu = psutil.cpu_percent(interval=1)
mem = psutil.virtual_memory()
disk = psutil.disk_usage('/')

print(f'  CPU: {cpu:.1f}%')
print(f'  Memory: {mem.percent:.1f}% ({mem.available / (1024**3):.2f} GB available)')
print(f'  Disk: {disk.percent:.1f}% used')
" 2>/dev/null || echo "  (psutil not installed)"

# Recent logs
echo -e "\n${BLUE}Recent Activity:${NC}"
if [ -f "logs/websocket.log" ]; then
    echo "  Last 3 WebSocket log entries:"
    tail -n 3 logs/websocket.log | sed 's/^/    /'
else
    echo "  No logs yet"
fi

echo ""
