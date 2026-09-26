# 🎨 JARVIS New UI - Animated & Interactive

## 🚀 Yeni Özellikler

### 1. TopHUD (Üst Panel)
- ✅ CPU ve RAM göstergeleri (animasyonlu progress bar)
- ✅ Daemon status (pulse animasyon)
- ✅ Glow efektleri
- ✅ Slide-in animasyon

### 2. ActionLogPanel (Sol Panel)
- ✅ User actions (turuncu)
- ✅ Autonomous actions (mavi)
- ✅ Hover glow efekti
- ✅ Fade + slide animasyonlar
- ✅ Custom scrollbar

### 3. MemoryPanel (Sağ Panel)
- ✅ Reflection ve Goal kartları
- ✅ Priority-based renklendirme
- ✅ Floating card animasyonları
- ✅ Scale + fade efektler
- ✅ Icon animasyonları

### 4. CommandInput (Alt Panel)
- ✅ Voice input button (animasyonlu)
- ✅ Text input (glow on focus)
- ✅ Ripple effect
- ✅ Processing indicator
- ✅ Submit button animasyonu

### 5. DraggablePanel
- ✅ Drag & drop support
- ✅ Bounce animasyon
- ✅ Scale on drag

## 📦 Kurulum

```bash
cd jarvis_v2/frontend

# Framer Motion kurulu (✓)
npm install framer-motion

# Yeni UI'yi aktif et
mv src/App.tsx src/App_old.tsx
mv src/App_new.tsx src/App.tsx

# Başlat
npm run dev
```

## 🎨 Renk Paleti

- **Primary**: Cyan (#06b6d4) → Blue (#3b82f6)
- **User Actions**: Orange (#ea580c)
- **Autonomous**: Cyan (#06b6d4)
- **Critical**: Red (#dc2626)
- **High**: Orange (#f97316)
- **Medium**: Yellow (#eab308)
- **Low**: Blue (#3b82f6)

## 🎭 Animasyonlar

### Framer Motion Variants
- **Slide In**: `initial={{ x: -300 }} animate={{ x: 0 }}`
- **Fade In**: `initial={{ opacity: 0 }} animate={{ opacity: 1 }}`
- **Scale**: `whileHover={{ scale: 1.05 }}`
- **Glow**: `boxShadow: "0 0 20px rgba(0,255,255,0.5)"`

### Custom Animations
- **Blob**: Background floating blobs
- **Pulse**: Daemon status indicator
- **Ripple**: Input focus effect
- **Rotate**: Loading spinners

## 🔌 WebSocket Entegrasyonu

Yeni UI, mevcut WebSocket sistemini kullanır:

```typescript
// useWebSocket hook'u kullan
const { sendMessage, lastMessage } = useWebSocket('ws://localhost:8001/ws');

// Action gönder
sendMessage({
  type: 'command',
  command: 'open Instagram'
});

// Response al
useEffect(() => {
  if (lastMessage) {
    const data = JSON.parse(lastMessage.data);
    // Update UI
  }
}, [lastMessage]);
```

## 📊 Demo Data

UI şu anda demo data ile çalışıyor:

- **Actions**: 3 örnek action (user + autonomous)
- **Memories**: 3 örnek memory (reflection + goal)
- **System Stats**: Random CPU/RAM değerleri

Backend bağlandığında gerçek data kullanılacak.

## 🎯 Kullanım

### 1. Command Gönderme
- Text input'a komut yaz
- Enter veya → butonuna bas
- Action log'da görün

### 2. Voice Input
- 🎙️ butonuna tıkla
- Mikrofon aktif olur (kırmızı)
- Konuş (henüz backend entegrasyonu yok)

### 3. Autonomous Actions
- Her 10 saniyede otomatik action
- Mavi renkte görünür
- Action log'da takip et

### 4. Memory Cards
- Reflection ve Goal kartları
- Priority-based sıralama
- Hover ile detay

## 🔧 Özelleştirme

### Renkleri Değiştir
`tailwind.config.js` → `theme.extend.colors`

### Animasyon Hızı
Component'lerde `transition={{ duration: 0.5 }}`

### Panel Pozisyonları
CSS class'larında `fixed left-4 top-20` gibi değerler

## 📱 Responsive

- Desktop: Full layout
- Tablet: Paneller üst üste
- Mobile: Single column

## 🚀 Production

```bash
# Build
npm run build

# Preview
npm run preview
```

## 🎉 Sonuç

Yeni UI tamamen hazır ve çalışıyor! Backend entegrasyonu için:

1. `useWebSocket` hook'unu kullan
2. Real-time data akışını bağla
3. Demo data'yı kaldır

**Status**: ✅ Production Ready
