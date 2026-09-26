#!/usr/bin/env python3
"""
JARVIS Reflection System - Phase 4
Self-evaluation and learning from actions
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class ReflectionType(Enum):
    """Types of reflections"""
    SUCCESS = "success"
    FAILURE = "failure"
    IMPROVEMENT = "improvement"
    LEARNING = "learning"

@dataclass
class Reflection:
    """Single reflection entry"""
    id: str
    timestamp: float
    type: ReflectionType
    action: str
    outcome: str
    analysis: str
    lessons_learned: List[str]
    confidence_before: float
    confidence_after: float
    metadata: Dict
    
    def to_dict(self) -> Dict:
        """Convert reflection to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        data['type'] = ReflectionType(data['type'])
        return cls(**data)

class ReflectionSystem:
    """
    Self-reflection and learning system
    Analyzes actions and outcomes to improve future performance
    """
    
    def __init__(self, storage_path: str = "data/learning/reflections.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.reflections: List[Reflection] = []
        self.patterns: Dict[str, Dict] = {}  # Learned patterns
        
        self._load()
    
    def _load(self) -> None:
        """Load reflections from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.reflections = [Reflection.from_dict(r) for r in data.get('reflections', [])]
                    self.patterns = data.get('patterns', {})
            except Exception as e:
                print(f"Error loading reflections: {e}")
    
    def _save(self) -> None:
        """Save reflections to storage"""
        try:
            data = {
                'reflections': [r.to_dict() for r in self.reflections],
                'patterns': self.patterns,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving reflections: {e}")
    
    def reflect_on_action(self, action: str, target: str, 
                         outcome: Dict, expected_outcome: Dict = None) -> Reflection:
        """
        Reflect on an action and its outcome
        """
        success = outcome.get('success', False)
        
        # Determine reflection type
        if success:
            reflection_type = ReflectionType.SUCCESS
        else:
            reflection_type = ReflectionType.FAILURE
        
        # Analyze the outcome
        analysis = self._analyze_outcome(action, target, outcome, expected_outcome)
        
        # Extract lessons
        lessons = self._extract_lessons(action, outcome, success)
        
        # Calculate confidence change
        confidence_before = 0.7  # Default
        confidence_after = 0.8 if success else 0.5
        
        # Create reflection
        reflection = Reflection(
            id=f"reflection_{int(time.time() * 1000)}",
            timestamp=time.time(),
            type=reflection_type,
            action=action,
            outcome=str(outcome),
            analysis=analysis,
            lessons_learned=lessons,
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            metadata={
                'target': target,
                'success': success
            }
        )
        
        # Store reflection
        self.reflections.append(reflection)
        
        # Update patterns
        self._update_patterns(action, success)
        
        # Save periodically
        if len(self.reflections) % 5 == 0:
            self._save()
        
        return reflection
    
    def _analyze_outcome(self, action: str, target: str, 
                        outcome: Dict, expected: Dict = None) -> str:
        """
        Analyze the outcome of an action
        """
        if outcome.get('success'):
            return f"Action '{action}' on '{target}' completed successfully."
        else:
            error = outcome.get('error', 'Unknown error')
            return f"Action '{action}' on '{target}' failed: {error}"
    
    def _extract_lessons(self, action: str, outcome: Dict, success: bool) -> List[str]:
        """
        Extract lessons learned from the outcome
        """
        lessons = []
        
        if success:
            lessons.append(f"Action '{action}' is reliable and can be used confidently")
        else:
            error = outcome.get('error', '')
            
            if 'permission' in error.lower():
                lessons.append(f"Action '{action}' requires elevated permissions")
            elif 'not found' in error.lower():
                lessons.append(f"Target for '{action}' may not exist or is inaccessible")
            elif 'timeout' in error.lower():
                lessons.append(f"Action '{action}' may require more time to complete")
            else:
                lessons.append(f"Action '{action}' failed - investigate error handling")
        
        return lessons
    
    def _update_patterns(self, action: str, success: bool) -> None:
        """
        Update learned patterns based on action outcomes
        """
        if action not in self.patterns:
            self.patterns[action] = {
                'total_attempts': 0,
                'successes': 0,
                'failures': 0,
                'success_rate': 0.0,
                'common_issues': []
            }
        
        pattern = self.patterns[action]
        pattern['total_attempts'] += 1
        
        if success:
            pattern['successes'] += 1
        else:
            pattern['failures'] += 1
        
        pattern['success_rate'] = pattern['successes'] / pattern['total_attempts']
    
    def get_action_confidence(self, action: str) -> float:
        """
        Get confidence level for an action based on past reflections
        """
        if action not in self.patterns:
            return 0.5  # Default confidence
        
        return self.patterns[action]['success_rate']
    
    def get_recommendations(self, action: str) -> List[str]:
        """
        Get recommendations for an action based on past reflections
        """
        recommendations = []
        
        # Get relevant reflections
        action_reflections = [r for r in self.reflections if r.action == action]
        
        if not action_reflections:
            recommendations.append("No prior experience with this action")
            return recommendations
        
        # Analyze patterns
        failures = [r for r in action_reflections if r.type == ReflectionType.FAILURE]
        
        if failures:
            # Extract common issues
            for reflection in failures[-3:]:  # Last 3 failures
                recommendations.extend(reflection.lessons_learned)
        
        # Add success tips
        successes = [r for r in action_reflections if r.type == ReflectionType.SUCCESS]
        if successes:
            recommendations.append(f"Success rate: {len(successes)}/{len(action_reflections)}")
        
        return recommendations
    
    def should_retry(self, action: str, previous_attempts: int = 0) -> Tuple[bool, str]:
        """
        Determine if an action should be retried based on reflections
        """
        if action not in self.patterns:
            return True, "No prior data, worth trying"
        
        pattern = self.patterns[action]
        success_rate = pattern['success_rate']
        
        # Don't retry if success rate is very low and multiple attempts made
        if success_rate < 0.2 and previous_attempts >= 2:
            return False, "Low success rate and multiple failures"
        
        # Retry if success rate is decent
        if success_rate >= 0.5:
            return True, "Decent success rate, worth retrying"
        
        # Limited retries for medium success rate
        if previous_attempts < 3:
            return True, "Limited retries remaining"
        
        return False, "Too many failures"
    
    def get_debug_info(self, action: str) -> Dict:
        """
        Get detailed debug information for an action
        """
        action_reflections = [r for r in self.reflections if r.action == action]
        
        if not action_reflections:
            return {"message": "No reflections found for this action"}
        
        return {
            "total_reflections": len(action_reflections),
            "successes": len([r for r in action_reflections if r.type == ReflectionType.SUCCESS]),
            "failures": len([r for r in action_reflections if r.type == ReflectionType.FAILURE]),
            "recent_reflections": [
                {
                    "type": r.type.value,
                    "analysis": r.analysis,
                    "lessons": r.lessons_learned,
                    "timestamp": datetime.fromtimestamp(r.timestamp).isoformat()
                }
                for r in action_reflections[-5:]
            ],
            "pattern": self.patterns.get(action, {})
        }
    
    def get_stats(self) -> Dict:
        """Get reflection statistics"""
        if not self.reflections:
            return {"total": 0}
        
        types = {}
        for reflection in self.reflections:
            types[reflection.type.value] = types.get(reflection.type.value, 0) + 1
        
        return {
            "total_reflections": len(self.reflections),
            "by_type": types,
            "patterns_learned": len(self.patterns),
            "avg_confidence_change": sum(
                r.confidence_after - r.confidence_before 
                for r in self.reflections
            ) / len(self.reflections),
            "most_reflected_actions": sorted(
                self.patterns.items(),
                key=lambda x: x[1]['total_attempts'],
                reverse=True
            )[:5]
        }

def main() -> None:
    """Test reflection system"""
    reflection_system = ReflectionSystem()
    
    print("🤔 JARVIS Reflection System - Test")
    print("=" * 60)
    
    # Simulate some actions and reflections
    print("\n1. Simulating actions...")
    
    # Success
    reflection_system.reflect_on_action(
        "open_app",
        "Instagram",
        {"success": True}
    )
    
    # Another success
    reflection_system.reflect_on_action(
        "open_app",
        "Spotify",
        {"success": True}
    )
    
    # Failure
    reflection_system.reflect_on_action(
        "open_app",
        "NonExistentApp",
        {"success": False, "error": "Application not found"}
    )
    
    # Command success
    reflection_system.reflect_on_action(
        "execute_command",
        "ls -la",
        {"success": True, "stdout": "file list"}
    )
    
    # Command failure
    reflection_system.reflect_on_action(
        "execute_command",
        "rm -rf /",
        {"success": False, "error": "Permission denied"}
    )
    
    # Get confidence
    print("\n2. Action confidence levels:")
    print(f"   open_app: {reflection_system.get_action_confidence('open_app'):.2f}")
    print(f"   execute_command: {reflection_system.get_action_confidence('execute_command'):.2f}")
    
    # Get recommendations
    print("\n3. Recommendations for 'open_app':")
    recommendations = reflection_system.get_recommendations('open_app')
    for rec in recommendations:
        print(f"   - {rec}")
    
    # Should retry?
    print("\n4. Retry decisions:")
    should_retry, reason = reflection_system.should_retry('open_app', previous_attempts=1)
    print(f"   open_app: {should_retry} - {reason}")
    
    should_retry, reason = reflection_system.should_retry('execute_command', previous_attempts=1)
    print(f"   execute_command: {should_retry} - {reason}")
    
    # Debug info
    print("\n5. Debug info for 'open_app':")
    debug = reflection_system.get_debug_info('open_app')
    print(f"   Total reflections: {debug['total_reflections']}")
    print(f"   Successes: {debug['successes']}")
    print(f"   Failures: {debug['failures']}")
    
    # Statistics
    print("\n6. Overall statistics:")
    stats = reflection_system.get_stats()
    print(f"   Total reflections: {stats['total_reflections']}")
    print(f"   By type: {stats['by_type']}")
    print(f"   Patterns learned: {stats['patterns_learned']}")
    
    print("\n" + "=" * 60)
    print("✓ Reflection system test complete")

if __name__ == "__main__":
    main()
