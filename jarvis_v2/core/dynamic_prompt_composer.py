#!/usr/bin/env python3
"""
JARVIS Dynamic Prompt Composer
Context-aware prompt generation based on memory, context, and user patterns

Features:
- Context-based prompt generation
- Memory integration
- User pattern learning
- Dynamic template selection
- Prompt optimization
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

class DynamicPromptComposer:
    """
    Dynamic Prompt Composer for context-aware LLM prompts
    """
    
    def __init__(self):
        self.prompt_templates = self._load_templates()
        self.user_patterns = {}
        self.context_history = []
        
        print("📝 Dynamic Prompt Composer initialized")
    
    def _load_templates(self) -> Dict:
        """Load prompt templates"""
        return {
            'simple_query': """You are JARVIS, an AI assistant. Answer this query concisely.

Query: {query}

Context:
{context}

Answer:""",
            
            'coding_task': """You are JARVIS, an expert programmer. Help with this coding task.

Task: {query}

Context:
- Language: {language}
- Previous work: {previous_work}
- User preferences: {preferences}

{context}

Provide clean, efficient code with explanations:""",
            
            'planning_task': """You are JARVIS, a strategic planner. Create a detailed plan.

Goal: {query}

Context:
- Available resources: {resources}
- Constraints: {constraints}
- Previous plans: {previous_plans}

{context}

Create a step-by-step plan:""",
            
            'analysis_task': """You are JARVIS, an analytical expert. Analyze this situation.

Subject: {query}

Context:
- Data: {data}
- Previous analysis: {previous_analysis}
- Focus areas: {focus_areas}

{context}

Provide detailed analysis:""",
            
            'error_resolution': """You are JARVIS, a debugging expert. Help resolve this error.

Error: {query}

Context:
- Error type: {error_type}
- Stack trace: {stack_trace}
- Recent changes: {recent_changes}
- Similar past errors: {similar_errors}

{context}

Suggest solutions:""",
            
            'autonomous_goal': """You are JARVIS, an autonomous agent. Generate a goal based on system state.

System State:
- CPU: {cpu}%
- Memory: {memory}%
- Disk: {disk}%
- Recent errors: {errors}
- User patterns: {patterns}

{context}

Generate ONE proactive goal (JSON format):
{{
    "goal": "clear goal description",
    "reasoning": "why this goal",
    "priority": "low|medium|high",
    "actions": ["action 1", "action 2"]
}}

JSON:"""
        }
    
    def compose_prompt(
        self,
        query: str,
        task_type: str = 'simple_query',
        context: Dict = None,
        memory_entries: List[Dict] = None,
        user_id: str = 'default'
    ) -> str:
        """
        Compose dynamic prompt based on context
        
        Args:
            query: User query
            task_type: Type of task (simple_query, coding_task, etc.)
            context: Additional context
            memory_entries: Relevant memory entries
            user_id: User identifier
        
        Returns:
            Composed prompt string
        """
        context = context or {}
        memory_entries = memory_entries or []
        
        # Get template
        template = self.prompt_templates.get(task_type, self.prompt_templates['simple_query'])
        
        # Build context string
        context_parts = []
        
        # Add memory context
        if memory_entries:
            context_parts.append("Recent Memory:")
            for entry in memory_entries[-5:]:  # Last 5 entries
                context_parts.append(f"- {entry.get('content', '')[:100]}")
        
        # Add user patterns
        if user_id in self.user_patterns:
            patterns = self.user_patterns[user_id]
            context_parts.append(f"\nUser Preferences:")
            context_parts.append(f"- Preferred language: {patterns.get('language', 'Python')}")
            context_parts.append(f"- Code style: {patterns.get('code_style', 'clean')}")
            context_parts.append(f"- Verbosity: {patterns.get('verbosity', 'medium')}")
        
        # Add custom context
        if context:
            context_parts.append("\nAdditional Context:")
            for key, value in context.items():
                if isinstance(value, (str, int, float, bool)):
                    context_parts.append(f"- {key}: {value}")
        
        context_str = "\n".join(context_parts)
        
        # Fill template
        try:
            prompt = template.format(
                query=query,
                context=context_str,
                language=context.get('language', 'Python'),
                previous_work=self._get_previous_work(user_id),
                preferences=self._get_user_preferences(user_id),
                resources=context.get('resources', 'Standard development environment'),
                constraints=context.get('constraints', 'None'),
                previous_plans=self._get_previous_plans(user_id),
                data=context.get('data', 'N/A'),
                previous_analysis=self._get_previous_analysis(user_id),
                focus_areas=context.get('focus_areas', 'General'),
                error_type=context.get('error_type', 'Unknown'),
                stack_trace=context.get('stack_trace', 'N/A'),
                recent_changes=context.get('recent_changes', 'None'),
                similar_errors=self._get_similar_errors(query),
                cpu=context.get('cpu', 0),
                memory=context.get('memory', 0),
                disk=context.get('disk', 0),
                errors=context.get('errors', 0),
                patterns=json.dumps(self.user_patterns.get(user_id, {}))
            )
        except KeyError as e:
            # Fallback to simple template
            prompt = self.prompt_templates['simple_query'].format(
                query=query,
                context=context_str
            )
        
        # Store in history
        self.context_history.append({
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'query': query,
            'prompt_length': len(prompt)
        })
        
        return prompt
    
    def _get_previous_work(self, user_id: str) -> str:
        """Get user's previous work summary"""
        if user_id not in self.user_patterns:
            return "No previous work"
        
        patterns = self.user_patterns[user_id]
        recent_tasks = patterns.get('recent_tasks', [])
        
        if not recent_tasks:
            return "No previous work"
        
        return ", ".join(recent_tasks[-3:])  # Last 3 tasks
    
    def _get_user_preferences(self, user_id: str) -> str:
        """Get user preferences summary"""
        if user_id not in self.user_patterns:
            return "Default preferences"
        
        patterns = self.user_patterns[user_id]
        return f"Language: {patterns.get('language', 'Python')}, Style: {patterns.get('code_style', 'clean')}"
    
    def _get_previous_plans(self, user_id: str) -> str:
        """Get previous planning tasks"""
        # This would query memory system
        return "No previous plans"
    
    def _get_previous_analysis(self, user_id: str) -> str:
        """Get previous analysis tasks"""
        # This would query memory system
        return "No previous analysis"
    
    def _get_similar_errors(self, error_query: str) -> str:
        """Get similar past errors"""
        # This would query memory/reflection system
        return "No similar errors found"
    
    def learn_user_pattern(self, user_id: str, pattern_data: Dict):
        """Learn user patterns from interactions"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                'language': 'Python',
                'code_style': 'clean',
                'verbosity': 'medium',
                'recent_tasks': []
            }
        
        # Update patterns
        patterns = self.user_patterns[user_id]
        
        if 'language' in pattern_data:
            patterns['language'] = pattern_data['language']
        
        if 'task' in pattern_data:
            patterns['recent_tasks'].append(pattern_data['task'])
            # Keep only last 10 tasks
            patterns['recent_tasks'] = patterns['recent_tasks'][-10:]
        
        if 'code_style' in pattern_data:
            patterns['code_style'] = pattern_data['code_style']
        
        if 'verbosity' in pattern_data:
            patterns['verbosity'] = pattern_data['verbosity']
    
    def optimize_prompt(self, prompt: str, max_length: int = 2000) -> str:
        """Optimize prompt length while preserving key information"""
        if len(prompt) <= max_length:
            return prompt
        
        # Simple truncation strategy
        # In production, this would use more sophisticated methods
        lines = prompt.split('\n')
        
        # Keep first and last parts, truncate middle
        keep_start = int(len(lines) * 0.3)
        keep_end = int(len(lines) * 0.3)
        
        optimized_lines = (
            lines[:keep_start] +
            ["\n[... context truncated ...]\n"] +
            lines[-keep_end:]
        )
        
        return '\n'.join(optimized_lines)
    
    def get_stats(self) -> Dict:
        """Get composer statistics"""
        return {
            'total_prompts': len(self.context_history),
            'users_tracked': len(self.user_patterns),
            'templates_available': len(self.prompt_templates),
            'avg_prompt_length': sum(h['prompt_length'] for h in self.context_history) / len(self.context_history) if self.context_history else 0
        }


# Singleton instance
_prompt_composer = None

def get_prompt_composer() -> DynamicPromptComposer:
    """Get singleton Dynamic Prompt Composer instance"""
    global _prompt_composer
    if _prompt_composer is None:
        _prompt_composer = DynamicPromptComposer()
    return _prompt_composer


# Test
if __name__ == "__main__":
    print("🧪 Testing Dynamic Prompt Composer...")
    
    composer = get_prompt_composer()
    
    # Test 1: Simple query
    print("\n1️⃣ Test: Simple query")
    prompt = composer.compose_prompt(
        "What is Python?",
        task_type='simple_query'
    )
    print(f"   Prompt length: {len(prompt)}")
    
    # Test 2: Coding task
    print("\n2️⃣ Test: Coding task")
    prompt = composer.compose_prompt(
        "Write a function to sort a list",
        task_type='coding_task',
        context={'language': 'Python'}
    )
    print(f"   Prompt length: {len(prompt)}")
    
    # Test 3: Learn user pattern
    print("\n3️⃣ Test: Learn user pattern")
    composer.learn_user_pattern('user1', {
        'language': 'TypeScript',
        'task': 'React component',
        'code_style': 'functional'
    })
    print(f"   User patterns: {composer.user_patterns}")
    
    # Test 4: Stats
    print("\n4️⃣ Test: Stats")
    stats = composer.get_stats()
    print(f"   Total prompts: {stats['total_prompts']}")
    print(f"   Avg length: {stats['avg_prompt_length']:.0f}")
    
    print("\n✅ Dynamic Prompt Composer test complete")
