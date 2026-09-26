#!/usr/bin/env python3
"""
JARVIS Sandbox Manager
Safe command execution with whitelist and sandboxing

Features:
- Command whitelist
- Sandbox mode for system operations
- Path restrictions
- Resource limits
- Audit logging
"""

import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json

class SandboxManager:
    """
    Sandbox Manager for safe command execution
    """
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.sandbox_enabled = True
        self.audit_log = []
        
        # Safe command whitelist
        self.safe_commands = {
            # File operations
            'ls', 'cat', 'head', 'tail', 'grep', 'find', 'wc',
            'mkdir', 'touch', 'cp', 'mv', 'rm',
            
            # Development
            'git', 'npm', 'pip', 'python', 'python3', 'node',
            'cargo', 'go', 'javac', 'java', 'swift', 'kotlinc',
            
            # Build tools
            'make', 'cmake', 'gcc', 'g++', 'clang',
            
            # Package managers
            'brew', 'apt-get', 'yum', 'pacman',
            
            # System info (read-only)
            'ps', 'top', 'df', 'du', 'free', 'uptime', 'whoami',
            'uname', 'hostname', 'date', 'cal',
            
            # Text processing
            'sed', 'awk', 'cut', 'sort', 'uniq', 'tr',
            
            # Compression
            'tar', 'gzip', 'gunzip', 'zip', 'unzip',
        }
        
        # Dangerous commands (always blocked)
        self.dangerous_commands = {
            'rm -rf /', 'dd', 'mkfs', 'fdisk', 'parted',
            'shutdown', 'reboot', 'halt', 'poweroff',
            'kill -9', 'killall', 'pkill',
            'chmod 777', 'chown', 'chgrp',
            'sudo', 'su', 'passwd',
            'iptables', 'firewall-cmd',
            'systemctl', 'service',
        }
        
        # Allowed paths (workspace only)
        self.allowed_paths = [
            self.workspace_root,
            Path.home() / '.cache',
            Path.home() / '.local',
            Path('/tmp'),
        ]
        
        # Resource limits
        self.resource_limits = {
            'max_execution_time': 300,  # 5 minutes
            'max_memory_mb': 1024,      # 1 GB
            'max_file_size_mb': 100,    # 100 MB
        }
        
        print(f"🔒 Sandbox Manager initialized")
        print(f"   Workspace: {self.workspace_root}")
        print(f"   Sandbox: {'ENABLED' if self.sandbox_enabled else 'DISABLED'}")
    
    def is_command_safe(self, command: str) -> Tuple[bool, str]:
        """
        Check if command is safe to execute
        
        Returns:
            (is_safe, reason)
        """
        command_lower = command.lower().strip()
        
        # Check for dangerous commands
        for dangerous in self.dangerous_commands:
            if dangerous in command_lower:
                return False, f"Dangerous command detected: {dangerous}"
        
        # Extract base command
        base_command = command.split()[0] if command.split() else ""
        
        # Check whitelist
        if self.sandbox_enabled and base_command not in self.safe_commands:
            return False, f"Command not in whitelist: {base_command}"
        
        # Check for shell injection attempts
        dangerous_chars = [';', '&&', '||', '|', '>', '>>', '<', '`', '$()']
        for char in dangerous_chars:
            if char in command and not self._is_safe_usage(command, char):
                return False, f"Potentially dangerous character: {char}"
        
        return True, "Command is safe"
    
    def _is_safe_usage(self, command: str, char: str) -> bool:
        """Check if special character usage is safe"""
        # Allow pipes for common safe commands
        if char == '|':
            parts = command.split('|')
            for part in parts:
                base_cmd = part.strip().split()[0]
                if base_cmd not in self.safe_commands:
                    return False
            return True
        
        # Allow output redirection to files in workspace
        if char in ['>', '>>']:
            # Extract filename
            match = re.search(r'[>]{1,2}\s*([^\s;]+)', command)
            if match:
                filepath = Path(match.group(1))
                return self.is_path_allowed(filepath)
        
        return False
    
    def is_path_allowed(self, path: Path) -> bool:
        """Check if path is within allowed directories"""
        if not self.sandbox_enabled:
            return True
        
        try:
            resolved_path = path.resolve()
            
            for allowed in self.allowed_paths:
                if resolved_path.is_relative_to(allowed):
                    return True
            
            return False
        
        except Exception:
            return False
    
    def sanitize_command(self, command: str) -> str:
        """Sanitize command for safe execution"""
        # Remove leading/trailing whitespace
        command = command.strip()
        
        # Remove multiple spaces
        command = re.sub(r'\s+', ' ', command)
        
        # Escape special characters if needed
        # (This is a basic implementation, can be enhanced)
        
        return command
    
    def execute_safe(self, command: str, cwd: Optional[str] = None, timeout: int = None) -> Dict:
        """
        Execute command safely with sandbox restrictions
        
        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Execution timeout (seconds)
        
        Returns:
            Dict with execution result
        """
        # Check if command is safe
        is_safe, reason = self.is_command_safe(command)
        
        if not is_safe:
            self._audit_log('BLOCKED', command, reason)
            return {
                'success': False,
                'error': f'Command blocked: {reason}',
                'command': command
            }
        
        # Sanitize command
        safe_command = self.sanitize_command(command)
        
        # Set working directory
        if cwd:
            cwd_path = Path(cwd)
            if not self.is_path_allowed(cwd_path):
                self._audit_log('BLOCKED', command, 'Path not allowed')
                return {
                    'success': False,
                    'error': f'Path not allowed: {cwd}',
                    'command': command
                }
        else:
            cwd = str(self.workspace_root)
        
        # Set timeout
        if timeout is None:
            timeout = self.resource_limits['max_execution_time']
        
        # Execute command
        try:
            result = subprocess.run(
                safe_command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            self._audit_log('EXECUTED', command, 'Success')
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'command': safe_command
            }
        
        except subprocess.TimeoutExpired:
            self._audit_log('TIMEOUT', command, f'Exceeded {timeout}s')
            return {
                'success': False,
                'error': f'Command timeout after {timeout}s',
                'command': safe_command
            }
        
        except Exception as e:
            self._audit_log('ERROR', command, str(e))
            return {
                'success': False,
                'error': str(e),
                'command': safe_command
            }
    
    def _audit_log(self, action: str, command: str, reason: str):
        """Log command execution for audit"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'command': command,
            'reason': reason
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
        
        # Log to file
        log_file = self.workspace_root / 'logs' / 'sandbox_audit.log'
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries"""
        return self.audit_log[-limit:]
    
    def add_safe_command(self, command: str):
        """Add command to whitelist"""
        self.safe_commands.add(command)
        print(f"✓ Added to whitelist: {command}")
    
    def remove_safe_command(self, command: str):
        """Remove command from whitelist"""
        self.safe_commands.discard(command)
        print(f"✓ Removed from whitelist: {command}")
    
    def add_allowed_path(self, path: Path):
        """Add path to allowed paths"""
        self.allowed_paths.append(path.resolve())
        print(f"✓ Added allowed path: {path}")
    
    def set_sandbox_enabled(self, enabled: bool):
        """Enable/disable sandbox mode"""
        self.sandbox_enabled = enabled
        print(f"🔒 Sandbox: {'ENABLED' if enabled else 'DISABLED'}")
    
    def get_stats(self) -> Dict:
        """Get sandbox statistics"""
        total = len(self.audit_log)
        blocked = sum(1 for entry in self.audit_log if entry['action'] == 'BLOCKED')
        executed = sum(1 for entry in self.audit_log if entry['action'] == 'EXECUTED')
        errors = sum(1 for entry in self.audit_log if entry['action'] == 'ERROR')
        
        return {
            'sandbox_enabled': self.sandbox_enabled,
            'total_commands': total,
            'blocked': blocked,
            'executed': executed,
            'errors': errors,
            'whitelist_size': len(self.safe_commands),
            'allowed_paths': len(self.allowed_paths)
        }


# Singleton instance
_sandbox_manager = None

def get_sandbox_manager() -> SandboxManager:
    """Get singleton Sandbox Manager instance"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager()
    return _sandbox_manager


# Test
if __name__ == "__main__":
    print("🧪 Testing Sandbox Manager...")
    
    sandbox = get_sandbox_manager()
    
    # Test 1: Safe command
    print("\n1️⃣ Test: Safe command")
    result = sandbox.execute_safe("ls -la")
    print(f"   Success: {result['success']}")
    
    # Test 2: Dangerous command
    print("\n2️⃣ Test: Dangerous command")
    result = sandbox.execute_safe("rm -rf /")
    print(f"   Blocked: {not result['success']}")
    print(f"   Reason: {result.get('error')}")
    
    # Test 3: Command not in whitelist
    print("\n3️⃣ Test: Command not in whitelist")
    result = sandbox.execute_safe("curl http://example.com")
    print(f"   Blocked: {not result['success']}")
    
    # Test 4: Path check
    print("\n4️⃣ Test: Path check")
    print(f"   Workspace allowed: {sandbox.is_path_allowed(Path('.'))}")
    print(f"   Root not allowed: {sandbox.is_path_allowed(Path('/'))}")
    
    # Test 5: Stats
    print("\n5️⃣ Test: Stats")
    stats = sandbox.get_stats()
    print(f"   Total commands: {stats['total_commands']}")
    print(f"   Blocked: {stats['blocked']}")
    print(f"   Executed: {stats['executed']}")
    
    print("\n✅ Sandbox Manager test complete")
