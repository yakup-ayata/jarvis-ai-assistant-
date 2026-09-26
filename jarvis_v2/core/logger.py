#!/usr/bin/env python3
"""
JARVIS Logging System
Centralized logging with color support, file output, and structured logging
"""

import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    FORMATS = {
        logging.DEBUG: Colors.BRIGHT_BLACK + '%(levelname)s' + Colors.RESET + ' - %(name)s - %(message)s',
        logging.INFO: Colors.BRIGHT_BLUE + '%(levelname)s' + Colors.RESET + ' - %(name)s - %(message)s',
        logging.WARNING: Colors.BRIGHT_YELLOW + '%(levelname)s' + Colors.RESET + ' - %(name)s - %(message)s',
        logging.ERROR: Colors.BRIGHT_RED + '%(levelname)s' + Colors.RESET + ' - %(name)s - %(message)s',
        logging.CRITICAL: Colors.BOLD + Colors.RED + '%(levelname)s' + Colors.RESET + ' - %(name)s - %(message)s',
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class StructuredLogger:
    """
    Structured logger with extra context support
    
    Usage:
        logger = StructuredLogger('my_module')
        logger.info('User action', extra={'user_id': '123', 'action': 'login'})
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
    
    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Internal log method with extra data support"""
        if extra:
            # Create a LogRecord with extra data
            record = self.logger.makeRecord(
                self.logger.name,
                level,
                "(unknown file)",
                0,
                message,
                (),
                None
            )
            record.extra_data = extra
            self.logger.handle(record)
        else:
            self.logger.log(level, message, **kwargs)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, extra, **kwargs)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, extra, **kwargs)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, extra, **kwargs)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, message, extra, **kwargs)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, extra, **kwargs)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    structured: bool = False
) -> logging.Logger:
    """
    Setup a logger with console and/or file output
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to output to console
        structured: Use JSON structured logging for file output
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        if structured:
            # Use JSON structured logging
            file_handler.setFormatter(StructuredFormatter())
        else:
            # Use standard text logging
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
    
    return logger


# Convenience function for quick logger setup
def get_logger(name: str, level: int = logging.INFO, structured: bool = False) -> logging.Logger:
    """
    Get a logger with default configuration
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
        structured: Use structured logging
    
    Returns:
        Configured logger
    """
    return setup_logger(
        name=name,
        level=level,
        log_file=f'logs/{name.split(".")[-1]}.log',
        console=True,
        structured=structured
    )


def get_structured_logger(name: str, level: int = logging.INFO) -> StructuredLogger:
    """
    Get a structured logger
    
    Args:
        name: Logger name
        level: Logging level
    
    Returns:
        StructuredLogger instance
    """
    # Setup base logger with structured file output
    setup_logger(
        name=name,
        level=level,
        log_file=f'logs/{name.split(".")[-1]}_structured.json',
        console=True,
        structured=True
    )
    
    return StructuredLogger(name, level)


# Module-level logger for testing
if __name__ == '__main__':
    logger = get_logger(__name__, logging.DEBUG)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
