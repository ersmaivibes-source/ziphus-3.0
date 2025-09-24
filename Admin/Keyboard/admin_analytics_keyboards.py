"""
Admin Analytics Keyboards
Consolidated admin analytics keyboard components
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class AdminAnalyticsKeyboards:
    """Admin analytics keyboard components."""
    
    def __init__(self):
        pass
    
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
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def admin_user_analytics_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create user analytics detail keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 کل کاربران", callback_data='analytics_total_users'),
                InlineKeyboardButton("📈 رشد روزانه", callback_data='analytics_daily_growth')
            ],
            [
                InlineKeyboardButton("🎯 کاربران فعال", callback_data='analytics_active_users'),
                InlineKeyboardButton("💎 کاربران پریمیوم", callback_data='analytics_premium_users')
            ],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data='admin_user_analytics')],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data='admin_analytics')]
        ])
    
    def admin_growth_analytics_keyboard(self, lang_code: str, period: str = '7d') -> InlineKeyboardMarkup:
        """Create growth analytics keyboard with period selection."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("7 روز", callback_data='growth_7d'),
                InlineKeyboardButton("30 روز", callback_data='growth_30d'),
                InlineKeyboardButton("90 روز", callback_data='growth_90d')
            ],
            [
                InlineKeyboardButton("📊 نمودار رشد", callback_data=f'growth_chart_{period}'),
                InlineKeyboardButton("📈 پیش‌بینی", callback_data=f'growth_prediction_{period}')
            ],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data='admin_growth_analytics')],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data='admin_analytics')]
        ])
    
    def admin_analytics_back(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create back button for analytics screens."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='admin_analytics')]
        ])
    
    def admin_growth_analytics_periods(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create growth analytics period selection keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("7 روز", callback_data='admin_growth_7'),
                InlineKeyboardButton("30 روز", callback_data='admin_growth_30'),
                InlineKeyboardButton("90 روز", callback_data='admin_growth_90')
            ],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='admin_analytics')]
        ])