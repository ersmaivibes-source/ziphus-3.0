"""
libhydrogram - Hydrogram Library Consolidation Module
==============================================

This module consolidates all Hydrogram library-related code from across the entire
Telegram bot into a single, organized structure. Following the ULTIMATE_ARCHITECTURE_DESIGN
pattern used for Users, Admin, and Security consolidation.

Components:
-----------
- Client/: Hydrogram Client initialization and configuration
- Handlers/: Handler registration and management
- Filters/: Hydrogram filters and decorators consolidation  
- Lifecycle/: Bot start, stop, and session management
- Configuration/: Telegram API and bot-specific configuration
- Utils/: Hydrogram-specific utilities and helpers

Usage:
------
from libhydrogram.Client.bot_client import BotClient
from libhydrogram.Handlers.handler_registry import HandlerRegistry
from libhydrogram.Lifecycle.bot_lifecycle import BotLifecycle

Version: 9.9.9.0
Framework: Hydrogram (Pyrogram fork)
"""

__version__ = "9.9.9.0"
__author__ = "Ziphus Bot Team"
__framework__ = "Hydrogram"

# general bot components exports
from .Client import BotClient
from .Handlers import HandlerRegistry  
from .Lifecycle import BotLifecycle
# Configuration has been moved to general for consolidation
# from .Configuration import BotConfiguration

__all__ = [
    'BotClient',
    'HandlerRegistry',
    'BotLifecycle'
    # 'BotConfiguration' - moved to general
]