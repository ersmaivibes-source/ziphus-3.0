"""
Combined Keyboard Manager
========================

Consolidated keyboard functionality from:
- Keyboard/Dynamic/keyboards.py
- Admin/Keyboard/admin_keyboards.py
- Users/Keyboard/user_keyboards.py

This provides backward compatibility while using the new modular structure.
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync

from Admin.Keyboard.admin_keyboards import AdminKeyboards
from Users.Keyboard.user_keyboards import UserKeyboards


class CombinedKeyboards:
    """Combined keyboard manager providing all functionality from the old Keyboards class."""
    
    def __init__(self):
        self.admin_kb = AdminKeyboards()
        self.user_kb = UserKeyboards()
    
    # User keyboard methods (delegated to UserKeyboards)
    def main_menu(self, lang_code: str, is_admin: bool = False) -> InlineKeyboardMarkup:
        """Create main menu keyboard."""
        return self.user_kb.main_menu(lang_code, is_admin)
    
    def language_selection(self, lang_code: str, is_initial: bool = False) -> InlineKeyboardMarkup:
        """Create language selection keyboard."""
        return self.user_kb.language_selection(lang_code, is_initial)
    
    def back_button_inline(self, lang_code: str, return_to: str) -> InlineKeyboardButton:
        """Create an inline back button object."""
        return self.user_kb.back_button_inline(lang_code, return_to)
        
    def back_button(self, lang_code: str, return_to: str) -> InlineKeyboardMarkup:
        """Create a full keyboard with a single back button."""
        return self.user_kb.back_button(lang_code, return_to)
    
    def cancel_button(self, lang_code: str, return_to: str = 'default') -> InlineKeyboardMarkup:
        """Create a full keyboard with a single cancel button."""
        return self.user_kb.cancel_button(lang_code, return_to)
    
    # Admin keyboard methods (delegated to AdminKeyboards)
    def admin_panel(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create the main admin panel keyboard."""
        return self.admin_kb.admin_panel(lang_code)
    
    def admin_back_button_inline(self, lang_code: str, return_to: str) -> InlineKeyboardButton:
        """Create an admin back button inline object."""
        return self.admin_kb.admin_back_button_inline(lang_code, return_to)
    
    def admin_back_button(self, lang_code: str, return_to: str) -> InlineKeyboardMarkup:
        """Create a full keyboard with admin back button."""
        return self.admin_kb.admin_back_button(lang_code, return_to)
    
    def admin_cancel_button(self, lang_code: str, return_to: str = 'admin_panel') -> InlineKeyboardMarkup:
        """Create admin cancel button keyboard."""
        return self.admin_kb.admin_cancel_button(lang_code, return_to)
    
    def admin_tickets_menu(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create admin tickets management keyboard."""
        return self.admin_kb.admin_tickets_menu(lang_code)
    
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
    
    def admin_system_health_back(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create back button for system health menu."""
        return self.admin_back_button(lang_code, 'admin_system_health')

    def admin_ticket_action_keyboard(self, ticket_id: int, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket action keyboard for admin notifications."""
        from Admin.Keyboard.admin_ticket_keyboards import AdminTicketKeyboards
        admin_ticket_kb = AdminTicketKeyboards()
        return admin_ticket_kb.admin_ticket_action_keyboard(ticket_id, lang_code)
    
    def admin_ticket_view_keyboard(self, ticket_id: int, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket view keyboard for detailed ticket management."""
        from Admin.Keyboard.admin_ticket_keyboards import AdminTicketKeyboards
        admin_ticket_kb = AdminTicketKeyboards()
        return admin_ticket_kb.admin_ticket_view_keyboard(ticket_id, lang_code)
    
    def admin_ticket_list_keyboard(self, tickets: list, page: int, total_pages: int, 
                                 status_filter: str, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket list keyboard with pagination and filtering."""
        from Admin.Keyboard.admin_ticket_keyboards import AdminTicketKeyboards
        admin_ticket_kb = AdminTicketKeyboards()
        return admin_ticket_kb.admin_ticket_list_keyboard(tickets, page, total_pages, status_filter, lang_code)
    
    def admin_ticket_stats_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket statistics keyboard."""
        from Admin.Keyboard.admin_ticket_keyboards import AdminTicketKeyboards
        admin_ticket_kb = AdminTicketKeyboards()
        return admin_ticket_kb.admin_ticket_stats_keyboard(lang_code)


# Create a global instance for backward compatibility
keyboards = CombinedKeyboards()