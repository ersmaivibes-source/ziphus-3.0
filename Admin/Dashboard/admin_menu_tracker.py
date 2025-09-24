"""
Admin menu tracking service for managing admin interface cleanup.
Tracks the last menu message for each admin to enable clean notification replacement.
"""

from typing import Optional
from hydrogram import Client
from hydrogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from general.Logging.logger_manager import get_logger, log_error_with_context

logger = get_logger(__name__)


class AdminMenuTracker:
    """Manages admin menu tracking and cleanup for notifications."""
    
    def __init__(self, redis_service, client: Client):
        """Initialize admin menu tracker."""
        self.redis = redis_service
        self.client = client
    
    async def track_admin_menu(self, admin_id: int, menu_message: Message) -> bool:
        """
        Track the last menu message for an admin.
        
        Args:
            admin_id: Admin's user ID
            menu_message: The menu message to track
            
        Returns:
            bool: Success status
        """
        try:
            key = f"admin_last_menu:{admin_id}"
            await self.redis.set_temp_data(key, menu_message.id, ttl=86400)  # 24 hours
            
            logger.debug(f"Tracked admin menu {menu_message.id} for admin {admin_id}")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'track_admin_menu',
                'admin_id': admin_id,
                'message_id': menu_message.id if menu_message else None
            })
            return False
    
    async def get_last_menu_id(self, admin_id: int) -> Optional[int]:
        """
        Get the last tracked menu message ID for an admin.
        
        Args:
            admin_id: Admin's user ID
            
        Returns:
            Optional[int]: Last menu message ID or None
        """
        try:
            key = f"admin_last_menu:{admin_id}"
            menu_id = await self.redis.get_temp_data(key)
            
            if menu_id:
                return int(menu_id)
            return None
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_last_menu_id',
                'admin_id': admin_id
            })
            return None
    
    async def clear_last_menu(self, admin_id: int) -> bool:
        """
        Clear the tracked menu for an admin.
        
        Args:
            admin_id: Admin's user ID
            
        Returns:
            bool: Success status
        """
        try:
            key = f"admin_last_menu:{admin_id}"
            await self.redis.delete_temp_data(key)
            
            logger.debug(f"Cleared admin menu tracking for admin {admin_id}")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'clear_last_menu',
                'admin_id': admin_id
            })
            return False
    
    async def replace_admin_menu(self, admin_id: int, new_message_text: str, 
                               reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply] = None, parse_mode=None) -> Optional[Message]:
        """
        Replace the admin's current menu with a new message.
        
        This method:
        1. Gets the admin's last menu message ID
        2. Deletes the old menu message
        3. Sends the new message
        4. Tracks the new message as the current menu
        
        Args:
            admin_id: Admin's user ID
            new_message_text: Text for the new message
            reply_markup: Keyboard markup for the new message
            parse_mode: Parse mode for the message
            
        Returns:
            Optional[Message]: The new message that was sent
        """
        try:
            # Get the last menu message ID
            last_menu_id = await self.get_last_menu_id(admin_id)
            
            # Delete the old menu if it exists
            if last_menu_id:
                try:
                    await self.client.delete_messages(admin_id, [last_menu_id])
                    logger.debug(f"Deleted old admin menu {last_menu_id} for admin {admin_id}")
                except Exception as delete_error:
                    logger.warning(f"Could not delete old menu {last_menu_id} for admin {admin_id}: {delete_error}")
            
            # Send the new message
            send_kwargs = {
                'chat_id': admin_id,
                'text': new_message_text,
                'parse_mode': parse_mode
            }
            if reply_markup is not None:
                send_kwargs['reply_markup'] = reply_markup
            
            new_message = await self.client.send_message(**send_kwargs)
            
            # Track the new message
            await self.track_admin_menu(admin_id, new_message)
            
            logger.info(f"Replaced admin menu for admin {admin_id}: old={last_menu_id}, new={new_message.id}")
            return new_message
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'replace_admin_menu',
                'admin_id': admin_id
            })
            
            # Fallback: try to send message without cleanup
            try:
                send_kwargs = {
                    'chat_id': admin_id,
                    'text': new_message_text,
                    'parse_mode': parse_mode
                }
                if reply_markup is not None:
                    send_kwargs['reply_markup'] = reply_markup
                
                new_message = await self.client.send_message(**send_kwargs)
                await self.track_admin_menu(admin_id, new_message)
                return new_message
            except Exception as fallback_error:
                log_error_with_context(fallback_error, {
                    'operation': 'replace_admin_menu_fallback',
                    'admin_id': admin_id
                })
                return None
    
    async def send_notification_replacing_menu(self, admin_id: int, notification_text: str,
                                             reply_markup=None, parse_mode=None) -> Optional[Message]:
        """
        Send a notification that replaces the admin's current menu.
        
        This is a wrapper around replace_admin_menu specifically for notifications.
        
        Args:
            admin_id: Admin's user ID  
            notification_text: Notification text
            reply_markup: Keyboard markup
            parse_mode: Parse mode
            
        Returns:
            Optional[Message]: The notification message that was sent
        """
        return await self.replace_admin_menu(
            admin_id, 
            notification_text, 
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    
    async def send_notification_with_auto_menu(self, admin_id: int, notification_text: str,
                                             reply_markup=None, parse_mode=None,
                                             auto_menu_delay: float = 3.0) -> Optional[Message]:
        """
        Send a notification that replaces the admin's current menu, then auto-opens a new menu after delay.
        
        Args:
            admin_id: Admin's user ID  
            notification_text: Notification text
            reply_markup: Keyboard markup for notification
            parse_mode: Parse mode
            auto_menu_delay: Seconds to wait before opening new menu
            
        Returns:
            Optional[Message]: The notification message that was sent
        """
        try:
            # Send notification replacing current menu
            notification_msg = await self.send_notification_replacing_menu(
                admin_id, notification_text, reply_markup, parse_mode
            )
            
            if notification_msg and auto_menu_delay > 0:
                # Schedule auto menu opening in background
                import asyncio
                asyncio.create_task(self._auto_open_menu_task(admin_id, auto_menu_delay))
            
            return notification_msg
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'send_notification_with_auto_menu',
                'admin_id': admin_id
            })
            return None
    
    async def _auto_open_menu_task(self, admin_id: int, delay_seconds: float):
        """Background task to auto-open menu after notification."""
        try:
            import asyncio
            await asyncio.sleep(delay_seconds)
            
            # Send admin panel menu to admin
            from general.Keyboard.combined_keyboards import keyboards
            from general.Language.Translations import get_text_sync
            
            # Get admin's language
            db = getattr(self.client, 'db', None)
            if db:
                user = await db.get_user(admin_id)
                lang_code = user.get('Language_Code', 'en') if user else 'en'
            else:
                lang_code = 'en'
            
            # Using optimized language system - no manager instance needed
        # Language is handled automatically in new system
            from hydrogram.types import InlineKeyboardMarkup
            menu_text = get_text_sync('admin_panel_title', lang_code or "en") or '🔧 **Admin Panel**'
            menu_keyboard = keyboards.admin_kb.admin_panel(lang_code)
            
            # Replace current notification with admin menu
            menu_msg = await self.replace_admin_menu(
                admin_id,
                menu_text,
                reply_markup=menu_keyboard
            )
            
            if menu_msg:
                logger.debug(f"Auto-opened admin menu for admin {admin_id}")
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'auto_open_menu_task',
                'admin_id': admin_id
            })
    
    async def update_menu_without_cleanup(self, admin_id: int, menu_message: Message) -> bool:
        """
        Update the tracked menu without cleaning up (for regular navigation).
        
        Args:
            admin_id: Admin's user ID
            menu_message: New menu message to track
            
        Returns:
            bool: Success status
        """
        return await self.track_admin_menu(admin_id, menu_message)
    
    async def cleanup_admin_interaction(self, admin_id: int, admin_reply_message: Message, 
                                      final_response_text: str, reply_markup=None, 
                                      cleanup_delay: float = 2.0) -> Optional[Message]:
        """
        Clean up an admin interaction by:
        1. Sending immediate response
        2. Scheduling cleanup of both admin reply and current menu
        3. Tracking the final response as new menu
        
        Args:
            admin_id: Admin's user ID
            admin_reply_message: The admin's reply message to be deleted
            final_response_text: Success/response message to send
            reply_markup: Keyboard for final response
            cleanup_delay: Delay before deleting messages
            
        Returns:
            Optional[Message]: The final response message
        """
        try:
            # Send immediate final response
            send_kwargs = {
                'chat_id': admin_id,
                'text': final_response_text
            }
            if reply_markup is not None:
                send_kwargs['reply_markup'] = reply_markup
            
            final_message = await self.client.send_message(**send_kwargs)
            
            # Track the final message as current menu
            await self.track_admin_menu(admin_id, final_message)
            
            # Schedule cleanup of admin reply + old menu in background
            import asyncio
            asyncio.create_task(self._cleanup_interaction_task(
                admin_id, admin_reply_message, cleanup_delay
            ))
            
            logger.debug(f"Scheduled admin interaction cleanup for admin {admin_id}")
            return final_message
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'cleanup_admin_interaction',
                'admin_id': admin_id
            })
            return None
    
    async def _cleanup_interaction_task(self, admin_id: int, admin_reply_message: Message, 
                                      cleanup_delay: float):
        """Background task to clean up admin interaction messages."""
        try:
            import asyncio
            await asyncio.sleep(cleanup_delay)
            
            # Get the previously tracked menu (before we updated it with final message)
            # We need to delete this from a stored backup or reconstruct the cleanup
            messages_to_delete = []
            
            # Always delete the admin's reply message
            messages_to_delete.append(admin_reply_message.id)
            
            # Delete the messages
            if messages_to_delete:
                try:
                    await self.client.delete_messages(admin_id, messages_to_delete)
                    logger.debug(f"Cleaned up {len(messages_to_delete)} admin interaction messages")
                except Exception as delete_error:
                    logger.warning(f"Could not delete admin interaction messages: {delete_error}")
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'cleanup_interaction_task',
                'admin_id': admin_id
            })


def create_admin_menu_tracker(redis_service, client: Client) -> AdminMenuTracker:
    """Create an admin menu tracker instance."""
    return AdminMenuTracker(redis_service, client)