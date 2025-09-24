"""
Admin Menu Keyboards
Consolidated admin menu and navigation keyboard components
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class AdminMenuKeyboards:
    """Admin menu and navigation keyboard components."""
    
    def __init__(self):
        pass
    
    def admin_main_menu_button(self, lang_code: str) -> InlineKeyboardButton:
        """Create admin panel button for main menu."""
        return InlineKeyboardButton(get_text_sync('admin_panel', lang_code), callback_data="admin_panel")
    
    def admin_message_type_selection(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create message type selection keyboard for admin broadcasts."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(get_text_sync('text_message', lang_code), callback_data='msg_type_text'),
                InlineKeyboardButton(get_text_sync('photo_message', lang_code), callback_data='msg_type_photo')
            ],
            [
                InlineKeyboardButton(get_text_sync('video_message', lang_code), callback_data='msg_type_video'),
                InlineKeyboardButton(get_text_sync('document_message', lang_code), callback_data='msg_type_document')
            ],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="admin_user_management")]
        ])
    
    def admin_broadcast_confirmation(self, user_count: int, lang_code: str) -> InlineKeyboardMarkup:
        """Create broadcast confirmation keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                get_text_sync('confirm_broadcast', lang_code).format(count=user_count),
                callback_data=f'confirm_broadcast_{user_count}'
            )],
            [InlineKeyboardButton("❌ لغو", callback_data="admin_user_management")]
        ])
    
    def admin_navigation_keyboard(self, current_section: str, lang_code: str) -> InlineKeyboardMarkup:
        """Create admin navigation keyboard based on current section."""
        buttons = []
        
        if current_section != 'analytics':
            buttons.append([InlineKeyboardButton("📊 Analytics", callback_data='admin_analytics')])
        
        if current_section != 'user_management':
            buttons.append([InlineKeyboardButton("👥 User Management", callback_data='admin_user_management')])
        
        if current_section != 'system_health':
            buttons.append([InlineKeyboardButton("🏥 System Health", callback_data='admin_system_health')])
        
        if current_section != 'tickets':
            buttons.append([InlineKeyboardButton("🎫 Tickets", callback_data='admin_tickets')])
        
        # Always add main menu option
        buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data='default')])
        
        return InlineKeyboardMarkup(buttons)
    
    def admin_quick_actions_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create quick actions keyboard for admin dashboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Quick Stats", callback_data='admin_quick_stats'),
                InlineKeyboardButton("🚨 Alert Check", callback_data='admin_check_alerts')
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data='admin_quick_broadcast'),
                InlineKeyboardButton("🎫 Latest Tickets", callback_data='admin_latest_tickets')
            ],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="admin_panel")]
        ])