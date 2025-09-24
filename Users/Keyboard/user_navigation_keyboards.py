"""
User Navigation Keyboards
Consolidated user navigation and flow keyboard components
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class UserNavigationKeyboards:
    """User navigation keyboard components."""
    
    def __init__(self):
        pass
    
    def support_tickets_keyboard(self, lang_code: str, has_tickets: bool = False) -> InlineKeyboardMarkup:
        """Create support tickets management keyboard."""
        buttons = [
            [InlineKeyboardButton(get_text_sync('create_new_ticket', lang_code), callback_data='create_ticket')]
        ]
        
        if has_tickets:
            buttons.append([InlineKeyboardButton(get_text_sync('my_tickets', lang_code), callback_data='my_tickets')])
        
        buttons.extend([
            [InlineKeyboardButton(get_text_sync('ticket_status', lang_code), callback_data='check_ticket_status')],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    def help_and_support_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create help and support keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(get_text_sync('faq', lang_code), callback_data='faq'),
                InlineKeyboardButton(get_text_sync('user_guide', lang_code), callback_data='user_guide')
            ],
            [
                InlineKeyboardButton(get_text_sync('contact_support', lang_code), callback_data='contact_support'),
                InlineKeyboardButton(get_text_sync('report_bug', lang_code), callback_data='report_bug')
            ],
            [
                InlineKeyboardButton(get_text_sync('feature_request', lang_code), callback_data='feature_request'),
                InlineKeyboardButton(get_text_sync('about_us', lang_code), callback_data='about_us')
            ],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
    
    def referral_system_keyboard(self, lang_code: str, referral_count: int = 0) -> InlineKeyboardMarkup:
        """Create referral system keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔗 My Referral Link", callback_data='get_referral_link'),
                InlineKeyboardButton(f"👥 Referrals: {referral_count}", callback_data='view_referrals')
            ],
            [
                InlineKeyboardButton("💰 Earnings", callback_data='referral_earnings'),
                InlineKeyboardButton("📊 Statistics", callback_data='referral_stats')
            ],
            [
                InlineKeyboardButton("📋 How it Works", callback_data='referral_guide'),
                InlineKeyboardButton("🎁 Bonuses", callback_data='referral_bonuses')
            ],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
    
    def privacy_settings_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create privacy settings keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👁️ Data Visibility", callback_data='data_visibility'),
                InlineKeyboardButton("🔒 Privacy Level", callback_data='privacy_level')
            ],
            [
                InlineKeyboardButton("📧 Email Preferences", callback_data='email_preferences'),
                InlineKeyboardButton("🔔 Notification Settings", callback_data='notification_settings')
            ],
            [
                InlineKeyboardButton("📊 Analytics Sharing", callback_data='analytics_sharing'),
                InlineKeyboardButton("🍪 Cookie Settings", callback_data='cookie_settings')
            ],
            [
                InlineKeyboardButton("📄 Download My Data", callback_data='download_data'),
                InlineKeyboardButton("🗑️ Delete My Data", callback_data='delete_data_confirm')
            ],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
    
    def notification_preferences_keyboard(self, lang_code: str, current_settings: dict = {}) -> InlineKeyboardMarkup:
        """Create notification preferences keyboard."""
        if current_settings is None:
            current_settings = {
                'email_notifications': True,
                'push_notifications': True,
                'marketing_emails': False,
                'security_alerts': True
            }
        
        buttons = []
        
        for setting, enabled in current_settings.items():
            status_emoji = "✅" if enabled else "❌"
            setting_name = setting.replace('_', ' ').title()
            buttons.append([
                InlineKeyboardButton(
                    f"{status_emoji} {setting_name}",
                    callback_data=f'toggle_{setting}'
                )
            ])
        
        buttons.extend([
            [InlineKeyboardButton("💾 Save Settings", callback_data='save_notification_settings')],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
        
        return InlineKeyboardMarkup(buttons)