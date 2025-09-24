"""
general Error Handling Module
==========================

Consolidated error handling functionality from:
- common/base.py (ErrorHandler)
- Errors/general/error_manager.py
- libhydrogram/Utils/error_utils.py

Moved to general for basic/general task consolidation.
"""

import asyncio
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, field

from general.Logging.logger_manager import get_logger

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """Error information structure."""
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    user_id: Optional[int] = None
    retryable: bool = False
    ignorable: bool = False


class CoreErrorManager:
    """Centralized error management for general functionality."""
    
    def __init__(self):
        """Initialize error manager."""
        self.error_history: List[ErrorInfo] = []
        self.error_handlers: Dict[str, Callable] = {}
        self.max_history_size = 1000
        
        # Common error mappings for user-friendly messages
        self.error_mappings = {
            'FLOOD_WAIT': 'Rate limit exceeded. Please try again later.',
            'MESSAGE_NOT_MODIFIED': 'Message content is the same.',
            'CHAT_ADMIN_REQUIRED': 'Admin privileges required for this action.',
            'USER_NOT_PARTICIPANT': 'User is not a member of this chat.',
            'BUTTON_URL_INVALID': 'Invalid button URL provided.',
            'MESSAGE_ID_INVALID': 'Message not found or already deleted.',
            'PEER_ID_INVALID': 'Invalid user or chat ID.',
            'CHANNEL_PRIVATE': 'This channel is private or doesn\'t exist.',
            'USER_DEACTIVATED_BAN': 'User account has been deactivated.',
            'USER_BLOCKED': 'User has blocked the bot.',
            'INPUT_USER_DEACTIVATED': 'User account is deactivated.',
            'ConnectionError': 'Connection issue. Please try again.',
            'TimeoutError': 'Operation timed out. Please try again.',
            'ValidationError': 'Invalid input provided.',
            'AuthenticationError': 'Authentication failed.',
            'PermissionError': 'Permission denied.'
        }
    
    def register_error_handler(self, error_type: str, handler: Callable):
        """Register a custom error handler for a specific error type."""
        self.error_handlers[error_type] = handler
        logger.info(f"Registered error handler for {error_type}")
    
    def _create_error_info(self, error: Exception, severity: ErrorSeverity, 
                          context: Dict[str, Any] = None) -> ErrorInfo:
        """Create error information structure."""
        return ErrorInfo(
            error_type=type(error).__name__,
            message=str(error),
            severity=severity,
            context=context or {},
            stack_trace=traceback.format_exc(),
            retryable=self._is_retryable_error(error),
            ignorable=self._is_ignorable_error(error)
        )
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        retryable_errors = [
            'ConnectionError',
            'TimeoutError',
            'FloodWait',
            'RPCError'
        ]
        return type(error).__name__ in retryable_errors
    
    def _is_ignorable_error(self, error: Exception) -> bool:
        """Determine if an error can be safely ignored."""
        ignorable_errors = [
            'MessageNotModified',
            'UserBlocked',
            'UserDeactivated'
        ]
        return type(error).__name__ in ignorable_errors
    
    def _add_to_history(self, error_info: ErrorInfo):
        """Add error to history with size limit."""
        self.error_history.append(error_info)
        
        # Maintain history size limit
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    async def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> ErrorInfo:
        """Handle a general error."""
        try:
            error_info = self._create_error_info(error, severity, context)
            
            # Log the error
            log_level = {
                ErrorSeverity.LOW: logger.debug,
                ErrorSeverity.MEDIUM: logger.error,
                ErrorSeverity.HIGH: logger.error,
                ErrorSeverity.CRITICAL: logger.critical
            }.get(severity, logger.error)
            
            log_level(f"Error handled: {error_info.message}")
            
            # Store in history
            self._add_to_history(error_info)
            
            # Try to find and execute specific handler
            error_type = type(error).__name__
            if error_type in self.error_handlers:
                try:
                    await self.error_handlers[error_type](error, context)
                except Exception as handler_error:
                    logger.error(f"Error handler failed: {handler_error}")
            
            return error_info
            
        except Exception as e:
            logger.critical(f"Error manager failed to handle error: {e}")
            return ErrorInfo(
                error_type="ErrorManagerFailure",
                message=f"Failed to handle error: {str(error)}",
                severity=ErrorSeverity.CRITICAL
            )
    
    async def handle_critical_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """Handle a critical error that may require application shutdown."""
        error_info = await self.handle_error(error, context, ErrorSeverity.CRITICAL)
        
        # Execute critical error handler if registered
        if "critical" in self.error_handlers:
            try:
                await self.error_handlers["critical"](error, context)
            except Exception as handler_error:
                logger.critical(f"Critical error handler failed: {handler_error}")
        
        return error_info
    
    def get_user_friendly_error(self, error: Exception) -> str:
        """Convert technical error to user-friendly message."""
        error_type = type(error).__name__
        
        # Try to get mapped error message
        if error_type in self.error_mappings:
            return self.error_mappings[error_type]
        
        # For specific error types with dynamic content
        if hasattr(error, 'ID') and error.ID in self.error_mappings:
            return self.error_mappings[error.ID]
        
        # Default fallback
        return "An unexpected error occurred. Please try again."
    
    def extract_error_info(self, error: Exception) -> Dict[str, Any]:
        """Extract comprehensive error information."""
        return {
            'type': type(error).__name__,
            'message': str(error),
            'retryable': self._is_retryable_error(error),
            'ignorable': self._is_ignorable_error(error),
            'user_message': self.get_user_friendly_error(error)
        }
    
    async def safe_operation_wrapper(self, operation: Callable, operation_name: str,
                                   error_message: str = None, *args, **kwargs) -> Optional[Any]:
        """
        Wrap an operation with comprehensive error handling.
        
        Args:
            operation: Async function to execute
            operation_name: Name for logging
            error_message: Custom error message
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Operation result or None if failed
        """
        try:
            return await operation(*args, **kwargs)
        except Exception as error:
            error_info = self.extract_error_info(error)
            
            # Use custom error message if provided
            if error_message:
                error_info['user_message'] = error_message
            
            context = {
                'operation': operation_name,
                'error_type': error_info['type'],
                'retryable': error_info['retryable'],
                'ignorable': error_info['ignorable']
            }
            
            if not error_info['ignorable']:
                await self.handle_error(error, context)
            else:
                logger.debug(f"Ignorable error in {operation_name}: {error_info['message']}")
            
            return None
    
    async def handle_error_with_retry(self, operation: Callable, max_retries: int = 3,
                                    base_delay: float = 1.0, backoff_factor: float = 2.0,
                                    *args, **kwargs) -> Optional[Any]:
        """
        Execute an operation with automatic retry for retryable errors.
        
        Args:
            operation: Async function to execute
            max_retries: Maximum number of retries
            base_delay: Base delay between retries
            backoff_factor: Backoff multiplier
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Operation result or None if failed
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception as error:
                last_error = error
                error_info = self.extract_error_info(error)
                
                # If error is ignorable, return None without logging as error
                if error_info['ignorable']:
                    logger.debug(f"Ignorable error in operation: {error_info['message']}")
                    return None
                
                # If not retryable or last attempt, break
                if not error_info['retryable'] or attempt >= max_retries:
                    break
                
                # Calculate delay for next attempt
                delay = base_delay * (backoff_factor ** attempt)
                
                logger.warning(
                    f"Retryable error in operation (attempt {attempt + 1}/{max_retries + 1}): "
                    f"{error_info['message']}. Retrying in {delay}s"
                )
                await asyncio.sleep(delay)
        
        # Log final error
        if last_error:
            await self.handle_error(last_error, {
                'operation': operation.__name__ if hasattr(operation, '__name__') else str(operation),
                'max_retries': max_retries,
                'final_attempt': True
            })
        
        return None
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for the last N hours."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff]
        
        stats = {
            'total_errors': len(recent_errors),
            'critical_errors': len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]),
            'high_errors': len([e for e in recent_errors if e.severity == ErrorSeverity.HIGH]),
            'medium_errors': len([e for e in recent_errors if e.severity == ErrorSeverity.MEDIUM]),
            'low_errors': len([e for e in recent_errors if e.severity == ErrorSeverity.LOW]),
            'error_types': {},
            'retryable_errors': len([e for e in recent_errors if e.retryable]),
            'ignorable_errors': len([e for e in recent_errors if e.ignorable])
        }
        
        # Count error types
        for error in recent_errors:
            error_type = error.error_type
            if error_type not in stats['error_types']:
                stats['error_types'][error_type] = 0
            stats['error_types'][error_type] += 1
        
        return stats


# Global error manager instance
_error_manager = None

def get_error_manager() -> CoreErrorManager:
    """Get the global general error manager."""
    global _error_manager
    if _error_manager is None:
        _error_manager = CoreErrorManager()
    return _error_manager

# Convenience functions for backward compatibility
async def handle_error(error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
    """Handle a general error."""
    return await get_error_manager().handle_error(error, context)

async def handle_critical_error(error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
    """Handle a critical error."""
    return await get_error_manager().handle_critical_error(error, context)

def log_error(error: Exception, context: Dict):
    """Log error with context (sync version for compatibility)."""
    logger.error(f"Error: {type(error).__name__}: {str(error)}", extra={'context': context})