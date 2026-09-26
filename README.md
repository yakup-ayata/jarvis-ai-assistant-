# 🤖 JARVIS AI Assistant

> Iron Man'deki JARVIS'i gerçek yapmaya çalışan bir öğrenci projesi. AI ile konuşabilir, komut verebilir ve bilgisayarınızı kontrol edebilirsiniz.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-React-61dafb.svg)](https://reactjs.org/)

**⚠️ Not:** Bu proje bir öğrenme projesidir. Production kullanımı için optimize edilmemiştir, bazı şeyler hala WIP (work in progress) durumunda.

---

## � Ne Yapıyor?

JARVIS ile konuşabilir, sorular sorabilir ve bilgisayarınızda komutlar çalıştırabilirsiniz. Iron Man filmlerinden ilham alınarak yapıldı!

**Yapabilecekleriniz:**
- 💬 Sohbet edip AI'dan fikir almak
- 🔍 Web'de araştırma yapıp özet almak  
- ⚡ Bilgisayarınızı kontrol etmek (uygulama aç, müzik çal, vs.)
- � PDF/Word dökümanlarınızı okuyup soru sorması
- 🗣️ Sesli yanıt alması (Text-to-Speech)

### Şu an Çalışan Özellikler

✅ Modern web arayüzü (React + TypeScript)  
✅ AI chat (OpenAI veya Gemini)  
✅ Web araması ve özet çıkarma  
✅ macOS sistem kontrolü  
✅ Gerçek zamanlı iletişim (WebSocket)  
✅ Sesli yanıt (TTS)  
✅ Doküman okuma (PDF, DOCX)

### Henüz Beta Olan Şeyler

⚠️ Çoklu-agent sistemi (bazen hata verebilir)  
⚠️ Uzun süreli hafıza (deneme aşamasında)  
⚠️ Otonom görev planlama  
⚠️ Sesli komut (henüz yok ama planlandı)

---

## 🎮 Nasıl Kullanılır?

JARVIS'e üç farklı şekilde komut verebilirsiniz:

### 💭 Fikir Sor (Opinion Mode)
Düşünce gerektiren sorular sorun:
```
"Yapay zeka hakkında ne düşünüyorsun?"
"En iyi programlama dili hangisi sence?"
```

### 📚 Bilgi İste (Information Mode)
Web'de araştırıp AI özeti alın:
```
"Tesla'nın son modelleri neler?"
"Python nedir açıkla"
"Quantum computing nasıl çalışır?"
```

### ⚡ Komut Ver (Command Mode)
Bilgisayarınızı kontrol edin:
```
"Instagram'ı aç"
"Ses seviyesini %50 yap"
"BMW ara ve ilk siteyi aç"
"Bohemian Rhapsody çal"
```

### � Denemek İstediklerim (Experimental)

Bunlar çalışıyor ama bazen hata verebilir:
- 🤖 Kod yazma ve test etme
- �️ Proje mimarisi planlama
- � Akıllı prompt oluşturma
- 🔍 Dokümanlarınızda anlam bazlı arama

---

## 🚀 Kurulum (5 Dakika)

### İhtiyaçlar

- Python 3.8 veya üstü
- Node.js 16 veya üstü  
- macOS (şimdilik sadece Mac destekleniyor)
- OpenAI veya Gemini API anahtarı

### Adım Adım Kurulum

**1. Projeyi İndir**
```bash
git clone https://github.com/yakup-ayata/jarvis-ai-assistant-.git
cd jarvis-ai-assistant-/jarvis_v2
```

**2. API Anahtarını Ekle**

`.env` dosyası oluştur ve API anahtarını ekle:
```bash
cp .env.example .env
nano .env  # veya favori editörünüzle açın
```

İçine şunu yaz (birini seç):
```bash
# OpenAI kullanacaksan (önerilen)
OPENAI_API_KEY=sk-proj-buraya-anahtarini-yaz

# Gemini kullanacaksan
GEMINI_API_KEY=buraya-anahtarini-yaz
```

**3. Her Şeyi Kur**
```bash
bash setup_enhanced.sh
```

Bu script şunları yapar:
- Python virtual environment oluşturur
- Tüm Python paketlerini yükler
- Frontend bağımlılıklarını yükler
- Her şeyin çalışır olduğunu kontrol eder

**4. Başlat!**
```bash
bash start.sh
```

**5. Tarayıcıda Aç**

http://localhost:5174 adresine git ve kullanmaya başla!

### Hızlı Test

Açıldıktan sonra şunları dene:
- "Merhaba!" yaz → AI cevap vermeli
- "Python nedir?" sor → Web araştırıp özet vermeli
- "Spotify'ı aç" de → Spotify açılmalı (varsa)

---

## 📚 Daha Fazla Bilgi

Projeyi daha iyi anlamak için:
- [QUICK_START.md](jarvis_v2/QUICK_START.md) - Hızlı başlangıç
- [ROADMAP.md](jarvis_v2/ROADMAP.md) - Gelecek planları
- [SYSTEM_STATUS.md](jarvis_v2/SYSTEM_STATUS.md) - Şu anki durum

---

## 🛠️ Teknolojiler

Projede kullanılan ana teknolojiler:

**Backend:**
- Python 3.8+ (ana dil)
- Flask (API server)
- WebSocket (gerçek zamanlı iletişim)
- OpenAI GPT-4o-mini / Gemini 2.0 Flash (AI)
- FAISS (vektör arama için)
- Sentence Transformers (embedding'ler için)

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS (stil)
- Zustand (state yönetimi)
- Vite (build tool)

**Diğer:**
- Playwright (browser otomasyonu)
- AppleScript (macOS kontrolü)

---

## 📂 Proje Yapısı

```
jarvis_v2/
├── core/              # AI beyni burda
│   ├── brain_service.py
│   ├── memory_system.py
│   ├── rag_engine.py
│   └── ...
├── api/               # Backend serverlar
│   ├── websocket_server_enhanced.py
│   └── gui_bridge.py
├── frontend/          # React UI
│   └── src/
│       ├── components/
│       ├── hooks/
│       └── services/
├── tools/             # Node.js tool server
├── tests/             # Testler
├── .env               # API anahtarların (GIT'e atma!)
├── start.sh           # Başlatma scripti
└── stop.sh            # Durdurma scripti
```

---

## 🐛 Sorun mu Var?

### "Command not found" hatası
```bash
# Script'lere çalıştırma izni ver
chmod +x start.sh stop.sh setup_enhanced.sh
```

### "Port already in use"
```bash
# Port'ları temizle
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9  
lsof -ti:5174 | xargs kill -9
```

### "API key not found"
- `.env` dosyasının `jarvis_v2` klasöründe olduğundan emin ol
- API anahtarının doğru formatta olduğunu kontrol et
- Boşluk veya tırnak olmadan yaz

### "Module not found" hatası
```bash
# Paketleri tekrar yükle
cd jarvis_v2
source .venv/bin/activate
pip install -r requirements.txt
```

Başka sorun mu var? [Issue aç](https://github.com/yakup-ayata/jarvis-ai-assistant-/issues) veya kod içindeki yorumlara bak!

---

## 🎯 Gelecek Planları

### ✅ Şu An Çalışıyor
- [x] Web arayüzü
- [x] AI chat (OpenAI/Gemini)
- [x] Web araması
- [x] macOS sistem kontrolü
- [x] Sesli yanıt (TTS)
- [x] Doküman okuma

### 🚧 Üzerinde Çalıştığım
- [ ] Sesli komut (wake word: "Hey Jarvis")
- [ ] Windows ve Linux desteği
- [ ] Daha iyi hafıza sistemi
- [ ] Plugin sistemi

### � Yapmak İstediklerim
- [ ] Mobil uygulama
- [ ] Bulut sürümü
- [ ] Çoklu kullanıcı desteği
- [ ] Daha akıllı öğrenme

---

## 🤝 Katkıda Bulunmak İster misin?

Pull request'ler ve öneriler her zaman hoş gelir! Bu benim bir öğrenci projesi olduğu için:
- Kod kalitesi mükemmel olmayabilir
- Bazı şeyler hala eksik
- Daha iyi yöntemler biliyorsan paylaş!

**Nasıl katkıda bulunabilirsin:**
1. Repo'yu fork'la
2. Yeni bir branch oluştur (`git checkout -b yeni-ozellik`)
3. Değişikliklerini yap
4. Commit'le (`git commit -m 'Harika özellik eklendi'`)
5. Push'la (`git push origin yeni-ozellik`)
6. Pull request aç

Veya sadece issue açıp fikrini paylaş!

---

## 🎓 Öğrendiklerim

Bu projeyi yaparken öğrendiğim şeyler:
- Multi-agent sistemler nasıl çalışır
- RAG (Retrieval-Augmented Generation) nasıl implement edilir
- WebSocket ile gerçek zamanlı iletişim
- React + TypeScript ile modern UI
- Python ile sistem kontrolü
- AI ile doğal dil işleme

Bu projeyi yapmakta bana yardımcı olan tüm açık kaynak projelere ve AI modellerine teşekkürler!

---

## ⚖️ Lisans

MIT License - istediğin gibi kullanabilirsin!

```
MIT License

Copyright (c) 2024 Yakup Ayata

Kısaca: İstediğin gibi kullan, değiştir, paylaş. Sadece copyright'ı değiştirme.
Detaylar için LICENSE dosyasına bak.
```

---

## � İletişim

- **GitHub**: [@yakup-ayata](https://github.com/yakup-ayata)
- **Repository**: [jarvis-ai-assistant-](https://github.com/yakup-ayata/jarvis-ai-assistant-)
- **Bug/Öneri**: [Issue Aç](https://github.com/yakup-ayata/jarvis-ai-assistant-/issues)

Sorular, öneriler veya sadece "merhaba" demek için issue açabilirsin!

---

## 💡 Son Notlar

Bu proje Iron Man filmlerinden esinlenerek, AI ve otomasyon öğrenmek için yapıldı. 

**Uyarı:** Production ortamında kullanmadan önce güvenlik testlerinden geçirmeyi unutma! API anahtarlarını kimseyle paylaşma.

Keyifli kodlamalar! 🚀

---

<div align="center">

### ⭐ Beğendiysen yıldız vermeyi unutma!

**Iron Man hayranlarına ve AI severlere ithaf olunur** 🤖❤️

*"Sometimes you gotta run before you can walk." - Tony Stark*

</div>
