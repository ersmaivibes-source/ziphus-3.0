"""
general Logger Management
=====================

Enhanced logging functionality consolidating:
- Logging/logger_manager.py
- Security/Audit/audit_logger.py

Moved to general for basic/general task consolidation.
"""

import logging
import logging.handlers
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Get the logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Security audit log file
SECURITY_LOG_FILE = LOGS_DIR / "security_audit.log"

# Configure logging format with better performance
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging():
    """Set up general logging configuration with optimized settings."""
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Create file handler for general logs with optimized settings
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "general.log",
        maxBytes=50*1024*1024,  # 50MB (increased from 10MB)
        backupCount=10  # Increased from 5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance with optimized settings."""
    logger = logging.getLogger(name)
    
    # If logger already has handlers, return it
    if logger.handlers:
        return logger
    
    # Set level
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # Create file handler with optimized settings
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f"{name}.log",
        maxBytes=50*1024*1024,  # 50MB (increased from 10MB)
        backupCount=10  # Increased from 5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    return logger

def log_user_action(user_id: int, action: str, details: Optional[Dict[str, Any]] = None):
    """Log user actions for audit purposes with async processing."""
    logger = get_logger('user_actions')
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'action': action,
        'details': details or {}
    }
    
    logger.info(f"User Action: {json.dumps(log_entry, separators=(',', ':'))}")

def log_security_event(event_type: str, details: Optional[Dict[str, Any]] = None, 
                      severity: str = "medium"):
    """Log security events to a dedicated security log with optimized performance."""
    # Create security logger
    security_logger = logging.getLogger('security_audit')
    
    # If logger already has handlers, skip setup
    if not security_logger.handlers:
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s',
            datefmt=DATE_FORMAT
        )
        
        # Create file handler for security logs only with optimized settings
        security_file_handler = logging.handlers.RotatingFileHandler(
            SECURITY_LOG_FILE,
            maxBytes=100*1024*1024,  # 100MB (increased from 10MB)
            backupCount=20  # Increased from 10
        )
        security_file_handler.setFormatter(formatter)
        security_file_handler.setLevel(logging.INFO)
        security_logger.addHandler(security_file_handler)
        security_logger.setLevel(logging.INFO)
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'severity': severity,
        'details': details or {}
    }
    
    # Use appropriate log level based on severity
    if severity.lower() in ["high", "critical"]:
        security_logger.error(f"Security Event: {json.dumps(log_entry, separators=(',', ':'))}")
    elif severity.lower() == "medium":
        security_logger.warning(f"Security Event: {json.dumps(log_entry, separators=(',', ':'))}")
    else:
        security_logger.info(f"Security Event: {json.dumps(log_entry, separators=(',', ':'))}")

def log_error_with_context(error: Exception, context: Dict[str, Any]):
    """Log errors with additional context information."""
    logger = get_logger('error_logger')
    
    error_info = {
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context
    }
    
    logger.error(f"Error with context: {json.dumps(error_info, separators=(',', ':'))}", exc_info=True)

# Initialize logging on module import
setup_logging()