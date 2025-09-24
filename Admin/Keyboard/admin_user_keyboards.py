"""
Admin User Management Keyboards
Consolidated from Admin/User_Management/admin_user_management.py and related files
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class AdminUserKeyboards:
    """Admin user management keyboard components."""
    
    def __init__(self):
        pass
    
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
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def admin_user_list_keyboard(self, users: list, page: int, total_pages: int, lang_code: str) -> InlineKeyboardMarkup:
        """Create user list keyboard with pagination."""
        keyboard = []
        
        # User action buttons
        action_buttons = []
        for user in users:
            user_id = user['user_id']
            action_buttons.append(
                InlineKeyboardButton(
                    f"👤 {user['first_name']}",
                    callback_data=f"user_detail_{user_id}"
                )
            )
        
        # Add users in rows of 2
        for i in range(0, len(action_buttons), 2):
            keyboard.append(action_buttons[i:i+2])
        
        # Pagination buttons
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(
                InlineKeyboardButton("⏪ قبلی", callback_data=f"user_list_{page-1}")
            )
        
        if page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton("بعدی ⏩", callback_data=f"user_list_{page+1}")
            )
        
        if pagination_buttons:
            keyboard.append(pagination_buttons)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="user_management")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def admin_user_detail_keyboard(self, user_id: int, is_banned: bool, lang_code: str) -> InlineKeyboardMarkup:
        """Create user detail management keyboard."""
        keyboard = []
        
        # Ban/Unban button
        if is_banned:
            keyboard.append([
                InlineKeyboardButton("🔓 آزاد کردن کاربر", callback_data=f"user_unban_{user_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔒 مسدود کردن کاربر", callback_data=f"user_ban_{user_id}")
            ])
        
        # Tickets button
        keyboard.append([
            InlineKeyboardButton("📮 مشاهده تیکت‌ها", callback_data=f"user_tickets_{user_id}_1")
        ])
        
        # Send message button
        keyboard.append([
            InlineKeyboardButton("✉️ ارسال پیام", callback_data=f"user_message_{user_id}")
        ])
        
        # Back button
        keyboard.append([
            InlineKeyboardButton("⬅️ بازگشت به لیست", callback_data="user_list_1")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def admin_user_stats_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create user statistics keyboard."""
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="user_stats")],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="user_management")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def admin_user_search_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create user search keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔖 جستجو با نام کاربری", callback_data="search_username")],
            [InlineKeyboardButton("🆔 جستجو با شناسه کاربر", callback_data="search_userid")],
            [InlineKeyboardButton("👤 جستجو با نام", callback_data="search_name")],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="user_management")]
        ])
    
    def admin_mass_message_audience_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create mass message audience selection keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text_sync('all_users', lang_code), callback_data='mass_msg_all')],
            [
                InlineKeyboardButton(get_text_sync('persian_users', lang_code), callback_data='mass_msg_fa'),
                InlineKeyboardButton(get_text_sync('english_users', lang_code), callback_data='mass_msg_en')
            ],
            [InlineKeyboardButton(get_text_sync('pro_users', lang_code), callback_data='mass_msg_pro')],
            [InlineKeyboardButton(get_text_sync('users_no_email', lang_code), callback_data='mass_msg_no_email')],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data="admin_user_management")]
        ])