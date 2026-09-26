#!/bin/bash

echo "🤖 Starting JARVIS AGENT - Full Computer Control..."
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🟩 Activating virtual environment..."
    source .venv/bin/activate
fi

# Kill existing
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:5174 | xargs kill -9 2>/dev/null || true
sleep 1

# Start Agent Backend
echo "🧠 Starting JARVIS Agent (port 8000)..."
python3 api/jarvis_agent.py > logs/backend.log 2>&1 &
sleep 2

if lsof -ti:8000 > /dev/null; then
    echo "   ✅ Agent Backend running"
else
    echo "   ❌ Backend failed"
    exit 1
fi

# Start WebSocket
echo "🔌 Starting WebSocket (port 8001)..."
python3 api/websocket_server.py > logs/websocket.log 2>&1 &
sleep 2

if lsof -ti:8001 > /dev/null; then
    echo "   ✅ WebSocket running"
fi

# Start Frontend
echo "🎨 Starting Frontend (port 5174)..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
cd ..
sleep 3

if lsof -ti:5174 > /dev/null; then
    echo "   ✅ Frontend running"
fi

echo ""
echo "============================================"
echo "✅ JARVIS AGENT Ready!"
echo "============================================"
echo "📡 Backend:    http://localhost:8000"
echo "🔌 WebSocket:  ws://localhost:8001/ws"
echo "🎨 Frontend:   http://localhost:5174"
echo "============================================"
echo ""
echo "🤖 JARVIS Agent Capabilities:"
echo "   • Understands ANY command"
echo "   • Creates execution plans"
echo "   • Executes step by step"
echo "   • Full computer control"
echo ""
echo "🎤 Try:"
echo "   • 'Instagram'ı aç'"
echo "   • 'Ses seviyesini %50 yap'"
echo "   • 'BMW arat ve ilk siteye git'"
echo "   • 'Tesla hakkında bilgi ver'"
echo ""
