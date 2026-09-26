#!/usr/bin/env python3
"""
JARVIS Watchdog Manager - Enhanced
Monitors system health and restarts services if needed

Features:
- Continuous background monitoring (disk, RAM, CPU, dependency updates)
- Auto-restart crashed services
- Memory leak detection
- Performance optimization
- Dependency update checking
- Integration with self-healing system
"""

import os
import sys
import time
import signal
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import json
import asyncio

class WatchdogManager:
    """Enhanced Watchdog Manager with continuous monitoring"""
    
    def __init__(self, config_path: str = "config/watchdog.yaml"):
        self.config_path = config_path
        self.pid_dir = Path(".pids")
        self.log_dir = Path("logs")
        self.running = True
        
        # Ensure directories exist
        self.pid_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # Service definitions
        self.services = {
            "backend": {
                "command": ["python3", "api/websocket_server_enhanced.py"],
                "port": 8001,
                "pid_file": self.pid_dir / "backend.pid",
                "log_file": self.log_dir / "backend.log",
                "restart_delay": 5,
                "memory_limit_mb": 500,  # Alert if exceeds
                "cpu_limit_percent": 80
            },
            "tools": {
                "command": ["node", "tools/server.js"],
                "port": 8002,
                "pid_file": self.pid_dir / "tools.pid",
                "log_file": self.log_dir / "tools.log",
                "restart_delay": 5,
                "memory_limit_mb": 300,
                "cpu_limit_percent": 70
            },
            "frontend": {
                "command": ["npm", "run", "dev"],
                "port": 5174,
                "pid_file": self.pid_dir / "frontend.pid",
                "log_file": self.log_dir / "frontend.log",
                "restart_delay": 10,
                "cwd": "frontend",
                "memory_limit_mb": 400,
                "cpu_limit_percent": 60
            }
        }
        
        # Health check intervals (seconds)
        self.check_interval = 10
        self.max_restart_attempts = 3
        self.restart_window = 60  # Reset restart counter after 60 seconds
        
        # Restart tracking
        self.restart_counts: Dict[str, int] = {name: 0 for name in self.services}
        self.last_restart: Dict[str, float] = {name: 0 for name in self.services}
        
        # Enhanced monitoring
        self.system_metrics_history: List[Dict] = []
        self.max_history = 100  # Keep last 100 metrics
        self.memory_leak_threshold = 1.5  # 50% increase = potential leak
        self.dependency_check_interval = 3600  # Check every hour
        self.last_dependency_check = 0
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
        # Also write to watchdog log
        with open(self.log_dir / "watchdog.log", "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    def is_process_running(self, pid: int) -> bool:
        """Check if process is running"""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def get_service_pid(self, service_name: str) -> Optional[int]:
        """Get PID from pid file"""
        service = self.services[service_name]
        pid_file = service["pid_file"]
        
        if not pid_file.exists():
            return None
        
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            return pid if self.is_process_running(pid) else None
        except (ValueError, IOError):
            return None
    
    def start_service(self, service_name: str) -> bool:
        """Start a service"""
        service = self.services[service_name]
        
        self.log(f"Starting {service_name}...")
        
        try:
            # Open log file
            log_file = open(service["log_file"], "a")
            
            # Start process
            cwd = service.get("cwd", ".")
            process = subprocess.Popen(
                service["command"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Save PID
            with open(service["pid_file"], "w") as f:
                f.write(str(process.pid))
            
            # Wait a bit and check if it started
            time.sleep(2)
            
            if self.is_process_running(process.pid):
                self.log(f"✓ {service_name} started (PID: {process.pid})")
                return True
            else:
                self.log(f"✗ {service_name} failed to start", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"✗ Error starting {service_name}: {e}", "ERROR")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a service"""
        pid = self.get_service_pid(service_name)
        
        if not pid:
            self.log(f"{service_name} is not running")
            return True
        
        self.log(f"Stopping {service_name} (PID: {pid})...")
        
        try:
            # Try graceful shutdown first
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # Wait for process to stop
            for _ in range(10):
                if not self.is_process_running(pid):
                    self.log(f"✓ {service_name} stopped")
                    return True
                time.sleep(0.5)
            
            # Force kill if still running
            self.log(f"Force killing {service_name}...", "WARN")
            os.killpg(os.getpgid(pid), signal.SIGKILL)
            time.sleep(1)
            
            return not self.is_process_running(pid)
            
        except Exception as e:
            self.log(f"Error stopping {service_name}: {e}", "ERROR")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        current_time = time.time()
        
        # Reset restart counter if outside window
        if current_time - self.last_restart[service_name] > self.restart_window:
            self.restart_counts[service_name] = 0
        
        # Check restart limit
        if self.restart_counts[service_name] >= self.max_restart_attempts:
            self.log(
                f"✗ {service_name} exceeded max restart attempts ({self.max_restart_attempts})",
                "ERROR"
            )
            return False
        
        # Stop and start
        self.stop_service(service_name)
        time.sleep(self.services[service_name]["restart_delay"])
        
        success = self.start_service(service_name)
        
        if success:
            self.restart_counts[service_name] += 1
            self.last_restart[service_name] = current_time
        
        return success
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if service is healthy"""
        service = self.services[service_name]
        pid = self.get_service_pid(service_name)
        
        # Check if process is running
        if not pid or not self.is_process_running(pid):
            self.log(f"✗ {service_name} is not running", "WARN")
            return False
        
        # Check if port is listening
        if not self.is_port_in_use(service["port"]):
            self.log(f"✗ {service_name} port {service['port']} not listening", "WARN")
            return False
        
        return True
    
    def monitor_loop(self) -> None:
        """Main monitoring loop with enhanced features"""
        self.log("🚀 JARVIS Watchdog started (Enhanced Mode)")
        
        # Start all services
        for service_name in self.services:
            if not self.check_service_health(service_name):
                self.start_service(service_name)
        
        # Monitor loop
        while self.running:
            try:
                time.sleep(self.check_interval)
                
                # 1. Check service health
                for service_name in self.services:
                    if not self.check_service_health(service_name):
                        self.log(f"⚠️  {service_name} unhealthy, restarting...", "WARN")
                        self.restart_service(service_name)
                
                # 2. Monitor system metrics
                self.monitor_system_metrics()
                
                # 3. Check for memory leaks
                self.check_memory_leaks()
                
                # 4. Monitor resource usage per service
                self.monitor_service_resources()
                
                # 5. Check dependencies (hourly)
                current_time = time.time()
                if current_time - self.last_dependency_check > self.dependency_check_interval:
                    self.check_dependencies()
                    self.last_dependency_check = current_time
                
            except KeyboardInterrupt:
                self.log("Received shutdown signal")
                self.running = False
            except Exception as e:
                self.log(f"Error in monitor loop: {e}", "ERROR")
    
    def monitor_system_metrics(self) -> None:
        """Monitor overall system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024
            }
            
            # Add to history
            self.system_metrics_history.append(metrics)
            if len(self.system_metrics_history) > self.max_history:
                self.system_metrics_history.pop(0)
            
            # Alert on high usage
            if cpu_percent > 90:
                self.log(f"⚠️  High CPU usage: {cpu_percent}%", "WARN")
            
            if memory.percent > 90:
                self.log(f"⚠️  High memory usage: {memory.percent}%", "WARN")
            
            if disk.percent > 90:
                self.log(f"⚠️  High disk usage: {disk.percent}%", "WARN")
            
            # Save metrics to file
            metrics_file = self.log_dir / "system_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(self.system_metrics_history[-10:], f, indent=2)
        
        except Exception as e:
            self.log(f"Error monitoring system metrics: {e}", "ERROR")
    
    def check_memory_leaks(self) -> None:
        """Check for potential memory leaks"""
        if len(self.system_metrics_history) < 10:
            return
        
        try:
            # Compare current memory with 10 checks ago
            current = self.system_metrics_history[-1]['memory_percent']
            past = self.system_metrics_history[-10]['memory_percent']
            
            if current > past * self.memory_leak_threshold:
                self.log(
                    f"⚠️  Potential memory leak detected: {past}% → {current}%",
                    "WARN"
                )
                
                # Trigger garbage collection
                import gc
                gc.collect()
                self.log("   Triggered garbage collection")
        
        except Exception as e:
            self.log(f"Error checking memory leaks: {e}", "ERROR")
    
    def monitor_service_resources(self) -> None:
        """Monitor resource usage per service"""
        for service_name, service in self.services.items():
            pid = self.get_service_pid(service_name)
            
            if not pid:
                continue
            
            try:
                process = psutil.Process(pid)
                
                # Get resource usage
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # Check limits
                if memory_mb > service.get('memory_limit_mb', 1000):
                    self.log(
                        f"⚠️  {service_name} exceeds memory limit: {memory_mb:.1f}MB",
                        "WARN"
                    )
                
                if cpu_percent > service.get('cpu_limit_percent', 100):
                    self.log(
                        f"⚠️  {service_name} exceeds CPU limit: {cpu_percent}%",
                        "WARN"
                    )
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            except Exception as e:
                self.log(f"Error monitoring {service_name} resources: {e}", "ERROR")
    
    def check_dependencies(self) -> None:
        """Check for dependency updates"""
        self.log("🔍 Checking dependencies...")
        
        try:
            # Check Python dependencies
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                outdated = json.loads(result.stdout)
                
                if outdated:
                    self.log(f"   Found {len(outdated)} outdated Python packages")
                    
                    # Log first 5
                    for pkg in outdated[:5]:
                        self.log(
                            f"   - {pkg['name']}: {pkg['version']} → {pkg['latest_version']}",
                            "INFO"
                        )
                else:
                    self.log("   ✓ All Python packages up to date")
        
        except Exception as e:
            self.log(f"Error checking Python dependencies: {e}", "ERROR")
        
        # Check Node.js dependencies
        frontend_dir = Path("frontend")
        if frontend_dir.exists():
            try:
                result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=frontend_dir,
                    timeout=30
                )
                
                if result.stdout:
                    outdated = json.loads(result.stdout)
                    
                    if outdated:
                        self.log(f"   Found {len(outdated)} outdated npm packages")
                    else:
                        self.log("   ✓ All npm packages up to date")
            
            except Exception as e:
                self.log(f"Error checking npm dependencies: {e}", "ERROR")
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'system_metrics': self.system_metrics_history[-1] if self.system_metrics_history else {},
            'restart_counts': self.restart_counts
        }
        
        for service_name in self.services:
            pid = self.get_service_pid(service_name)
            healthy = self.check_service_health(service_name)
            
            service_status = {
                'running': pid is not None,
                'healthy': healthy,
                'pid': pid,
                'restart_count': self.restart_counts[service_name]
            }
            
            if pid:
                try:
                    process = psutil.Process(pid)
                    service_status['cpu_percent'] = process.cpu_percent(interval=0.1)
                    service_status['memory_mb'] = process.memory_info().rss / 1024 / 1024
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process no longer exists or we don't have permission
                    pass
            
            status['services'][service_name] = service_status
        
        return status
    
    def shutdown(self) -> None:
        """Shutdown all services"""
        self.log("Shutting down all services...")
        
        for service_name in self.services:
            self.stop_service(service_name)
        
        self.log("✓ Watchdog shutdown complete")

def main() -> None:
    """Main entry point"""
    watchdog = WatchdogManager()
    
    # Handle signals
    def signal_handler(signum, frame):
        watchdog.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        watchdog.monitor_loop()
    finally:
        watchdog.shutdown()

if __name__ == "__main__":
    main()
