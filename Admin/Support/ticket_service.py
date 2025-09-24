"""
Ticket service for managing support tickets.
Handles ticket creation, updates, and notifications.
"""

from typing import List, Optional
from hydrogram import Client

from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger, log_error_with_context
from general.Common.formatters import format_ticket_notification
from Admin.Dashboard.admin_menu_tracker import create_admin_menu_tracker

logger = get_logger(__name__)


class TicketService:
    """Manages ticket operations and notifications."""
    
    def __init__(self, db: DatabaseManager, redis_service=None):
        """Initialize ticket service."""
        self.db = db
        self.redis = redis_service
        self.menu_tracker = None

    async def notify_admins_new_ticket(self, app: Client, ticket_id: int,
                                     user_id: int, subject: str,
                                     category: str, priority: str):
        """Notify all admins about new ticket, replacing their current menu."""
        try:
            # Initialize menu tracker if not already done
            if not self.menu_tracker and self.redis:
                self.menu_tracker = create_admin_menu_tracker(self.redis, app)
            
            # Get all admins with language info in a single query
            admins = await self.db.get_admins()
            
            if not admins:
                logger.warning("No admins found to notify about new ticket")
                return
            
            # Format notification message
            notification = format_ticket_notification(
                ticket_id, user_id, 'en', subject, category, priority
            )
            
            # Send to each admin, replacing their current menu with auto-opening
            successful_notifications = 0
            for admin in admins:
                admin_id = None
                try:
                    admin_id = admin['Chat_Id']
                    lang_code = admin.get('Language_Code', 'en')  # استفاده مستقیم از داده‌های بهینه‌شده
                    
                    if self.menu_tracker:
                        # Use menu tracker to replace current menu with notification + auto menu
                        notification_msg = await self.menu_tracker.send_notification_with_auto_menu(
                            admin_id,
                            notification['text'],
                            reply_markup=notification['keyboard'],
                            auto_menu_delay=5.0  # Auto-open admin menu after 5 seconds
                        )
                        if notification_msg:
                            successful_notifications += 1
                    else:
                        # Fallback to regular send if no menu tracker
                        await app.send_message(
                            admin_id,
                            notification['text'],
                            reply_markup=notification['keyboard']
                        )
                        successful_notifications += 1
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
            
            logger.info(f"Notified {successful_notifications}/{len(admins)} admins about ticket #{ticket_id}")
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'notify_admins_new_ticket',
                'ticket_id': ticket_id
            })
        
    async def notify_admins_ticket_update(self, app: Client, ticket_id: int,
                                        user_id: int, message: str):
        """Notify all admins about ticket update."""
        try:
            # Get all admins with language info in a single query
            admins = await self.db.get_admins()
            
            if not admins:
                logger.warning("No admins found to notify about ticket update")
                return
            
            # Get user info
            user = await self.db.get_user(user_id)
            username = user.get('Username', 'Unknown') if user else 'Unknown'
            
            # Send to each admin
            successful_notifications = 0
            for admin in admins:
                admin_id = None
                try:
                    admin_id = admin['Chat_Id']
                    lang_code = admin.get('Language_Code', 'en')
                    
                    # Format notification message
                    if lang_code == 'fa':
                        notification_text = f"""
🔄 **به‌روزرسانی تیکت**

🎫 **شماره تیکت:** #{ticket_id}
👤 **کاربر:** @{username} ({user_id})
💬 **پیام:** {message[:200]}{'...' if len(message) > 200 else ''}

برای پاسخ دادن کلیک کنید.
"""
                    else:
                        notification_text = f"""
🔄 **Ticket Update**

🎫 **Ticket #:** {ticket_id}
👤 **User:** @{username} ({user_id})
💬 **Message:** {message[:200]}{'...' if len(message) > 200 else ''}

Click to respond.
"""
                    
                    # Create inline keyboard
                    from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("📖 View Ticket", callback_data=f'admin_view_ticket_{ticket_id}')],
                        [InlineKeyboardButton("💬 Reply", callback_data=f'admin_reply_ticket_{ticket_id}')]
                    ])
                    
                    await app.send_message(
                        admin_id,
                        notification_text,
                        reply_markup=keyboard
                    )
                    successful_notifications += 1
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
            
            logger.info(f"Notified {successful_notifications}/{len(admins)} admins about update to ticket #{ticket_id}")
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'notify_admins_ticket_update',
                'ticket_id': ticket_id
            })
    
    async def notify_user_reply(self, app: Client, ticket_id: int,
                              user_id: int, admin_reply: str):
        """Notify user about admin reply to their ticket."""
        try:
            # Get user info
            user = await self.db.get_user(user_id)
            if not user:
                return
            
            lang_code = user.get('Language_Code', 'en')
            
            # Format notification
            if lang_code == 'fa':
                message = f"""
💬 **پاسخ جدید از پشتیبانی**

🎫 **شماره تیکت:** #{ticket_id}
📝 **پیام:** {admin_reply[:100]}...

برای مشاهده کامل تیکت به بخش پشتیبانی مراجعه کنید.
"""
            else:
                message = f"""
💬 **New Support Reply**

🎫 **Ticket #:** {ticket_id}
📝 **Message:** {admin_reply[:100]}...

Visit support section to view full ticket.
"""
            
            await app.send_message(user_id, message)
            logger.info(f"Notified user {user_id} about reply to ticket #{ticket_id}")
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'notify_user_reply',
                'ticket_id': ticket_id
            })
    
    async def auto_close_old_tickets(self, days: int = 7) -> int:
        """Auto-close tickets that haven't been updated in X days."""
        try:
            # This would be implemented with a scheduled task
            # For now, just log the intention
            logger.info(f"Would auto-close tickets older than {days} days")
            return 0
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'auto_close_old_tickets'
            })
            return 0