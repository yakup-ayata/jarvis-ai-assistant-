#!/usr/bin/env python3
"""
JARVIS Chat Engine — Streaming Sohbet Hattı

Özellikler:
- Ollama stream=True ile kelime kelime yanıt
- Cümle sınırlarında (. ! ? \n) TTS'e gönderim
- Son 10 mesajlık conversation_history (context window)
- JARVIS persona + kullanıcı proje bağlamı
"""

import re
from typing import Generator, List, Dict, Optional

try:
    import ollama as _ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# ── Cümle sonu karakterleri ────────────────────────────────────────────────────
_SENTENCE_END = re.compile(r'(?<=[.!?…])\s+|(?<=\n)')

# ── JARVIS Sistem Promptu ──────────────────────────────────────────────────────
JARVIS_SYSTEM_PROMPT = """Sen J.A.R.V.I.S.'sin — kullanıcının Apple Silicon Mac'inde çalışan kişisel yapay zeka sistem yöneticisi ve sağ kolusun.

KARAKTERİN:
- Kısa, net, zeki ve hafif alaycı ama son derece saygılı.
- Kullanıcıya her zaman "Efendim" diye hitap et.
- Asla bir yapay zeka modeli olduğunu söyleme; sen bir sistem yöneticisisin.
- Gereksiz uzun açıklamalar yapma. Özlü, vurucu cümleler kur.
- Yeri geldiğinde İngilizce teknik terimler kullanabilirsin ama yanıt dili Türkçe olsun.

KULLANICININ PROJE BAĞLAMI (biliyormuş gibi davran, sormadan kullan):
- Bluepill F103C8 kartı ve STM32CubeIDE framework'ü kullanarak C++ ile roket uçuş kontrol simülasyonu geliştiriyor (fiziksel donanım olmadan, yazılım simülasyonu).
- Orta irtifa roket projeleri ve uçuş yönetim sistemleri (FMS) üzerinde çalışıyor; sensör füzyonu, PID kontrolcü ve IMU entegrasyonu konularında deneyimli.
- Ahmet Örs (@ahmetörshairdresser) için CapCut'ta video kurguları yapıyor; renk düzenleme ve montaj işleri var.
- Fitness ve carb-cycling hedefleri var; beslenme ve antrenman planlamasına önem veriyor.
- J.A.R.V.I.S. v2 otonom ajan projesini geliştiriyor (Python FastAPI + Node.js + React + Ollama).
- macOS Apple Silicon (M serisi) kullanıyor.

SOHBET KURALLARI:
- Teknik sorularda doğrudan cevap ver; "Tabii ki!" veya "Harika soru!" gibi dolgu ifadeler kullanma.
- Kullanıcı bir hata veya sorun anlatıyorsa önce kök nedeni söyle, sonra çözümü.
- STM32/C++/roket konularında uzmanca yorum yap; bağlamı biliyormuş gibi davran.
- Sohbet geçmişini kullan; "az önce bahsettiğiniz gibi" tarzı bağlantılar kur.
- Carb-cycling veya fitness sorusu gelirse makro hesaplamalarına gir, genel tavsiye verme."""


class ChatEngine:
    """
    Streaming sohbet motoru.
    Her instance kendi conversation_history'sini tutar.
    """

    def __init__(self, model: str = "llama3:latest", max_history: int = 10):
        self.model = model
        self.max_history = max_history
        # [ {"role": "user"|"assistant", "content": "..."}, ... ]
        self.history: List[Dict[str, str]] = []

    # ── Public API ─────────────────────────────────────────────────────────────

    def stream_response(self, user_message: str) -> Generator[str, None, None]:
        """
        Kullanıcı mesajına streaming yanıt üret.
        Her yield: bir cümle (nokta/ünlem/soru işaretinde kesilir).
        Blocking — asyncio.to_thread içinde çağrılmalı.
        """
        if not OLLAMA_AVAILABLE:
            yield "Ollama kurulu değil efendim."
            return

        # Geçmişe ekle
        self.history.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
        messages += self.history[-self.max_history:]

        buffer        = ""
        full_response = ""

        try:
            stream = _ollama.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={"temperature": 0.65, "num_predict": 600},
            )

            for chunk in stream:
                token = chunk.get("message", {}).get("content", "")
                if not token:
                    continue
                buffer        += token
                full_response += token

                # Cümle sonu: nokta/ünlem/soru + boşluk veya satır sonu
                sentences = _split_sentences(buffer)
                if len(sentences) > 1:
                    for sentence in sentences[:-1]:
                        s = sentence.strip()
                        if s and len(s) > 2:   # çok kısa parçaları atla
                            yield s
                    buffer = sentences[-1]

            # Kalan buffer
            if buffer.strip():
                yield buffer.strip()

        except Exception as e:
            err = f"Bir sorun oluştu efendim: {str(e)}"
            yield err
            full_response = f"[ERROR] {str(e)}"

        # Yanıtı geçmişe ekle
        clean = full_response.strip()
        if clean and not clean.startswith("[ERROR]"):
            self.history.append({"role": "assistant", "content": clean})

        # Geçmişi kırp
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def add_to_history(self, role: str, content: str) -> None:
        """Dışarıdan geçmişe mesaj ekle (tool sonuçları için)."""
        self.history.append({"role": role, "content": content})

    def clear_history(self) -> None:
        """Konuşma geçmişini temizle."""
        self.history.clear()

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.history)


# ── Yardımcı ──────────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    """
    Metni cümlelere böl.
    Nokta/ünlem/soru işareti + boşluk veya satır sonu = cümle sonu.
    """
    parts = re.split(r'(?<=[.!?…])\s+|(?<=\n)', text)
    return parts if parts else [text]


# ── Singleton ─────────────────────────────────────────────────────────────────

_chat_engine: Optional[ChatEngine] = None


def get_chat_engine(model: str = "llama3:latest") -> ChatEngine:
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = ChatEngine(model=model)
    return _chat_engine
