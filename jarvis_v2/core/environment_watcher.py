#!/usr/bin/env python3
"""
JARVIS Environment Watcher - Phase 0
Monitors system resources and environment changes
"""

import psutil
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class SystemMetrics:
    """System metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float
    active_processes: int
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_available_gb": self.memory_available_gb,
            "disk_percent": self.disk_percent,
            "network_sent_mb": self.network_sent_mb,
            "network_recv_mb": self.network_recv_mb,
            "active_processes": self.active_processes
        }

class EnvironmentWatcher:
    """Monitors system environment and resources"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Thresholds for alerts
        self.thresholds = {
            "cpu_high": 80.0,
            "memory_high": 85.0,
            "disk_high": 90.0,
            "memory_low_gb": 2.0
        }
        
        # Metrics history (keep last 100 samples)
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 100
        
        # Network baseline
        self.net_io_start = psutil.net_io_counters()
        
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024 ** 3)
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network
        net_io = psutil.net_io_counters()
        network_sent_mb = (net_io.bytes_sent - self.net_io_start.bytes_sent) / (1024 ** 2)
        network_recv_mb = (net_io.bytes_recv - self.net_io_start.bytes_recv) / (1024 ** 2)
        
        # Processes
        active_processes = len(psutil.pids())
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_gb=memory_available_gb,
            disk_percent=disk_percent,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_processes=active_processes
        )
    
    def check_thresholds(self, metrics: SystemMetrics) -> List[Dict]:
        """Check if any thresholds are exceeded"""
        alerts = []
        
        if metrics.cpu_percent > self.thresholds["cpu_high"]:
            alerts.append({
                "type": "cpu_high",
                "severity": "warning",
                "message": f"CPU usage high: {metrics.cpu_percent:.1f}%",
                "value": metrics.cpu_percent,
                "threshold": self.thresholds["cpu_high"]
            })
        
        if metrics.memory_percent > self.thresholds["memory_high"]:
            alerts.append({
                "type": "memory_high",
                "severity": "warning",
                "message": f"Memory usage high: {metrics.memory_percent:.1f}%",
                "value": metrics.memory_percent,
                "threshold": self.thresholds["memory_high"]
            })
        
        if metrics.memory_available_gb < self.thresholds["memory_low_gb"]:
            alerts.append({
                "type": "memory_low",
                "severity": "critical",
                "message": f"Low memory available: {metrics.memory_available_gb:.2f} GB",
                "value": metrics.memory_available_gb,
                "threshold": self.thresholds["memory_low_gb"]
            })
        
        if metrics.disk_percent > self.thresholds["disk_high"]:
            alerts.append({
                "type": "disk_high",
                "severity": "warning",
                "message": f"Disk usage high: {metrics.disk_percent:.1f}%",
                "value": metrics.disk_percent,
                "threshold": self.thresholds["disk_high"]
            })
        
        return alerts
    
    def get_top_processes(self, limit: int = 5) -> List[Dict]:
        """Get top processes by CPU and memory"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'] or 0,
                    'memory_percent': proc.info['memory_percent'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU
        top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
        
        # Sort by memory
        top_memory = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]
        
        return {
            'top_cpu': top_cpu,
            'top_memory': top_memory
        }
    
    def add_metrics(self, metrics: SystemMetrics):
        """Add metrics to history"""
        self.metrics_history.append(metrics)
        
        # Keep only last N samples
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of recent metrics"""
        if not self.metrics_history:
            return {}
        
        recent = self.metrics_history[-10:]  # Last 10 samples
        
        return {
            "avg_cpu": sum(m.cpu_percent for m in recent) / len(recent),
            "avg_memory": sum(m.memory_percent for m in recent) / len(recent),
            "min_memory_available": min(m.memory_available_gb for m in recent),
            "samples": len(recent)
        }
    
    def save_metrics(self):
        """Save metrics history to file"""
        metrics_file = self.log_dir / "system_metrics.json"
        
        data = {
            "last_updated": datetime.now().isoformat(),
            "metrics": [m.to_dict() for m in self.metrics_history[-50:]]  # Last 50
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_dir / "environment.log", "a") as f:
            f.write(log_message)
        
        print(log_message.strip())
    
    def monitor_once(self) -> Dict:
        """Single monitoring cycle"""
        # Get metrics
        metrics = self.get_current_metrics()
        self.add_metrics(metrics)
        
        # Check thresholds
        alerts = self.check_thresholds(metrics)
        
        # Get top processes if there are alerts
        top_processes = None
        if alerts:
            top_processes = self.get_top_processes()
        
        # Log alerts
        for alert in alerts:
            self.log(f"⚠️  {alert['message']}", alert['severity'].upper())
        
        return {
            "metrics": metrics.to_dict(),
            "alerts": alerts,
            "top_processes": top_processes,
            "summary": self.get_metrics_summary()
        }

def main():
    """Test the environment watcher"""
    watcher = EnvironmentWatcher()
    
    print("🔍 JARVIS Environment Watcher - Test Mode")
    print("=" * 50)
    
    for i in range(5):
        print(f"\n📊 Sample {i+1}/5")
        result = watcher.monitor_once()
        
        metrics = result['metrics']
        print(f"CPU: {metrics['cpu_percent']:.1f}%")
        print(f"Memory: {metrics['memory_percent']:.1f}% ({metrics['memory_available_gb']:.2f} GB available)")
        print(f"Disk: {metrics['disk_percent']:.1f}%")
        print(f"Processes: {metrics['active_processes']}")
        
        if result['alerts']:
            print("\n⚠️  Alerts:")
            for alert in result['alerts']:
                print(f"  - {alert['message']}")
        
        time.sleep(2)
    
    # Save metrics
    watcher.save_metrics()
    print(f"\n✓ Metrics saved to {watcher.log_dir}/system_metrics.json")

if __name__ == "__main__":
    main()
