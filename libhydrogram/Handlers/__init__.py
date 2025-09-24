"""
libhydrogram Handlers Module
======================

Consolidates all Hydrogram handler registration and management.
"""

from .handler_registry import HandlerRegistry
from .registration_manager import RegistrationManager

__all__ = ['HandlerRegistry', 'RegistrationManager']