#!/usr/bin/env python3
"""
JARVIS Master Orchestrator
Coordinates all systems: Brain, Multi-Agent Coder, Self-Healing, Watchdog

This is the central nervous system that brings everything together.
"""

import asyncio
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

# Import all subsystems
from brain_service_offline import BrainService
from multi_agent_coder import MultiAgentCoder, Language, Framework
from self_healing import SelfHealingSystem
from developer_brain import DeveloperBrain
from memory_system import MemorySystem
from reflection_system import ReflectionSystem
from autonomous_goals import AutonomousGoalGenerator
from autonomous_architect import AutonomousArchitect

class MasterOrchestrator:
    """
    Master Orchestrator - Coordinates all JARVIS subsystems
    
    Features:
    - Unified command processing
    - Intelligent routing to appropriate subsystem
    - Parallel execution coordination
    - System-wide monitoring
    - Engineering mode management
    """
    
    def __init__(self):
        print("🎯 Initializing JARVIS Master Orchestrator...")
        
        # Initialize all subsystems
        self.brain = BrainService()
        self.multi_agent_coder = MultiAgentCoder()
        self.self_healing = SelfHealingSystem()
        self.developer_brain = DeveloperBrain()
        self.memory = MemorySystem()
        self.reflection = ReflectionSystem()
        self.autonomous_goals = AutonomousGoalGenerator()
        self.autonomous_architect = AutonomousArchitect()
        
        # System state
        self.engineering_mode = False
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}
        
        # Statistics
        self.stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'engineering_tasks': 0,
            'self_healing_events': 0
        }
        
        print("✅ Master Orchestrator initialized")
    
    def set_engineering_mode(self, enabled: bool):
        """Enable/disable engineering mode"""
        self.engineering_mode = enabled
        print(f"🔧 Engineering Mode: {'ENABLED' if enabled else 'DISABLED'}")
    
    async def process_command(self, command: str, context: Dict = None) -> Dict:
        """
        Main entry point for all commands
        
        Routes to appropriate subsystem based on command type
        """
        self.stats['total_commands'] += 1
        context = context or {}
        
        print(f"\n📥 Processing command: {command}")
        
        try:
            # Step 1: Classify command with brain
            classification = self.brain.classify_query(command)
            print(f"   Classification: {classification.value}")
            
            # Step 2: Route to appropriate handler
            if self._is_coding_task(command):
                result = await self._handle_coding_task(command, context)
            
            elif self._is_developer_task(command):
                result = await self._handle_developer_task(command, context)
            
            elif self._is_system_task(command):
                result = await self._handle_system_task(command, context)
            
            else:
                result = await self._handle_general_task(command, context)
            
            # Step 3: Store in memory
            await self._store_interaction(command, result)
            
            # Step 4: Update statistics
            if result.get('success'):
                self.stats['successful_commands'] += 1
            else:
                self.stats['failed_commands'] += 1
            
            return result
        
        except Exception as e:
            print(f"❌ Error processing command: {e}")
            self.stats['failed_commands'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _is_coding_task(self, command: str) -> bool:
        """Check if command is a coding task"""
        coding_keywords = [
            'write code', 'create function', 'implement', 'code',
            'algorithm', 'class', 'method', 'api', 'endpoint'
        ]
        return any(kw in command.lower() for kw in coding_keywords)
    
    def _is_developer_task(self, command: str) -> bool:
        """Check if command is a developer task"""
        dev_keywords = [
            'create project', 'scaffold', 'dockerfile', 'docker-compose',
            'analyze error', 'optimize code', 'dependencies', 'build',
            'design architecture', 'architecture', 'infrastructure', 'stack'
        ]
        return any(kw in command.lower() for kw in dev_keywords)
    
    def _is_system_task(self, command: str) -> bool:
        """Check if command is a system task"""
        system_keywords = [
            'open', 'close', 'restart', 'volume', 'brightness',
            'screenshot', 'search', 'file', 'folder'
        ]
        return any(kw in command.lower() for kw in system_keywords)
    
    async def _handle_coding_task(self, command: str, context: Dict) -> Dict:
        """Handle coding tasks with multi-agent system"""
        print("   → Routing to Multi-Agent Coder")
        
        if not self.engineering_mode:
            return {
                'success': False,
                'error': 'Engineering mode is disabled. Enable it to use coding features.',
                'suggestion': 'Enable Engineering Mode in the UI'
            }
        
        self.stats['engineering_tasks'] += 1
        
        # Detect language and framework
        language = self._detect_language(command)
        framework = self._detect_framework(command)
        
        # Add framework to context if detected
        if framework:
            context['framework'] = framework.value
        
        # Process with multi-agent coder
        result = await self.multi_agent_coder.process_coding_task(
            command,
            language,
            context,
            framework
        )
        
        return result
    
    async def _handle_developer_task(self, command: str, context: Dict) -> Dict:
        """Handle developer tasks"""
        print("   → Routing to Developer Brain / Autonomous Architect")
        
        if not self.engineering_mode:
            return {
                'success': False,
                'error': 'Engineering mode is disabled.',
                'suggestion': 'Enable Engineering Mode in the UI'
            }
        
        self.stats['engineering_tasks'] += 1
        
        # Check if this is an architecture design task
        if any(kw in command.lower() for kw in ['design architecture', 'architecture', 'infrastructure', 'stack']):
            # Use Autonomous Architect
            print("   → Using Autonomous Architect")
            
            # Extract requirements from command
            requirements = {
                'type': 'web',  # Default
                'scale': 'medium',
                'budget': 'medium',
                'timeline': 'weeks',
                'features': []
            }
            
            # Parse command for requirements
            if 'small' in command.lower():
                requirements['scale'] = 'small'
            elif 'large' in command.lower():
                requirements['scale'] = 'large'
            
            if 'api' in command.lower():
                requirements['type'] = 'api'
            elif 'mobile' in command.lower():
                requirements['type'] = 'mobile'
            elif 'data' in command.lower():
                requirements['type'] = 'data_pipeline'
            
            # Design architecture
            architecture = await self.autonomous_architect.design_architecture(requirements)
            
            return {
                'success': True,
                'type': 'architecture_design',
                'architecture': architecture,
                'autonomous': True
            }
        
        else:
            # Use Developer Brain
            result = self.developer_brain.process_command(command, context)
            return result
    
    async def _handle_system_task(self, command: str, context: Dict) -> Dict:
        """Handle system control tasks"""
        print("   → Routing to Brain Service")
        
        # Process with brain service
        result = self.brain.process_command(command, context)
        
        return result
    
    async def _handle_general_task(self, command: str, context: Dict) -> Dict:
        """Handle general tasks"""
        print("   → Routing to Brain Service")
        
        # Process with brain service
        result = self.brain.process_command(command, context)
        
        return result
    
    def _detect_language(self, command: str) -> Language:
        """Detect programming language from command - EXPANDED"""
        command_lower = command.lower()
        
        # Web Frontend
        if 'html' in command_lower:
            return Language.HTML
        elif 'css' in command_lower and 'tailwind' not in command_lower:
            return Language.CSS
        elif 'typescript' in command_lower or 'tsx' in command_lower:
            return Language.TYPESCRIPT
        elif 'javascript' in command_lower or 'js' in command_lower:
            return Language.JAVASCRIPT
        
        # Frameworks (as language targets)
        elif 'react' in command_lower:
            return Language.REACT
        elif 'vue' in command_lower:
            return Language.VUE
        elif 'angular' in command_lower:
            return Language.ANGULAR
        elif 'svelte' in command_lower:
            return Language.SVELTE
        elif 'next.js' in command_lower or 'nextjs' in command_lower:
            return Language.NEXTJS
        elif 'nuxt' in command_lower:
            return Language.NUXTJS
        
        # Web Backend
        elif 'python' in command_lower:
            return Language.PYTHON
        elif 'php' in command_lower:
            return Language.PHP
        elif 'ruby' in command_lower or 'rails' in command_lower:
            return Language.RUBY
        elif 'go' in command_lower or 'golang' in command_lower:
            return Language.GO
        elif 'c#' in command_lower or 'csharp' in command_lower or '.net' in command_lower:
            return Language.CSHARP
        
        # Mobile
        elif 'dart' in command_lower or 'flutter' in command_lower:
            return Language.FLUTTER
        elif 'swift' in command_lower:
            return Language.SWIFT
        elif 'kotlin' in command_lower:
            return Language.KOTLIN
        elif 'java' in command_lower and 'javascript' not in command_lower:
            return Language.JAVA
        elif 'objective-c' in command_lower or 'objc' in command_lower:
            return Language.OBJECTIVE_C
        elif 'react native' in command_lower:
            return Language.REACT_NATIVE
        
        # System & Performance
        elif 'rust' in command_lower:
            return Language.RUST
        elif 'c++' in command_lower or 'cpp' in command_lower:
            return Language.CPP
        elif 'c' in command_lower and 'c++' not in command_lower:
            return Language.C
        elif 'zig' in command_lower:
            return Language.ZIG
        elif 'carbon' in command_lower:
            return Language.CARBON
        
        # Data Science & AI
        elif 'r' in command_lower and ('data' in command_lower or 'statistics' in command_lower):
            return Language.R
        elif 'julia' in command_lower:
            return Language.JULIA
        elif 'scala' in command_lower:
            return Language.SCALA
        
        # Database
        elif 'sql' in command_lower:
            return Language.SQL
        elif 'graphql' in command_lower:
            return Language.GRAPHQL
        
        # DevOps & Scripting
        elif 'bash' in command_lower or 'shell' in command_lower:
            return Language.BASH
        elif 'powershell' in command_lower:
            return Language.POWERSHELL
        elif 'yaml' in command_lower:
            return Language.YAML
        elif 'dockerfile' in command_lower or 'docker' in command_lower:
            return Language.DOCKERFILE
        
        # Functional
        elif 'haskell' in command_lower:
            return Language.HASKELL
        elif 'erlang' in command_lower:
            return Language.ERLANG
        elif 'elixir' in command_lower:
            return Language.ELIXIR
        elif 'f#' in command_lower or 'fsharp' in command_lower:
            return Language.FSHARP
        elif 'clojure' in command_lower:
            return Language.CLOJURE
        
        # Legacy & Academic
        elif 'cobol' in command_lower:
            return Language.COBOL
        elif 'fortran' in command_lower:
            return Language.FORTRAN
        elif 'ada' in command_lower:
            return Language.ADA
        elif 'matlab' in command_lower:
            return Language.MATLAB
        
        else:
            return Language.PYTHON  # Default
    
    def _detect_framework(self, command: str) -> Optional[Framework]:
        """Detect framework from command"""
        command_lower = command.lower()
        
        # Frontend Frameworks
        if 'react' in command_lower and 'native' not in command_lower:
            return Framework.REACT
        elif 'vue' in command_lower:
            return Framework.VUE
        elif 'angular' in command_lower:
            return Framework.ANGULAR
        elif 'svelte' in command_lower:
            return Framework.SVELTE
        elif 'next.js' in command_lower or 'nextjs' in command_lower:
            return Framework.NEXTJS
        elif 'nuxt' in command_lower:
            return Framework.NUXTJS
        
        # CSS Frameworks
        elif 'tailwind' in command_lower:
            return Framework.TAILWIND
        elif 'bootstrap' in command_lower:
            return Framework.BOOTSTRAP
        elif 'sass' in command_lower or 'scss' in command_lower:
            return Framework.SASS
        elif 'less' in command_lower:
            return Framework.LESS
        
        # Backend Frameworks - Node.js
        elif 'express' in command_lower:
            return Framework.EXPRESS
        elif 'nestjs' in command_lower or 'nest.js' in command_lower:
            return Framework.NESTJS
        elif 'fastify' in command_lower:
            return Framework.FASTIFY
        elif 'koa' in command_lower:
            return Framework.KOA
        
        # Backend Frameworks - Python
        elif 'django' in command_lower:
            return Framework.DJANGO
        elif 'flask' in command_lower:
            return Framework.FLASK
        elif 'fastapi' in command_lower:
            return Framework.FASTAPI
        
        # Backend Frameworks - PHP
        elif 'laravel' in command_lower:
            return Framework.LARAVEL
        elif 'symfony' in command_lower:
            return Framework.SYMFONY
        
        # Backend Frameworks - Ruby
        elif 'rails' in command_lower or 'ruby on rails' in command_lower:
            return Framework.RAILS
        elif 'sinatra' in command_lower:
            return Framework.SINATRA
        
        # Backend Frameworks - .NET
        elif 'asp.net' in command_lower or 'aspnet' in command_lower:
            return Framework.ASPNET_CORE
        
        # Mobile Frameworks
        elif 'flutter' in command_lower:
            return Framework.FLUTTER
        elif 'react native' in command_lower:
            return Framework.REACT_NATIVE
        elif 'ionic' in command_lower:
            return Framework.IONIC
        elif 'xamarin' in command_lower:
            return Framework.XAMARIN
        
        # AI/ML Frameworks
        elif 'tensorflow' in command_lower:
            return Framework.TENSORFLOW
        elif 'pytorch' in command_lower:
            return Framework.PYTORCH
        elif 'keras' in command_lower:
            return Framework.KERAS
        elif 'scikit' in command_lower or 'sklearn' in command_lower:
            return Framework.SCIKIT_LEARN
        
        # Data Science
        elif 'pandas' in command_lower:
            return Framework.PANDAS
        elif 'numpy' in command_lower:
            return Framework.NUMPY
        elif 'matplotlib' in command_lower:
            return Framework.MATPLOTLIB
        
        # Game Engines
        elif 'unity' in command_lower:
            return Framework.UNITY
        elif 'unreal' in command_lower:
            return Framework.UNREAL
        elif 'godot' in command_lower:
            return Framework.GODOT
        
        # Desktop
        elif 'electron' in command_lower:
            return Framework.ELECTRON
        elif 'maui' in command_lower:
            return Framework.DOTNET_MAUI
        
        # DevOps
        elif 'docker' in command_lower and 'file' not in command_lower:
            return Framework.DOCKER
        elif 'kubernetes' in command_lower or 'k8s' in command_lower:
            return Framework.KUBERNETES
        elif 'terraform' in command_lower:
            return Framework.TERRAFORM
        elif 'ansible' in command_lower:
            return Framework.ANSIBLE
        
        return None
    
    async def _store_interaction(self, command: str, result: Dict):
        """Store interaction in memory"""
        try:
            interaction = {
                'command': command,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'engineering_mode': self.engineering_mode
            }
            
            # Store in memory system
            await asyncio.to_thread(
                self.memory.store_interaction,
                interaction
            )
        
        except Exception as e:
            print(f"   Warning: Failed to store interaction: {e}")
    
    async def monitor_system_health(self):
        """Continuous system health monitoring"""
        print("🏥 Starting system health monitoring...")
        
        while True:
            try:
                # Get system metrics
                import psutil
                
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                metrics = {
                    'cpu': cpu,
                    'memory': memory.percent,
                    'disk': disk.percent,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Check for issues
                if cpu > 90 or memory.percent > 90 or disk.percent > 90:
                    print(f"⚠️  High resource usage detected!")
                    
                    # Trigger self-healing
                    if self.engineering_mode:
                        await self.self_healing.optimize_memory()
                        self.stats['self_healing_events'] += 1
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
            
            except Exception as e:
                print(f"Error in health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def process_autonomous_goals(self):
        """Process autonomous goals in background"""
        print("🎯 Starting autonomous goal processing...")
        
        while True:
            try:
                if self.engineering_mode:
                    # Check for autonomous goals
                    goals = await asyncio.to_thread(
                        self.autonomous_goals.get_pending_goals
                    )
                    
                    for goal in goals:
                        print(f"   Processing autonomous goal: {goal.get('description')}")
                        
                        # Process goal
                        result = await self.process_command(
                            goal.get('description'),
                            {'autonomous': True}
                        )
                        
                        # Update goal status
                        await asyncio.to_thread(
                            self.autonomous_goals.update_goal_status,
                            goal.get('id'),
                            'completed' if result.get('success') else 'failed'
                        )
                
                # Sleep for 60 seconds
                await asyncio.sleep(60)
            
            except Exception as e:
                print(f"Error in autonomous goal processing: {e}")
                await asyncio.sleep(60)
    
    async def start_background_tasks(self):
        """Start all background tasks"""
        print("🚀 Starting background tasks...")
        
        tasks = [
            asyncio.create_task(self.monitor_system_health()),
            asyncio.create_task(self.process_autonomous_goals())
        ]
        
        await asyncio.gather(*tasks)
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            'engineering_mode': self.engineering_mode,
            'stats': self.stats,
            'brain_stats': self.brain.get_stats(),
            'coder_stats': self.multi_agent_coder.get_stats(),
            'healing_stats': self.self_healing.get_healing_stats(),
            'memory_stats': self.memory.get_stats(),
            'timestamp': datetime.now().isoformat()
        }


# Singleton instance
_orchestrator = None

def get_orchestrator() -> MasterOrchestrator:
    """Get singleton Master Orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MasterOrchestrator()
    return _orchestrator


# Test
if __name__ == "__main__":
    async def test():
        print("🧪 Testing Master Orchestrator...")
        
        orchestrator = get_orchestrator()
        
        # Enable engineering mode
        orchestrator.set_engineering_mode(True)
        
        # Test 1: System task
        print("\n1️⃣ Test: System task")
        result = await orchestrator.process_command("open instagram")
        print(f"   Success: {result.get('success')}")
        
        # Test 2: Coding task
        print("\n2️⃣ Test: Coding task")
        result = await orchestrator.process_command(
            "write a Python function to calculate fibonacci"
        )
        print(f"   Success: {result.get('success')}")
        
        # Test 3: Developer task
        print("\n3️⃣ Test: Developer task")
        result = await orchestrator.process_command(
            "create a React project with TypeScript"
        )
        print(f"   Success: {result.get('success')}")
        
        # Test 4: System status
        print("\n4️⃣ Test: System status")
        status = orchestrator.get_system_status()
        print(f"   Total commands: {status['stats']['total_commands']}")
        print(f"   Success rate: {status['stats']['successful_commands']}/{status['stats']['total_commands']}")
        
        print("\n✅ Master Orchestrator test complete")
    
    asyncio.run(test())
