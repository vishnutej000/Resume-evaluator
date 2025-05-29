"""
Logging utilities for the resume evaluator system.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and structured output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors."""
        if hasattr(record, 'color') and record.color:
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        return super().format(record)


class StructuredLogger:
    """Structured logger for the resume evaluator system."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logger with file and console handlers."""
        logger = logging.getLogger(self.name)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Set log level
        log_level = getattr(logging, self.config.get('level', 'INFO').upper())
        logger.setLevel(log_level)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_formatter = CustomFormatter(
            fmt=self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            datefmt=self.config.get('date_format', '%Y-%m-%d %H:%M:%S')
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler for main logs
        main_log_file = self.config.get('main_log', 'logs/app.log')
        file_handler = self._create_rotating_handler(main_log_file)
        file_formatter = logging.Formatter(
            fmt=self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            datefmt=self.config.get('date_format', '%Y-%m-%d %H:%M:%S')
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error handler for errors only
        error_log_file = self.config.get('error_log', 'logs/errors.log')
        error_handler = self._create_rotating_handler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def _create_rotating_handler(self, filename: str) -> logging.handlers.RotatingFileHandler:
        """Create a rotating file handler."""
        max_bytes = self.config.get('max_file_size_mb', 10) * 1024 * 1024
        backup_count = self.config.get('backup_count', 5)
        
        return logging.handlers.RotatingFileHandler(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log_with_extra(logging.INFO, message, extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log error message."""
        self._log_with_extra(logging.ERROR, message, extra, exc_info=exc_info)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log_with_extra(logging.WARNING, message, extra)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log_with_extra(logging.DEBUG, message, extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self._log_with_extra(logging.CRITICAL, message, extra)
    
    def _log_with_extra(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log message with extra context."""
        if extra:
            message = f"{message} | Context: {json.dumps(extra, default=str)}"
        
        self.logger.log(level, message, exc_info=exc_info)
    
    def log_performance(self, operation: str, duration: float, extra: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        perf_data = {
            'operation': operation,
            'duration_seconds': round(duration, 3),
            'timestamp': datetime.now().isoformat()
        }
        
        if extra:
            perf_data.update(extra)
        
        # Write to performance log file
        perf_log_file = self.config.get('performance_log', 'logs/performance.log')
        try:
            with open(perf_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(perf_data)}\n")
        except Exception as e:
            self.error(f"Failed to write performance log: {e}")
        
        self.info(f"Performance: {operation} took {duration:.3f}s", extra)
    
    def log_audit(self, action: str, details: Dict[str, Any]):
        """Log audit trail."""
        audit_data = {
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        # Write to audit log file
        audit_log_file = self.config.get('audit_log', 'logs/audit.log')
        try:
            with open(audit_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(audit_data)}\n")
        except Exception as e:
            self.error(f"Failed to write audit log: {e}")
        
        self.info(f"Audit: {action}", audit_data['details'])


def get_logger(name: str, config: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """Get a structured logger instance."""
    if config is None:
        config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S',
            'main_log': 'logs/app.log',
            'error_log': 'logs/errors.log',
            'performance_log': 'logs/performance.log',
            'audit_log': 'logs/audit.log',
            'max_file_size_mb': 10,
            'backup_count': 5
        }
    
    return StructuredLogger(name, config)


# Global logger instances
main_logger = None
agent_logger = None
performance_logger = None


def init_loggers(config: Optional[Dict[str, Any]] = None):
    """Initialize global logger instances."""
    global main_logger, agent_logger, performance_logger
    
    main_logger = get_logger('main', config)
    agent_logger = get_logger('agents', config)
    performance_logger = get_logger('performance', config)