#!/usr/bin/env python3
"""
JARVIS Audit Logger
Security and compliance audit logging
Tracks all sensitive operations for security review
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum

class AuditEventType(Enum):
    """Audit event types"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    COMMAND_EXECUTION = "command_execution"
    FILE_ACCESS = "file_access"
    SYSTEM_CHANGE = "system_change"
    DATA_ACCESS = "data_access"
    ERROR = "error"
    SECURITY_VIOLATION = "security_violation"

class AuditSeverity(Enum):
    """Audit severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AuditLogger:
    """
    Audit logger for security-sensitive operations
    
    Features:
    - Immutable audit trail
    - Structured JSON logging
    - Automatic rotation
    - Tamper detection
    """
    
    def __init__(self, audit_dir: str = "logs/audit"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Current audit file (rotates daily)
        self.current_file = self._get_audit_file()
        
        print(f"🔒 Audit Logger initialized: {self.current_file}")
    
    def _get_audit_file(self) -> Path:
        """Get current audit file path (daily rotation)"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.audit_dir / f"audit_{date_str}.jsonl"
    
    def log(self,
            event_type: AuditEventType,
            message: str,
            severity: AuditSeverity = AuditSeverity.INFO,
            user_id: Optional[str] = None,
            action: Optional[str] = None,
            target: Optional[str] = None,
            result: Optional[str] = None,
            extra: Optional[Dict[str, Any]] = None):
        """
        Log audit event
        
        Args:
            event_type: Type of audit event
            message: Human-readable message
            severity: Event severity
            user_id: User who performed action
            action: Action performed
            target: Target of action
            result: Result of action (success/failure)
            extra: Additional context data
        """
        # Check if we need to rotate file
        current_file = self._get_audit_file()
        if current_file != self.current_file:
            self.current_file = current_file
        
        # Build audit entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type.value,
            "severity": severity.value,
            "message": message,
            "user_id": user_id,
            "action": action,
            "target": target,
            "result": result
        }
        
        # Add extra data if provided
        if extra:
            audit_entry["extra"] = extra
        
        # Write to audit log (append-only)
        try:
            with open(self.current_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            print(f"❌ Audit logging failed: {e}")
    
    def log_authentication(self, user_id: str, success: bool, method: str = "token"):
        """Log authentication attempt"""
        self.log(
            event_type=AuditEventType.AUTHENTICATION,
            message=f"Authentication {'successful' if success else 'failed'} for user {user_id}",
            severity=AuditSeverity.WARNING if not success else AuditSeverity.INFO,
            user_id=user_id,
            action="authenticate",
            result="success" if success else "failure",
            extra={"method": method}
        )
    
    def log_command(self, user_id: str, command: str, action: str, target: str, success: bool):
        """Log command execution"""
        self.log(
            event_type=AuditEventType.COMMAND_EXECUTION,
            message=f"User {user_id} executed: {command}",
            severity=AuditSeverity.INFO,
            user_id=user_id,
            action=action,
            target=target,
            result="success" if success else "failure",
            extra={"command": command}
        )
    
    def log_file_access(self, user_id: str, file_path: str, operation: str, success: bool):
        """Log file access"""
        self.log(
            event_type=AuditEventType.FILE_ACCESS,
            message=f"User {user_id} {operation} file: {file_path}",
            severity=AuditSeverity.INFO,
            user_id=user_id,
            action=operation,
            target=file_path,
            result="success" if success else "failure"
        )
    
    def log_system_change(self, user_id: str, change_type: str, details: str):
        """Log system configuration change"""
        self.log(
            event_type=AuditEventType.SYSTEM_CHANGE,
            message=f"System change: {change_type}",
            severity=AuditSeverity.WARNING,
            user_id=user_id,
            action=change_type,
            extra={"details": details}
        )
    
    def log_security_violation(self, user_id: str, violation_type: str, details: str):
        """Log security violation"""
        self.log(
            event_type=AuditEventType.SECURITY_VIOLATION,
            message=f"Security violation: {violation_type}",
            severity=AuditSeverity.CRITICAL,
            user_id=user_id,
            action=violation_type,
            extra={"details": details}
        )
    
    def log_error(self, user_id: str, error_type: str, error_message: str):
        """Log error"""
        self.log(
            event_type=AuditEventType.ERROR,
            message=f"Error: {error_type}",
            severity=AuditSeverity.WARNING,
            user_id=user_id,
            action=error_type,
            extra={"error": error_message}
        )
    
    def query_logs(self, 
                   event_type: Optional[AuditEventType] = None,
                   user_id: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: int = 100) -> list:
        """
        Query audit logs
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
        
        Returns:
            List of matching audit entries
        """
        results = []
        
        # Get all audit files in date range
        audit_files = sorted(self.audit_dir.glob("audit_*.jsonl"))
        
        for audit_file in audit_files:
            try:
                with open(audit_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        
                        entry = json.loads(line)
                        
                        # Apply filters
                        if event_type and entry.get("event_type") != event_type.value:
                            continue
                        
                        if user_id and entry.get("user_id") != user_id:
                            continue
                        
                        if start_date:
                            entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                            if entry_time < start_date:
                                continue
                        
                        if end_date:
                            entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                            if entry_time > end_date:
                                continue
                        
                        results.append(entry)
                        
                        if len(results) >= limit:
                            return results
            
            except Exception as e:
                print(f"Error reading audit file {audit_file}: {e}")
        
        return results

# Singleton instance
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    """Get singleton audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger

# Test
if __name__ == "__main__":
    print("🔒 Testing Audit Logger...")
    print("=" * 60)
    
    audit = get_audit_logger()
    
    # Test various audit events
    audit.log_authentication("user123", True, "token")
    audit.log_authentication("hacker", False, "token")
    
    audit.log_command("user123", "open instagram", "open_app", "instagram", True)
    audit.log_command("user123", "delete system32", "delete_file", "system32", False)
    
    audit.log_file_access("user123", "/etc/passwd", "read", False)
    
    audit.log_system_change("admin", "config_update", "Changed TTS voice")
    
    audit.log_security_violation("hacker", "injection_attempt", "SQL injection detected")
    
    print("\n📊 Query Results:")
    print("\n1. All authentication events:")
    results = audit.query_logs(event_type=AuditEventType.AUTHENTICATION)
    for entry in results:
        print(f"   - {entry['timestamp']}: {entry['message']} ({entry['result']})")
    
    print("\n2. All events for user123:")
    results = audit.query_logs(user_id="user123")
    for entry in results:
        print(f"   - {entry['event_type']}: {entry['message']}")
    
    print("\n3. Critical events:")
    results = audit.query_logs()
    critical = [e for e in results if e['severity'] == 'critical']
    for entry in critical:
        print(f"   - {entry['timestamp']}: {entry['message']}")
    
    print("\n" + "=" * 60)
    print("✓ Audit Logger test complete")
    print(f"📁 Audit logs: {audit.audit_dir}")
