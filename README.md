<div align="center">

# 🤖 JARVIS AI Assistant

### *Advanced Autonomous AI System with Full Computer Control*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node-%3E%3D16-brightgreen.svg)](https://nodejs.org/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg)](https://www.typescriptlang.org/)

*An intelligent AI assistant that understands commands, creates plans, and executes them autonomously with real-time feedback*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

JARVIS is a cutting-edge autonomous AI system that brings Iron Man's AI assistant to life. Built with modern technologies and enterprise-grade architecture, it provides seamless computer control, intelligent conversation, and autonomous task execution.

### What Makes JARVIS Special?

- 🧠 **Multi-Agent Architecture** - Specialized agents working together for complex tasks
- 🎯 **Autonomous Execution** - Plans and executes tasks without constant supervision
- 🔒 **Enterprise Security** - Built-in security filters, audit logging, and sandbox execution
- 💾 **Advanced Memory System** - Long-term memory with RAG (Retrieval-Augmented Generation)
- 🎨 **Modern UI** - Sleek React interface with real-time WebSocket communication
- 🔊 **Voice Integration** - Text-to-Speech with multi-language support
- 📚 **Document Intelligence** - PDF, DOCX parsing with semantic search
- 🛡️ **Self-Healing** - Automatic error detection and recovery

---

## ✨ Features

### 🎯 Core Capabilities

#### 💭 Opinion Mode
Ask philosophical questions and get thoughtful AI perspectives:
```
"What do you think about artificial intelligence?"
"What's the best programming language and why?"
```

#### 📚 Information Mode
Research any topic with web-powered AI synthesis:
```
"Tell me about Tesla's latest models"
"Explain quantum computing"
"What are the newest features in Python 3.12?"
```

#### ⚡ Command Mode
Full system control and automation:
```
"Open Instagram"
"Set volume to 50%"
"Search for BMW and open the first website"
"Play Bohemian Rhapsody on Spotify"
"Take a screenshot"
```

### 🚀 Advanced Features

- **🤖 Multi-Agent Coding** - Autonomous code generation and testing
- **🏗️ Autonomous Architect** - System design and architecture planning
- **📊 Dynamic Prompt Composition** - Context-aware prompt optimization
- **🔍 RAG Engine** - Semantic search over your documents
- **🎙️ Wake Word Detection** - Voice-activated commands
- **🌐 Web Automation** - Browser control with Playwright
- **📝 Reflection System** - Self-improvement through analysis
- **⚠️ Risk Assessment** - Safety-first command execution
- **🔐 Audit Logging** - Complete activity tracking

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - Core backend runtime
- **Node.js 16+** - Frontend and tools
- **macOS** - Primary platform (Linux/Windows support planned)
- **API Key** - OpenAI or Google Gemini

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yakup-ayata/jarvis-ai-assistant-.git
cd jarvis-ai-assistant-
```

2. **Configure API Keys**
```bash
cd jarvis_v2
cp .env.example .env
# Edit .env and add your API key
```

`.env` example:
```bash
# Option 1: OpenAI (Recommended)
OPENAI_API_KEY=sk-proj-your-key-here

# Option 2: Google Gemini
GEMINI_API_KEY=your-gemini-key-here
```

3. **Run Setup Script**
```bash
bash setup_enhanced.sh
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Install Node.js dependencies
- ✅ Setup RAG engine packages
- ✅ Install Playwright browsers
- ✅ Verify all components

4. **Start JARVIS**
```bash
bash start.sh
```

5. **Access the Interface**
- 🎨 **Frontend**: http://localhost:5174
- 🧠 **Backend API**: http://localhost:8000
- 🔌 **WebSocket**: ws://localhost:8001

---

## 📚 Documentation

### Core Documentation
- [📖 Quick Start Guide](jarvis_v2/QUICK_START.md) - Get started in 5 minutes
- [🏗️ Architecture Overview](jarvis_v2/SYSTEM_ARCHITECTURE_ANALYSIS.md) - System design
- [✅ Feature Checklist](jarvis_v2/FEATURE_CHECKLIST.md) - Complete feature list
- [🗺️ Roadmap](jarvis_v2/ROADMAP.md) - Future development plans

### Technical Guides
- [🛠️ Setup Guide](jarvis_v2/setup_enhanced.sh) - Automated setup
- [🔒 Security Guide](jarvis_v2/SECURITY_FIXES_COMPLETE.md) - Security features
- [🧪 Testing Guide](jarvis_v2/tests/README.md) - Run tests
- [🎨 Frontend Guide](jarvis_v2/frontend/NEWUI_README.md) - UI development

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     JARVIS AI System                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │   Frontend   │◄────►│  WebSocket   │◄────►│ Backend  │ │
│  │  React + TS  │      │    Server    │      │  Python  │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│                                                      │      │
│  ┌─────────────────────────────────────────────────┘      │
│  │                                                          │
│  ├─► 🧠 Brain Service (LLM Integration)                   │
│  ├─► 💾 Memory System (RAG + Vector Store)                │
│  ├─► 🤖 Multi-Agent Coder                                 │
│  ├─► 🏗️ Autonomous Architect                             │
│  ├─► 🔒 Security Filter                                   │
│  ├─► ⚠️ Risk Engine                                       │
│  ├─► 📝 Reflection System                                 │
│  ├─► 🔊 TTS Service                                       │
│  └─► 🛠️ Tool Server (Node.js)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend
- **Runtime**: Python 3.8+
- **Framework**: Flask + WebSocket
- **AI/ML**: 
  - OpenAI GPT-4o-mini / Google Gemini 2.0 Flash
  - Sentence Transformers (Embeddings)
  - FAISS (Vector Search)
- **Data Processing**: 
  - PyPDF2 (PDF parsing)
  - python-docx (Word documents)
  - BeautifulSoup4 (Web scraping)

#### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Build Tool**: Vite
- **Real-time**: WebSocket API

#### Tools & Automation
- **Browser Automation**: Playwright
- **System Control**: AppleScript (macOS)
- **Package Management**: pip, npm

---

## 📂 Project Structure

```
jarvis-ai-assistant-/
├── jarvis_v2/                    # Main application
│   ├── api/                      # API Layer
│   │   ├── gui_bridge.py        # GUI communication
│   │   └── websocket_server_enhanced.py
│   ├── core/                     # Core AI Components
│   │   ├── brain_service.py     # LLM integration
│   │   ├── memory_system.py     # Long-term memory
│   │   ├── multi_agent_coder.py # Code generation
│   │   ├── autonomous_architect.py
│   │   ├── rag_engine.py        # RAG implementation
│   │   ├── tts_service.py       # Text-to-Speech
│   │   ├── security_filter.py   # Security layer
│   │   ├── risk_engine.py       # Risk assessment
│   │   └── ...                  # 20+ modules
│   ├── frontend/                 # React UI
│   │   ├── src/
│   │   │   ├── components/      # React components
│   │   │   ├── hooks/           # Custom hooks
│   │   │   ├── services/        # Business logic
│   │   │   └── styles/          # CSS/Tailwind
│   │   └── package.json
│   ├── tools/                    # Node.js Tools
│   │   └── server.js            # Tool execution server
│   ├── tests/                    # Test Suite
│   ├── data/                     # User data
│   │   ├── memory/              # Memory storage
│   │   └── learning/            # Learning data
│   ├── .env.example             # Environment template
│   ├── start.sh                 # Start script
│   ├── stop.sh                  # Stop script
│   └── setup_enhanced.sh        # Setup automation
└── README.md                     # This file
```

---

## 🎮 Usage Examples

### Web Interface

1. Open http://localhost:5174
2. Type your command or question
3. Watch JARVIS think and execute
4. Get real-time feedback

### API Usage

```python
import requests

# Send a command
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "message": "Open Spotify and play some jazz",
        "mode": "command"
    }
)

result = response.json()
print(result['response'])
```

### WebSocket Integration

```javascript
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('JARVIS:', data.message);
};

ws.send(JSON.stringify({
  type: 'command',
  message: 'What is the weather like?'
}));
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...          # OpenAI API key
GEMINI_API_KEY=...             # Google Gemini API key (alternative)

# Optional
PORT=8000                       # Backend port
WS_PORT=8001                    # WebSocket port
FRONTEND_PORT=5174              # Frontend port
LOG_LEVEL=INFO                  # Logging level
ENABLE_TTS=true                 # Text-to-Speech
TTS_VOICE=Daniel                # TTS voice name
```

---

## 🛠️ Management Commands

```bash
# Start all services
bash start.sh

# Stop all services
bash stop.sh

# Check status
bash status.sh

# View logs
tail -f jarvis_v2/logs/backend.log
tail -f jarvis_v2/logs/websocket.log

# Run tests
cd jarvis_v2/tests
bash run_bugfix_tests.sh
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
lsof -ti:5174 | xargs kill -9
```

### API Key Issues
- Verify `.env` file exists and contains valid API key
- Check API key format (OpenAI starts with `sk-proj-`)
- Ensure no extra spaces or quotes

### Module Not Found
```bash
# Reinstall dependencies
cd jarvis_v2
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend Build Errors
```bash
cd jarvis_v2/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 🗺️ Roadmap

### ✅ Completed (v2.0)
- [x] Multi-agent architecture
- [x] RAG engine with document processing
- [x] WebSocket real-time communication
- [x] Security and risk assessment
- [x] Text-to-Speech integration
- [x] Modern React UI
- [x] Comprehensive testing suite

### 🚧 In Progress
- [ ] Multi-platform support (Windows, Linux)
- [ ] Voice input (Speech-to-Text)
- [ ] Plugin system
- [ ] Docker containerization

### 🔮 Future Plans
- [ ] Multi-user support
- [ ] Cloud deployment
- [ ] Mobile app (React Native)
- [ ] Advanced personalization
- [ ] Integration marketplace

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/jarvis-ai-assistant-.git
cd jarvis-ai-assistant-/jarvis_v2

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Yakup Ayata

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- Inspired by **Iron Man's JARVIS**
- Built with ❤️ by [Yakup Ayata](https://github.com/yakup-ayata)
- Special thanks to the open-source community
- Powered by OpenAI and Google Gemini

---

## 📧 Contact

- **GitHub**: [@yakup-ayata](https://github.com/yakup-ayata)
- **Repository**: [jarvis-ai-assistant-](https://github.com/yakup-ayata/jarvis-ai-assistant-)
- **Issues**: [Report a Bug](https://github.com/yakup-ayata/jarvis-ai-assistant-/issues)

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

**Made with 🤖 and ❤️**

</div>
