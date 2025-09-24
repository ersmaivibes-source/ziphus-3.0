"""
Admin Ticket Management Keyboards
Consolidated from Support/Tickets/ and Tools/Formatters/formatters.py
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class AdminTicketKeyboards:
    """Admin ticket management keyboard components."""
    
    def __init__(self):
        pass
    
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
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def admin_ticket_action_keyboard(self, ticket_id: int, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket action keyboard for admin notifications."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🔍 View #{ticket_id}", callback_data=f'admin_view_ticket_{ticket_id}')],
            [
                InlineKeyboardButton('💬 Reply', callback_data=f'admin_reply_ticket_{ticket_id}'),
                InlineKeyboardButton('🟡 Progress', callback_data=f'admin_mark_progress_{ticket_id}')
            ],
            [InlineKeyboardButton('📋 All Tickets', callback_data='admin_tickets')]
        ])
    
    def admin_ticket_view_keyboard(self, ticket_id: int, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket view keyboard for detailed ticket management."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 View Ticket", callback_data=f'admin_view_ticket_{ticket_id}')],
            [InlineKeyboardButton("💬 Reply", callback_data=f'admin_reply_ticket_{ticket_id}')]
        ])
    
    def admin_ticket_list_keyboard(self, tickets: list, page: int, total_pages: int, 
                                 status_filter: str, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket list keyboard with pagination and filtering."""
        keyboard = []
        
        # Ticket buttons (limit to 5 per page for readability)
        for ticket in tickets[:5]:
            ticket_id = ticket['id']
            priority_emoji = "🔴" if ticket['priority'] == 'high' else "🟡" if ticket['priority'] == 'medium' else "🟢"
            keyboard.append([
                InlineKeyboardButton(
                    f"{priority_emoji} #{ticket_id} - {ticket['subject'][:20]}...",
                    callback_data=f"admin_view_ticket_{ticket_id}"
                )
            ])
        
        # Status filter buttons
        filter_buttons = []
        if status_filter != 'open':
            filter_buttons.append(InlineKeyboardButton("📖 Open", callback_data='admin_open_tickets'))
        if status_filter != 'progress':
            filter_buttons.append(InlineKeyboardButton("🟡 Progress", callback_data='admin_progress_tickets'))
        if status_filter != 'closed':
            filter_buttons.append(InlineKeyboardButton("✅ Closed", callback_data='admin_closed_tickets'))
        
        if filter_buttons:
            # Split into rows of 2
            for i in range(0, len(filter_buttons), 2):
                keyboard.append(filter_buttons[i:i+2])
        
        # Pagination
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(
                InlineKeyboardButton("⏪ Previous", callback_data=f"admin_tickets_{status_filter}_{page-1}")
            )
        if page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton("Next ⏩", callback_data=f"admin_tickets_{status_filter}_{page+1}")
            )
        
        if pagination_buttons:
            keyboard.append(pagination_buttons)
        
        # Back button
        keyboard.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="admin_panel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def admin_ticket_stats_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create ticket statistics keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Daily Stats", callback_data='ticket_stats_daily'),
                InlineKeyboardButton("📈 Weekly Stats", callback_data='ticket_stats_weekly')
            ],
            [
                InlineKeyboardButton("🎯 Category Stats", callback_data='ticket_stats_category'),
                InlineKeyboardButton("⏱️ Response Time", callback_data='ticket_stats_response')
            ],
            [InlineKeyboardButton("🔄 Refresh", callback_data='admin_ticket_stats')],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data='admin_tickets')]
        ])