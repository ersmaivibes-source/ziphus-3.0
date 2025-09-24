"""
Main Admin Keyboard Manager
Consolidated admin keyboard functionality from Keyboard/Dynamic/keyboards.py
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class AdminKeyboards:
    """Main admin keyboard manager consolidated from multiple sources."""
    
    def __init__(self):
        pass
    
    def admin_panel(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create the main admin panel keyboard."""
        buttons = [
            [
                InlineKeyboardButton(get_text_sync('admin_analytics', lang_code), callback_data='admin_analytics'),
                InlineKeyboardButton(get_text_sync('admin_user_management', lang_code), callback_data='admin_user_management')
            ],
            # Bot Management button is removed. Tickets can be moved here or kept under a different section.
            [
                InlineKeyboardButton(get_text_sync('admin_system_health', lang_code), callback_data='admin_system_health'),
                InlineKeyboardButton(get_text_sync('admin_tickets', lang_code), callback_data='admin_tickets')
            ],
            [
                self.admin_back_button_inline(lang_code, 'default')
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def admin_back_button_inline(self, lang_code: str, return_to: str) -> InlineKeyboardButton:
        """Create an admin back button inline object."""
        return InlineKeyboardButton(get_text_sync('back', lang_code), callback_data=return_to)
    
    def admin_back_button(self, lang_code: str, return_to: str) -> InlineKeyboardMarkup:
        """Create a full keyboard with admin back button."""
        return InlineKeyboardMarkup([[self.admin_back_button_inline(lang_code, return_to)]])
    
    def admin_cancel_button(self, lang_code: str, return_to: str = 'admin_panel') -> InlineKeyboardMarkup:
        """Create admin cancel button keyboard."""
        return InlineKeyboardMarkup([[InlineKeyboardButton(get_text_sync('cancel', lang_code), callback_data=f'admin_cancel_{return_to}')]])
        
    def admin_user_management(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create admin user management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(get_text_sync('admin_user_search', lang_code), callback_data='admin_user_search'),
                InlineKeyboardButton(get_text_sync('admin_mass_message', lang_code), callback_data='admin_mass_message')
            ],
            [
                InlineKeyboardButton(get_text_sync('admin_block_user', lang_code), callback_data='admin_block_user'),
                InlineKeyboardButton(get_text_sync('admin_unblock_user', lang_code), callback_data='admin_unblock_user')
            ],
            [
                InlineKeyboardButton(get_text_sync('admin_block_list', lang_code), callback_data='admin_block_list'),
                InlineKeyboardButton(get_text_sync('admin_promote_admin', lang_code), callback_data='admin_promote_admin')
            ],
            [self.admin_back_button_inline(lang_code, 'admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)
        
    def admin_analytics(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create admin analytics keyboard."""
        buttons = [
            [
                InlineKeyboardButton(get_text_sync('user_analytics', lang_code), callback_data='admin_user_analytics'),
                InlineKeyboardButton(get_text_sync('chat_analytics', lang_code), callback_data='admin_chat_analytics')
            ],
            [
                InlineKeyboardButton(get_text_sync('referral_analytics', lang_code), callback_data='admin_referral_analytics'),
                InlineKeyboardButton(get_text_sync('growth_analytics', lang_code), callback_data='admin_growth_analytics')
            ],
            [InlineKeyboardButton(get_text_sync('feature_analytics', lang_code), callback_data='admin_feature_analytics')],
            [self.admin_back_button_inline(lang_code, 'admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)

    def admin_system_health_menu(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create system health management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(get_text_sync('admin_system_status', lang_code), callback_data='admin_system_status'),
                InlineKeyboardButton(get_text_sync('admin_database_health', lang_code), callback_data='admin_database_health')
            ],
            [
                InlineKeyboardButton(get_text_sync('admin_run_health_check', lang_code), callback_data='admin_run_health_check'),
                InlineKeyboardButton(get_text_sync('admin_cleanup_data', lang_code), callback_data='admin_cleanup_data')
            ],
            [InlineKeyboardButton(get_text_sync('admin_refresh_analytics', lang_code), callback_data='admin_refresh_analytics')],
            [self.admin_back_button_inline(lang_code, 'admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)

    def admin_tickets_menu(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create admin tickets management keyboard."""
        buttons = [
            [
                InlineKeyboardButton(get_text_sync('admin_open_tickets', lang_code), callback_data='admin_open_tickets'),
                InlineKeyboardButton(get_text_sync('admin_progress_tickets', lang_code), callback_data='admin_progress_tickets')
            ],
            [
                InlineKeyboardButton(get_text_sync('admin_closed_tickets', lang_code), callback_data='admin_closed_tickets'),
                InlineKeyboardButton(get_text_sync('admin_ticket_stats', lang_code), callback_data='admin_ticket_stats')
            ],
            [self.admin_back_button_inline(lang_code, 'admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)