#!/usr/bin/env python3
"""
JARVIS Self-Healing System
Auto-patch & Hot Reload for system stability

Features:
- Project-level: build errors, test failures → auto-fix
- System-level: backend crash, tool server crash → auto-patch & hot reload
- Memory + logs analyzed for errors & optimization
- Continuous background monitoring
"""

import asyncio
import json
import time
import os
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HealingStrategy(Enum):
    """Healing strategies"""
    RESTART = "restart"           # Restart service
    PATCH = "patch"               # Apply code patch
    ROLLBACK = "rollback"         # Rollback to previous version
    DEPENDENCY_FIX = "dependency" # Fix dependencies
    CONFIG_FIX = "config"         # Fix configuration

class SelfHealingSystem:
    """
    Self-Healing System with auto-patch and hot reload
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.healing_history = []
        self.monitored_services = {}
        self.error_patterns = self._load_error_patterns()
        self.healing_enabled = True
        
        print("🔧 Self-Healing System initialized")
    
    def _load_error_patterns(self) -> Dict:
        """Load common error patterns and solutions"""
        return {
            # Python errors
            "ModuleNotFoundError": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.DEPENDENCY_FIX,
                "solution": "pip install {module}"
            },
            "ImportError": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.DEPENDENCY_FIX,
                "solution": "pip install {module}"
            },
            "SyntaxError": {
                "severity": ErrorSeverity.CRITICAL,
                "strategy": HealingStrategy.PATCH,
                "solution": "Fix syntax error at line {line}"
            },
            "IndentationError": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.PATCH,
                "solution": "Fix indentation at line {line}"
            },
            "TypeError": {
                "severity": ErrorSeverity.MEDIUM,
                "strategy": HealingStrategy.PATCH,
                "solution": "Add type conversion or check"
            },
            "AttributeError": {
                "severity": ErrorSeverity.MEDIUM,
                "strategy": HealingStrategy.PATCH,
                "solution": "Check attribute exists before access"
            },
            "ConnectionError": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.RESTART,
                "solution": "Restart service and check network"
            },
            "TimeoutError": {
                "severity": ErrorSeverity.MEDIUM,
                "strategy": HealingStrategy.CONFIG_FIX,
                "solution": "Increase timeout value"
            },
            
            # Node.js errors
            "Cannot find module": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.DEPENDENCY_FIX,
                "solution": "npm install {module}"
            },
            "EADDRINUSE": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.RESTART,
                "solution": "Kill process on port and restart"
            },
            "ECONNREFUSED": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.RESTART,
                "solution": "Restart dependent service"
            },
            
            # Build errors
            "Build failed": {
                "severity": ErrorSeverity.HIGH,
                "strategy": HealingStrategy.PATCH,
                "solution": "Analyze build log and fix errors"
            },
            "Test failed": {
                "severity": ErrorSeverity.MEDIUM,
                "strategy": HealingStrategy.PATCH,
                "solution": "Fix failing tests"
            }
        }
    
    async def monitor_service(self, service_name: str, check_command: str, restart_command: str):
        """
        Monitor a service and auto-restart if it crashes
        
        Args:
            service_name: Name of service
            check_command: Command to check if service is running
            restart_command: Command to restart service
        """
        self.monitored_services[service_name] = {
            "check_command": check_command,
            "restart_command": restart_command,
            "status": "running",
            "last_check": datetime.now(),
            "restart_count": 0
        }
        
        print(f"👁️  Monitoring service: {service_name}")
        
        while self.healing_enabled:
            try:
                # Check if service is running
                result = subprocess.run(
                    check_command,
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    # Service is down
                    print(f"⚠️  Service {service_name} is down!")
                    await self._heal_service(service_name)
                else:
                    self.monitored_services[service_name]["status"] = "running"
                
                self.monitored_services[service_name]["last_check"] = datetime.now()
                
            except Exception as e:
                print(f"❌ Error monitoring {service_name}: {e}")
            
            # Check every 30 seconds
            await asyncio.sleep(30)
    
    async def _heal_service(self, service_name: str):
        """Heal a crashed service"""
        service = self.monitored_services[service_name]
        
        print(f"🔧 Healing service: {service_name}")
        
        # Strategy 1: Simple restart
        try:
            result = subprocess.run(
                service["restart_command"],
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                service["status"] = "running"
                service["restart_count"] += 1
                
                healing_record = {
                    "service": service_name,
                    "strategy": HealingStrategy.RESTART.value,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.healing_history.append(healing_record)
                
                print(f"✅ Service {service_name} restarted successfully")
                return
        
        except Exception as e:
            print(f"❌ Failed to restart {service_name}: {e}")
        
        # Strategy 2: Analyze logs and patch
        log_path = self.project_root / "logs" / f"{service_name}.log"
        if log_path.exists():
            await self._analyze_and_patch(service_name, log_path)
    
    async def analyze_error_log(self, log_path: Path) -> Dict:
        """
        Analyze error log and identify issues
        
        Returns:
            Dict with errors, severity, and suggested fixes
        """
        print(f"📋 Analyzing log: {log_path}")
        
        if not log_path.exists():
            return {"error": "Log file not found"}
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Extract errors
        errors = []
        
        for pattern, info in self.error_patterns.items():
            if pattern in log_content:
                # Extract context
                lines = log_content.split('\n')
                error_lines = [line for line in lines if pattern in line]
                
                for error_line in error_lines[:5]:  # Limit to 5 occurrences
                    errors.append({
                        "pattern": pattern,
                        "severity": info["severity"].value,
                        "strategy": info["strategy"].value,
                        "solution": info["solution"],
                        "context": error_line[:200]
                    })
        
        # Determine overall severity
        if errors:
            max_severity = max(
                ErrorSeverity[e["severity"].upper()] for e in errors
            )
        else:
            max_severity = ErrorSeverity.LOW
        
        return {
            "log_path": str(log_path),
            "total_errors": len(errors),
            "errors": errors,
            "max_severity": max_severity.value,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_and_patch(self, service_name: str, log_path: Path):
        """Analyze logs and apply patches"""
        analysis = await self.analyze_error_log(log_path)
        
        if not analysis.get("errors"):
            print(f"   No errors found in log")
            return
        
        print(f"   Found {analysis['total_errors']} errors")
        
        for error in analysis["errors"]:
            strategy = HealingStrategy(error["strategy"])
            
            if strategy == HealingStrategy.DEPENDENCY_FIX:
                await self._fix_dependency(error)
            
            elif strategy == HealingStrategy.PATCH:
                await self._apply_code_patch(error)
            
            elif strategy == HealingStrategy.CONFIG_FIX:
                await self._fix_config(error)
    
    async def _fix_dependency(self, error: Dict):
        """Fix missing dependency"""
        print(f"   Fixing dependency: {error['pattern']}")
        
        # Extract module name
        if "ModuleNotFoundError" in error["pattern"]:
            # Parse: ModuleNotFoundError: No module named 'requests'
            module = error["context"].split("'")[1] if "'" in error["context"] else "unknown"
            
            # Install module
            try:
                result = subprocess.run(
                    f"pip install {module}",
                    shell=True,
                    capture_output=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Installed {module}")
                    
                    healing_record = {
                        "type": "dependency_fix",
                        "module": module,
                        "success": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.healing_history.append(healing_record)
                else:
                    print(f"   ❌ Failed to install {module}")
            
            except Exception as e:
                print(f"   ❌ Error installing {module}: {e}")
        
        elif "Cannot find module" in error["pattern"]:
            # Node.js module
            module = error["context"].split("'")[1] if "'" in error["context"] else "unknown"
            
            try:
                result = subprocess.run(
                    f"npm install {module}",
                    shell=True,
                    capture_output=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Installed {module}")
            
            except Exception as e:
                print(f"   ❌ Error installing {module}: {e}")
    
    async def _apply_code_patch(self, error: Dict):
        """Apply code patch to fix error"""
        print(f"   Applying code patch for: {error['pattern']}")
        
        # This would use the multi-agent coder to generate and apply patch
        # For now, just log the action
        
        healing_record = {
            "type": "code_patch",
            "error": error["pattern"],
            "success": False,  # Would be True after actual patch
            "note": "Requires manual intervention or LLM-based patch generation",
            "timestamp": datetime.now().isoformat()
        }
        
        self.healing_history.append(healing_record)
    
    async def _fix_config(self, error: Dict):
        """Fix configuration issue"""
        print(f"   Fixing config for: {error['pattern']}")
        
        # This would modify config files based on error
        # For now, just log the action
        
        healing_record = {
            "type": "config_fix",
            "error": error["pattern"],
            "success": False,
            "note": "Requires config file modification",
            "timestamp": datetime.now().isoformat()
        }
        
        self.healing_history.append(healing_record)
    
    async def hot_reload_module(self, module_path: str):
        """
        Hot reload a Python module without restarting
        
        Args:
            module_path: Path to module file
        """
        print(f"🔥 Hot reloading: {module_path}")
        
        try:
            import importlib
            import sys
            
            # Convert path to module name
            module_name = module_path.replace('/', '.').replace('.py', '')
            
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                print(f"   ✅ Reloaded {module_name}")
                
                healing_record = {
                    "type": "hot_reload",
                    "module": module_name,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.healing_history.append(healing_record)
            else:
                print(f"   ⚠️  Module {module_name} not loaded")
        
        except Exception as e:
            print(f"   ❌ Hot reload failed: {e}")
    
    async def optimize_memory(self):
        """Analyze memory usage and optimize"""
        print("🧠 Optimizing memory...")
        
        import gc
        import psutil
        
        # Get current memory usage
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Force garbage collection
        gc.collect()
        
        # Get memory after cleanup
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        freed = mem_before - mem_after
        
        print(f"   Memory before: {mem_before:.2f} MB")
        print(f"   Memory after: {mem_after:.2f} MB")
        print(f"   Freed: {freed:.2f} MB")
        
        healing_record = {
            "type": "memory_optimization",
            "freed_mb": freed,
            "timestamp": datetime.now().isoformat()
        }
        
        self.healing_history.append(healing_record)
        
        return {
            "mem_before": mem_before,
            "mem_after": mem_after,
            "freed": freed
        }
    
    def get_healing_stats(self) -> Dict:
        """Get healing statistics"""
        total_healings = len(self.healing_history)
        
        by_type = {}
        success_count = 0
        
        for record in self.healing_history:
            record_type = record.get("type", "unknown")
            by_type[record_type] = by_type.get(record_type, 0) + 1
            
            if record.get("success"):
                success_count += 1
        
        return {
            "total_healings": total_healings,
            "success_rate": (success_count / total_healings * 100) if total_healings > 0 else 0,
            "by_type": by_type,
            "monitored_services": len(self.monitored_services),
            "healing_enabled": self.healing_enabled
        }
    
    def stop_monitoring(self):
        """Stop all monitoring"""
        self.healing_enabled = False
        print("🛑 Self-healing monitoring stopped")


# Singleton instance
_self_healing = None

def get_self_healing() -> SelfHealingSystem:
    """Get singleton Self-Healing System instance"""
    global _self_healing
    if _self_healing is None:
        _self_healing = SelfHealingSystem()
    return _self_healing


# Test
if __name__ == "__main__":
    async def test():
        print("🧪 Testing Self-Healing System...")
        
        healer = get_self_healing()
        
        # Test 1: Analyze error log
        print("\n1️⃣ Test: Analyze error log")
        
        # Create test log
        test_log = Path("test_error.log")
        test_log.write_text("""
2024-03-02 10:00:00 - ERROR - ModuleNotFoundError: No module named 'requests'
2024-03-02 10:00:01 - ERROR - TypeError: unsupported operand type(s) for +: 'int' and 'str'
2024-03-02 10:00:02 - ERROR - ConnectionError: Failed to connect to localhost:8000
        """)
        
        analysis = await healer.analyze_error_log(test_log)
        print(f"   Total errors: {analysis['total_errors']}")
        print(f"   Max severity: {analysis['max_severity']}")
        
        # Clean up
        test_log.unlink()
        
        # Test 2: Memory optimization
        print("\n2️⃣ Test: Memory optimization")
        result = await healer.optimize_memory()
        print(f"   Freed: {result['freed']:.2f} MB")
        
        # Test 3: Stats
        print("\n3️⃣ Test: Healing stats")
        stats = healer.get_healing_stats()
        print(f"   Total healings: {stats['total_healings']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        
        print("\n✅ Self-Healing System test complete")
    
    asyncio.run(test())
