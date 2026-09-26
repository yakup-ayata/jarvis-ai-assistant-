#!/usr/bin/env python3
"""
JARVIS Brain Service - Phase 1
Tiered Intelligence System: Rule Engine → Mini Model → Full Planner
OFFLINE: Uses Ollama for local LLM
"""

import os
import time
import json
from typing import Dict, Optional, Tuple, List
from enum import Enum
from dataclasses import dataclass
import re

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Ollama not installed. Install with: pip install ollama")

class IntelligenceLevel(Enum):
    """Intelligence tiers"""
    RULE_ENGINE = "rule"      # 0ms - Pattern matching
    MINI_MODEL = "mini"       # Fast - Simple reasoning
    FULL_PLANNER = "full"     # Slow - Complex multi-step

@dataclass
class QueryAnalysis:
    """Query analysis result"""
    level: IntelligenceLevel
    confidence: float
    reasoning: str
    estimated_time_ms: int

class BrainService:
    """
    Tiered Intelligence System
    Automatically routes queries to appropriate intelligence level
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Rule patterns for instant responses
        self.rule_patterns = {
            # System commands
            r"open\s+(instagram|spotify|chrome|safari|mail|notes)": {
                "action": "open_app",
                "confidence": 0.95
            },
            r"close\s+(instagram|spotify|chrome|safari|mail|notes)": {
                "action": "close_app",
                "confidence": 0.95
            },
            r"volume\s+(\d+)": {
                "action": "set_volume",
                "confidence": 0.95
            },
            r"mute|unmute": {
                "action": "toggle_mute",
                "confidence": 0.95
            },
            
            # Web navigation
            r"go to\s+([\w\.]+)": {
                "action": "open_url",
                "confidence": 0.90
            },
            r"search\s+(.+)": {
                "action": "web_search",
                "confidence": 0.85
            },
            
            # Simple queries
            r"what time|what's the time": {
                "action": "get_time",
                "confidence": 0.95
            },
            r"what date|what's the date": {
                "action": "get_date",
                "confidence": 0.95
            },
        }
        
        # Mini model triggers (medium complexity)
        self.mini_triggers = [
            "how do i",
            "can you",
            "please",
            "explain",
            "what is",
            "who is",
            "where is",
            "when is",
        ]
        
        # Full planner triggers (high complexity)
        self.full_triggers = [
            "create",
            "build",
            "develop",
            "analyze",
            "compare",
            "research",
            "plan",
            "strategy",
            "multiple steps",
            "first.*then",
            "after that",
        ]
        
        # Statistics
        self.stats = {
            "rule_engine": 0,
            "mini_model": 0,
            "full_planner": 0,
            "total_queries": 0
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze query and determine appropriate intelligence level
        """
        query_lower = query.lower().strip()
        
        # 1. Try Rule Engine (0ms)
        for pattern, rule in self.rule_patterns.items():
            if re.search(pattern, query_lower):
                return QueryAnalysis(
                    level=IntelligenceLevel.RULE_ENGINE,
                    confidence=rule["confidence"],
                    reasoning=f"Matched rule pattern: {pattern}",
                    estimated_time_ms=0
                )
        
        # 2. Check for Full Planner triggers
        for trigger in self.full_triggers:
            if trigger in query_lower:
                return QueryAnalysis(
                    level=IntelligenceLevel.FULL_PLANNER,
                    confidence=0.80,
                    reasoning=f"Complex task detected: '{trigger}'",
                    estimated_time_ms=2000
                )
        
        # 3. Check for Mini Model triggers
        for trigger in self.mini_triggers:
            if trigger in query_lower:
                return QueryAnalysis(
                    level=IntelligenceLevel.MINI_MODEL,
                    confidence=0.85,
                    reasoning=f"Medium complexity: '{trigger}'",
                    estimated_time_ms=500
                )
        
        # 4. Default to Mini Model for short queries
        if len(query_lower.split()) <= 5:
            return QueryAnalysis(
                level=IntelligenceLevel.MINI_MODEL,
                confidence=0.70,
                reasoning="Short query, using mini model",
                estimated_time_ms=500
            )
        
        # 5. Default to Full Planner for complex queries
        return QueryAnalysis(
            level=IntelligenceLevel.FULL_PLANNER,
            confidence=0.75,
            reasoning="Complex query, using full planner",
            estimated_time_ms=2000
        )
    
    def execute_rule_engine(self, query: str) -> Dict:
        """
        Execute rule-based response (0ms)
        """
        query_lower = query.lower().strip()
        
        for pattern, rule in self.rule_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                action = rule["action"]
                params = match.groups() if match.groups() else []
                
                return {
                    "success": True,
                    "action": action,
                    "params": params,
                    "response_time_ms": 0,
                    "level": "rule_engine"
                }
        
        return {
            "success": False,
            "error": "No rule matched",
            "level": "rule_engine"
        }
    
    def execute_mini_model(self, query: str) -> Dict:
        """
        Execute mini model (fast, simple reasoning)
        For now, this is a placeholder - will integrate actual model in Phase 7
        """
        start_time = time.time()
        
        # Placeholder: Simple keyword-based response
        query_lower = query.lower()
        
        response = {
            "success": True,
            "level": "mini_model",
            "query": query,
            "response": "Mini model response (placeholder)",
            "response_time_ms": int((time.time() - start_time) * 1000)
        }
        
        return response
    
    def execute_full_planner(self, query: str) -> Dict:
        """
        Execute full planner (complex, multi-step reasoning)
        For now, this is a placeholder - will integrate actual planner in Phase 5
        """
        start_time = time.time()
        
        # Placeholder: Will integrate with LLM
        response = {
            "success": True,
            "level": "full_planner",
            "query": query,
            "plan": [
                {"step": 1, "action": "analyze_query"},
                {"step": 2, "action": "generate_plan"},
                {"step": 3, "action": "execute_plan"}
            ],
            "response": "Full planner response (placeholder)",
            "response_time_ms": int((time.time() - start_time) * 1000)
        }
        
        return response
    
    def process_query(self, query: str) -> Dict:
        """
        Main entry point: Analyze and process query
        """
        self.stats["total_queries"] += 1
        
        # Analyze query
        analysis = self.analyze_query(query)
        
        # Route to appropriate level
        if analysis.level == IntelligenceLevel.RULE_ENGINE:
            self.stats["rule_engine"] += 1
            result = self.execute_rule_engine(query)
        elif analysis.level == IntelligenceLevel.MINI_MODEL:
            self.stats["mini_model"] += 1
            result = self.execute_mini_model(query)
        else:  # FULL_PLANNER
            self.stats["full_planner"] += 1
            result = self.execute_full_planner(query)
        
        # Add analysis info
        result["analysis"] = {
            "level": analysis.level.value,
            "confidence": analysis.confidence,
            "reasoning": analysis.reasoning,
            "estimated_time_ms": analysis.estimated_time_ms
        }
        
        return result
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        total = self.stats["total_queries"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "percentages": {
                "rule_engine": (self.stats["rule_engine"] / total) * 100,
                "mini_model": (self.stats["mini_model"] / total) * 100,
                "full_planner": (self.stats["full_planner"] / total) * 100
            }
        }

def main():
    """Test the brain service"""
    brain = BrainService()
    
    print("🧠 JARVIS Brain Service - Tiered Intelligence Test")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "open instagram",
        "volume 50",
        "what time is it",
        "how do i install python",
        "explain quantum computing",
        "create a web scraper that extracts data from multiple sites",
        "search for best restaurants",
        "go to google.com",
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        result = brain.process_query(query)
        
        analysis = result.get("analysis", {})
        print(f"   Level: {analysis.get('level', 'unknown')}")
        print(f"   Confidence: {analysis.get('confidence', 0):.2f}")
        print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
        print(f"   Time: {result.get('response_time_ms', 0)}ms")
        
        if result.get("action"):
            print(f"   Action: {result['action']}")
            if result.get("params"):
                print(f"   Params: {result['params']}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 Statistics:")
    stats = brain.get_stats()
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Rule engine: {stats['rule_engine']} ({stats['percentages']['rule_engine']:.1f}%)")
    print(f"   Mini model: {stats['mini_model']} ({stats['percentages']['mini_model']:.1f}%)")
    print(f"   Full planner: {stats['full_planner']} ({stats['percentages']['full_planner']:.1f}%)")

if __name__ == "__main__":
    main()


    def process_with_llm(self, query: str, level: IntelligenceLevel = IntelligenceLevel.MINI_MODEL) -> Dict:
        """
        Process query with local Ollama LLM (OFFLINE)
        """
        if not OLLAMA_AVAILABLE:
            return {
                "success": False,
                "error": "Ollama not available",
                "fallback": "rule_engine"
            }
        
        try:
            # Create prompt based on user's new JARVIS persona
            prompt = f"""SENİN ROLÜN:
Sen J.A.R.V.I.S.'sin. Kullanıcının macOS (Apple Silicon) tabanlı bilgisayarını tam yetkiyle kontrol eden, zeki, proaktif ve otonom bir yapay zeka asistanısın. Görevin, kullanıcının doğal dilde söylediği her cümleyi analiz etmek, niyetini anlamak ve bunu Node.js sunucusunun işleyebileceği kesin komutlara (JSON formatında) çevirmektir.

KARAKTERİN:
Kibar, net, analitik ve profesyonel. Kullanıcıya "Efendim" diye hitap et. Asla bir yapay zeka modeli olduğunu söyleme, sen bir sistem yöneticisisin.

ELİNDEKİ ARAÇLAR (TOOLS):
Aşağıdaki araçlardan sadece BİRİNİ seçerek işlem yapabilirsin:
1. "open_app": Bilgisayardaki bir uygulamayı açmak için. (Parametre: "app_name")
2. "web_action": Tarayıcıda bir site açmak veya arama yapmak için. (Parametreler: "action_type" [değeri "go_to_url" veya "search" olmalı], "query")
3. "run_terminal": İşletim sisteminde bir işlemi tetiklemek, dosya oluşturmak veya ayar değiştirmek için macOS zsh terminal komutu. (Parametre: "command")
4. "chat_only": Kullanıcı sadece soru soruyorsa, fikir istiyorsa veya bir bilgisayar eylemi gerekmiyorsa. (Parametre: "response_text")

GÜVENLİK KURALLARI (GUARDRAILS):
- Dosya silme (rm, trash), disk formatlama, sistem şifresi değiştirme veya tehlikeli olabilecek terminal komutları istendiğinde ASLA İŞLEM YAPMA. Bunun yerine "chat_only" aracını seç ve kullanıcıdan sesli onay iste ("Efendim, bu işlem sistem dosyalarını etkileyebilir. Onaylıyor musunuz?").

ÇIKTI FORMATI (ÇOK ÖNEMLİ):
Bana YALNIZCA geçerli bir JSON objesi döndüreceksin. Başında, sonunda veya içinde hiçbir açıklama, selamlama veya markdown (```json vb.) OLMAYACAK. Sadece ve sadece ham JSON döneceksin.

JSON ŞABLONU:
{{
  "tool": "secilen_arac_adi",
  "parameters": {{
    "param_adi": "param_degeri"
  }},
  "voice_reply": "Kullanıcıya okunacak sesli yanıtın (kısa, havalı ve öz)"
}}

Kkullanıcı komutu: {query}"""
            
            # Call Ollama
            response = ollama.chat(
                model='llama3:latest',
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.3,
                    'num_predict': 300
                }
            )
            
            # Parse response
            content = response['message']['content'].strip()
            
            # Try to extract JSON
            try:
                # Find JSON in response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Translate to backend format
                    backend_result = {
                        "success": True,
                        "llm_used": "ollama",
                        "model": "llama3:latest",
                        "voice_reply": result.get("voice_reply"),
                        "raw_json": result
                    }
                    
                    tool = result.get("tool")
                    params = result.get("parameters", {})
                    
                    if tool == "chat_only":
                        backend_result["action"] = None
                        backend_result["target"] = None
                        if not backend_result["voice_reply"]:
                            backend_result["voice_reply"] = params.get("response_text", "")
                    elif tool == "open_app":
                        backend_result["action"] = "open_app"
                        backend_result["target"] = params.get("app_name")
                    elif tool == "web_action":
                        action_type = params.get("action_type")
                        backend_result["action"] = "open_url" if action_type == "go_to_url" else "web_search"
                        backend_result["target"] = params.get("query")
                    elif tool == "run_terminal":
                        backend_result["action"] = "execute_command"
                        backend_result["target"] = params.get("command")
                        backend_result["risk_level"] = "high" # Require approval for safety
                    else:
                        backend_result["action"] = tool
                        backend_result["target"] = str(params)
                    
                    return backend_result
                else:
                    return {
                        "success": True,
                        "action": None,
                        "raw_response": content,
                        "llm_used": "ollama",
                        "model": "llama3:latest",
                        "voice_reply": content
                    }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "action": None,
                    "raw_response": content,
                    "llm_used": "ollama",
                    "model": "llama3:latest",
                    "parse_error": "Could not parse JSON",
                    "voice_reply": "Efendim, işlem sonucunu çözümleyemedim."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": "rule_engine"
            }
    
    def process_command(self, command: str) -> Dict:
        """
        Main entry point: Process command with appropriate intelligence level
        """
        start_time = time.time()
        
        # Analyze query
        analysis = self.analyze_query(command)
        
        # Update stats
        self.stats["total_queries"] += 1
        
        # Route to appropriate handler
        if analysis.level == IntelligenceLevel.RULE_ENGINE:
            self.stats["rule_engine"] += 1
            result = self._execute_rule(command, analysis)
        
        elif analysis.level == IntelligenceLevel.MINI_MODEL:
            self.stats["mini_model"] += 1
            result = self.process_with_llm(command, IntelligenceLevel.MINI_MODEL)
        
        else:  # FULL_PLANNER
            self.stats["full_planner"] += 1
            result = self.process_with_llm(command, IntelligenceLevel.FULL_PLANNER)
        
        # Add metadata
        result['processing_time_ms'] = int((time.time() - start_time) * 1000)
        result['intelligence_level'] = analysis.level.value
        result['confidence'] = analysis.confidence
        
        return result
    
    def _execute_rule(self, command: str, analysis: QueryAnalysis) -> Dict:
        """Execute rule-based command (instant)"""
        command_lower = command.lower().strip()
        
        for pattern, rule in self.rule_patterns.items():
            match = re.search(pattern, command_lower)
            if match:
                return {
                    "success": True,
                    "intent": rule["action"],
                    "action": rule["action"],
                    "target": match.group(1) if match.groups() else None,
                    "risk_level": "low",
                    "method": "rule_engine"
                }
        
        return {
            "success": False,
            "error": "No matching rule found"
        }
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return self.stats.copy()


# Test function
if __name__ == "__main__":
    print("🧠 JARVIS Brain Service - Offline LLM Test")
    print("=" * 50)
    
    brain = BrainService()
    
    test_commands = [
        "open instagram",
        "search for python tutorials",
        "what time is it",
        "create a plan to learn machine learning",
    ]
    
    for cmd in test_commands:
        print(f"\n📝 Command: {cmd}")
        result = brain.process_command(cmd)
        print(f"✓ Result: {json.dumps(result, indent=2)}")
    
    print(f"\n📊 Stats: {brain.get_stats()}")
