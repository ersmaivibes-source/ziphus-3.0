"""
Client Manager for Advanced Operations
====================================

Additional client management utilities and helpers.
"""

from hydrogram import Client
from hydrogram.errors import FloodWait, SessionPasswordNeeded
import asyncio
from typing import Optional, Dict, Any

from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)

class ClientManager:
    """Advanced client management utilities."""
    
    def __init__(self, client: Client):
        """Initialize client manager."""
        self.client = client
        self._retry_config = {
            'max_retries': 3,
            'base_delay': 1,
            'backoff_factor': 2
        }
    
    async def safe_call(self, operation: str, func, *args, **kwargs) -> Optional[Any]:
        """
        Safely execute a client operation with retry logic.
        
        Args:
            operation: Operation name for logging
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Operation result or None if failed
        """
        for attempt in range(self._retry_config['max_retries']):
            try:
                return await func(*args, **kwargs)
                
            except FloodWait as e:
                wait_time = getattr(e, 'value', 1)
                try:
                    wait_seconds = float(wait_time)
                    logger.warning(f"FloodWait in {operation}: waiting {wait_seconds}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_seconds)
                except (ValueError, TypeError):
                    logger.warning(f"FloodWait in {operation}: waiting 1s (attempt {attempt + 1}) - invalid wait time: {wait_time}")
                    await asyncio.sleep(1.0)
                continue
                
            except Exception as e:
                if attempt == self._retry_config['max_retries'] - 1:
                    log_error_with_context(e, {
                        'operation': operation,
                        'attempt': attempt + 1,
                        'final_attempt': True
                    })
                    return None
                
                delay = self._retry_config['base_delay'] * (self._retry_config['backoff_factor'] ** attempt)
                logger.warning(f"Error in {operation}, retrying in {delay}s (attempt {attempt + 1}): {str(e)}")
                await asyncio.sleep(float(delay))
        
        return None
    
    async def safe_send_message(self, chat_id: int, text: str, **kwargs) -> Optional[Any]:
        """Safely send a message with error handling."""
        return await self.safe_call(
            'send_message',
            self.client.send_message,
            chat_id, text, **kwargs
        )
    
    async def safe_edit_message(self, chat_id: int, message_id: int, text: str, **kwargs) -> Optional[Any]:
        """Safely edit a message with error handling."""
        return await self.safe_call(
            'edit_message_text',
            self.client.edit_message_text,
            chat_id, message_id, text, **kwargs
        )
    
    async def safe_delete_message(self, chat_id: int, message_id: int) -> bool:
        """Safely delete a message with error handling."""
        result = await self.safe_call(
            'delete_messages',
            self.client.delete_messages,
            chat_id, message_id
        )
        return result is not None
    
    async def get_client_info(self) -> Dict[str, Any]:
        """Get comprehensive client information."""
        try:
            me = await self.client.get_me()
            return {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name,
                'is_bot': me.is_bot,
                'is_verified': me.is_verified,
                'is_premium': me.is_premium,
                'is_connected': self.client.is_connected,
                'session_name': self.client.name
            }
        except Exception as e:
            log_error_with_context(e, {'operation': 'get_client_info'})
            return {}
    
    def configure_retry(self, max_retries: int = 3, base_delay: int = 1, backoff_factor: int = 2):
        """Configure retry settings."""
        self._retry_config.update({
            'max_retries': max_retries,
            'base_delay': base_delay, 
            'backoff_factor': backoff_factor
        })
        logger.info(f"Updated retry configuration: {self._retry_config}")