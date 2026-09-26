#!/usr/bin/env python3
"""
JARVIS GUI Bridge - Phase 6
Connects GUI with core systems (daemon, goals, memory, etc.)
"""

import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from brain_service import BrainService
from risk_engine import RiskEngine, PermissionManager
from security_filter import SecurityFilter, RateLimiter
from memory_system import MemorySystem
from reflection_system import ReflectionSystem
from autonomous_goals import AutonomousGoalGenerator

class GUIBridge:
    """
    Bridge between GUI and core systems
    Provides unified API for frontend
    """
    
    def __init__(self):
        # Initialize core systems
        self.brain = BrainService()
        self.risk_engine = RiskEngine()
        self.permission_manager = PermissionManager()
        self.security_filter = SecurityFilter()
        self.rate_limiter = RateLimiter()
        self.memory = MemorySystem()
        self.reflection = ReflectionSystem()
        self.goal_generator = AutonomousGoalGenerator()
        
        # Tool server URL
        self.tool_server_url = "http://localhost:8002"
    
    async def process_user_command(self, command: str, user_id: str = "default") -> Dict:
        """
        Process user command through full pipeline
        """
        # 1. Rate limit check
        allowed, reason = self.rate_limiter.check_rate_limit(user_id)
        if not allowed:
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "reason": reason
            }
        
        # 2. Security check
        security_check = self.security_filter.check_input(command)
        if not security_check.is_safe:
            return {
                "success": False,
                "error": "Security threat detected",
                "threat_level": security_check.threat_level,
                "threats": security_check.threats_found
            }
        
        # 3. Store in memory
        self.memory.remember(command, "query", importance=0.6)
        
        # 4. Brain analysis
        brain_result = self.brain.process_query(command)
        
        # 5. If action needed, check risk
        if brain_result.get("action"):
            action = brain_result["action"]
            target = brain_result.get("params", [None])[0] if brain_result.get("params") else None
            
            # Risk analysis
            risk_analysis = self.risk_engine.analyze_action(action, target or "")
            
            # Check if approval needed
            if risk_analysis.requires_approval:
                approval_request = self.permission_manager.request_approval(
                    action, target or "", risk_analysis
                )
                
                if not approval_request.get("approved"):
                    # Return approval request to GUI
                    return {
                        "success": False,
                        "requires_approval": True,
                        "approval_request": approval_request,
                        "brain_result": brain_result
                    }
        
        # 6. Return result
        return {
            "success": True,
            "brain_result": brain_result,
            "context": self.memory.get_context(n=5)
        }
    
    def approve_action(self, action_hash: str, action: str, target: str) -> Dict:
        """
        User approves an action
        """
        self.permission_manager.approve_action(action_hash, action, target)
        
        return {
            "success": True,
            "message": "Action approved",
            "action": action,
            "target": target
        }
    
    def deny_action(self, action_hash: str, action: str, target: str) -> Dict:
        """
        User denies an action
        """
        self.permission_manager.deny_action(action_hash, action, target)
        
        return {
            "success": True,
            "message": "Action denied",
            "action": action,
            "target": target
        }
    
    def get_pending_approvals(self) -> List[Dict]:
        """
        Get all pending approval requests
        """
        # This would come from a queue in production
        # For now, return empty list
        return []
    
    def get_autonomous_suggestions(self) -> List[Dict]:
        """
        Get autonomous goal suggestions
        """
        pending_goals = self.goal_generator.get_pending_goals()
        
        suggestions = []
        for goal in pending_goals:
            suggestions.append({
                "id": goal.id,
                "description": goal.goal_description,
                "reasoning": goal.reasoning,
                "priority": goal.priority.value,
                "actions": goal.actions,
                "trigger": goal.trigger,
                "timestamp": datetime.fromtimestamp(goal.timestamp).isoformat()
            })
        
        return suggestions
    
    def approve_goal(self, goal_id: str) -> Dict:
        """
        Approve an autonomous goal
        """
        success = self.goal_generator.approve_goal(goal_id)
        
        if success:
            return {
                "success": True,
                "message": "Goal approved",
                "goal_id": goal_id
            }
        else:
            return {
                "success": False,
                "error": "Goal not found or already processed"
            }
    
    def reject_goal(self, goal_id: str) -> Dict:
        """
        Reject an autonomous goal
        """
        success = self.goal_generator.reject_goal(goal_id)
        
        if success:
            return {
                "success": True,
                "message": "Goal rejected",
                "goal_id": goal_id
            }
        else:
            return {
                "success": False,
                "error": "Goal not found or already processed"
            }
    
    def get_system_status(self) -> Dict:
        """
        Get overall system status
        """
        return {
            "brain": self.brain.get_stats(),
            "memory": self.memory.get_stats(),
            "reflection": self.reflection.get_stats(),
            "goals": self.goal_generator.get_stats(),
            "permissions": self.permission_manager.get_stats(),
            "rate_limits": self.rate_limiter.get_stats()
        }
    
    def get_debug_info(self, action: str = None) -> Dict:
        """
        Get debug information
        """
        if action:
            return {
                "action": action,
                "reflection": self.reflection.get_debug_info(action),
                "confidence": self.reflection.get_action_confidence(action),
                "recommendations": self.reflection.get_recommendations(action)
            }
        else:
            return {
                "system_status": self.get_system_status(),
                "recent_context": self.memory.get_context(n=10)
            }
    
    def get_logs(self, log_type: str = "all", n: int = 50) -> List[Dict]:
        """
        Get system logs
        """
        logs = []
        
        # Get recent memories as logs
        if log_type in ["all", "memory"]:
            recent = self.memory.short_term.get_recent(n)
            for entry in recent:
                logs.append({
                    "type": "memory",
                    "subtype": entry.type,
                    "content": entry.content,
                    "timestamp": datetime.fromtimestamp(entry.timestamp).isoformat(),
                    "importance": entry.importance
                })
        
        # Get recent reflections as logs
        if log_type in ["all", "reflection"]:
            recent_reflections = self.reflection.reflections[-n:]
            for reflection in recent_reflections:
                logs.append({
                    "type": "reflection",
                    "subtype": reflection.type.value,
                    "action": reflection.action,
                    "analysis": reflection.analysis,
                    "timestamp": datetime.fromtimestamp(reflection.timestamp).isoformat()
                })
        
        # Sort by timestamp
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return logs[:n]

def main():
    """Test GUI bridge"""
    import asyncio
    
    bridge = GUIBridge()
    
    print("🖥️  JARVIS GUI Bridge - Test")
    print("=" * 60)
    
    # Test command processing
    print("\n1. Processing user command...")
    result = asyncio.run(bridge.process_user_command("open Instagram"))
    print(f"   Success: {result['success']}")
    if result.get('brain_result'):
        print(f"   Action: {result['brain_result'].get('action')}")
    
    # Test autonomous suggestions
    print("\n2. Getting autonomous suggestions...")
    suggestions = bridge.get_autonomous_suggestions()
    print(f"   Found {len(suggestions)} suggestions")
    
    # Test system status
    print("\n3. System status...")
    status = bridge.get_system_status()
    print(f"   Brain queries: {status['brain']['total_queries']}")
    print(f"   Memory entries: {status['memory']['short_term']['total']}")
    print(f"   Reflections: {status['reflection']['total_reflections']}")
    
    # Test logs
    print("\n4. Recent logs...")
    logs = bridge.get_logs(n=5)
    print(f"   Retrieved {len(logs)} log entries")
    for log in logs[:3]:
        print(f"   - [{log['type']}] {log.get('content', log.get('action', 'N/A'))}")
    
    print("\n" + "=" * 60)
    print("✓ GUI bridge test complete")

if __name__ == "__main__":
    main()
