#!/usr/bin/env python3
"""
JARVIS Core Daemon Agent - Phase 1
Always-on, event-driven AI agent with tiered intelligence
"""

import os
import sys
import time
import signal
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import threading

from brain_service import BrainService, IntelligenceLevel
from environment_watcher import EnvironmentWatcher

class DaemonAgent:
    """
    Core daemon agent - always running, event-driven
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.running = True
        self.config_path = config_path
        
        # Initialize components
        self.brain = BrainService()
        self.env_watcher = EnvironmentWatcher()
        
        # Event queue
        self.event_queue: List[Dict] = []
        self.event_lock = threading.Lock()
        
        # Monitoring intervals
        self.env_check_interval = 30  # seconds
        self.health_check_interval = 60  # seconds
        
        # State
        self.state = {
            "started_at": datetime.now().isoformat(),
            "status": "initializing",
            "last_query": None,
            "last_event": None,
            "total_queries": 0,
            "total_events": 0
        }
        
        # Logs
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.log("🚀 JARVIS Daemon Agent initializing...")
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp and level"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        print(log_message)
        
        with open(self.log_dir / "daemon.log", "a") as f:
            f.write(log_message + "\n")
    
    def add_event(self, event_type: str, data: Dict) -> None:
        """Add event to queue for processing"""
        with self.event_lock:
            event = {
                "type": event_type,
                "data": data,
                "timestamp": time.time()
            }
            self.event_queue.append(event)
            self.state["total_events"] += 1
            self.state["last_event"] = event
            
            self.log(f"📥 Event added: {event_type}")
    
    def process_event(self, event: Dict) -> None:
        """Process a single event from the queue"""
        event_type = event["type"]
        data = event["data"]
        
        self.log(f"⚙️  Processing event: {event_type}")
        
        if event_type == "system_alert":
            self.handle_system_alert(data)
        elif event_type == "user_query":
            self.handle_user_query(data)
        elif event_type == "autonomous_trigger":
            self.handle_autonomous_trigger(data)
        else:
            self.log(f"⚠️  Unknown event type: {event_type}", "WARN")
    
    def handle_system_alert(self, data: Dict) -> None:
        """Handle system resource alerts and log them"""
        alert = data.get("alert", {})
        alert_type = alert.get("type")
        
        self.log(f"🚨 System alert: {alert.get('message')}", "WARN")
        
        # For now, just log. In Phase 5, we'll add autonomous actions
        # Example: High CPU → suggest closing apps
        # Example: Low memory → suggest cleanup
    
    def handle_user_query(self, data: Dict) -> Optional[Dict]:
        """Handle user query and process with brain service"""
        query = data.get("query", "")
        
        if not query:
            return
        
        self.log(f"💬 User query: '{query}'")
        
        # Process with brain service
        result = self.brain.process_query(query)
        
        self.state["total_queries"] += 1
        self.state["last_query"] = {
            "query": query,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log result
        analysis = result.get("analysis", {})
        self.log(
            f"✓ Processed with {analysis.get('level', 'unknown')} "
            f"(confidence: {analysis.get('confidence', 0):.2f})"
        )
        
        return result
    
    def handle_autonomous_trigger(self, data: Dict) -> None:
        """Handle autonomous thinking trigger for goal generation"""
        trigger_type = data.get("trigger_type")
        
        self.log(f"🤔 Autonomous trigger: {trigger_type}")
        
        # For now, just log. In Phase 5, we'll add autonomous goal generation
    
    def monitor_environment(self) -> None:
        """Monitor system environment and check for alerts"""
        while self.running:
            try:
                # Get metrics
                result = self.env_watcher.monitor_once()
                
                # Check for alerts
                alerts = result.get("alerts", [])
                for alert in alerts:
                    self.add_event("system_alert", {"alert": alert})
                
                # Save metrics periodically
                self.env_watcher.save_metrics()
                
                time.sleep(self.env_check_interval)
                
            except Exception as e:
                self.log(f"Error in environment monitoring: {e}", "ERROR")
                time.sleep(self.env_check_interval)
    
    def process_event_queue(self) -> None:
        """Process events from queue continuously"""
        while self.running:
            try:
                # Get events
                with self.event_lock:
                    events = self.event_queue.copy()
                    self.event_queue.clear()
                
                # Process each event
                for event in events:
                    self.process_event(event)
                
                time.sleep(1)  # Check queue every second
                
            except Exception as e:
                self.log(f"Error processing event queue: {e}", "ERROR")
                time.sleep(1)
    
    def health_check(self) -> None:
        """Periodic health check and state saving"""
        while self.running:
            try:
                self.log("💚 Health check: OK")
                
                # Save state
                self.save_state()
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.log(f"Error in health check: {e}", "ERROR")
                time.sleep(self.health_check_interval)
    
    def save_state(self) -> None:
        """Save daemon state to JSON file"""
        state_file = self.log_dir / "daemon_state.json"
        
        state_data = {
            **self.state,
            "brain_stats": self.brain.get_stats(),
            "env_summary": self.env_watcher.get_metrics_summary()
        }
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def start(self) -> None:
        """Start the daemon agent and monitoring threads"""
        self.log("🚀 Starting JARVIS Daemon Agent...")
        self.state["status"] = "running"
        
        # Start monitoring threads
        env_thread = threading.Thread(target=self.monitor_environment, daemon=True)
        event_thread = threading.Thread(target=self.process_event_queue, daemon=True)
        health_thread = threading.Thread(target=self.health_check, daemon=True)
        
        env_thread.start()
        event_thread.start()
        health_thread.start()
        
        self.log("✓ All monitoring threads started")
        self.log("✓ Daemon agent is now running")
        
        # Main loop - just keep alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("Received shutdown signal")
            self.shutdown()
    
    def shutdown(self) -> None:
        """Shutdown the daemon and save final state"""
        self.log("🛑 Shutting down daemon agent...")
        self.running = False
        self.state["status"] = "stopped"
        
        # Save final state
        self.save_state()
        
        self.log("✓ Daemon agent stopped")

def main() -> None:
    """Main entry point for daemon agent"""
    daemon = DaemonAgent()
    
    # Handle signals
    def signal_handler(signum, frame):
        daemon.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start daemon
    daemon.start()

if __name__ == "__main__":
    main()
