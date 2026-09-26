#!/bin/bash

# JARVIS v2 - Enhanced Setup Script
# Installs all dependencies and sets up the enhanced system

set -e  # Exit on error

echo "🚀 JARVIS v2 - Enhanced Setup"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  Warning: This script is optimized for macOS${NC}"
    echo "Some features may not work on other platforms"
    echo ""
fi

# Step 1: Check Python
echo -e "${GREEN}1️⃣  Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "   ✓ Python $PYTHON_VERSION found"
else
    echo -e "${RED}   ✗ Python 3 not found${NC}"
    echo "   Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

# Step 2: Check Node.js
echo -e "${GREEN}2️⃣  Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✓ Node.js $NODE_VERSION found"
else
    echo -e "${RED}   ✗ Node.js not found${NC}"
    echo "   Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Step 3: Check Ollama
echo -e "${GREEN}3️⃣  Checking Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo "   ✓ Ollama found"
else
    echo -e "${YELLOW}   ⚠️  Ollama not found${NC}"
    echo "   Install from: https://ollama.ai/"
    echo "   Then run: ollama pull llama3"
fi

# Step 4: Create directories
echo -e "${GREEN}4️⃣  Creating directories...${NC}"
mkdir -p .pids
mkdir -p logs
mkdir -p data/learning
mkdir -p data/memory
mkdir -p data/conversations
mkdir -p data/documents
mkdir -p data/semantic_vectors
echo "   ✓ Directories created"

# Step 5: Install Python dependencies
echo -e "${GREEN}5️⃣  Installing Python dependencies...${NC}"
pip3 install -r requirements.txt
echo "   ✓ Python dependencies installed"

# Step 6: Install Tool Server dependencies
echo -e "${GREEN}6️⃣  Installing Tool Server dependencies...${NC}"
cd tools
npm install
echo "   ✓ Tool Server dependencies installed"
cd ..

# Step 7: Install Frontend dependencies
echo -e "${GREEN}7️⃣  Installing Frontend dependencies...${NC}"
cd frontend
npm install
echo "   ✓ Frontend dependencies installed"
cd ..

# Step 8: Optional - Install iStats for fan monitoring (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}8️⃣  Installing iStats (optional)...${NC}"
    if command -v gem &> /dev/null; then
        gem install iStats 2>/dev/null || echo "   ⚠️  iStats installation failed (optional)"
    else
        echo "   ⚠️  Ruby gems not found, skipping iStats"
    fi
fi

# Step 9: Create .env file if not exists
echo -e "${GREEN}9️⃣  Setting up environment...${NC}"
if [ ! -f .env ]; then
    cat > .env << EOF
# JARVIS v2 Configuration

# LLM Settings
OLLAMA_MODEL=llama3:latest
OLLAMA_HOST=http://localhost:11434

# Server Ports
BACKEND_PORT=8001
TOOL_SERVER_PORT=8002
FRONTEND_PORT=5174

# Engineering Mode (true/false)
ENGINEERING_MODE=true

# Logging
LOG_LEVEL=INFO

# Memory Settings
MAX_MEMORY_ENTRIES=1000
VECTOR_DIMENSION=384

# Self-Healing
AUTO_HEALING=true
MAX_RESTART_ATTEMPTS=3

# Watchdog
HEALTH_CHECK_INTERVAL=10
DEPENDENCY_CHECK_INTERVAL=3600
EOF
    echo "   ✓ .env file created"
else
    echo "   ✓ .env file already exists"
fi

# Step 10: Create start script
echo -e "${GREEN}🔟 Creating start script...${NC}"
cat > start_all.sh << 'EOF'
#!/bin/bash

# JARVIS v2 - Start All Services

echo "🚀 Starting JARVIS v2..."
echo ""

# Start Backend + WebSocket
echo "1️⃣  Starting Backend + WebSocket..."
python3 api/websocket_server_enhanced.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .pids/backend.pid
echo "   ✓ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start Tool Server
echo "2️⃣  Starting Tool Server..."
cd tools
npm start > ../logs/tools.log 2>&1 &
TOOLS_PID=$!
echo $TOOLS_PID > ../.pids/tools.pid
echo "   ✓ Tool Server started (PID: $TOOLS_PID)"
cd ..

# Wait for tool server to start
sleep 3

# Start Frontend
echo "3️⃣  Starting Frontend..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.pids/frontend.pid
echo "   ✓ Frontend started (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📡 Services:"
echo "   - Backend:     http://localhost:8001"
echo "   - Tool Server: http://localhost:8002"
echo "   - Frontend:    http://localhost:5174"
echo ""
echo "📝 Logs:"
echo "   - Backend:     tail -f logs/backend.log"
echo "   - Tool Server: tail -f logs/tools.log"
echo "   - Frontend:    tail -f logs/frontend.log"
echo ""
echo "🛑 To stop all services: ./stop_all.sh"
echo ""
EOF

chmod +x start_all.sh
echo "   ✓ start_all.sh created"

# Step 11: Create stop script
cat > stop_all.sh << 'EOF'
#!/bin/bash

# JARVIS v2 - Stop All Services

echo "🛑 Stopping JARVIS v2..."
echo ""

# Stop Backend
if [ -f .pids/backend.pid ]; then
    BACKEND_PID=$(cat .pids/backend.pid)
    echo "1️⃣  Stopping Backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "   ⚠️  Backend not running"
    rm .pids/backend.pid
fi

# Stop Tool Server
if [ -f .pids/tools.pid ]; then
    TOOLS_PID=$(cat .pids/tools.pid)
    echo "2️⃣  Stopping Tool Server (PID: $TOOLS_PID)..."
    kill $TOOLS_PID 2>/dev/null || echo "   ⚠️  Tool Server not running"
    rm .pids/tools.pid
fi

# Stop Frontend
if [ -f .pids/frontend.pid ]; then
    FRONTEND_PID=$(cat .pids/frontend.pid)
    echo "3️⃣  Stopping Frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "   ⚠️  Frontend not running"
    rm .pids/frontend.pid
fi

# Kill any remaining processes on ports
echo "4️⃣  Cleaning up ports..."
lsof -ti:8001,8002,5174 | xargs kill -9 2>/dev/null || true

echo ""
echo "✅ All services stopped!"
echo ""
EOF

chmod +x stop_all.sh
echo "   ✓ stop_all.sh created"

# Step 12: Create status script
cat > check_status.sh << 'EOF'
#!/bin/bash

# JARVIS v2 - Check Status

echo "📊 JARVIS v2 Status"
echo "==================="
echo ""

# Check Backend
echo "1️⃣  Backend (Port 8001):"
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "   ✅ Running"
    curl -s http://localhost:8001/health | jq . 2>/dev/null || echo "   (Health check failed)"
else
    echo "   ❌ Not running"
fi
echo ""

# Check Tool Server
echo "2️⃣  Tool Server (Port 8002):"
if lsof -Pi :8002 -sTCP:LISTEN -t >/dev/null ; then
    echo "   ✅ Running"
    curl -s http://localhost:8002/health | jq . 2>/dev/null || echo "   (Health check failed)"
else
    echo "   ❌ Not running"
fi
echo ""

# Check Frontend
echo "3️⃣  Frontend (Port 5174):"
if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "   ✅ Running"
else
    echo "   ❌ Not running"
fi
echo ""

# Check Ollama
echo "4️⃣  Ollama:"
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1 ; then
    echo "   ✅ Running"
else
    echo "   ❌ Not running"
fi
echo ""

# System Resources
echo "5️⃣  System Resources:"
echo "   CPU:  $(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')"
echo "   RAM:  $(top -l 1 | grep "PhysMem" | awk '{print $2}' | sed 's/M//')"
echo "   Disk: $(df -h / | tail -1 | awk '{print $5}')"
echo ""
EOF

chmod +x check_status.sh
echo "   ✓ check_status.sh created"

# Done!
echo ""
echo "================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Start Ollama (if not running):"
echo "   ollama serve"
echo "   ollama pull llama3"
echo ""
echo "2. Start all services:"
echo "   ./start_all.sh"
echo ""
echo "3. Check status:"
echo "   ./check_status.sh"
echo ""
echo "4. Open browser:"
echo "   http://localhost:5174"
echo ""
echo "5. Enable Engineering Mode in the UI"
echo ""
echo "📖 Documentation:"
echo "   - ENHANCED_FEATURES.md - New features guide"
echo "   - SYSTEM_COMPLETE_FINAL.md - Complete system overview"
echo "   - STARTUP_SUCCESS.md - Startup guide"
echo ""
echo "🎉 Enjoy JARVIS v2!"
echo ""
