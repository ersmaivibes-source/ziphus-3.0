"""
Hydrogram Decorator Utilities
============================

Utilities for working with Hydrogram decorators and handler registration.
"""

from hydrogram import Client, filters
from hydrogram.types import Message, CallbackQuery
from functools import wraps
from typing import Callable, Any, List, Optional
from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)


class DecoratorUtils:
    """Utilities for Hydrogram decorators and handler management."""
    
    @staticmethod
    def error_handler_decorator(func: Callable):
        """
        Add comprehensive error handling to a handler function.
        
        Args:
            func: Handler function to wrap
            
        Returns:
            Wrapped function with error handling
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Extract context from arguments
                context = {'handler': func.__name__}
                
                if args:
                    if hasattr(args[1], 'from_user'):  # Message or CallbackQuery
                        context['user_id'] = args[1].from_user.id
                    if hasattr(args[1], 'chat'):  # Message
                        context['chat_id'] = args[1].chat.id
                    if hasattr(args[1], 'data'):  # CallbackQuery
                        context['callback_data'] = args[1].data
                
                log_error_with_context(e, context)
                
                # Try to send error message to user
                try:
                    if args and len(args) > 1:
                        if hasattr(args[1], 'reply_text'):  # Message
                            await args[1].reply_text("An error occurred. Please try again.")
                        elif hasattr(args[1], 'answer'):  # CallbackQuery
                            await args[1].answer("An error occurred. Please try again.", show_alert=True)
                except Exception:
                    pass  # Silently fail if we can't send error message
        
        return wrapper
    
    @staticmethod
    def rate_limit_decorator(max_calls: int = 30, window_seconds: int = 60):
        """
        Add rate limiting to a handler function.
        
        Args:
            max_calls: Maximum calls allowed
            window_seconds: Time window in seconds
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable):
            # This would integrate with your rate limiting system
            # For now, just returning the original function
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Rate limiting logic would go here
                return await func(*args, **kwargs)
            
            return wrapper
        
        return decorator