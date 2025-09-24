"""
general Decorators Module - Decorator Consolidation
================================================

Consolidates all decorator functionality from across the codebase.
"""

from .core_decorators import (
    CoreDecorators,
    check_user_banned,
    inject_user_and_lang,
    admin_required,
    error_handler,
    security_audit_log,
    input_validation,
    require_permissions,
    rate_limit,
    secure_endpoint,
    retry,
    timeout
)

__all__ = [
    'CoreDecorators',
    'check_user_banned',
    'inject_user_and_lang',
    'admin_required',
    'error_handler',
    'security_audit_log',
    'input_validation',
    'require_permissions',
    'rate_limit',
    'secure_endpoint',
    'retry',
    'timeout'
]