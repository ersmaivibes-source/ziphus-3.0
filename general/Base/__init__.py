"""
general Base Module - Base Classes and Interfaces Consolidation
============================================================

Consolidates all base classes and interfaces from across the codebase.
"""

from .base_classes import (
    BaseService,
    BaseManager,
    SafeHandlerUtils,
    SecurityUtils,
    MessageUtils,
    ValidationMixin,
    OperationResult,
    AsyncContextManager,
    Singleton,
    ConfigurableComponent
)

__all__ = [
    'BaseService',
    'BaseManager',
    'SafeHandlerUtils',
    'SecurityUtils',
    'MessageUtils',
    'ValidationMixin',
    'OperationResult',
    'AsyncContextManager',
    'Singleton',
    'ConfigurableComponent'
]