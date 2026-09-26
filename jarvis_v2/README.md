# 🤖 JARVIS Agent - Tam Bilgisayar Kontrolü

Akıllı AI asistan - Her türlü komutu anlayıp, plan oluşturup, adım adım çalıştırır.

## 🎯 Özellikler

### 3 Ana Fonksiyon:

1. **💭 GÖRÜŞ (Opinion)** - Düşünce ve fikir soruları
   - "Yapay zeka hakkında ne düşünüyorsun?"
   - "Sence en iyi programlama dili hangisi?"

2. **📚 BİLGİ (Information)** - Web araştırması + AI sentezi
   - "Tesla hakkında bilgi ver"
   - "Python nedir?"
   - "BMW'nin yeni modelleri neler?"

3. **⚡ KOMUT (Command)** - Sistem kontrolü ve otomasyon
   - "Instagram'ı aç"
   - "Ses seviyesini %50 yap"
   - "BMW arat ve ilk siteye git"
   - "Bohemian Rhapsody çal"

## 📁 Proje Yapısı

```
jarvis_v2/
├── api/
│   ├── jarvis_agent.py      # Ana backend (Flask)
│   └── websocket_server.py  # WebSocket sunucusu
├── frontend/                 # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── hooks/
│   └── package.json
├── data/                     # Konuşma geçmişi ve hafıza
├── logs/                     # Sistem logları
├── .env                      # API anahtarları
├── start_agent.sh           # Tüm sistemi başlat
└── README.md

Toplam: ~20 dosya (gereksiz 200+ dosya temizlendi)
```

## 🚀 Kurulum

### 1. API Anahtarı Ekle

`.env` dosyasını düzenle:

```bash
# Seçenek 1: OpenAI (Önerilen)
OPENAI_API_KEY=sk-proj-your-key-here

# Seçenek 2: Gemini
GEMINI_API_KEY=your-gemini-key-here
```

### 2. Bağımlılıkları Yükle

```bash
# Python bağımlılıkları
pip3 install flask flask-cors python-dotenv requests duckduckgo-search

# Frontend bağımlılıkları
cd frontend
npm install
cd ..
```

### 3. Sistemi Başlat

```bash
bash start_agent.sh
```

Servisler:
- 🧠 Backend: http://localhost:8000
- 🔌 WebSocket: ws://localhost:8001/ws
- 🎨 Frontend: http://localhost:5174

## 💻 Kullanım

### Web Arayüzü
http://localhost:5174 adresine git ve konuşmaya başla!

### API Kullanımı

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"message": "Instagram'ı aç"}
)

print(response.json())
```

## 🔧 Teknik Detaylar

### Backend (jarvis_agent.py)
- **Framework**: Flask
- **LLM**: Gemini 2.0 Flash (fallback: OpenAI GPT-4o-mini)
- **Web Search**: DuckDuckGo
- **Planlama**: LLM-powered execution planning
- **Komutlar**: macOS AppleScript + subprocess

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Real-time**: WebSocket

### Desteklenen Komutlar
- ✅ Uygulama açma (Instagram, Spotify, vb.)
- ✅ Web sitesi açma
- ✅ Web araması
- ✅ Müzik kontrolü (Spotify, Apple Music)
- ✅ Ses seviyesi kontrolü
- ✅ Ekran görüntüsü
- ✅ Terminal komutları

## 🐛 Sorun Giderme

### "I'm having trouble understanding that command"
- API anahtarını kontrol et (`.env` dosyası)
- Backend loglarına bak: `tail -f logs/backend.log`

### Port zaten kullanımda
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
lsof -ti:5174 | xargs kill -9
```

### Gemini API kotası doldu
- OpenAI API anahtarı ekle (otomatik fallback)
- Veya birkaç saat bekle (günlük kota sıfırlanır)

## 📊 Sistem Durumu

```bash
# Backend logları
tail -f logs/backend.log

# WebSocket logları
tail -f logs/websocket.log

# Çalışan servisler
lsof -i :8000,8001,5174
```

## 🎯 Gelecek Özellikler

- [ ] Ses kontrolü (wake word detection)
- [ ] Daha fazla platform desteği (Windows, Linux)
- [ ] Gelişmiş hafıza sistemi
- [ ] Plugin sistemi
- [ ] Multi-user desteği

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

---

**Not**: Bu proje macOS için optimize edilmiştir. Diğer platformlar için komutlar uyarlanmalıdır.
