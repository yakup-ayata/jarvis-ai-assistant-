# JARVIS V2 - Quick Start Guide

## 🚀 Hızlı Başlangıç

### 1. Sistemi Başlat
```bash
cd jarvis_v2
./start.sh
```

Bu komut otomatik olarak başlatır:
- ✅ Ollama LLM Server (port 11434)
- ✅ Tool Server (port 8002)
- ✅ WebSocket Server (port 8001)
- ✅ Frontend UI (port 5173)

### 2. Tarayıcıda Aç
```
http://localhost:5173
```

### 3. JARVIS ile Konuş!
- "Open Instagram"
- "Create a React component"
- "What's the weather?"
- "Write a Python function to sort a list"

---

## 🛑 Sistemi Durdur
```bash
./stop.sh
```

---

## 📊 Sistem Durumunu Kontrol Et
```bash
./status.sh
```

---

## 🧠 AI Modelleri

JARVIS otomatik olarak en uygun modeli seçer:

| Model | Kullanım | Boyut | Hız |
|-------|----------|-------|-----|
| llama3:latest | Genel sorular, planlama | 4.7 GB | ⚡ Hızlı |
| codellama:latest | Kod yazma, debugging | 3.8 GB | 🐢 Yavaş ama güçlü |

### Model Switching Örnekleri:
- "What time is it?" → llama3 (hızlı)
- "Write a sorting algorithm" → codellama (kod)
- "Plan a web app architecture" → llama3 (planlama)

---

## 🎯 Özellikler

### ✅ Tamamen Offline
- İnternet bağlantısı gerektirmez
- Tüm veriler local kalır
- API key gerektirmez

### ✅ Multi-Agent Coding
- Planner, Architect, Coder agents
- Paralel kod üretimi
- 40+ dil desteği

### ✅ Self-Healing
- Otomatik hata düzeltme
- Build error recovery
- Hot reload

### ✅ RAG Engine
- PDF, DOCX, Markdown desteği
- Semantic search
- Document Q&A

### ✅ Browser Automation
- Playwright entegrasyonu
- Form filling
- Web scraping

---

## 🔧 Engineering Mode

Frontend'te Engineering Mode'u aktifleştir:
1. Sağ üstteki 🔧 butonuna tıkla
2. Toggle'ı aç
3. JARVIS artık kod yazabilir!

Engineering Mode özellikleri:
- ✅ Multi-language code generation
- ✅ Fullstack project scaffolding
- ✅ Self-healing & optimization
- ✅ Autonomous development

---

## 📝 Örnek Komutlar

### Sistem Kontrolü
```
"Open Instagram"
"Close Chrome"
"Set volume to 50"
"What time is it?"
```

### Kod Yazma
```
"Create a React component for a login form"
"Write a Python function to calculate fibonacci"
"Scaffold a FastAPI project"
"Refactor this code"
```

### Döküman Sorguları
```
"What does the contract say about payment?"
"Summarize this document"
"Find information about pricing"
```

### Planlama
```
"Design a microservices architecture"
"Plan a CI/CD pipeline"
"Create a database schema for e-commerce"
```

---

## 🐛 Sorun Giderme

### Ollama çalışmıyor
```bash
ollama serve
```

### Port zaten kullanımda
```bash
./stop.sh
./start.sh
```

### Frontend build hatası
```bash
cd frontend
npm install
npm run build
```

### Python import hatası
```bash
pip install -r requirements.txt
```

---

## 📊 Sistem Gereksinimleri

- **OS**: macOS (M1/M2/M3 optimize)
- **RAM**: 8 GB minimum, 16 GB önerilen
- **Disk**: 20 GB boş alan
- **Python**: 3.9+
- **Node.js**: 18+
- **Ollama**: Latest

---

## 🎉 Başarılı Kurulum Kontrolü

Tüm servisler çalışıyorsa:
```bash
./status.sh
```

Çıktı:
```
📊 JARVIS V2 System Status
================================

Services:
  ✓ Ollama (Port: 11434)
  ✓ Tool Server (Port: 8002)
  ✓ WebSocket (Port: 8001)
  ✓ Frontend (Port: 5173)

Ollama Models:
  ✓ llama3:latest
  ✓ codellama:latest
```

---

## 📚 Daha Fazla Bilgi

- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - Detaylı sistem durumu
- [LANGUAGE_FRAMEWORK_SUPPORT.md](LANGUAGE_FRAMEWORK_SUPPORT.md) - Desteklenen diller
- [FEATURE_CHECKLIST.md](FEATURE_CHECKLIST.md) - Özellik listesi

---

**Hazır!** JARVIS V2 kullanıma hazır. Keyifli kodlamalar! 🚀
