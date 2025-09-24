"""
User Account Management Keyboards
Consolidated user account-related keyboard components
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class UserAccountKeyboards:
    """User account management keyboard components."""
    
    def __init__(self):
        pass
    
    def email_registration_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create email registration navigation keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text_sync('register_email', lang_code), callback_data='register_email')],
            [InlineKeyboardButton(get_text_sync('sign_in_with_email', lang_code), callback_data='sign-in-with-email')],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
    
    def email_verification_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create email verification keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Resend Code", callback_data='resend_verification')],
            [InlineKeyboardButton("✏️ Change Email", callback_data='change_email_during_verification')],
            [InlineKeyboardButton(get_text_sync('cancel', lang_code), callback_data='settings_account')]
        ])
    
    def password_change_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create password change navigation keyboard."""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Set New Password", callback_data='set_new_password')],
            [InlineKeyboardButton("🔑 Change Password", callback_data='change_existing_password')],
            [InlineKeyboardButton("🔄 Forgot Password", callback_data='forgot_password')],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
    
    def account_recovery_keyboard(self, lang_code: str, has_email: bool = False) -> InlineKeyboardMarkup:
        """Create account recovery keyboard."""
        buttons = []
        
        if has_email:
            buttons.append([InlineKeyboardButton("📧 Recover with Email", callback_data='recover_with_email')])
        
        buttons.extend([
            [InlineKeyboardButton("🆔 Recover with ID", callback_data='recover_with_id')],
            [InlineKeyboardButton("🎫 Contact Support", callback_data='recovery_support')],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    def profile_management_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create profile management keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👤 View Profile", callback_data='view_profile'),
                InlineKeyboardButton("✏️ Edit Profile", callback_data='edit_profile')
            ],
            [
                InlineKeyboardButton("📧 Change Email", callback_data='change_email'),
                InlineKeyboardButton("🔐 Change Password", callback_data='change_password')
            ],
            [
                InlineKeyboardButton("🌐 Language", callback_data='change_language'),
                InlineKeyboardButton("🔔 Notifications", callback_data='notification_settings')
            ],
            [InlineKeyboardButton("🗑️ Delete Account", callback_data='delete_account_confirm')],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])
    
    def wallet_management_keyboard(self, lang_code: str, balance: float = 0.0) -> InlineKeyboardMarkup:
        """Create wallet management keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"💰 Balance: ${balance:.2f}", callback_data='view_balance'),
                InlineKeyboardButton("💳 Add Funds", callback_data='add_funds')
            ],
            [
                InlineKeyboardButton("📊 Transaction History", callback_data='transaction_history'),
                InlineKeyboardButton("💸 Withdraw", callback_data='withdraw_funds')
            ],
            [
                InlineKeyboardButton("🎁 Referral Earnings", callback_data='referral_earnings'),
                InlineKeyboardButton("💰 Bonuses", callback_data='view_bonuses')
            ],
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='settings_account')]
        ])