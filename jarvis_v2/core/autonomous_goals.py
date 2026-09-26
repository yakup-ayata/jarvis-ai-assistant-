#!/usr/bin/env python3
"""
JARVIS Autonomous Goal Generator - Phase 5
Event-driven goal creation and execution with user approval
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class GoalStatus(Enum):
    """Goal execution status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class GoalPriority(Enum):
    """Goal priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Goal:
    """Autonomous goal"""
    id: str
    timestamp: float
    trigger: str  # What triggered this goal
    trigger_data: Dict
    goal_description: str
    reasoning: str
    actions: List[Dict]  # List of actions to execute
    priority: GoalPriority
    status: GoalStatus
    risk_level: str  # From risk engine
    requires_approval: bool
    approved_by: Optional[str] = None
    approved_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict] = None
    
    def to_dict(self):
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        data['priority'] = GoalPriority(data['priority'])
        data['status'] = GoalStatus(data['status'])
        return cls(**data)

class AutonomousGoalGenerator:
    """
    Generates and manages autonomous goals based on system events
    """
    
    def __init__(self, storage_path: str = "data/goals.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.goals: List[Goal] = []
        self.goal_index: Dict[str, Goal] = {}
        
        # Goal generation rules
        self.goal_rules = self._initialize_rules()
        
        self._load()
    
    def _initialize_rules(self) -> Dict:
        """
        Initialize goal generation rules
        Maps triggers to goal templates
        """
        return {
            # System resource triggers
            "cpu_high": {
                "description": "Optimize CPU usage",
                "reasoning": "CPU usage is high, system may be slow",
                "actions": [
                    {"action": "get_system_info", "target": None},
                    {"action": "suggest_optimization", "target": "cpu"}
                ],
                "priority": GoalPriority.MEDIUM,
                "requires_approval": False
            },
            
            "memory_high": {
                "description": "Free up memory",
                "reasoning": "Memory usage is high, may cause slowdowns",
                "actions": [
                    {"action": "get_system_info", "target": None},
                    {"action": "suggest_cleanup", "target": "memory"}
                ],
                "priority": GoalPriority.HIGH,
                "requires_approval": False
            },
            
            "memory_critical": {
                "description": "Emergency memory cleanup",
                "reasoning": "Memory critically low, immediate action needed",
                "actions": [
                    {"action": "close_unused_apps", "target": None},
                    {"action": "clear_cache", "target": None}
                ],
                "priority": GoalPriority.CRITICAL,
                "requires_approval": True
            },
            
            "disk_high": {
                "description": "Clean up disk space",
                "reasoning": "Disk space running low",
                "actions": [
                    {"action": "analyze_disk_usage", "target": None},
                    {"action": "suggest_cleanup", "target": "disk"}
                ],
                "priority": GoalPriority.MEDIUM,
                "requires_approval": False
            },
            
            # Workflow triggers
            "new_project_folder": {
                "description": "Setup project workflow",
                "reasoning": "New project folder detected, offer setup assistance",
                "actions": [
                    {"action": "suggest_git_init", "target": None},
                    {"action": "suggest_venv_setup", "target": None}
                ],
                "priority": GoalPriority.LOW,
                "requires_approval": False
            },
            
            "repeated_task": {
                "description": "Automate repeated task",
                "reasoning": "Task repeated multiple times, can be automated",
                "actions": [
                    {"action": "analyze_pattern", "target": None},
                    {"action": "suggest_automation", "target": None}
                ],
                "priority": GoalPriority.LOW,
                "requires_approval": False
            },
            
            # Maintenance triggers
            "system_idle": {
                "description": "Perform maintenance tasks",
                "reasoning": "System idle, good time for maintenance",
                "actions": [
                    {"action": "update_check", "target": None},
                    {"action": "cleanup_temp", "target": None}
                ],
                "priority": GoalPriority.LOW,
                "requires_approval": False
            }
        }
    
    def _load(self):
        """Load goals from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.goals = [Goal.from_dict(g) for g in data]
                    self.goal_index = {g.id: g for g in self.goals}
            except Exception as e:
                print(f"Error loading goals: {e}")
    
    def _save(self):
        """Save goals to storage"""
        try:
            data = [g.to_dict() for g in self.goals]
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving goals: {e}")
    
    def generate_goal(self, trigger: str, trigger_data: Dict) -> Optional[Goal]:
        """
        Generate a goal based on trigger
        """
        # Check if we have a rule for this trigger
        if trigger not in self.goal_rules:
            return None
        
        rule = self.goal_rules[trigger]
        
        # Create goal
        goal = Goal(
            id=f"goal_{int(time.time() * 1000)}",
            timestamp=time.time(),
            trigger=trigger,
            trigger_data=trigger_data,
            goal_description=rule["description"],
            reasoning=rule["reasoning"],
            actions=rule["actions"],
            priority=rule["priority"],
            status=GoalStatus.PENDING if rule["requires_approval"] else GoalStatus.APPROVED,
            risk_level="low",  # Will be updated by risk engine
            requires_approval=rule["requires_approval"]
        )
        
        # Store goal
        self.goals.append(goal)
        self.goal_index[goal.id] = goal
        
        self._save()
        
        return goal
    
    def approve_goal(self, goal_id: str, approved_by: str = "user") -> bool:
        """Approve a pending goal"""
        goal = self.goal_index.get(goal_id)
        
        if not goal:
            return False
        
        if goal.status != GoalStatus.PENDING:
            return False
        
        goal.status = GoalStatus.APPROVED
        goal.approved_by = approved_by
        goal.approved_at = time.time()
        
        self._save()
        return True
    
    def reject_goal(self, goal_id: str) -> bool:
        """Reject a pending goal"""
        goal = self.goal_index.get(goal_id)
        
        if not goal:
            return False
        
        if goal.status != GoalStatus.PENDING:
            return False
        
        goal.status = GoalStatus.REJECTED
        self._save()
        return True
    
    def start_goal(self, goal_id: str) -> bool:
        """Start executing a goal"""
        goal = self.goal_index.get(goal_id)
        
        if not goal:
            return False
        
        if goal.status != GoalStatus.APPROVED:
            return False
        
        goal.status = GoalStatus.IN_PROGRESS
        self._save()
        return True
    
    def complete_goal(self, goal_id: str, result: Dict) -> bool:
        """Mark goal as completed"""
        goal = self.goal_index.get(goal_id)
        
        if not goal:
            return False
        
        goal.status = GoalStatus.COMPLETED
        goal.completed_at = time.time()
        goal.result = result
        
        self._save()
        return True
    
    def fail_goal(self, goal_id: str, error: str) -> bool:
        """Mark goal as failed"""
        goal = self.goal_index.get(goal_id)
        
        if not goal:
            return False
        
        goal.status = GoalStatus.FAILED
        goal.result = {"error": error}
        
        self._save()
        return True
    
    def get_pending_goals(self) -> List[Goal]:
        """Get goals waiting for approval"""
        return [g for g in self.goals if g.status == GoalStatus.PENDING]
    
    def get_approved_goals(self) -> List[Goal]:
        """Get approved goals ready for execution"""
        return [g for g in self.goals if g.status == GoalStatus.APPROVED]
    
    def get_active_goals(self) -> List[Goal]:
        """Get currently executing goals"""
        return [g for g in self.goals if g.status == GoalStatus.IN_PROGRESS]
    
    def get_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        """Get goal by ID"""
        return self.goal_index.get(goal_id)
    
    def get_stats(self) -> Dict:
        """Get goal statistics"""
        if not self.goals:
            return {"total": 0}
        
        status_counts = {}
        priority_counts = {}
        
        for goal in self.goals:
            status_counts[goal.status.value] = status_counts.get(goal.status.value, 0) + 1
            priority_counts[goal.priority.value] = priority_counts.get(goal.priority.value, 0) + 1
        
        return {
            "total_goals": len(self.goals),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "pending_approval": len(self.get_pending_goals()),
            "ready_to_execute": len(self.get_approved_goals()),
            "currently_executing": len(self.get_active_goals())
        }

def main():
    """Test autonomous goal generator"""
    goal_gen = AutonomousGoalGenerator()
    
    print("🎯 JARVIS Autonomous Goal Generator - Test")
    print("=" * 60)
    
    # Simulate triggers
    print("\n1. Generating goals from triggers...")
    
    # CPU high trigger
    goal1 = goal_gen.generate_goal(
        "cpu_high",
        {"cpu_percent": 85, "threshold": 80}
    )
    print(f"   ✓ Generated: {goal1.goal_description}")
    print(f"     Priority: {goal1.priority.value}")
    print(f"     Status: {goal1.status.value}")
    print(f"     Requires approval: {goal1.requires_approval}")
    
    # Memory critical trigger
    goal2 = goal_gen.generate_goal(
        "memory_critical",
        {"memory_percent": 95, "available_gb": 0.5}
    )
    print(f"   ✓ Generated: {goal2.goal_description}")
    print(f"     Priority: {goal2.priority.value}")
    print(f"     Status: {goal2.status.value}")
    print(f"     Requires approval: {goal2.requires_approval}")
    
    # New project folder trigger
    goal3 = goal_gen.generate_goal(
        "new_project_folder",
        {"path": "/Users/user/projects/new_app"}
    )
    print(f"   ✓ Generated: {goal3.goal_description}")
    
    # Get pending goals
    print("\n2. Pending goals (require approval):")
    pending = goal_gen.get_pending_goals()
    for goal in pending:
        print(f"   - {goal.goal_description} ({goal.priority.value})")
    
    # Approve a goal
    print("\n3. Approving critical goal...")
    goal_gen.approve_goal(goal2.id, approved_by="user")
    print(f"   ✓ Goal approved: {goal2.goal_description}")
    
    # Start execution
    print("\n4. Starting goal execution...")
    goal_gen.start_goal(goal2.id)
    print(f"   ✓ Goal started: {goal2.goal_description}")
    
    # Complete goal
    print("\n5. Completing goal...")
    goal_gen.complete_goal(goal2.id, {"success": True, "freed_memory_gb": 2.5})
    print(f"   ✓ Goal completed: {goal2.goal_description}")
    
    # Statistics
    print("\n6. Goal statistics:")
    stats = goal_gen.get_stats()
    print(f"   Total goals: {stats['total_goals']}")
    print(f"   By status: {stats['by_status']}")
    print(f"   By priority: {stats['by_priority']}")
    print(f"   Pending approval: {stats['pending_approval']}")
    
    print("\n" + "=" * 60)
    print("✓ Autonomous goal generator test complete")

if __name__ == "__main__":
    main()
