"""
Admin System Management Keyboards
Consolidated system health and management keyboard components
"""

from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from general.Language.Translations import get_text_sync


class AdminSystemKeyboards:
    """Admin system management keyboard components."""
    
    def __init__(self):
        pass
    
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
            [InlineKeyboardButton(get_text_sync('back', lang_code), callback_data='admin_panel')]
        ]
        return InlineKeyboardMarkup(buttons)
    
    def admin_system_status_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create system status detail keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🗄️ Database", callback_data='check_database_status'),
                InlineKeyboardButton("🔄 Redis", callback_data='check_redis_status')
            ],
            [
                InlineKeyboardButton("🌐 API Status", callback_data='check_api_status'),
                InlineKeyboardButton("📊 Server Load", callback_data='check_server_load')
            ],
            [
                InlineKeyboardButton("💾 Storage", callback_data='check_storage_status'),
                InlineKeyboardButton("🔗 Connectivity", callback_data='check_connectivity')
            ],
            [InlineKeyboardButton("🔄 Refresh All", callback_data='admin_system_status')],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data='admin_system_health')]
        ])
    
    def admin_database_health_keyboard(self, lang_code: str) -> InlineKeyboardMarkup:
        """Create database health management keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Connection Pool", callback_data='db_connection_pool'),
                InlineKeyboardButton("⚡ Query Performance", callback_data='db_query_performance')
            ],
            [
                InlineKeyboardButton("💾 Storage Usage", callback_data='db_storage_usage'),
                InlineKeyboardButton("🔄 Active Queries", callback_data='db_active_queries')
            ],
            [
                InlineKeyboardButton("🧹 Run Cleanup", callback_data='db_run_cleanup'),
                InlineKeyboardButton("🔧 Optimize", callback_data='db_optimize')
            ],
            [InlineKeyboardButton("🔄 Refresh", callback_data='admin_database_health')],
            [InlineKeyboardButton("⬅️ بازگشت", callback_data='admin_system_health')]
        ])
    
    def admin_cleanup_confirmation_keyboard(self, lang_code: str, cleanup_type: str) -> InlineKeyboardMarkup:
        """Create cleanup confirmation keyboard."""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"✅ {get_text_sync('confirm_cleanup', lang_code)}", callback_data=f'confirm_cleanup_{cleanup_type}'),
                InlineKeyboardButton(f"❌ {get_text_sync('cancel', lang_code)}", callback_data='admin_system_health')
            ]
        ])