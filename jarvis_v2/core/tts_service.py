#!/usr/bin/env python3
"""
JARVIS TTS Service - Backend Text-to-Speech
Uses pyttsx3 for offline, high-quality speech
"""

import pyttsx3
from typing import Optional, Dict, Callable
import threading
import queue
import time

class TTSService:
    """
    Backend TTS service with pyttsx3
    Supports async speech generation with callbacks
    """
    
    def __init__(self):
        self.engine = None
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.enabled = True  # Backend TTS enabled for JARVIS voice
        
        # Initialize engine
        self._init_engine()
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        
        print("🎙️  TTS Service initialized")
    
    def _init_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            
            # Try to find Daniel voice on macOS
            daniel_voice = None
            for voice in voices:
                if 'daniel' in voice.name.lower():
                    daniel_voice = voice
                    break
            
            if daniel_voice:
                self.engine.setProperty('voice', daniel_voice.id)
                print(f"   ✓ Using voice: {daniel_voice.name}")
            else:
                # Use first English voice
                for voice in voices:
                    if 'en' in voice.languages[0].lower():
                        self.engine.setProperty('voice', voice.id)
                        print(f"   ✓ Using voice: {voice.name}")
                        break
            
            # Set properties for JARVIS-like voice
            self.engine.setProperty('rate', 175)      # Speed (default: 200)
            self.engine.setProperty('volume', 0.95)   # Volume (0.0 to 1.0)
            
        except Exception as e:
            print(f"   ✗ TTS initialization error: {e}")
            self.engine = None
    
    def speak(self, text: str, priority: str = 'normal', 
              on_start: Optional[Callable] = None,
              on_end: Optional[Callable] = None):
        """
        Add text to speech queue with input sanitization
        
        Args:
            text: Text to speak
            priority: 'low', 'normal', 'high', 'critical'
            on_start: Callback when speech starts
            on_end: Callback when speech ends
        """
        if not self.enabled or not self.engine:
            return
        
        # Sanitize input to prevent TTS injection attacks
        sanitized_text = self._sanitize_text(text)
        
        if not sanitized_text:
            return
        
        self.speech_queue.put({
            'text': sanitized_text,
            'priority': priority,
            'on_start': on_start,
            'on_end': on_end,
            'timestamp': time.time()
        })
    
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text input to prevent TTS injection
        
        Removes:
        - Control characters
        - Excessive whitespace
        - Potential SSML injection
        - Very long texts (DoS prevention)
        """
        if not text:
            return ""
        
        # Limit length (prevent DoS)
        MAX_LENGTH = 5000
        if len(text) > MAX_LENGTH:
            text = text[:MAX_LENGTH] + "..."
        
        # Remove control characters except newline and tab
        sanitized = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        # Remove potential SSML tags (if engine supports SSML)
        sanitized = sanitized.replace('<', '').replace('>', '')
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized.strip()
    
    def _process_queue(self):
        """Process speech queue in background thread"""
        while True:
            try:
                item = self.speech_queue.get()
                
                # Handle priority
                if item['priority'] in ['critical', 'high']:
                    # Clear queue for high priority messages
                    cleared = 0
                    while not self.speech_queue.empty():
                        try:
                            self.speech_queue.get_nowait()
                            cleared += 1
                        except queue.Empty:
                            break
                    
                    if cleared > 0:
                        print(f"   ⚡ Cleared {cleared} messages for priority speech")
                
                # Start speaking
                self.is_speaking = True
                
                # Call on_start callback
                if item['on_start']:
                    try:
                        item['on_start']()
                    except Exception as e:
                        print(f"   ✗ on_start callback error: {e}")
                
                # Speak
                if self.engine:
                    self.engine.say(item['text'])
                    self.engine.runAndWait()
                
                # End speaking
                self.is_speaking = False
                
                # Call on_end callback
                if item['on_end']:
                    try:
                        item['on_end']()
                    except Exception as e:
                        print(f"   ✗ on_end callback error: {e}")
                
            except Exception as e:
                print(f"   ✗ TTS processing error: {e}")
                self.is_speaking = False
    
    def stop(self):
        """Stop current speech and clear queue"""
        if self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                # Ignore errors when stopping TTS engine
                pass
        
        # Clear queue
        cleared = 0
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                cleared += 1
            except queue.Empty:
                break
        
        self.is_speaking = False
        
        if cleared > 0:
            print(f"   🛑 Stopped TTS, cleared {cleared} messages")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable TTS"""
        self.enabled = enabled
        
        if not enabled:
            self.stop()
        
        print(f"   {'✓' if enabled else '✗'} TTS {'enabled' if enabled else 'disabled'}")
    
    def get_status(self) -> Dict:
        """Get TTS status"""
        return {
            'enabled': self.enabled,
            'is_speaking': self.is_speaking,
            'queue_size': self.speech_queue.qsize(),
            'engine_available': self.engine is not None
        }

# Singleton instance
_tts_service = None

def get_tts_service() -> TTSService:
    """Get singleton TTS service instance"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service

if __name__ == "__main__":
    # Test TTS service
    print("🧪 Testing TTS Service...")
    
    tts = get_tts_service()
    
    print("\n1. Testing basic speech...")
    tts.speak("Good morning, sir. All systems operational.")
    time.sleep(3)
    
    print("\n2. Testing priority speech...")
    tts.speak("This is a normal message", priority='normal')
    tts.speak("This is a critical alert", priority='critical')
    time.sleep(3)
    
    print("\n3. Testing callbacks...")
    def on_start():
        print("   → Speech started")
    
    def on_end():
        print("   → Speech ended")
    
    tts.speak("Testing callbacks, sir", on_start=on_start, on_end=on_end)
    time.sleep(3)
    
    print("\n4. Status:")
    status = tts.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n✓ TTS Service test complete")
