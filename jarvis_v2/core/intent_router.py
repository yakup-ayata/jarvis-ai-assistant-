#!/usr/bin/env python3
"""
JARVIS Intent Router
~0.5s hızında niyet belirleyici.

Kural motoru önce çalışır (0ms).
Belirsiz durumlarda küçük bir LLM çağrısı yapılır (~300ms).

Döndürür:
  "action"  → JSON Tool Calling hattı
  "chat"    → Streaming sohbet hattı
"""

import re
from typing import Literal

IntentType = Literal["action", "chat"]

# ── Kural tabanlı hızlı eşleşmeler ────────────────────────────────────────────

# Kesinlikle eylem gerektiren kalıplar
_ACTION_PATTERNS = [
    # Uygulama kontrolü — "X'ı/i/u/ü aç/kapat" Türkçe ek yapısı
    r"\b(aç|kapat|başlat|durdur|open|close|launch|quit)\b.{0,40}\b(uygulama|app|program|spotify|chrome|safari|vscode|terminal|instagram|mail|notes|capcut|finder|xcode|stm32)\b",
    r"\b(spotify|chrome|safari|vscode|terminal|instagram|mail|notes|capcut|finder|xcode|stm32cubeide)\b.{0,20}\b(aç|kapat|open|close)\b",
    # Türkçe iyelik eki + aç/kapat: "CapCut'ı aç", "Spotify'ı aç"
    r"\b\w+['']?[ıiuü]\s+(aç|kapat)\b",
    r"\b\w+['']?[yı]\s+(aç|kapat)\b",
    # Ses / parlaklık — sayı veya yön kelimesi içeriyorsa eylem
    r"\b(ses|volume|parlaklık|brightness)\b.{0,20}\b(\d+|kıs|aç|artır|azalt|up|down|set|yükselt|düşür)\b",
    r"\b(sesi|volume)\b.{0,10}\b(\d+|kıs|aç|artır|azalt|kapat|yükselt|düşür)\b",
    r"\bses\s+\d+",   # "ses 50", "sesi 50'ye"
    r"\b\d+['']?e\s+(ayarla|getir|çek)\b",  # "50'ye ayarla"
    # Dosya / kod yazma
    r"\b(yaz|oluştur|create|write|yeni dosya|new file)\b.{0,60}\b\.(py|cpp|ts|tsx|js|html|css|go|rs|java|txt|md)\b",
    r"\b(kod yaz|write code|script yaz)\b",
    r"\b(klasör|folder|dizin|directory)\b.{0,30}\b(oluştur|create|yap|mkdir)\b",
    # Dosya düzenleme — uzantılı dosya adı içeriyorsa eylem
    r"\b(düzenle|güncelle|ekle|değiştir|refactor|fix|edit|update|modify)\b.{0,40}\b\.(py|cpp|ts|tsx|js|html|css|go|rs|java)\b",
    r"\b\w+\.(py|cpp|ts|tsx|js|html|css|go|rs|java)\b.{0,30}\b(düzenle|güncelle|ekle|değiştir|refactor|fix|edit|update)\b",
    # Terminal / kurulum
    r"\b(npm|pip|git|brew|yarn|cargo|go get)\b",
    r"\b(kur|install|setup|init|clone)\b.{0,30}\b(paket|package|repo|proje|project)\b",
    # Web gezinme
    r"\b(git|aç|open|gir|navigate)\b.{0,30}\b(https?://|www\.|\.(com|net|org|io|dev|tr))\b",
    r"\b(ara|search|google|arat)\b.{0,60}",
    # Sistem
    r"\b(ekran görüntüsü|screenshot|screencapture)\b",
    r"\b(wifi|bluetooth|uçak modu|airplane mode)\b.{0,20}\b(aç|kapat|toggle)\b",
    r"\b(pil|battery|şarj|charge)\b.{0,20}\b(durumu|status|göster|show)\b",
]

# Kesinlikle sohbet olan kalıplar
_CHAT_PATTERNS = [
    r"^(nasılsın|naber|ne haber|iyi misin|merhaba|selam|hey jarvis)\b",
    r"\b(anlat|açıkla|nedir|ne demek|hakkında|hakkında bilgi|explain|what is|tell me about)\b",
    r"\b(düşünüyorsun|düşünürsün|fikrin|görüşün|önerin|tavsiye|recommend|suggest|opinion)\b",
    r"\b(neden|niçin|nasıl çalışır|nasıl yapılır|why|how does|how to)\b",
    r"\b(karşılaştır|fark nedir|hangisi daha|compare|difference between|which is better)\b",
    r"\b(hata nerede|bug nerede|mantık hatası|logic error|debug|sorun nerede)\b",
    r"\b(teşekkür|sağ ol|thanks|thank you|harika|bravo|süper)\b",
    r"\b(şaka|fıkra|eğlenceli|komik|joke|funny)\b",
    # Karşılaştırma soruları (mu/mi ile biten)
    r"\b\w+\s+(mu|mi|mı|mü)\s+\w+\s+(mu|mi|mı|mü)\b",
]

_ACTION_RE = [re.compile(p, re.IGNORECASE) for p in _ACTION_PATTERNS]
_CHAT_RE   = [re.compile(p, re.IGNORECASE) for p in _CHAT_PATTERNS]


def route_intent(command: str) -> IntentType:
    """
    Kullanıcı komutunun niyetini belirle.
    Kural motoru yeterli değilse LLM'e sor (opsiyonel, şimdilik kural tabanlı).
    """
    cmd = command.strip()

    # 1. Eylem kalıplarını kontrol et
    for pattern in _ACTION_RE:
        if pattern.search(cmd):
            return "action"

    # 2. Sohbet kalıplarını kontrol et
    for pattern in _CHAT_RE:
        if pattern.search(cmd):
            return "chat"

    # 3. Belirsiz: kısa cümleler genellikle sohbet, uzunlar eylem
    word_count = len(cmd.split())
    if word_count <= 4:
        return "chat"   # "Nasılsın?", "Teşekkürler" gibi
    if word_count >= 10:
        return "chat"   # Uzun açıklama/soru cümleleri

    # 4. Default: eylem (güvenli taraf)
    return "action"
