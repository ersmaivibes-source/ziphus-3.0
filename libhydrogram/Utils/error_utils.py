"""
Error Handling Utilities for libhydrogram
===================================

Specialized error handling for Hydrogram operations.
"""

from hydrogram.errors import (
    FloodWait, MessageNotModified, ChatAdminRequired, UserNotParticipant,
    ButtonUrlInvalid, MessageIdInvalid, PeerIdInvalid, ChannelPrivate,
    UserDeactivated, UserBlocked, RPCError
)
from typing import Dict, Any, Optional, Callable
import asyncio
from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)


class ErrorUtils:
    """Utilities for handling Hydrogram-specific errors."""
    
    ERROR_MAPPINGS = {
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
        'INPUT_USER_DEACTIVATED': 'User account is deactivated.'
    }
    
    @staticmethod
    def get_user_friendly_error(error: Exception) -> str:
        """
        Convert technical error to user-friendly message.
        
        Args:
            error: Exception object
            
        Returns:
            User-friendly error message
        """
        if isinstance(error, RPCError):
            error_id = error.ID
            if error_id in ErrorUtils.ERROR_MAPPINGS:
                return ErrorUtils.ERROR_MAPPINGS[error_id]
        
        error_type = type(error).__name__
        if error_type in ErrorUtils.ERROR_MAPPINGS:
            return ErrorUtils.ERROR_MAPPINGS[error_type]
        
        return "An unexpected error occurred. Please try again."
    
    @staticmethod
    def is_retryable_error(error: Exception) -> bool:
        """
        Check if an error is retryable.
        
        Args:
            error: Exception object
            
        Returns:
            True if error is retryable
        """
        retryable_errors = [FloodWait]
        
        if isinstance(error, RPCError):
            retryable_rpc_errors = [
                'INTERNAL_SERVER_ERROR',
                'NETWORK_ERROR',
                'TIMEOUT',
                'CONNECTION_DEVICE_ERROR'
            ]
            return error.ID in retryable_rpc_errors
        
        return any(isinstance(error, err_type) for err_type in retryable_errors)
    
    @staticmethod
    def is_ignorable_error(error: Exception) -> bool:
        """
        Check if an error can be safely ignored.
        
        Args:
            error: Exception object
            
        Returns:
            True if error can be ignored
        """
        ignorable_errors = [MessageNotModified]
        
        if isinstance(error, RPCError):
            ignorable_rpc_errors = [
                'MESSAGE_NOT_MODIFIED',
                'QUERY_TOO_OLD',
                'MESSAGE_DELETE_FORBIDDEN'
            ]
            return error.ID in ignorable_rpc_errors
        
        return any(isinstance(error, err_type) for err_type in ignorable_errors)
    
    @staticmethod
    def extract_error_info(error: Exception) -> Dict[str, Any]:
        """
        Extract comprehensive error information.
        
        Args:
            error: Exception object
            
        Returns:
            Dictionary with error details
        """
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'retryable': ErrorUtils.is_retryable_error(error),
            'ignorable': ErrorUtils.is_ignorable_error(error),
            'user_message': ErrorUtils.get_user_friendly_error(error)
        }
        
        if isinstance(error, FloodWait):
            error_info['wait_time'] = error.value
        
        if isinstance(error, RPCError):
            error_info['rpc_id'] = error.ID
            error_info['rpc_code'] = error.CODE
        
        return error_info
    
    @staticmethod
    async def handle_error_with_retry(operation: Callable, max_retries: int = 3,
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
                error_info = ErrorUtils.extract_error_info(error)
                
                # If error is ignorable, return None without logging as error
                if error_info['ignorable']:
                    logger.debug(f"Ignorable error in operation: {error_info['message']}")
                    return None
                
                # If not retryable or last attempt, break
                if not error_info['retryable'] or attempt >= max_retries:
                    break
                
                # Calculate delay for next attempt
                if isinstance(error, FloodWait):
                    delay = float(getattr(error, 'value', 1))
                else:
                    delay = base_delay * (backoff_factor ** attempt)
                
                logger.warning(
                    f"Retryable error in operation (attempt {attempt + 1}/{max_retries + 1}): "
                    f"{error_info['message']}. Retrying in {delay}s"
                )
                await asyncio.sleep(delay)
        
        # Log final error
        if last_error:
            log_error_with_context(last_error, {
                'operation': operation.__name__ if hasattr(operation, '__name__') else 'unknown',
                'max_retries': max_retries,
                'final_attempt': True
            })
        
        return None
    
    @staticmethod
    def create_error_context(operation: str, **additional_context) -> Dict[str, Any]:
        """
        Create standardized error context for logging.
        
        Args:
            operation: Name of the operation
            **additional_context: Additional context data
            
        Returns:
            Standardized error context
        """
        context = {
            'operation': operation,
            'timestamp': None,  # Will be added by logger
            'module': 'libhydrogram'
        }
        context.update(additional_context)
        return context
    
    @staticmethod
    async def safe_operation_wrapper(operation: Callable, operation_name: str,
                                   error_message: Optional[str] = None, *args, **kwargs) -> Optional[Any]:
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
            error_info = ErrorUtils.extract_error_info(error)
            
            # Use custom error message if provided
            if error_message:
                error_info['user_message'] = error_message
            
            context = ErrorUtils.create_error_context(
                operation_name,
                error_type=error_info['type'],
                retryable=error_info['retryable'],
                ignorable=error_info['ignorable']
            )
            
            if not error_info['ignorable']:
                log_error_with_context(error, context)
            else:
                logger.debug(f"Ignorable error in {operation_name}: {error_info['message']}")
            
            return None