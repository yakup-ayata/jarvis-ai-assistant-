#!/usr/bin/env python3
"""
JARVIS Risk Engine - Phase 3
Analyzes action risk and manages permissions
"""

import re
import json
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

class RiskLevel(Enum):
    """Risk levels for actions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskAnalysis:
    """Risk analysis result"""
    level: RiskLevel
    score: float  # 0-100
    reasons: List[str]
    requires_approval: bool
    auto_approve: bool

class RiskEngine:
    """
    Analyzes action risk and determines if approval is needed
    """
    
    def __init__(self):
        # Risk patterns
        self.risk_patterns = {
            # CRITICAL - Never auto-approve
            "critical": [
                r"rm\s+-rf",
                r"sudo",
                r"chmod\s+777",
                r"mkfs",
                r"dd\s+if=",
                r"format",
                r"delete.*system",
                r">/dev/",
            ],
            
            # HIGH - Requires approval
            "high": [
                r"delete",
                r"remove",
                r"kill\s+-9",
                r"shutdown",
                r"reboot",
                r"chmod",
                r"chown",
                r"install",
                r"uninstall",
            ],
            
            # MEDIUM - May require approval
            "medium": [
                r"write",
                r"modify",
                r"update",
                r"create.*file",
                r"execute",
                r"run.*script",
            ],
            
            # LOW - Auto-approve
            "low": [
                r"read",
                r"list",
                r"show",
                r"get",
                r"open",
                r"view",
            ]
        }
        
        # Action risk scores (base scores)
        self.action_risks = {
            # LOW (0-30)
            "open_app": 10,
            "close_app": 15,
            "get_volume": 5,
            "get_system_info": 5,
            "open_url": 20,
            "web_search": 10,
            
            # MEDIUM (31-60)
            "set_volume": 35,
            "take_screenshot": 40,
            "execute_command": 50,  # Base, can increase
            
            # HIGH (61-80)
            "install_package": 70,
            "modify_file": 65,
            
            # CRITICAL (81-100)
            "delete_file": 85,
            "system_shutdown": 95,
        }
        
        # Auto-approve thresholds
        self.auto_approve_threshold = 30  # Score <= 30 auto-approves
        self.requires_approval_threshold = 31  # Score > 30 requires approval
    
    def analyze_action(self, action: str, target: str = "", params: Dict = None) -> RiskAnalysis:
        """
        Analyze action risk
        """
        params = params or {}
        
        # Get base risk score
        base_score = self.action_risks.get(action, 50)  # Default: MEDIUM
        
        # Analyze target for risk patterns
        target_risk = self._analyze_target(target)
        
        # Analyze params
        params_risk = self._analyze_params(params)
        
        # Calculate final score
        final_score = min(100, base_score + target_risk + params_risk)
        
        # Determine risk level
        if final_score >= 81:
            level = RiskLevel.CRITICAL
        elif final_score >= 61:
            level = RiskLevel.HIGH
        elif final_score >= 31:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        # Collect reasons
        reasons = []
        if base_score >= 50:
            reasons.append(f"Action '{action}' has elevated base risk")
        if target_risk > 0:
            reasons.append(f"Target contains risky patterns")
        if params_risk > 0:
            reasons.append(f"Parameters contain risky values")
        
        # Determine approval requirements
        requires_approval = final_score > self.auto_approve_threshold
        auto_approve = final_score <= self.auto_approve_threshold
        
        return RiskAnalysis(
            level=level,
            score=final_score,
            reasons=reasons if reasons else ["Standard action"],
            requires_approval=requires_approval,
            auto_approve=auto_approve
        )
    
    def _analyze_target(self, target: str) -> int:
        """Analyze target string for risk patterns"""
        if not target:
            return 0
        
        target_lower = target.lower()
        risk_score = 0
        
        # Check critical patterns
        for pattern in self.risk_patterns["critical"]:
            if re.search(pattern, target_lower):
                risk_score += 50
        
        # Check high patterns
        for pattern in self.risk_patterns["high"]:
            if re.search(pattern, target_lower):
                risk_score += 30
        
        # Check medium patterns
        for pattern in self.risk_patterns["medium"]:
            if re.search(pattern, target_lower):
                risk_score += 15
        
        return min(50, risk_score)  # Cap at 50
    
    def _analyze_params(self, params: Dict) -> int:
        """Analyze parameters for risk"""
        risk_score = 0
        
        # Check for dangerous flags
        dangerous_flags = ["force", "recursive", "no-confirm", "yes"]
        
        for key, value in params.items():
            if isinstance(value, str):
                value_lower = value.lower()
                if any(flag in value_lower for flag in dangerous_flags):
                    risk_score += 20
        
        return min(30, risk_score)  # Cap at 30

class PermissionManager:
    """
    Manages user permissions and approval history
    """
    
    def __init__(self, storage_path: str = "data/permissions.json"):
        self.storage_path = storage_path
        self.approvals: Dict[str, Dict] = {}
        self.denials: Dict[str, Dict] = {}
        self.auto_approved_actions: List[str] = []
        
        # Load existing data
        self._load()
    
    def _load(self):
        """Load permissions from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.approvals = data.get("approvals", {})
                self.denials = data.get("denials", {})
                self.auto_approved_actions = data.get("auto_approved_actions", [])
        except FileNotFoundError:
            pass
    
    def _save(self):
        """Save permissions to storage"""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {
            "approvals": self.approvals,
            "denials": self.denials,
            "auto_approved_actions": self.auto_approved_actions
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_action_hash(self, action: str, target: str) -> str:
        """Generate hash for action+target combination"""
        combined = f"{action}:{target}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def request_approval(self, action: str, target: str, risk_analysis: RiskAnalysis) -> Dict:
        """
        Request user approval for action
        Returns approval request that should be sent to user
        """
        action_hash = self._get_action_hash(action, target)
        
        # Check if action is in auto-approved list
        if action in self.auto_approved_actions:
            return {
                "approved": True,
                "reason": "Action is in auto-approved list",
                "auto": True
            }
        
        # Check if this specific action+target was approved before
        if action_hash in self.approvals:
            approval = self.approvals[action_hash]
            # Check if approval is still valid (within 24 hours)
            approved_at = datetime.fromisoformat(approval["timestamp"])
            if datetime.now() - approved_at < timedelta(hours=24):
                return {
                    "approved": True,
                    "reason": "Previously approved (within 24h)",
                    "auto": True
                }
        
        # Return approval request
        return {
            "approved": False,
            "requires_approval": True,
            "action": action,
            "target": target,
            "risk_level": risk_analysis.level.value,
            "risk_score": risk_analysis.score,
            "reasons": risk_analysis.reasons,
            "action_hash": action_hash
        }
    
    def approve_action(self, action_hash: str, action: str, target: str):
        """Record user approval"""
        self.approvals[action_hash] = {
            "action": action,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        self._save()
    
    def deny_action(self, action_hash: str, action: str, target: str):
        """Record user denial"""
        self.denials[action_hash] = {
            "action": action,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        self._save()
    
    def add_auto_approved_action(self, action: str):
        """Add action to auto-approved list"""
        if action not in self.auto_approved_actions:
            self.auto_approved_actions.append(action)
            self._save()
    
    def remove_auto_approved_action(self, action: str):
        """Remove action from auto-approved list"""
        if action in self.auto_approved_actions:
            self.auto_approved_actions.remove(action)
            self._save()
    
    def get_stats(self) -> Dict:
        """Get permission statistics"""
        return {
            "total_approvals": len(self.approvals),
            "total_denials": len(self.denials),
            "auto_approved_actions": self.auto_approved_actions,
            "recent_approvals": list(self.approvals.values())[-5:],
            "recent_denials": list(self.denials.values())[-5:]
        }

def main():
    """Test the risk engine"""
    risk_engine = RiskEngine()
    permission_manager = PermissionManager()
    
    print("🔒 JARVIS Risk Engine - Test")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        ("open_app", "Instagram", {}),
        ("set_volume", "50", {}),
        ("execute_command", "ls -la", {}),
        ("execute_command", "rm -rf /", {}),
        ("execute_command", "sudo reboot", {}),
        ("delete_file", "/important/file.txt", {}),
        ("take_screenshot", "screenshot.png", {}),
    ]
    
    for action, target, params in test_cases:
        print(f"\n📝 Action: {action} ({target})")
        
        # Analyze risk
        analysis = risk_engine.analyze_action(action, target, params)
        
        print(f"   Risk Level: {analysis.level.value.upper()}")
        print(f"   Risk Score: {analysis.score}/100")
        print(f"   Auto-approve: {analysis.auto_approve}")
        print(f"   Requires approval: {analysis.requires_approval}")
        print(f"   Reasons: {', '.join(analysis.reasons)}")
        
        # Check permission
        if analysis.requires_approval:
            approval_request = permission_manager.request_approval(action, target, analysis)
            if approval_request.get("approved"):
                print(f"   ✓ Auto-approved: {approval_request['reason']}")
            else:
                print(f"   ⚠️  Requires user approval")
    
    print("\n" + "=" * 60)
    print("📊 Permission Stats:")
    stats = permission_manager.get_stats()
    print(f"   Total approvals: {stats['total_approvals']}")
    print(f"   Total denials: {stats['total_denials']}")
    print(f"   Auto-approved actions: {stats['auto_approved_actions']}")

if __name__ == "__main__":
    main()
