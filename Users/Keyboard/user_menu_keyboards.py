"""
User Menu Keyboards
Consolidated user menu keyboard components
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class UserMenuKeyboards:
    """User menu keyboard components."""
    
    def __init__(self):
        pass
    
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
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='default')]
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
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='default')]
        ]
        return InlineKeyboardMarkup(buttons)