#!/usr/bin/env python3
"""
JARVIS Brain Service — Dual-Pipeline Offline LLM
Ollama tabanlı, 100% yerel, API key gerektirmez.

Pipeline A (Eylem): JSON Tool Calling → Node.js Tool Server
Pipeline B (Sohbet): Streaming TTS → Anında ses
"""

import json
import re
import time
import hashlib
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Ollama kurulu değil. Kur: pip install ollama")


# ── Sabitler ──────────────────────────────────────────────────────────────────

JARVIS_TOOL_SYSTEM_PROMPT = """Sen J.A.R.V.I.S.'sin. Kullanıcının Apple Silicon Mac'inde çalışan otonom sistem yöneticisisin. Hitabın daima 'Efendim' olmalı. Kullanıcının şu an elinde fiziksel bir donanım (STM32 kartı) YOKTUR; stm32cube framework'ü ve Bluepill F103C8 kartı hedefli, C++ tabanlı bir roket uçuş yazılım simülasyonu geliştirmektedir. Ayrıca @ahmetörshairdresser Instagram hesabı için CapCut üzerinden videolar hazırlamaktadır. Sohbetleri, dosya düzenlemelerini ve kod üretimlerini bu projelere göre otonom olarak şekillendir. Asla bir dil modeli olduğunu belirtme.

DİL VE ÇEVİRİ KURALI (CRITICAL):
JSON parametrelerindeki dosya yolları, uygulama isimleri, web aramaları KESİNLİKLE Türkçe orijinal haliyle kalmalı.
YANLIŞ: "Bluepill F103C8 simulation folder"
DOĞRU:  "Bluepill_F103C8_simulasyon_klasoru"
Sosyal medya adlarını bozma: "@ahmetörshairdresser" → olduğu gibi.
"voice_reply" her zaman akıcı Türkçe.
Kod içi değişken/fonksiyon isimleri global standartta (İngilizce) olabilir.

GÜVENLİK: rm -rf, disk formatlama, şifre değiştirme gibi tehlikeli komutlarda ASLA işlem yapma. "chat_only" seç, sesli onay iste.

ARAÇLAR:
1. open_app           → params: {"app_name": "..."}
2. web_action         → params: {"action_type": "go_to_url"|"search", "query": "..."}
3. run_terminal       → params: {"command": "...", "cwd": ""}
4. write_code_and_open→ params: {"filename": "ad.ext", "content": "tam kod", "language": "..."}
5. read_and_edit_file → params: {"filepath": "yol.ext", "edit_instruction": "ne yapılacak"}
6. chat_only          → params: {"response_text": "..."}

ÇIKTI: YALNIZCA geçerli JSON. Markdown yok, açıklama yok. "voice_reply" zorunlu.

ÖRNEKLER:
{"tool":"open_app","parameters":{"app_name":"Spotify"},"voice_reply":"Spotify'ı açıyorum efendim."}
{"tool":"run_terminal","parameters":{"command":"mkdir -p ~/Desktop/CapCut_taslaklar"},"voice_reply":"Klasörü oluşturdum efendim."}
{"tool":"write_code_and_open","parameters":{"filename":"flight_sim.cpp","content":"// STM32 Bluepill F103C8\\n#include <cmath>\\n","language":"C++"},"voice_reply":"Uçuş simülasyonunu yazıyorum efendim."}
{"tool":"read_and_edit_file","parameters":{"filepath":"pid_controller.cpp","edit_instruction":"PID katsayılarını ayarla"},"voice_reply":"Dosyanızı inceleyip güncelliyorum efendim."}
{"tool":"chat_only","parameters":{"response_text":"..."},"voice_reply":"Türkçe yanıt efendim."}"""


# ── Enum'lar ──────────────────────────────────────────────────────────────────

class IntelligenceLevel(Enum):
    RULE_ENGINE = "rule"
    MINI_MODEL  = "mini"
    FULL_PLANNER = "full"


class QueryType(Enum):
    RESEARCH     = "research"
    OPINION      = "opinion"
    ACTION       = "action"
    PLANNING     = "planning"
    ANALYSIS     = "analysis"
    CONVERSATION = "conversation"


# ── BrainService ──────────────────────────────────────────────────────────────

class BrainService:
    """
    Dual-Pipeline Brain Service.

    Pipeline A → process_command()  : JSON Tool Calling (eylem)
    Pipeline B → chat_engine.py     : Streaming sohbet (ayrı modül)
    """

    def __init__(self, model: str = "llama3:latest"):
        self.model = model
        self.error_history: List[Dict] = []

        # Kısa süreli hafıza (son 10 tur)
        self.conversation_history: List[Dict] = []
        self.MAX_HISTORY = 10

        # Yanıt önbelleği
        self.response_cache: Dict[str, Dict] = {}
        self.CACHE_TTL    = 300   # saniye
        self.CACHE_MAX    = 100

        # Ollama timeout
        self.ollama_timeout = 30

        # Model seçimi
        self.available_models = {
            "mini":    "llama3:latest",
            "full":    "codellama:latest",
            "planner": "llama3:latest",
        }
        self.current_model_tier = "mini"

        # Kural motoru (0ms)
        self._build_rule_patterns()

        # İstatistik
        self.stats: Dict = {
            "rule_engine": 0, "mini_model": 0,
            "full_planner": 0, "total": 0, "query_types": {}
        }

    # ── Kural Motoru ──────────────────────────────────────────────────────────

    def _build_rule_patterns(self):
        self.rule_patterns = {
            # Uygulama aç — Türkçe iyelik eki + aç
            r"\b\w+['']?[ıiuü]\s+aç\b": {"action": "open_app",   "confidence": 0.95},
            r"\b(aç|open)\s+(spotify|chrome|safari|vscode|terminal|instagram|mail|notes|capcut|finder|xcode|stm32cubeide)\b":
                {"action": "open_app", "confidence": 0.95},
            r"\b(spotify|chrome|safari|vscode|terminal|instagram|mail|notes|capcut)\b.{0,15}\b(aç|open)\b":
                {"action": "open_app", "confidence": 0.95},
            # Uygulama kapat
            r"\b(kapat|close)\s+(spotify|chrome|safari|vscode|terminal|instagram|mail|notes)\b":
                {"action": "close_app", "confidence": 0.95},
            # Ses
            r"\b(ses|volume|sesi)\b.{0,15}\b(\d+)\b": {"action": "set_volume", "confidence": 0.95},
            r"\bses\s+\d+":                             {"action": "set_volume", "confidence": 0.95},
            r"\b\d+['']?e\s+(ayarla|getir)\b":          {"action": "set_volume", "confidence": 0.90},
            # Web
            r"\b(ara|search|google)\b.{0,60}":          {"action": "web_search", "confidence": 0.85},
            r"\b(git|gir|open)\b.{0,30}\b(https?://|www\.|\.(com|net|org|io|dev|tr))\b":
                {"action": "open_url", "confidence": 0.90},
            # Sistem
            r"\b(ekran görüntüsü|screenshot)\b":        {"action": "screenshot",  "confidence": 0.95},
            r"\bsaat kaç\b":                             {"action": "get_time",    "confidence": 0.95},
        }

    # ── Sınıflandırma ─────────────────────────────────────────────────────────

    def classify_query(self, command: str) -> QueryType:
        cmd = command.lower()

        code_kw = [
            "yaz", "write", "kod yaz", "write code", "oluştur", "create",
            "c++ yaz", "python yaz", "script", "program", "simülasyon",
            "simulation", "hesap makinesi", "calculator", "api yaz", "bot yaz",
        ]
        if any(k in cmd for k in code_kw):
            return QueryType.PLANNING

        edit_kw = [
            "düzenle", "güncelle", "ekle", "değiştir", "düzelt",
            "edit", "update", "modify", "refactor", "fix", "add to",
        ]
        if any(k in cmd for k in edit_kw):
            return QueryType.PLANNING

        terminal_kw = ["npm", "pip install", "git clone", "vite", "kur", "install", "setup"]
        if any(k in cmd for k in terminal_kw):
            return QueryType.ACTION

        research_kw = ["nedir", "anlat", "what is", "how does", "explain", "define", "tell me about"]
        if any(k in cmd for k in research_kw):
            return QueryType.RESEARCH

        opinion_kw = ["düşünüyorsun", "öneri", "tavsiye", "should i", "recommend", "suggest", "best", "opinion"]
        if any(k in cmd for k in opinion_kw):
            return QueryType.OPINION

        planning_kw = ["plan", "build", "develop", "design", "geliştir", "tasarla"]
        if any(k in cmd for k in planning_kw):
            return QueryType.PLANNING

        analysis_kw = ["analiz", "karşılaştır", "analyze", "compare", "evaluate"]
        if any(k in cmd for k in analysis_kw):
            return QueryType.ANALYSIS

        action_kw = ["open", "close", "run", "execute", "aç", "kapat", "çalıştır"]
        if any(k in cmd for k in action_kw):
            return QueryType.ACTION

        return QueryType.CONVERSATION

    def select_model(self, command: str, query_type: QueryType) -> str:
        cmd = command.lower()
        code_signals = [
            "write code", "kod yaz", "yaz", "implement", "refactor", "debug",
            "c++", "python", "javascript", "typescript", "java", "rust", "go",
            "html", "css", "script", "program", "simülasyon", "simulation",
        ]
        if any(k in cmd for k in code_signals):
            self.current_model_tier = "full"
            return self.available_models["full"]

        if query_type == QueryType.PLANNING or any(k in cmd for k in ["plan", "design", "architecture"]):
            self.current_model_tier = "planner"
            return self.available_models["planner"]

        self.current_model_tier = "mini"
        return self.available_models["mini"]

    # ── Hafıza ────────────────────────────────────────────────────────────────

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({
            "role": role, "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.conversation_history) > self.MAX_HISTORY:
            self.conversation_history = self.conversation_history[-self.MAX_HISTORY:]

    # ── Önbellek ──────────────────────────────────────────────────────────────

    def _cache_key(self, command: str) -> str:
        return hashlib.md5(command.lower().strip().encode()).hexdigest()

    def _get_cached(self, command: str) -> Optional[Dict]:
        key = self._cache_key(command)
        if key in self.response_cache:
            entry = self.response_cache[key]
            if time.time() - entry["ts"] < self.CACHE_TTL:
                print(f"💾 Cache hit: {command[:40]}")
                return entry["data"]
            del self.response_cache[key]
        return None

    def _set_cache(self, command: str, data: Dict):
        if len(self.response_cache) >= self.CACHE_MAX:
            oldest = min(self.response_cache, key=lambda k: self.response_cache[k]["ts"])
            del self.response_cache[oldest]
        self.response_cache[self._cache_key(command)] = {"data": data, "ts": time.time()}

    # ── Ana Giriş Noktası ─────────────────────────────────────────────────────

    def process_command(self, command: str, context: Dict = None) -> Dict:
        """
        Pipeline A: Komutu JSON Tool çağrısına dönüştür.
        Döndürür: { tool, parameters, voice_reply, action, ... }
        """
        t0 = time.time()
        self.stats["total"] += 1
        context = context or {}
        cmd_lower = command.lower().strip()

        # 1. Önbellek
        cached = self._get_cached(command)
        if cached:
            return {**cached, "from_cache": True,
                    "processing_time_ms": int((time.time() - t0) * 1000)}

        # 2. Sınıflandır
        query_type = self.classify_query(command)
        self.stats["query_types"][query_type.value] = \
            self.stats["query_types"].get(query_type.value, 0) + 1
        self.add_to_history("user", command)

        # 3. Kural motoru (0ms)
        for pattern, rule in self.rule_patterns.items():
            m = re.search(pattern, cmd_lower)
            if m:
                self.stats["rule_engine"] += 1
                target = m.group(1) if m.lastindex and m.lastindex >= 1 else ""
                result = {
                    "success": True, "tool": rule["action"],
                    "action": rule["action"], "target": target,
                    "parameters": {"app_name": target} if rule["action"] == "open_app" else {},
                    "voice_reply": f"Hemen yapıyorum efendim.",
                    "risk_level": "low", "method": "rule_engine",
                    "confidence": rule["confidence"],
                    "query_type": query_type.value,
                    "processing_time_ms": int((time.time() - t0) * 1000),
                }
                self.add_to_history("assistant", json.dumps(result))
                self._set_cache(command, result)
                return result

        # 4. LLM
        is_complex = any(k in cmd_lower for k in ["create", "build", "plan", "analyze", "develop"])
        model = self.select_model(command, query_type)
        orig_model = self.model
        self.model = model

        level = (IntelligenceLevel.FULL_PLANNER
                 if is_complex or query_type in (QueryType.PLANNING, QueryType.ANALYSIS)
                 else IntelligenceLevel.MINI_MODEL)

        if level == IntelligenceLevel.FULL_PLANNER:
            self.stats["full_planner"] += 1
        else:
            self.stats["mini_model"] += 1

        result = self._call_llm(command, level, context)
        self.model = orig_model

        result["processing_time_ms"] = int((time.time() - t0) * 1000)
        result["query_type"] = query_type.value
        self.add_to_history("assistant", json.dumps(result))
        if result.get("success"):
            self._set_cache(command, result)
        return result

    # ── LLM Çağrısı ──────────────────────────────────────────────────────────

    def _call_llm(self, command: str, level: IntelligenceLevel, context: Dict) -> Dict:
        if not OLLAMA_AVAILABLE:
            return {"success": False, "error": "Ollama kurulu değil.", "method": "unavailable"}

        ctx_str = ""
        if context:
            ctx_str = (
                f"\n[Bağlam] CPU:{context.get('cpu','?')}% "
                f"RAM:{context.get('ram','?')}% "
                f"Konuşma:{len(self.conversation_history)} tur"
            )

        user_msg = f"Kullanıcı komutu: {command}{ctx_str}"

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": JARVIS_TOOL_SYSTEM_PROMPT},
                    {"role": "user",   "content": user_msg},
                ],
                options={
                    "temperature": 0.1,
                    "num_predict": 600 if level == IntelligenceLevel.FULL_PLANNER else 350,
                },
            )
            raw = response["message"]["content"].strip()
        except Exception as e:
            return {"success": False, "error": str(e), "method": "llm_failed"}

        # Markdown fence temizle
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
            raw = raw.strip()

        # JSON çıkar
        js = raw[raw.find("{"):raw.rfind("}") + 1]
        if not js:
            return {"success": False, "error": "LLM JSON döndürmedi.", "raw": raw}

        try:
            parsed = json.loads(js)
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON parse hatası: {e}", "raw": js}

        tool   = parsed.get("tool") or parsed.get("action", "")
        params = parsed.get("parameters", {})

        TOOL_MAP = {
            "open_app":            "open_app",
            "web_action":          "web_action",
            "run_terminal":        "run_terminal",
            "write_code_and_open": "write_code_and_open",
            "read_and_edit_file":  "read_and_edit_file",
            "chat_only":           "chat_only",
        }
        action = TOOL_MAP.get(tool, tool)

        return {
            "success":        True,
            "tool":           tool,
            "action":         action,
            "parameters":     params,
            "voice_reply":    parsed.get("voice_reply", ""),
            "method":         "llm",
            "model":          self.model,
            "level":          level.value,
            # Geriye dönük uyumluluk
            "target":         (params.get("app_name") or params.get("query") or
                               params.get("filepath") or params.get("filename") or ""),
            "filename":       params.get("filename", ""),
            "content":        params.get("content", ""),
            "language":       params.get("language", ""),
            "filepath":       params.get("filepath", ""),
            "command":        params.get("command", ""),
            "cwd":            params.get("cwd", ""),
            "open_in_vscode": True,
            "risk_level":     parsed.get("risk_level", "low"),
            "confidence":     parsed.get("confidence", 0.9),
        }

    # ── Yardımcı Metodlar ─────────────────────────────────────────────────────

    def reflect_on_error(self, error: Dict) -> Dict:
        self.error_history.append(error)
        if not OLLAMA_AVAILABLE:
            return {"analysis": "Ollama yok", "suggestion": "Manuel kontrol et"}
        try:
            prompt = (
                f"JARVIS hata analisti olarak şu hatayı analiz et ve JSON döndür:\n"
                f"Eylem: {error.get('action')}\n"
                f"Hedef: {error.get('target')}\n"
                f"Hata: {error.get('error')}\n\n"
                '{"root_cause":"...","suggestion":"...","alternative":"..."}'
            )
            r = ollama.chat(model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            options={"temperature": 0.3, "num_predict": 300})
            raw = r["message"]["content"].strip()
            js = raw[raw.find("{"):raw.rfind("}") + 1]
            return json.loads(js) if js else {"analysis": raw}
        except Exception as e:
            return {"error": str(e)}

    def generate_goal_suggestion(self, context: Dict) -> Optional[Dict]:
        if not OLLAMA_AVAILABLE:
            return None
        try:
            prompt = (
                f"JARVIS otonom ajan. Sistem durumuna göre BİR hedef öner (JSON):\n"
                f"CPU:{context.get('cpu',0)}% RAM:{context.get('ram',0)}% "
                f"Disk:{context.get('disk',0)}% Hatalar:{len(self.error_history)}\n\n"
                '{"goal":"...","reasoning":"...","priority":"low|medium|high","actions":[]}\n'
                'Hedef gerekmiyorsa: {"goal":null}'
            )
            r = ollama.chat(model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            options={"temperature": 0.5, "num_predict": 300})
            raw = r["message"]["content"].strip()
            js = raw[raw.find("{"):raw.rfind("}") + 1]
            if js:
                g = json.loads(js)
                return g if g.get("goal") else None
        except Exception:
            pass
        return None

    def get_stats(self) -> Dict:
        return {
            **self.stats,
            "conversation_length": len(self.conversation_history),
            "error_count": len(self.error_history),
            "cache_size": len(self.response_cache),
        }
