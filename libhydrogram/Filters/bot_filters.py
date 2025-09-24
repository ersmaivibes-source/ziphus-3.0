"""
Bot Filters Module
=================

Consolidated bot filters for message handling.
"""

from hydrogram import filters
from hydrogram.types import Message, CallbackQuery
from functools import wraps
from typing import Callable, Any

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config

# Get the general configuration
core_config = get_core_config()

# Admin filter using general configuration
def admin_filter(_, __, message: Message) -> bool:
    """Check if user is admin."""
    # Get admin IDs from general configuration (this would need to be added to general config)
    admin_ids = []  # This should be configured in the general configuration
    return message.from_user.id in admin_ids if message.from_user else False

# Create filters
admin_cmd = filters.create(admin_filter)
private_chat = filters.private
group_chat = filters.group

# Rate limiting filter
def rate_limit(max_per_minute: int = 30):
    """Rate limiting decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(client: Any, update: Any, *args, **kwargs):
            # Rate limiting implementation would go here
            # Using general configuration for rate limits
            return await func(client, update, *args, **kwargs)
        return wrapper
    return decorator
