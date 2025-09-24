"""
Secure Logging Module for Ziphus Bot.
Implements secure logging with data sanitization and security event tracking.
"""

import logging
import logging.handlers
import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class SecurityAwareFormatter(logging.Formatter):
    """Custom formatter that sanitizes sensitive data from logs."""
    
    SENSITIVE_KEYS = {
        'password', 'token', 'secret', 'key', 'api_key', 'private_key',
        'auth', 'authorization', 'session', 'cookie', 'credentials',
        'wallet', 'crypto', 'payment', 'card', 'cvv', 'pin', 'ssn',
        'email', 'phone', 'address', 'ip_address', 'user_agent'
    }
    
    SENSITIVE_PATTERNS = [
        r'\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b',  # Credit card
        r'\\b\\d{3}-\\d{2}-\\d{4}\\b',  # SSN
        r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b',  # Email
        r'\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b',  # IP address
        r'Bearer\\s+[A-Za-z0-9\\-._~+/]+=*',  # Bearer tokens
        r'[Aa]pi[_-]?[Kk]ey[\\s:=]+[A-Za-z0-9\\-._~+/]+=*',  # API keys
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern_regex = [re.compile(pattern) for pattern in self.SENSITIVE_PATTERNS]
    
    def format(self, record):
        # Sanitize the record
        record = self._sanitize_record(record)
        return super().format(record)
    
    def _sanitize_record(self, record):
        """Sanitize sensitive data from log record."""
        # Sanitize message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._sanitize_string(record.msg)
        
        # Sanitize args
        if hasattr(record, 'args') and record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_args.append(self._sanitize_string(arg))
                elif isinstance(arg, dict):
                    sanitized_args.append(self._sanitize_dict(arg))
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        
        # Sanitize extra fields
        for key, value in record.__dict__.items():
            if key.lower() in self.SENSITIVE_KEYS:
                record.__dict__[key] = '[REDACTED]'
            elif isinstance(value, str):
                record.__dict__[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                record.__dict__[key] = self._sanitize_dict(value)
        
        return record
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize sensitive patterns in string."""
        if not text:
            return text
        
        sanitized = text
        
        # Apply regex patterns
        for pattern in self.pattern_regex:
            sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return sanitized
    
    def _sanitize_dict(self, data: dict) -> dict:
        """Sanitize sensitive data in dictionary."""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            key_lower = str(key).lower()
            
            if any(sensitive in key_lower for sensitive in self.SENSITIVE_KEYS):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_dict(item) if isinstance(item, dict) 
                                else self._sanitize_string(item) if isinstance(item, str) 
                                else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized


class SecureJsonFormatter(SecurityAwareFormatter):
    """JSON formatter with security-aware sanitization."""
    
    def format(self, record):
        # First sanitize, then format as JSON
        record = self._sanitize_record(record)
        
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module if hasattr(record, 'module') else record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_obj[key] = value
        
        return json.dumps(log_obj, ensure_ascii=False, default=str)


@dataclass
class SecurityEvent:
    """Represents a security-related event for logging."""
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source: str
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            'event_type': self.event_type,
            'severity': self.severity,
            'source': self.source,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }


class SecureLogger:
    """Enhanced secure logger with threat detection and sanitization."""
    
    def __init__(self, name: str = "ziphus_secure"):
        """Initialize secure logger."""
        self.logger = logging.getLogger(name)
        self.security_events: List[SecurityEvent] = []
        self._setup_secure_logging()
    
    def _setup_secure_logging(self):
        """Setup secure logging configuration."""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler with security-aware formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = SecurityAwareFormatter(
            '[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler with JSON formatting
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "secure_bot.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(SecureJsonFormatter())
        
        # Security events handler
        security_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "security_events.log",
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=20,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(SecureJsonFormatter())
        
        # Error handler
        error_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "secure_errors.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(SecureJsonFormatter())
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(security_handler)
        self.logger.addHandler(error_handler)
        
        # Configure third-party loggers
        logging.getLogger('hydrogram').setLevel(logging.WARNING)
        logging.getLogger('aiomysql').setLevel(logging.WARNING)
        logging.getLogger('redis').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    def log_security_event(self, event_type: str, severity: str, source: str,
                          user_id: Optional[int] = None, ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None, **kwargs):
        """Log a security event."""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=kwargs
        )
        
        # Store event
        self.security_events.append(event)
        
        # Log event
        log_level = {
            'LOW': logging.INFO,
            'MEDIUM': logging.WARNING,
            'HIGH': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }.get(severity, logging.WARNING)
        
        self.logger.log(
            log_level,
            f"SECURITY_EVENT: {event_type}",
            extra=event.to_dict()
        )
    
    def log_user_action(self, user_id: int, action: str, ip_address: str = None, **kwargs):
        """Log user action with security context."""
        self.logger.info(
            f"User action: {action}",
            extra={
                'user_id': user_id,
                'action': action,
                'ip_address': ip_address,
                'action_type': 'USER_ACTION',
                **kwargs
            }
        )
    
    def log_admin_action(self, admin_id: int, action: str, target_id: int = None, 
                        ip_address: str = None, **kwargs):
        """Log admin action with enhanced security logging."""
        self.logger.warning(
            f"Admin action: {action}",
            extra={
                'admin_id': admin_id,
                'action': action,
                'target_id': target_id,
                'ip_address': ip_address,
                'action_type': 'ADMIN_ACTION',
                **kwargs
            }
        )
        
        # Also log as security event
        self.log_security_event(
            event_type='ADMIN_ACTION',
            severity='MEDIUM',
            source='admin_interface',
            user_id=admin_id,
            ip_address=ip_address,
            action=action,
            target_id=target_id,
            **kwargs
        )
    
    def log_authentication_event(self, event_type: str, user_id: int = None,
                                ip_address: str = None, success: bool = None, **kwargs):
        """Log authentication-related events."""
        severity = 'LOW' if success else 'HIGH'
        
        self.log_security_event(
            event_type=f'AUTH_{event_type}',
            severity=severity,
            source='authentication',
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            **kwargs
        )
    
    def log_suspicious_activity(self, activity_type: str, user_id: int = None,
                              ip_address: str = None, **kwargs):
        """Log suspicious activity."""
        self.log_security_event(
            event_type=f'SUSPICIOUS_{activity_type}',
            severity='HIGH',
            source='threat_detection',
            user_id=user_id,
            ip_address=ip_address,
            **kwargs
        )
    
    def log_error_secure(self, error: Exception, context: dict = None, 
                        user_id: int = None, ip_address: str = None):
        """Log error with security-aware context sanitization."""
        # Sanitize context
        if context:
            formatter = SecurityAwareFormatter()
            context = formatter._sanitize_dict(context)
        
        self.logger.error(
            f"Error: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={
                'error_type': type(error).__name__,
                'user_id': user_id,
                'ip_address': ip_address,
                'context': context or {}
            }
        )
    
    def get_security_events(self, hours: int = 24, severity: str = None) -> List[SecurityEvent]:
        """Get security events from the last N hours."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        events = [e for e in self.security_events if e.timestamp >= cutoff]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        return events
    
    def get_threat_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of threats in the last N hours."""
        events = self.get_security_events(hours)
        
        summary = {
            'total_events': len(events),
            'critical_events': len([e for e in events if e.severity == 'CRITICAL']),
            'high_events': len([e for e in events if e.severity == 'HIGH']),
            'medium_events': len([e for e in events if e.severity == 'MEDIUM']),
            'low_events': len([e for e in events if e.severity == 'LOW']),
            'unique_users': len(set(e.user_id for e in events if e.user_id)),
            'unique_ips': len(set(e.ip_address for e in events if e.ip_address)),
            'event_types': {}
        }
        
        # Count event types
        for event in events:
            event_type = event.event_type
            if event_type not in summary['event_types']:
                summary['event_types'][event_type] = 0
            summary['event_types'][event_type] += 1
        
        return summary


# Global secure logger instance
secure_logger = SecureLogger()


def get_secure_logger() -> SecureLogger:
    """Get global secure logger instance."""
    return secure_logger


# Convenience functions for backward compatibility
def log_user_action_secure(user_id: int, action: str, **kwargs):
    """Log user action securely."""
    secure_logger.log_user_action(user_id, action, **kwargs)


def log_admin_action_secure(admin_id: int, action: str, **kwargs):
    """Log admin action securely."""
    secure_logger.log_admin_action(admin_id, action, **kwargs)


def log_error_secure(error: Exception, context: dict = None, **kwargs):
    """Log error securely."""
    secure_logger.log_error_secure(error, context, **kwargs)


def log_security_event(event_type: str, severity: str, **kwargs):
    """Log security event."""
    secure_logger.log_security_event(event_type, severity, 'application', **kwargs)


def log_authentication_event(event_type: str, **kwargs):
    """Log authentication event."""
    secure_logger.log_authentication_event(event_type, **kwargs)


def log_suspicious_activity(activity_type: str, **kwargs):
    """Log suspicious activity."""
    secure_logger.log_suspicious_activity(activity_type, **kwargs)