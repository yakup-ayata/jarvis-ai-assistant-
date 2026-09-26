#!/usr/bin/env python3
"""
JARVIS Enhanced WebSocket Server — Dual-Pipeline Mimarisi
Port 8001 | FastAPI + WebSocket

Pipeline A (Eylem)  : Intent Router → Brain Service → Tool Server (Node.js 8002)
Pipeline B (Sohbet) : Intent Router → Chat Engine → Streaming TTS
"""

import asyncio
import json
import psutil
import re
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Dict, Set

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

# ── Core modülleri ────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from audit_logger import get_audit_logger
from auth import get_auth_service
from autonomous_goals import AutonomousGoalGenerator
from brain_service_offline import BrainService
from chat_engine import get_chat_engine
from developer_brain import get_developer_brain
from gui_bridge import GUIBridge
from intent_router import route_intent
from jarvis_personality import JarvisPersonality
from memory_system import MemorySystem
from rag_engine import RAGEngine
from reflection_system import ReflectionSystem
from tts_service import get_tts_service


# ── Pydantic Modeller ─────────────────────────────────────────────────────────

class MsgType(str, Enum):
    USER_COMMAND    = "user_command"
    AUTHENTICATE    = "authenticate"
    COMMAND         = "command"
    APPROVE_ACTION  = "approve_action"
    DENY_ACTION     = "deny_action"
    GET_SUGGESTIONS = "get_suggestions"
    APPROVE_GOAL    = "approve_goal"
    REJECT_GOAL     = "reject_goal"
    GET_STATUS      = "get_status"
    GET_LOGS        = "get_logs"
    GET_DEBUG       = "get_debug"
    UPLOAD_DOCUMENT = "upload_document"
    LIST_DOCUMENTS  = "list_documents"
    DELETE_DOCUMENT = "delete_document"
    RAG_STATS       = "rag_stats"
    INTERRUPT_SPEECH= "interrupt_speech"


class WSMessage(BaseModel):
    type: MsgType
    message: str = Field(default="", max_length=10000)
    timestamp: str = Field(default="")

    @validator("message")
    def sanitize(cls, v):
        if not v:
            return v
        for bad in ["<script", "javascript:", "onerror=", "onclick="]:
            if bad in v.lower():
                raise ValueError("Geçersiz karakter tespit edildi.")
        return v.strip()


class AuthMsg(BaseModel):
    type: MsgType = MsgType.AUTHENTICATE
    token: str = Field(..., min_length=10)


class UserCmdMsg(WSMessage):
    type: MsgType = MsgType.USER_COMMAND
    context: Dict = Field(default_factory=dict)


class DocMsg(BaseModel):
    type: MsgType
    file_path: str = Field(default="")
    source: str = Field(default="")

    @validator("file_path", "source")
    def no_traversal(cls, v):
        if v and (".." in v or v.startswith("/")):
            raise ValueError("Geçersiz dosya yolu.")
        return v


# ── FastAPI ───────────────────────────────────────────────────────────────────

app = FastAPI(title="JARVIS WebSocket API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


# ── ConnectionManager ─────────────────────────────────────────────────────────

class ConnectionManager:
    """Tüm WebSocket bağlantılarını ve iş mantığını yönetir."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.authenticated: Dict[WebSocket, Dict] = {}

        # Servisler
        self.brain       = BrainService()
        self.memory      = MemorySystem()
        self.reflection  = ReflectionSystem()
        self.goal_gen    = AutonomousGoalGenerator()
        self.tts         = get_tts_service()
        self.personality = JarvisPersonality()
        self.rag         = RAGEngine()
        self.rag.set_llm(self.brain)
        self.gui_bridge  = GUIBridge()
        self.auth        = get_auth_service()
        self.audit       = get_audit_logger()
        self.chat_engine = get_chat_engine(model="llama3:latest")

        self._metrics_task = None

        print("✓ JARVIS WebSocket Server hazır (Dual-Pipeline)")

    # ── Bağlantı Yönetimi ─────────────────────────────────────────────────────

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.add(ws)
        print(f"✓ Bağlandı. Toplam: {len(self.active_connections)}")
        await self._send(ws, {
            "type": "connection", "status": "connected",
            "system_status": self.gui_bridge.get_system_status()
        })
        if not self._metrics_task or self._metrics_task.done():
            self._metrics_task = asyncio.create_task(self._broadcast_metrics())

    def disconnect(self, ws: WebSocket):
        self.active_connections.discard(ws)
        self.authenticated.pop(ws, None)
        print(f"✗ Ayrıldı. Toplam: {len(self.active_connections)}")

    # ── Metrik Yayını ─────────────────────────────────────────────────────────

    async def _broadcast_metrics(self):
        while self.active_connections:
            try:
                cpu  = psutil.cpu_percent(interval=1)
                mem  = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                await self._broadcast({"type": "metrics", "cpu": cpu,
                                        "ram": mem.percent, "disk": disk.percent})
                # Otonom hedef tetikleyiciler
                if cpu > 80:
                    await self._trigger_goal("cpu_high", {"cpu_percent": cpu})
                if mem.percent > 90:
                    await self._trigger_goal("memory_critical", {"memory_percent": mem.percent})
                elif mem.percent > 75:
                    await self._trigger_goal("memory_high", {"memory_percent": mem.percent})
                if disk.percent > 85:
                    await self._trigger_goal("disk_high", {"disk_percent": disk.percent})
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Metrik hatası: {e}")
                await asyncio.sleep(5)

    async def _trigger_goal(self, trigger: str, data: Dict):
        recent = [g for g in self.goal_gen.goals
                  if g.trigger == trigger and (time.time() - g.timestamp) < 300]
        if recent:
            return
        goal = self.goal_gen.generate_goal(trigger, data)
        if goal:
            await self._broadcast({
                "type": "goal", "title": goal.goal_description,
                "description": goal.reasoning, "priority": goal.priority.value,
                "requires_approval": goal.requires_approval,
                "goal_id": goal.id, "timestamp": "Şimdi"
            })

    # ── Mesaj Gönderme ────────────────────────────────────────────────────────

    async def _send(self, ws: WebSocket, msg: dict):
        try:
            if ws.client_state.name == "CONNECTED":
                await ws.send_json(msg)
        except Exception as e:
            print(f"Gönderme hatası: {e}")

    async def _broadcast(self, msg: dict):
        dead = set()
        for ws in self.active_connections:
            try:
                if ws.client_state.name == "CONNECTED":
                    await ws.send_json(msg)
                else:
                    dead.add(ws)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(ws)

    async def _speak(self, msg: dict):
        """Mesajı yayınla + TTS ile seslendir."""
        mtype = msg.get("type", "")
        text  = msg.get("message") or msg.get("error") or msg.get("title") or ""

        # Kişilik katmanı
        if mtype == "action" and text:
            text = self.personality.enhance_action(text)
            msg["message"] = text
        elif mtype == "error" and text:
            text = self.personality.enhance_error(text)
            msg["error"] = text
        elif mtype == "success" and text:
            text = self.personality.enhance_success(text)
            msg["message"] = text
        elif mtype == "goal":
            text = self.personality.enhance_goal(msg.get("title", ""))
            msg["title"] = text

        await self._broadcast(msg)

        if text and self.tts.enabled and self.tts.get_status()["engine_available"]:
            try:
                self.tts.speak(text, priority="normal")
            except Exception as e:
                print(f"TTS hatası: {e}")


    # ── Tool Server İletişimi ─────────────────────────────────────────────────

    async def _tool(self, action: str, target: str = "", params: Dict = None) -> Dict:
        """Tool Server'a tek istek gönder."""
        import aiohttp
        timeout = 120 if action in ("write_code_and_open", "run_terminal",
                                     "update_file_content", "read_and_edit_file") else 15
        payload = {"action": action, "target": target, "params": params or {}}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post("http://localhost:8002/action",
                                  json=payload,
                                  timeout=aiohttp.ClientTimeout(total=timeout)) as r:
                    return await r.json()
        except Exception as e:
            return {"success": False, "error": str(e), "note": "Tool Server çalışmıyor olabilir."}

    async def _execute(self, result: Dict) -> Dict:
        """LLM sonucunu Tool Server'a ilet."""
        action = result.get("action", "")
        params = result.get("parameters", {})

        if action == "write_code_and_open":
            return await self._tool("write_code_and_open", params.get("filename", ""),
                                    {"filename": params.get("filename"),
                                     "content":  params.get("content", ""),
                                     "open_in_vscode": True})
        if action == "run_terminal":
            return await self._tool("run_terminal", params.get("command", ""),
                                    {"command": params.get("command", ""),
                                     "cwd":     params.get("cwd", "")})
        if action == "web_action":
            atype = params.get("action_type", "search")
            query = params.get("query", "")
            real_action = "open_url" if atype == "go_to_url" else "web_search"
            return await self._tool(real_action, query)
        if action == "open_app":
            return await self._tool("open_app", params.get("app_name", ""),
                                    {"app_name": params.get("app_name", "")})

        # Genel
        target = (params.get("app_name") or params.get("query") or
                  params.get("filepath") or params.get("filename") or
                  result.get("target", ""))
        return await self._tool(action, target, params)

    # ── Pipeline B: Streaming Sohbet ──────────────────────────────────────────

    async def _pipeline_chat(self, ws: WebSocket, command: str,
                              user_id: str, timestamp: str):
        await self._broadcast({"type": "system_state", "state": "thinking",
                                "timestamp": timestamp})
        full_text = ""
        count = 0
        try:
            sentences = await asyncio.to_thread(
                lambda: list(self.chat_engine.stream_response(command))
            )
            await self._broadcast({"type": "system_state", "state": "acting",
                                    "timestamp": timestamp})
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                full_text += s + " "
                count += 1
                await self._broadcast({"type": "chat_chunk", "text": s,
                                        "index": count, "timestamp": timestamp})
                if self.tts.enabled and self.tts.get_status()["engine_available"]:
                    self.tts.speak(s, priority="normal")

            await self._broadcast({"type": "chat_complete",
                                    "full_text": full_text.strip(),
                                    "sentence_count": count,
                                    "timestamp": timestamp})
            self.memory.remember(
                content=f"Sohbet: {command[:80]} → {full_text[:120]}",
                entry_type="query",
                metadata={"user_id": user_id, "pipeline": "chat"},
                importance=0.4
            )
        except Exception as e:
            print(f"❌ Chat streaming hatası: {e}")
            await self._broadcast({"type": "error",
                                    "error": f"Sohbet hatası efendim: {e}"})
        finally:
            await self._broadcast({"type": "system_state", "state": "idle",
                                    "timestamp": timestamp})

    # ── Pipeline A: Eylem ─────────────────────────────────────────────────────

    async def _pipeline_action(self, ws: WebSocket, command: str,
                                context: Dict, user_id: str, timestamp: str):
        # RAG kontrolü
        if (any(k in command.lower() for k in
                ["document", "dosya", "what does", "according to", "contract", "report"])
                and len(self.rag.list_documents()) > 0):
            try:
                await self._speak({"type": "action",
                                    "message": "Belgelerinizi tarıyorum efendim...",
                                    "source": "system", "timestamp": timestamp})
                rag = await self.rag.query(command)
                self.memory.remember(f"RAG: {rag['answer'][:100]}", "action",
                                     {"sources": rag["sources"]}, 0.8)
                await self._speak({"type": "rag_answer", "message": rag["answer"],
                                    "sources": rag["sources"], "source": "system",
                                    "timestamp": timestamp})
                await self._broadcast({"type": "system_state", "state": "idle",
                                        "timestamp": timestamp})
                return
            except Exception as e:
                print(f"RAG hatası: {e}")

        # LLM
        await self._broadcast({"type": "system_state", "state": "thinking",
                                "timestamp": timestamp})
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self.brain.process_command, command,
                                  {"user_id": user_id, **context}),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            result = {"action": "chat_only", "tool": "chat_only",
                      "voice_reply": "Sistem yanıt vermekte zorlanıyor efendim.",
                      "parameters": {}, "risk_level": "low"}

        await self._broadcast({"type": "system_state", "state": "acting",
                                "timestamp": timestamp})
        print(f"✅ Brain: {result.get('tool','?')} | {result.get('voice_reply','')[:60]}")

        action = result.get("action", "")
        params = result.get("parameters", {})
        voice  = result.get("voice_reply") or "İşleniyor efendim..."

        # Sesli bildirim
        await self._speak({"type": "action", "message": voice,
                            "source": "system", "timestamp": timestamp})

        # Güvenlik: yüksek risk
        if result.get("risk_level") == "high":
            await self._broadcast({"type": "approval_request",
                                    "action": result, "command": command})
            await self._broadcast({"type": "system_state", "state": "idle",
                                    "timestamp": timestamp})
            return

        # chat_only
        if action == "chat_only":
            self.memory.remember(f"Chat: {command}", "query",
                                 {"user_id": user_id}, 0.4)
            await self._broadcast({"type": "system_state", "state": "idle",
                                    "timestamp": timestamp})
            return

        # read_and_edit_file
        if action == "read_and_edit_file":
            filepath = params.get("filepath") or result.get("filepath", "")
            instr    = params.get("edit_instruction", command)
            await self._do_read_edit(ws, instr, filepath, user_id, timestamp)
            await self._broadcast({"type": "system_state", "state": "idle",
                                    "timestamp": timestamp})
            return

        # Diğer eylemler
        exec_result = await self._execute(result)
        self.audit.log_command(user_id=user_id, command=command,
                               action=action, target=result.get("target", ""),
                               success=exec_result.get("success", False))
        print(f"🎬 Sonuç: {exec_result}")

        self.memory.remember(
            f"Eylem: {action} → {result.get('target','')}",
            "action",
            {"result": exec_result, "command": command},
            0.7 if exec_result.get("success") else 0.8
        )

        reflection = self.reflection.reflect_on_action(
            action=action, target=result.get("target", ""),
            outcome=exec_result
        )
        await self._broadcast({"type": "action",
                                "message": f"Tamamlandı: {command}",
                                "result": exec_result, "source": "system",
                                "timestamp": timestamp})
        if reflection:
            await self._broadcast({"type": "reflection",
                                    "title": f"Reflection: {action}",
                                    "content": reflection.analysis,
                                    "priority": "high" if not exec_result.get("success") else "medium",
                                    "timestamp": "Şimdi"})
        await self._broadcast({"type": "system_state", "state": "idle",
                                "timestamp": timestamp})

    # ── Dosya Okuma/Düzenleme (2 Aşamalı) ────────────────────────────────────

    async def _do_read_edit(self, ws: WebSocket, instruction: str,
                             filepath: str, user_id: str, timestamp: str):
        if not filepath:
            await self._speak({"type": "error",
                                "error": "Hangi dosyayı düzenleyeceğimi belirtmediniz efendim."})
            return

        await self._speak({"type": "action",
                            "message": "Dosyanızı inceliyorum efendim...",
                            "source": "system", "timestamp": timestamp})

        read = await self._tool("read_file_content", filepath, {"filepath": filepath})
        if not read.get("success") or read.get("error") == "FILE_NOT_FOUND":
            await self._speak({"type": "error",
                                "error": f"Dosya bulunamadı efendim: {filepath}"})
            return

        content  = read.get("content", "")
        filename = read.get("filename", filepath)
        print(f"📖 {filename}: {len(content)} karakter okundu")

        await self._speak({"type": "action",
                            "message": "Kodu analiz edip güncelliyorum efendim...",
                            "source": "system", "timestamp": timestamp})

        edit_prompt = (
            f"Sen JARVIS'sin, uzman bir programcısın. Kullanıcı mevcut bir dosyayı değiştirmek istiyor.\n\n"
            f"Dosya: {filename}\nMevcut içerik:\n```\n{content}\n```\n\n"
            f"Kullanıcı isteği: {instruction}\n\n"
            "Talimatlar:\n"
            "- TAMAMEN güncellenmiş dosya içeriğini döndür (sadece değişen kısımları değil).\n"
            "- Mevcut işlevselliği koru (açıkça kaldırılması istenmediği sürece).\n"
            "- YALNIZCA geçerli JSON döndür:\n"
            '{"updated_content":"tam güncellenmiş içerik","summary":"ne değişti","language":"dil"}'
        )

        try:
            import ollama as _ol
            import signal as _sig

            def _to(s, f): raise TimeoutError("LLM edit timeout")
            _sig.signal(_sig.SIGALRM, _to)
            _sig.alarm(60)
            r = _ol.chat(model=self.brain.model,
                         messages=[{"role": "user", "content": edit_prompt}],
                         options={"temperature": 0.2, "num_predict": 2000})
            _sig.alarm(0)
            raw = r["message"]["content"].strip()
        except Exception as e:
            await self._speak({"type": "error",
                                "error": f"LLM düzenleme hatası efendim: {e}"})
            return

        js = raw[raw.find("{"):raw.rfind("}") + 1]
        try:
            data = json.loads(js)
        except Exception:
            await self._speak({"type": "error",
                                "error": "LLM geçerli JSON döndürmedi efendim."})
            return

        new_content = data.get("updated_content", "")
        summary     = data.get("summary", "Dosya güncellendi")
        if not new_content:
            await self._speak({"type": "error",
                                "error": "LLM güncellenmiş içerik üretemedi efendim."})
            return

        write = await self._tool("update_file_content", filepath,
                                  {"filepath": filepath, "new_content": new_content,
                                   "open_in_vscode": True})
        if write.get("success"):
            self.audit.log_command(user_id=user_id, command=instruction,
                                   action="read_and_edit_file", target=filepath, success=True)
            self.memory.remember(f"Düzenlendi {filename}: {summary}", "action",
                                 {"filepath": filepath, "summary": summary}, 0.8)
            await self._speak({"type": "success",
                                "message": f"{filename} güncellendi efendim. {summary}",
                                "source": "system", "timestamp": timestamp})
        else:
            await self._speak({"type": "error",
                                "error": f"Dosya yazılamadı efendim: {write.get('error','?')}"})


    # ── Ana Mesaj Yönlendirici ────────────────────────────────────────────────

    async def handle_message(self, ws: WebSocket, data: dict):
        mtype = data.get("type")

        # Auth bypass
        if mtype != "authenticate" and ws not in self.authenticated:
            await self._send(ws, {"type": "error",
                                   "error": "Kimlik doğrulama gerekli efendim.",
                                   "code": "AUTH_REQUIRED"})
            return

        try:
            if mtype == "authenticate":
                await self._auth(ws, AuthMsg(**data))

            elif mtype == "user_command":
                msg = UserCmdMsg(**data)
                await self._route_command(ws, msg)

            elif mtype == "interrupt_speech":
                self.tts.stop()
                await self._broadcast({"type": "system_state", "state": "idle"})
                print("🛑 Ses kesildi")

            elif mtype in ("upload_document", "delete_document"):
                doc = DocMsg(**data)
                if mtype == "upload_document":
                    await self._upload_doc(ws, doc)
                else:
                    await self._delete_doc(ws, doc)

            elif mtype == "list_documents":
                await self._send(ws, {"type": "documents_list",
                                       "documents": self.rag.list_documents()})
            elif mtype == "rag_stats":
                await self._send(ws, {"type": "rag_stats",
                                       "stats": self.rag.get_stats()})
            elif mtype == "get_status":
                await self._send(ws, {"type": "system_status",
                                       "status": self.gui_bridge.get_system_status()})
            elif mtype == "approve_goal":
                await self._approve_goal(ws, data)
            elif mtype == "reject_goal":
                gid = data.get("goal_id")
                if self.goal_gen.reject_goal(gid):
                    await self._broadcast({"type": "action",
                                            "message": "Hedef reddedildi efendim.",
                                            "source": "system"})
            else:
                await self._send(ws, {"type": "error",
                                       "error": f"Bilinmeyen mesaj tipi: {mtype}"})

        except ValueError as e:
            await self._send(ws, {"type": "error", "error": str(e),
                                   "code": "VALIDATION_ERROR"})
        except Exception as e:
            await self._send(ws, {"type": "error", "error": str(e),
                                   "code": "INTERNAL_ERROR"})

    # ── Yardımcı Handler'lar ──────────────────────────────────────────────────

    async def _auth(self, ws: WebSocket, msg: AuthMsg):
        payload = self.auth.verify_token(msg.token)
        if payload:
            self.authenticated[ws] = payload
            self.audit.log_authentication(payload.get("user_id"), True, "token")
            await self._send(ws, {"type": "authenticated",
                                   "user_id": payload.get("user_id"),
                                   "username": payload.get("username")})
        else:
            self.audit.log_authentication("unknown", False, "token")
            await self._send(ws, {"type": "error", "error": "Geçersiz token.",
                                   "code": "AUTH_FAILED"})

    async def _route_command(self, ws: WebSocket, msg: UserCmdMsg):
        command   = msg.message
        user_info = self.authenticated.get(ws, {})
        user_id   = user_info.get("user_id", "unknown")

        print(f"📨 Komut: {command}")
        await self._broadcast({"type": "system_state", "state": "listening",
                                "timestamp": msg.timestamp})
        self.memory.remember(command, "query",
                             {"source": "user", "user_id": user_id}, 0.6)

        intent = route_intent(command)
        print(f"🧭 Intent: {intent.upper()}")

        if intent == "chat":
            await self._pipeline_chat(ws, command, user_id, msg.timestamp)
        else:
            await self._pipeline_action(ws, command, msg.context,
                                         user_id, msg.timestamp)

    async def _upload_doc(self, ws: WebSocket, doc: DocMsg):
        try:
            await self._speak({"type": "action",
                                "message": "Belge işleniyor efendim..."})
            stats = await self.rag.add_document(doc.file_path)
            await self._speak({"type": "success",
                                "message": f"Belge eklendi: {stats['chunks']} parça efendim."})
        except Exception as e:
            await self._speak({"type": "error",
                                "error": f"Belge hatası efendim: {e}"})

    async def _delete_doc(self, ws: WebSocket, doc: DocMsg):
        try:
            n = self.rag.delete_document(doc.source)
            await self._speak({"type": "success",
                                "message": f"{n} parça silindi efendim."})
        except Exception as e:
            await self._speak({"type": "error",
                                "error": f"Silme hatası efendim: {e}"})

    async def _approve_goal(self, ws: WebSocket, data: dict):
        gid = data.get("goal_id")
        if self.goal_gen.approve_goal(gid, approved_by="user"):
            goal = self.goal_gen.get_goal_by_id(gid)
            self.goal_gen.start_goal(gid)
            for act in goal.actions:
                res = await self._tool(act.get("action", ""), act.get("target", ""))
                await self._broadcast({"type": "action",
                                        "message": f"Çalışıyor: {act.get('action')}",
                                        "result": res, "source": "autonomous"})
            self.goal_gen.complete_goal(gid, {"success": True})


# ── Singleton ─────────────────────────────────────────────────────────────────

manager = ConnectionManager()


# ── WebSocket Endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket bağlantı noktası.
    Local geliştirme: token olmadan otomatik auth.
    Production: ?token=JWT_TOKEN
    """
    await manager.connect(websocket)

    # Otomatik auth (local)
    if not token:
        default_token = manager.auth.create_default_token()
        payload = manager.auth.verify_token(default_token)
        manager.authenticated[websocket] = payload
    else:
        payload = manager.auth.verify_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Geçersiz token")
            return
        manager.authenticated[websocket] = payload

    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket hatası: {e}")
        manager.disconnect(websocket)


# ── HTTP Endpoint'ler ─────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "jarvis-websocket",
            "connections": len(manager.active_connections)}

@app.get("/status")
async def status():
    return manager.gui_bridge.get_system_status()


# ── Başlatma ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("🔌 JARVIS WebSocket Server — Dual-Pipeline")
    print("   ws://localhost:8001/ws")
    print("   http://localhost:8001/health")
    uvicorn.run(app, host="0.0.0.0", port=8001)
