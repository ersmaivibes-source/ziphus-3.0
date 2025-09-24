"""
general Error Module - Error Handling Consolidation
=================================================

Consolidates all error handling functionality from across the codebase.
"""

from .error_manager import (
    CoreErrorManager,
    ErrorSeverity,
    ErrorInfo,
    get_error_manager,
    handle_error,
    handle_critical_error,
    log_error
)

__all__ = [
    'CoreErrorManager',
    'ErrorSeverity', 
    'ErrorInfo',
    'get_error_manager',
    'handle_error',
    'handle_critical_error',
    'log_error'
]