"""
User Settings & Account Keyboards
Consolidated user settings and account management keyboard components
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class UserSettingsKeyboards:
    """User settings keyboard components."""
    
    def __init__(self):
        pass
    
    def settings_account_menu(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create unified Settings & Account menu keyboard."""
        buttons = [
            [InlineKeyboardButton(get_text_sync('account_upgrade', lang_code), callback_data='account_upgrade')],
            [
                InlineKeyboardButton(get_text_sync('wallet_recharge', lang_code), callback_data='wallet_recharge'),
                InlineKeyboardButton(get_text_sync('account_history', lang_code), callback_data='account_history')
            ],
            [InlineKeyboardButton(get_text_sync('plan_limits', lang_code), callback_data='plan_limits')],
            [
                InlineKeyboardButton(get_text_sync('register_email', lang_code), callback_data='register_email'),
                InlineKeyboardButton(get_text_sync('sign_in_with_email', lang_code), callback_data='sign-in-with-email')
            ],
            [InlineKeyboardButton(get_text_sync('change_password', lang_code), callback_data='change_password')],
            [
                InlineKeyboardButton(get_text_sync('invite_friends', lang_code), callback_data='invite_friends'),
                InlineKeyboardButton(get_text_sync('support_tickets', lang_code), callback_data='support_tickets')
            ],
            [
                InlineKeyboardButton(get_text_sync('change_language', lang_code), callback_data='change_language'),
                InlineKeyboardButton(get_text_sync('clear_database', lang_code), callback_data='clear_database')
            ],
            [
                InlineKeyboardButton(get_text_sync('about_us', lang_code), callback_data='about_us'),
                InlineKeyboardButton(get_text_sync('faq', lang_code), callback_data='faq')
            ],
            [InlineKeyboardButton(get_text_sync('account_help', lang_code), callback_data='account_help')],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='default')]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def clear_database_confirm(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create clear database confirmation keyboard."""
        buttons = [
            [
                InlineKeyboardButton(f"❌ {get_text_sync('yes', lang_code)}", callback_data='clear_db_yes'),
                InlineKeyboardButton(f"✅ {get_text_sync('no', lang_code)}", callback_data='clear_db_no')
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def subscription_menu(self, lang_code: str, current_plan: str = 'free') -> InlineKeyboardMarkup:
        """Create subscription management keyboard."""
        buttons = []
        
        if current_plan == 'free':
            buttons.append([InlineKeyboardButton("💎 Upgrade to Premium", callback_data='upgrade_premium')])
            buttons.append([InlineKeyboardButton("🌟 Upgrade to Pro", callback_data='upgrade_pro')])
        elif current_plan == 'premium':
            buttons.append([InlineKeyboardButton("🌟 Upgrade to Pro", callback_data='upgrade_pro')])
            buttons.append([InlineKeyboardButton("📉 Downgrade to Free", callback_data='downgrade_free')])
        elif current_plan == 'pro':
            buttons.append([InlineKeyboardButton("📉 Downgrade to Premium", callback_data='downgrade_premium')])
            buttons.append([InlineKeyboardButton("📉 Downgrade to Free", callback_data='downgrade_free')])
        
        buttons.extend([
            [InlineKeyboardButton("📊 Plan Details", callback_data='plan_details')],
            [InlineKeyboardButton("💳 Payment History", callback_data='payment_history')],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data='settings_account')]
        ])
        
        return InlineKeyboardMarkup(buttons)