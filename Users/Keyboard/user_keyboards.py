"""
Main User Keyboard Manager
Consolidated user keyboard functionality from Keyboard/Dynamic/keyboards.py
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class UserKeyboards:
    """Main user keyboard manager consolidated from multiple sources."""
    
    def __init__(self):
        pass
    
    def main_menu(self, lang_code: str, is_admin: bool = False) -> InlineKeyboardMarkup:
        """Create main menu keyboard."""
        buttons = [
            [
                InlineKeyboardButton(get_text_sync('tools', lang_code), callback_data="tools"),
                InlineKeyboardButton(get_text_sync('orders', lang_code), callback_data="orders")
            ],
            [
                InlineKeyboardButton(get_text_sync('settings_account', lang_code), callback_data="settings_account")
            ]
        ]
        if is_admin:
            buttons.append([
                InlineKeyboardButton(get_text_sync('admin_panel', lang_code), callback_data="admin_panel")
            ])
        return InlineKeyboardMarkup(buttons)
    
    def back_button_inline(self, lang_code: str, return_to: str) -> InlineKeyboardButton:
        """Create an inline back button object."""
        return InlineKeyboardButton(get_text_sync('back', lang_code), callback_data=return_to)
        
    def back_button(self, lang_code: str, return_to: str) -> InlineKeyboardMarkup:
        """Create a full keyboard with a single back button."""
        return InlineKeyboardMarkup([[self.back_button_inline(lang_code, return_to)]])
    
    def cancel_button(self, lang_code: str, return_to: str = 'default') -> InlineKeyboardMarkup:
        """Create a full keyboard with a single cancel button."""
        return InlineKeyboardMarkup([[InlineKeyboardButton(get_text_sync('cancel', lang_code), callback_data=f'cancel_{return_to}')]])
    
    def language_selection(self, lang_code: str, is_initial: bool = False) -> InlineKeyboardMarkup:
        """Create language selection keyboard."""
        callback_prefix = "initial_lang_" if is_initial else "set_lang_"
        buttons = [
            [
                InlineKeyboardButton("فارسی 🇮🇷", callback_data=f"{callback_prefix}fa"),
                InlineKeyboardButton("ENGLISH 🇬🇧", callback_data=f"{callback_prefix}en")
            ]
        ]
        if not is_initial:
            buttons.append([
                self.back_button_inline(lang_code, 'settings_account')
            ])
        return InlineKeyboardMarkup(buttons)
    
    def tools_menu(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create tools menu keyboard."""
        buttons = [
            [InlineKeyboardButton(get_text_sync('media_downloader', lang_code), callback_data='media-downloader')],
            [InlineKeyboardButton(get_text_sync('file_format_converter', lang_code), callback_data='file-format-converter')],
            [InlineKeyboardButton(get_text_sync('file_link_converter', lang_code), callback_data='file-link-converter')],
            [InlineKeyboardButton(get_text_sync('file_quality_editor', lang_code), callback_data='file-quality-editor')],
            [InlineKeyboardButton(get_text_sync('ip_network_tool', lang_code), callback_data='ip-network-tool')],
            [InlineKeyboardButton(get_text_sync('bypass_sanctions', lang_code), callback_data='bypass-sanctions')],
            [InlineKeyboardButton(get_text_sync('antivirus_antiscammer', lang_code), callback_data='antivirus-antiscammer')],
            [InlineKeyboardButton(get_text_sync('fact_checker', lang_code), callback_data='fact-checker')],
            [InlineKeyboardButton(get_text_sync('smart_music_finder', lang_code), callback_data='smart-music-finder')],
            [InlineKeyboardButton(get_text_sync('smart_feed_reader', lang_code), callback_data='smart-feed-reader')],
            [InlineKeyboardButton(get_text_sync('smart_translator', lang_code), callback_data='smart-translator')],
            [InlineKeyboardButton(get_text_sync('live_stock_market', lang_code), callback_data='live-stock-market')],
            [InlineKeyboardButton(get_text_sync('temporary_email_sms', lang_code), callback_data='temporary-email-sms')],
            [InlineKeyboardButton(get_text_sync('apply_assistant', lang_code), callback_data='apply-assistant')],
            [InlineKeyboardButton(get_text_sync('telegram_search', lang_code), callback_data='telegram-search')],
            [InlineKeyboardButton(get_text_sync('voice_text_converter', lang_code), callback_data='voice-text-converter')],
            [InlineKeyboardButton(get_text_sync('movie_series_downloader', lang_code), callback_data='movie-series-downloader')],
            [InlineKeyboardButton(get_text_sync('book_article_downloader', lang_code), callback_data='book-article-downloader')],
            [InlineKeyboardButton(get_text_sync('artificial_intelligence', lang_code), callback_data='artificial-intelligence')],
            [self.back_button_inline(lang_code, 'default')]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def orders_menu(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create orders menu keyboard."""
        buttons = [
            [InlineKeyboardButton(get_text_sync('gift_card_request', lang_code), callback_data='gift-card-request')],
            [InlineKeyboardButton(get_text_sync('gem_and_rewards_request', lang_code), callback_data='gem-and-rewards-request')],
            [InlineKeyboardButton(get_text_sync('seo_request', lang_code), callback_data='seo-request')],
            [InlineKeyboardButton(get_text_sync('website_design_request', lang_code), callback_data='website-design-request')],
            [InlineKeyboardButton(get_text_sync('bot_design_request', lang_code), callback_data='bot-design-request')],
            [InlineKeyboardButton(get_text_sync('server_request', lang_code), callback_data='server-request')],
            [InlineKeyboardButton(get_text_sync('security_request', lang_code), callback_data='security-request')],
            [InlineKeyboardButton(get_text_sync('project_upload_channel', lang_code), callback_data='project-upload-channel')],
            [InlineKeyboardButton(get_text_sync('account_request_channel', lang_code), callback_data='account-request-channel')],
            [InlineKeyboardButton(get_text_sync('my_orders', lang_code), callback_data='my-orders')],
            [self.back_button_inline(lang_code, 'default')]
        ]
        return InlineKeyboardMarkup(buttons)
    
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
            [self.back_button_inline(lang_code, 'default')]
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