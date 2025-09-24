
"""
Admin handlers for system health and maintenance.
Handles system status checks, database health, and data cleanup operations.
"""

from typing import Optional
from hydrogram import Client, filters
from hydrogram.types import CallbackQuery

from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService
from Admin.System_Settings.system_health_service import SystemHealthService
from Admin.Reports.analytics_service import AnalyticsService
from general.Keyboard.combined_keyboards import keyboards
from general.Logging.logger_manager import get_logger, log_error_with_context

logger = get_logger(__name__)
from general.Language.Translations import get_text_sync
from general.Decorators.core_decorators import admin_required

# Global instances to be initialized by register_handlers
db: Optional[DatabaseManager] = None
redis: Optional[RedisService] = None
system_health_service: Optional[SystemHealthService] = None
analytics_service: Optional[AnalyticsService] = None
# keyboards instance will be used from combined_keyboards

# --- Entry Point Handlers (Triggered by Callbacks) ---

@admin_required()
async def admin_system_health_handler(client: Client, callback_query: CallbackQuery):
    """Handles the main system health menu."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id) if db else None
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        await callback_query.message.edit_text(
            get_text_sync('system_health_text', lang_code),
            reply_markup=keyboards.admin_system_health_menu(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_system_health_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_system_status_handler(client: Client, callback_query: CallbackQuery):
    """Displays the overall system status."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id) if db else None
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        logger.info(f"Admin {admin_id} viewed system status")
        
        if system_health_service is None:
            raise RuntimeError("System health service not initialized")
        
        health_metrics = await system_health_service.get_system_health()
        message = system_health_service.format_system_health(health_metrics, lang_code)
        
        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_system_health_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_system_status_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_database_health_handler(client: Client, callback_query: CallbackQuery):
    """Displays detailed database health."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id) if db else None
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        logger.info(f"Admin {admin_id} viewed database health")
        
        if system_health_service is None:
            raise RuntimeError("System health service not initialized")
        
        db_health = await system_health_service.get_database_health()
        message = system_health_service.format_database_health(db_health, lang_code)
        
        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_system_health_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_database_health_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_run_health_check_handler(client: Client, callback_query: CallbackQuery):
    """Runs a comprehensive, real-time health check."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id) if db else None
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        logger.info(f"Admin {admin_id} ran health check")
        await callback_query.message.edit_text(get_text_sync('running_health_check', lang_code))

        if system_health_service is None:
            raise RuntimeError("System health service not initialized")
        
        results = await system_health_service.run_health_check()
        
        # Formatting logic can be moved to a formatter if it grows
        status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "❌"}
        message = f"**{get_text_sync('system_health_check_title', lang_code)}**\n\n"
        message += f"**Overall Status:** {status_emoji.get(results['overall_status'], '❓')} {results['overall_status'].title()}\n\n"
        for component, status in results['checks'].items():
            message += f"• {component.title()}: {status_emoji.get(status, '❓')} {status.title()}\n"
        
        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_system_health_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_run_health_check_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_refresh_analytics_handler(client: Client, callback_query: CallbackQuery):
    """Refreshes the analytics cache."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id) if db else None
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        logger.info(f"Admin {admin_id} refreshed analytics cache")
        
        if analytics_service is None:
            raise RuntimeError("Analytics service not initialized")
        
        success = await analytics_service.refresh_analytics_cache()
        
        if success:
            await callback_query.answer(get_text_sync('analytics_cache_refreshed', lang_code), show_alert=True)
        else:
            await callback_query.answer(get_text_sync('failed_to_refresh_cache', lang_code), show_alert=True)
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_refresh_analytics_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

# --- Registration ---

def register_handlers(app: Client):
    """Registers all handlers for admin system health."""
    global db, redis, system_health_service, analytics_service
    db = getattr(app, 'db', None)
    redis = getattr(app, 'redis', None)
    if db is not None:
        system_health_service = SystemHealthService(db, redis)
        analytics_service = AnalyticsService(db) # Needed for cache refresh
    else:
        system_health_service = None
        analytics_service = None

    # Register callback handlers
    app.on_callback_query(filters.regex("^admin_system_health$"))(admin_system_health_handler)
    app.on_callback_query(filters.regex("^admin_system_status$"))(admin_system_status_handler)
    app.on_callback_query(filters.regex("^admin_database_health$"))(admin_database_health_handler)
    app.on_callback_query(filters.regex("^admin_run_health_check$"))(admin_run_health_check_handler)
    app.on_callback_query(filters.regex("^admin_refresh_analytics$"))(admin_refresh_analytics_handler)
    # Note: Data cleanup handlers could also go here.
    
    logger.info("Admin System Health handlers registered.")
