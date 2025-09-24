"""Conversation cleanup service for maintaining clean UI during multi-step processes.
Tracks and deletes intermediate messages to keep only final results visible.
"""

from typing import List, Optional, Dict, Any
import asyncio
from hydrogram import Client
from hydrogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)

class ConversationCleanup:
    """Handles conversation cleanup for multi-step processes."""
    
    def __init__(self, redis_service, client: Client):
        """Initialize cleanup service."""
        self.redis = redis_service
        self.client = client
    
    async def start_conversation(self, user_id: int, state: str, data: Optional[Dict] = None) -> bool:
        """
        Start a new conversation flow with cleanup tracking.
        
        Args:
            user_id: User's chat ID
            state: Conversation state name
            data: Additional state data
            
        Returns:
            bool: Success status
        """
        try:
            # Initialize cleanup tracking in state data
            if not data:
                data = {}
            
            data['cleanup_message_ids'] = []
            
            # Set user state with cleanup tracking
            success = await self.redis.set_user_state(user_id, state, data)
            
            if success:
                logger.debug(f"Started conversation cleanup tracking for user {user_id}, state {state}")
            
            return success
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'start_conversation',
                'user_id': user_id,
                'state': state
            })
            return False
    
    async def track_bot_message(self, user_id: int, message: Message) -> bool:
        """
        Track a bot message for cleanup.
        
        Args:
            user_id: User's chat ID
            message: Bot message to track
            
        Returns:
            bool: Success status
        """
        try:
            # Get current state
            state_data = await self.redis.get_user_state(user_id)
            if not state_data or 'cleanup_message_ids' not in state_data.get('data', {}):
                return False
            
            # Add message ID to cleanup list
            cleanup_ids = state_data['data']['cleanup_message_ids']
            cleanup_ids.append(message.id)
            
            # Update state
            await self.redis.set_user_state(
                user_id, 
                state_data['state'], 
                state_data['data']
            )
            
            logger.debug(f"Tracked bot message {message.id} for cleanup (user {user_id})")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'track_bot_message',
                'user_id': user_id,
                'message_id': message.id if message else None
            })
            return False
    
    async def track_user_message(self, user_id: int, message: Message) -> bool:
        """
        Track a user message for cleanup.
        
        Args:
            user_id: User's chat ID
            message: User message to track
            
        Returns:
            bool: Success status
        """
        try:
            # Get current state
            state_data = await self.redis.get_user_state(user_id)
            if not state_data or 'cleanup_message_ids' not in state_data.get('data', {}):
                return False
            
            # Add message ID to cleanup list
            cleanup_ids = state_data['data']['cleanup_message_ids']
            cleanup_ids.append(message.id)
            
            # Update state
            await self.redis.set_user_state(
                user_id, 
                state_data['state'], 
                state_data['data']
            )
            
            logger.debug(f"Tracked user message {message.id} for cleanup (user {user_id})")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'track_user_message',
                'user_id': user_id,
                'message_id': message.id if message else None
            })
            return False
    
    async def cleanup_conversation(self, user_id: int, keep_last_message: bool = False, delay_seconds: float = 2.0) -> bool:
        """
        Clean up all tracked messages for a conversation.
        
        Args:
            user_id: User's chat ID
            keep_last_message: Whether to keep the most recent bot message
            delay_seconds: Seconds to wait before deleting messages
            
        Returns:
            bool: Success status
        """
        try:
            # Get current state
            state_data = await self.redis.get_user_state(user_id)
            if not state_data or 'cleanup_message_ids' not in state_data.get('data', {}):
                return True  # No cleanup needed
            
            cleanup_ids = state_data['data']['cleanup_message_ids']
            
            if not cleanup_ids:
                return True  # No messages to clean up
            
            # Optionally keep the last message (usually the final result message)
            messages_to_delete = cleanup_ids[:-1] if keep_last_message else cleanup_ids
            
            if messages_to_delete:
                # Wait for the specified delay before cleanup
                if delay_seconds > 0:
                    logger.debug(f"Waiting {delay_seconds} seconds before cleanup for user {user_id}")
                    await asyncio.sleep(delay_seconds)
                
                # Delete messages in batches to avoid API limits
                batch_size = 100
                deleted_count = 0
                
                for i in range(0, len(messages_to_delete), batch_size):
                    batch = messages_to_delete[i:i + batch_size]
                    
                    try:
                        await self.client.delete_messages(user_id, batch)
                        deleted_count += len(batch)
                        logger.debug(f"Deleted batch of {len(batch)} messages for user {user_id}")
                        
                    except Exception as batch_error:
                        # Log but continue with other batches
                        logger.warning(f"Failed to delete message batch for user {user_id}: {batch_error}")
                        continue
                
                logger.info(f"Conversation cleanup completed for user {user_id}: {deleted_count} messages deleted")
            
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'cleanup_conversation',
                'user_id': user_id
            })
            return False
    
    async def cancel_conversation(self, user_id: int, delay_seconds: float = 2.0) -> bool:
        """
        Cancel a conversation and clean up all messages.
        
        Args:
            user_id: User's chat ID
            delay_seconds: Seconds to wait before deleting messages
            
        Returns:
            bool: Success status
        """
        try:
            # Clean up all messages with delay
            await self.cleanup_conversation(user_id, keep_last_message=False, delay_seconds=delay_seconds)
            
            # Clear user state
            await self.redis.clear_user_state(user_id)
            
            logger.debug(f"Cancelled conversation for user {user_id}")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'cancel_conversation',
                'user_id': user_id
            })
            return False
    
    async def complete_conversation(self, user_id: int, final_message: Optional[Message] = None, delay_seconds: float = 2.0) -> bool:
        """
        Complete a conversation by cleaning up messages and optionally tracking final message.
        
        Args:
            user_id: User's chat ID
            final_message: Final result message to keep (optional)
            delay_seconds: Seconds to wait before deleting messages
            
        Returns:
            bool: Success status
        """
        try:
            # Clean up all tracked messages with delay
            await self.cleanup_conversation(user_id, keep_last_message=False, delay_seconds=delay_seconds)
            
            # Clear user state
            await self.redis.clear_user_state(user_id)
            
            logger.debug(f"Completed conversation for user {user_id}")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'complete_conversation',
                'user_id': user_id
            })
            return False
    
    async def complete_conversation_with_delayed_cleanup(self, user_id: int, delay_seconds: float = 2.0) -> bool:
        """
        Complete a conversation with delayed cleanup (for immediate responses).
        
        This method:
        1. Immediately clears the user state so they can continue
        2. Schedules cleanup of tracked messages after a delay
        
        Args:
            user_id: User's chat ID
            delay_seconds: Seconds to wait before deleting messages
            
        Returns:
            bool: Success status
        """
        try:
            # Clear user state immediately so user can continue
            await self.redis.clear_user_state(user_id)
            
            # Schedule delayed cleanup in background
            asyncio.create_task(self._delayed_cleanup_task(user_id, delay_seconds))
            
            logger.debug(f"Scheduled delayed cleanup for user {user_id}")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'complete_conversation_with_delayed_cleanup',
                'user_id': user_id
            })
            return False
    
    async def _delayed_cleanup_task(self, user_id: int, delay_seconds: float):
        """Background task to handle delayed cleanup."""
        try:
            await asyncio.sleep(delay_seconds)
            await self.cleanup_conversation(user_id, keep_last_message=False, delay_seconds=0)
            logger.debug(f"Completed delayed cleanup for user {user_id}")
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'delayed_cleanup_task',
                'user_id': user_id
            })
    
    async def handle_input_error(self, user_id: int, error_message: Message, new_prompt_text: str, 
                                reply_markup=None, delay_seconds: float = 2.0) -> Message:
        """
        Handle user input error by cleaning up old messages and showing a fresh prompt.
        
        This method:
        1. Tracks the error message
        2. Waits for the specified delay
        3. Deletes the previous prompt and user's invalid input
        4. Sends a new clean prompt for the user to try again
        
        Args:
            user_id: User's chat ID
            error_message: The error message that was just sent
            new_prompt_text: Text for the new clean prompt
            reply_markup: Keyboard markup for the new prompt
            delay_seconds: Seconds to wait before cleanup
            
        Returns:
            Message: The new prompt message
        """
        try:
            # Track the error message
            await self.track_bot_message(user_id, error_message)
            
            # Wait for user to read the error message
            if delay_seconds > 0:
                logger.debug(f"Waiting {delay_seconds} seconds for user to read error message")
                await asyncio.sleep(delay_seconds)
            
            # Get current state and cleanup old messages (but keep error message for now)
            state_data = await self.redis.get_user_state(user_id)
            if state_data and 'cleanup_message_ids' in state_data.get('data', {}):
                cleanup_ids = state_data['data']['cleanup_message_ids'][:-1]  # Exclude error message
                
                if cleanup_ids:
                    # Delete old messages (prompt and invalid user input)
                    try:
                        await self.client.delete_messages(user_id, cleanup_ids)
                        logger.debug(f"Deleted {len(cleanup_ids)} old messages after input error for user {user_id}")
                    except Exception as delete_error:
                        logger.warning(f"Failed to delete old messages after error: {delete_error}")
            
            # Send new clean prompt
            new_prompt = await error_message.reply_text(new_prompt_text, reply_markup=reply_markup)
            
            # Delete the error message now
            try:
                await self.client.delete_messages(user_id, [error_message.id])
            except Exception as delete_error:
                logger.warning(f"Failed to delete error message: {delete_error}")
            
            # Reset cleanup tracking with just the new prompt
            if state_data:
                current_state = state_data['state']
                other_data = {k: v for k, v in state_data['data'].items() if k != 'cleanup_message_ids'}
                other_data['cleanup_message_ids'] = [new_prompt.id]
                await self.redis.set_user_state(user_id, current_state, other_data)
            
            logger.debug(f"Handled input error for user {user_id}, sent clean new prompt")
            return new_prompt
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'handle_input_error',
                'user_id': user_id
            })
            return error_message
    
    async def restart_conversation_step(self, user_id: int, state: str, prompt_text: str, 
                                       reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply] = None, 
                                       additional_data: Optional[Dict] = None) -> Optional[Message]:
        """
        Restart a conversation step with a clean interface after an error.
        
        Args:
            user_id: User's chat ID
            state: New conversation state
            prompt_text: Text for the clean prompt
            reply_markup: Keyboard markup
            additional_data: Additional state data
            
        Returns:
            Message: The new prompt message
        """
        try:
            # Clear current state and cleanup
            await self.cleanup_conversation(user_id, keep_last_message=False, delay_seconds=0)
            
            # Start fresh conversation step
            if not additional_data:
                additional_data = {}
            additional_data['cleanup_message_ids'] = []
            
            await self.redis.set_user_state(user_id, state, additional_data)
            
            # Send clean prompt
            if reply_markup:
                new_prompt = await self.client.send_message(user_id, prompt_text, reply_markup=reply_markup)
            else:
                new_prompt = await self.client.send_message(user_id, prompt_text)
            
            # Track the new prompt
            await self.track_bot_message(user_id, new_prompt)
            
            return new_prompt
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'restart_conversation_step',
                'user_id': user_id
            })
            return None


def create_cleanup_service(redis_service, client: Client) -> ConversationCleanup:
    """Create a conversation cleanup service instance."""
    return ConversationCleanup(redis_service, client)