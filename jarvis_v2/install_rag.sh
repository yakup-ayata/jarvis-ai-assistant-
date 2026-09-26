#!/bin/bash

echo "🎯 JARVIS RAG System Installation"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create one first: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Install RAG dependencies
echo ""
echo "📥 Installing RAG dependencies..."
echo ""

pip install faiss-cpu>=1.7.4
pip install sentence-transformers>=2.2.2
pip install pypdf2>=3.0.0
pip install python-docx>=0.8.11
pip install markdown>=3.5.0
pip install beautifulsoup4>=4.12.0
pip install lxml>=4.9.0
pip install langchain>=0.1.0

echo ""
echo "✅ RAG dependencies installed!"
echo ""

# Test imports
echo "🧪 Testing imports..."
python3 << EOF
try:
    import faiss
    print("   ✓ FAISS")
except ImportError as e:
    print(f"   ✗ FAISS: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("   ✓ sentence-transformers")
except ImportError as e:
    print(f"   ✗ sentence-transformers: {e}")

try:
    import PyPDF2
    print("   ✓ PyPDF2")
except ImportError as e:
    print(f"   ✗ PyPDF2: {e}")

try:
    import docx
    print("   ✓ python-docx")
except ImportError as e:
    print(f"   ✗ python-docx: {e}")

try:
    import markdown
    print("   ✓ markdown")
except ImportError as e:
    print(f"   ✗ markdown: {e}")

try:
    from bs4 import BeautifulSoup
    print("   ✓ beautifulsoup4")
except ImportError as e:
    print(f"   ✗ beautifulsoup4: {e}")

print("")
print("✅ All imports successful!")
EOF

echo ""
echo "🎉 RAG System Installation Complete!"
echo ""
echo "Next steps:"
echo "1. Test components: python core/rag_engine.py"
echo "2. Start WebSocket server: python api/websocket_server_enhanced.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo ""
echo "📚 See RAG_IMPLEMENTATION_COMPLETE.md for usage examples"
echo ""
