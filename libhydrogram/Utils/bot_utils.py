"""
Bot Utility Functions
====================

General utilities for bot operations.
"""

from hydrogram import Client
from hydrogram.types import Message, CallbackQuery, User
from hydrogram.errors import FloodWait, MessageNotModified
from typing import Optional, Dict, Any, List
import asyncio
from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)


class BotUtils:
    """Utility functions for bot operations."""
    
    @staticmethod
    async def safe_send_message(client: Client, chat_id: int, text: str, 
                               max_retries: int = 3, **kwargs) -> Optional[Message]:
        """
        Safely send a message with retry logic.
        
        Args:
            client: Hydrogram client
            chat_id: Target chat ID
            text: Message text
            max_retries: Maximum retry attempts
            **kwargs: Additional parameters for send_message
            
        Returns:
            Message object or None if failed
        """
        for attempt in range(max_retries):
            try:
                return await client.send_message(chat_id, text, **kwargs)
            except FloodWait as e:
                if attempt < max_retries - 1:
                    wait_time = float(getattr(e, 'value', 1))
                    logger.warning(f"FloodWait: sleeping for {wait_time} seconds (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"FloodWait exceeded max retries for chat {chat_id}")
                    return None
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Send message error (attempt {attempt + 1}): {e}. Retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    log_error_with_context(e, {
                        'operation': 'safe_send_message',
                        'chat_id': chat_id,
                        'attempt': attempt + 1
                    })
                    return None
        return None
    
    @staticmethod
    async def safe_edit_message(client: Client, chat_id: int, message_id: int, 
                               text: str, max_retries: int = 3, **kwargs) -> bool:
        """
        Safely edit a message with retry logic.
        
        Args:
            client: Hydrogram client
            chat_id: Target chat ID
            message_id: Message ID to edit
            text: New message text
            max_retries: Maximum retry attempts
            **kwargs: Additional parameters for edit_message_text
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                await client.edit_message_text(chat_id, message_id, text, **kwargs)
                return True
            except MessageNotModified:
                logger.debug("Message not modified - content is the same")
                return True
            except FloodWait as e:
                if attempt < max_retries - 1:
                    wait_time = float(getattr(e, 'value', 1))
                    logger.warning(f"FloodWait: sleeping for {wait_time} seconds (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"FloodWait exceeded max retries for message edit")
                    return False
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    logger.warning(f"Edit message error (attempt {attempt + 1}): {e}. Retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    log_error_with_context(e, {
                        'operation': 'safe_edit_message',
                        'chat_id': chat_id,
                        'message_id': message_id,
                        'attempt': attempt + 1
                    })
                    return False
        return False
    
    @staticmethod
    async def safe_answer_callback(callback_query: CallbackQuery, text: Optional[str] = None, 
                                  show_alert: bool = False, max_retries: int = 3) -> bool:
        """
        Safely answer a callback query with retry logic.
        
        Args:
            callback_query: Callback query to answer
            text: Optional text to show
            show_alert: Whether to show as alert
            max_retries: Maximum retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                await callback_query.answer(text, show_alert=show_alert)
                return True
            except FloodWait as e:
                if attempt < max_retries - 1:
                    wait_time = float(getattr(e, 'value', 1))
                    logger.warning(f"FloodWait on callback answer: sleeping for {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("FloodWait exceeded max retries for callback answer")
                    return False
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    logger.warning(f"Callback answer error (attempt {attempt + 1}): {e}. Retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    log_error_with_context(e, {
                        'operation': 'safe_answer_callback',
                        'callback_id': callback_query.id,
                        'attempt': attempt + 1
                    })
                    return False
        return False
    
    @staticmethod
    def extract_user_info(user: User) -> Dict[str, Any]:
        """
        Extract comprehensive user information.
        
        Args:
            user: Hydrogram User object
            
        Returns:
            Dictionary with user information
        """
        return {
            'id': user.id,
            'is_self': user.is_self,
            'is_contact': user.is_contact,
            'is_mutual_contact': user.is_mutual_contact,
            'is_deleted': user.is_deleted,
            'is_bot': user.is_bot,
            'is_verified': user.is_verified,
            'is_restricted': user.is_restricted,
            'is_scam': user.is_scam,
            'is_fake': user.is_fake,
            'is_premium': user.is_premium,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'language_code': user.language_code,
            'dc_id': user.dc_id,
            'phone_number': user.phone_number,
            'status': str(user.status) if hasattr(user, 'status') else None
        }
    
    @staticmethod
    def format_user_mention(user: User, use_id: bool = False) -> str:
        """
        Format a user mention.
        
        Args:
            user: Hydrogram User object
            use_id: Whether to use ID-based mention
            
        Returns:
            Formatted mention string
        """
        if use_id:
            display_name = user.first_name or f"User{user.id}"
            return f'<a href="tg://user?id={user.id}">{display_name}</a>'
        elif user.username:
            return f"@{user.username}"
        else:
            display_name = user.first_name or f"User{user.id}"
            return f'<a href="tg://user?id={user.id}">{display_name}</a>'
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 4096, suffix: str = "...") -> str:
        """
        Truncate text to fit Telegram message limits.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add when truncated
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        truncated_length = max_length - len(suffix)
        return text[:truncated_length] + suffix
    
    @staticmethod
    async def get_chat_member_count(client: Client, chat_id: int) -> Optional[int]:
        """
        Get the number of members in a chat.
        
        Args:
            client: Hydrogram client
            chat_id: Chat ID
            
        Returns:
            Member count or None if failed
        """
        try:
            chat = await client.get_chat(chat_id)
            return chat.members_count
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_chat_member_count',
                'chat_id': chat_id
            })
            return None
    
    @staticmethod
    def split_message(text: str, max_length: int = 4096) -> List[str]:
        """
        Split a long message into multiple parts.
        
        Args:
            text: Text to split
            max_length: Maximum length per part
            
        Returns:
            List of message parts
        """
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current_part = ""
        
        # Split by lines first to preserve formatting
        lines = text.split('\n')
        
        for line in lines:
            # If a single line is too long, split it by words
            if len(line) > max_length:
                words = line.split(' ')
                for word in words:
                    if len(current_part) + len(word) + 1 <= max_length:
                        current_part += (" " if current_part else "") + word
                    else:
                        if current_part:
                            parts.append(current_part)
                            current_part = word
                        else:
                            # Single word longer than max_length
                            parts.append(word[:max_length])
                            current_part = word[max_length:]
            else:
                if len(current_part) + len(line) + 1 <= max_length:
                    current_part += ("\n" if current_part else "") + line
                else:
                    if current_part:
                        parts.append(current_part)
                    current_part = line
        
        if current_part:
            parts.append(current_part)
        
        return parts