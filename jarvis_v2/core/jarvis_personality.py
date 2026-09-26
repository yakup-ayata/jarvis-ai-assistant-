#!/usr/bin/env python3
"""
JARVIS Personality Layer - Tony Stark Style
Adds character and personality to all responses
"""

import random
from typing import Dict

class JarvisPersonality:
    """
    Add Tony Stark style personality to JARVIS responses
    """
    
    # Greetings
    GREETINGS = [
        "Good morning, sir",
        "Welcome back, sir",
        "At your service, sir",
        "Good to see you, sir",
        "Systems online, sir",
    ]
    
    # Confirmations
    CONFIRMATIONS = [
        "Right away, sir",
        "Consider it done, sir",
        "On it, sir",
        "Certainly, sir",
        "Immediately, sir",
        "Of course, sir",
        "As you wish, sir",
    ]
    
    # Action acknowledgments
    ACTION_PREFIXES = [
        "Opening",
        "Launching",
        "Activating",
        "Initializing",
        "Starting",
    ]
    
    ACTION_SUFFIXES = [
        "sir",
        "as requested",
        "for you, sir",
    ]
    
    # Warnings
    WARNINGS = [
        "Sir, I must advise caution",
        "That might not be wise, sir",
        "I recommend reconsidering, sir",
        "Sir, I would advise against that",
        "Perhaps we should reconsider, sir",
    ]
    
    # Errors
    ERRORS = [
        "I'm afraid that didn't work, sir",
        "We have a problem, sir",
        "Something went wrong, sir",
        "That didn't go as planned, sir",
        "I encountered an issue, sir",
    ]
    
    # Autonomous goals
    GOAL_PREFIXES = [
        "Sir, I've detected",
        "Sir, I notice",
        "Sir, may I suggest",
        "Sir, I recommend",
        "Sir, I propose",
    ]
    
    # Success
    SUCCESS = [
        "Done, sir",
        "Complete, sir",
        "Task completed, sir",
        "All set, sir",
        "Finished, sir",
    ]
    
    # Thinking
    THINKING = [
        "One moment, sir",
        "Processing, sir",
        "Analyzing, sir",
        "Working on it, sir",
        "Give me a moment, sir",
    ]
    
    @staticmethod
    def enhance_greeting() -> str:
        """Generate a greeting"""
        return random.choice(JarvisPersonality.GREETINGS)
    
    @staticmethod
    def enhance_action(action: str, target: str = None) -> str:
        """
        Enhance action message with personality
        
        Examples:
            "open instagram" → "Opening Instagram for you, sir"
            "close app" → "Closing application, sir"
        """
        prefix = random.choice(JarvisPersonality.ACTION_PREFIXES)
        suffix = random.choice(JarvisPersonality.ACTION_SUFFIXES)
        
        if target:
            return f"{prefix} {target}, {suffix}"
        else:
            return f"{prefix} {action}, {suffix}"
    
    @staticmethod
    def enhance_confirmation(message: str = None) -> str:
        """Generate a confirmation"""
        confirmation = random.choice(JarvisPersonality.CONFIRMATIONS)
        
        if message:
            return f"{confirmation}. {message}"
        else:
            return confirmation
    
    @staticmethod
    def enhance_warning(message: str) -> str:
        """Enhance warning message"""
        prefix = random.choice(JarvisPersonality.WARNINGS)
        return f"{prefix}. {message}"
    
    @staticmethod
    def enhance_error(error: str) -> str:
        """Enhance error message"""
        prefix = random.choice(JarvisPersonality.ERRORS)
        return f"{prefix}. {error}"
    
    @staticmethod
    def enhance_goal(goal: str) -> str:
        """Enhance autonomous goal message"""
        prefix = random.choice(JarvisPersonality.GOAL_PREFIXES)
        return f"{prefix} {goal}"
    
    @staticmethod
    def enhance_success(message: str = None) -> str:
        """Enhance success message"""
        success = random.choice(JarvisPersonality.SUCCESS)
        
        if message:
            return f"{success}. {message}"
        else:
            return success
    
    @staticmethod
    def enhance_thinking() -> str:
        """Generate thinking message"""
        return random.choice(JarvisPersonality.THINKING)
    
    @staticmethod
    def enhance_message(message: str, message_type: str) -> str:
        """
        Enhance any message with personality based on type
        
        Args:
            message: Original message
            message_type: 'greeting', 'action', 'confirmation', 'warning', 
                         'error', 'goal', 'success', 'thinking'
        
        Returns:
            Enhanced message with JARVIS personality
        """
        if message_type == 'greeting':
            return JarvisPersonality.enhance_greeting()
        
        elif message_type == 'action':
            return JarvisPersonality.enhance_action(message)
        
        elif message_type == 'confirmation':
            return JarvisPersonality.enhance_confirmation(message)
        
        elif message_type == 'warning':
            return JarvisPersonality.enhance_warning(message)
        
        elif message_type == 'error':
            return JarvisPersonality.enhance_error(message)
        
        elif message_type == 'goal':
            return JarvisPersonality.enhance_goal(message)
        
        elif message_type == 'success':
            return JarvisPersonality.enhance_success(message)
        
        elif message_type == 'thinking':
            return JarvisPersonality.enhance_thinking()
        
        else:
            # Default: add "sir" if not present
            if 'sir' not in message.lower():
                return f"{message}, sir"
            return message

def main():
    """Test JARVIS personality"""
    print("🎭 Testing JARVIS Personality...")
    print("=" * 60)
    
    # Test greetings
    print("\n1. Greetings:")
    for _ in range(3):
        print(f"   {JarvisPersonality.enhance_greeting()}")
    
    # Test actions
    print("\n2. Actions:")
    print(f"   {JarvisPersonality.enhance_action('open', 'Instagram')}")
    print(f"   {JarvisPersonality.enhance_action('close', 'Safari')}")
    print(f"   {JarvisPersonality.enhance_action('set volume to 50%')}")
    
    # Test confirmations
    print("\n3. Confirmations:")
    for _ in range(3):
        print(f"   {JarvisPersonality.enhance_confirmation()}")
    
    # Test warnings
    print("\n4. Warnings:")
    print(f"   {JarvisPersonality.enhance_warning('CPU usage is high')}")
    print(f"   {JarvisPersonality.enhance_warning('Memory critically low')}")
    
    # Test errors
    print("\n5. Errors:")
    print(f"   {JarvisPersonality.enhance_error('Connection failed')}")
    print(f"   {JarvisPersonality.enhance_error('Application not found')}")
    
    # Test goals
    print("\n6. Autonomous Goals:")
    print(f"   {JarvisPersonality.enhance_goal('high CPU usage. Shall I optimize?')}")
    print(f"   {JarvisPersonality.enhance_goal('you have been working for 8 hours. Perhaps a break?')}")
    
    # Test success
    print("\n7. Success:")
    for _ in range(3):
        print(f"   {JarvisPersonality.enhance_success()}")
    
    # Test thinking
    print("\n8. Thinking:")
    for _ in range(3):
        print(f"   {JarvisPersonality.enhance_thinking()}")
    
    print("\n" + "=" * 60)
    print("✓ JARVIS Personality test complete")

if __name__ == "__main__":
    main()
