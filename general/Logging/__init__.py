"""
general Logging Module - Centralized Logging Consolidation
=======================================================

Consolidates all logging functionality from across the codebase.
"""

from .logger_manager import (
    get_logger,
    log_user_action,
    log_security_event,
    log_error_with_context
)

__all__ = [
    'get_logger',
    'log_user_action',
    'log_security_event',
    'log_error_with_context'
]