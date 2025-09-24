
"""
Admin handlers for analytics and reporting.
Handles user, chat, referral, and growth analytics displays.
"""

from hydrogram import Client, filters
from hydrogram.types import CallbackQuery, Message

from general.Database.MySQL.db_manager import DatabaseManager
from Admin.Reports.analytics_service import AnalyticsService
from Admin.Keyboard.admin_analytics_keyboards import AdminAnalyticsKeyboards
from general.Logging.logger_manager import get_logger, log_admin_action, log_error_with_context

logger = get_logger(__name__)
from general.Language.Translations import get_text_sync
from general.Decorators.core_decorators import admin_required

# Global instances to be initialized by register_handlers
db: DatabaseManager
analytics_service: AnalyticsService
keyboards = AdminAnalyticsKeyboards()

# --- Entry Point Handlers (Triggered by Callbacks) ---

@admin_required()
async def admin_analytics_handler(client: Client, callback_query: CallbackQuery):
    """Handles the main analytics menu."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        await callback_query.message.edit_text(
            get_text_sync('admin_analytics_dashboard', lang_code),
            reply_markup=keyboards.admin_analytics(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_analytics_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_user_analytics_handler(client: Client, callback_query: CallbackQuery):
    """Displays user analytics."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        log_admin_action(admin_id, 'viewed_user_analytics')
        
        analytics_data = await analytics_service.get_user_analytics()
        message = analytics_service.format_user_analytics(analytics_data, lang_code)
        
        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_analytics_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_user_analytics_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_chat_analytics_handler(client: Client, callback_query: CallbackQuery):
    """Displays chat analytics."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        log_admin_action(admin_id, 'viewed_chat_analytics')

        analytics_data = await analytics_service.get_chat_analytics()
        message = analytics_service.format_chat_analytics(analytics_data, lang_code)
        
        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_analytics_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_chat_analytics_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_referral_analytics_handler(client: Client, callback_query: CallbackQuery):
    """Displays referral analytics."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        log_admin_action(admin_id, 'viewed_referral_analytics')
        
        analytics_data = await analytics_service.get_referral_analytics()
        message = analytics_service.format_referral_analytics(analytics_data, lang_code)
        
        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_analytics_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_referral_analytics_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_growth_analytics_handler(client: Client, callback_query: CallbackQuery):
    """Displays growth analytics period selection."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        await callback_query.message.edit_text(
            get_text_sync('admin_select_time_range', lang_code),
            reply_markup=keyboards.admin_growth_analytics_periods(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_growth_analytics_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_growth_period_handler(client: Client, callback_query: CallbackQuery):
    """Displays growth analytics for a specific period."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        period_days = int(callback_query.data.split('_')[-1]) if callback_query.data else 0
        log_admin_action(admin_id, f'viewed_growth_analytics_{period_days}_days')

        analytics_data = await analytics_service.get_growth_analytics(period_days)
        message = analytics_service.format_growth_analytics(analytics_data, lang_code)
        
        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_analytics_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_growth_period_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_feature_analytics_handler(client: Client, callback_query: CallbackQuery):
    """Displays feature usage analytics."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        log_admin_action(admin_id, 'viewed_feature_analytics')
        
        # Use the analytics service to get feature usage statistics
        feature_stats = await analytics_service.get_feature_usage_stats()
        
        if feature_stats:
            # Format the feature statistics
            message = "📊 **Feature Usage Analytics**\n\n"
            for feature, usage in sorted(feature_stats.items(), key=lambda x: x[1], reverse=True):
                message += f"• {feature}: {usage:,}\n"
        else:
            message = get_text_sync('admin_feature_analytics_note', lang_code)

        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_analytics_back(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_feature_analytics_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

# --- Registration ---

def register_handlers(app: Client):
    """Registers all handlers for admin analytics."""
    global db, analytics_service
    db = app.db
    analytics_service = AnalyticsService(db)

    # Register callback handlers
    app.on_callback_query(filters.regex("^admin_analytics$"))(admin_analytics_handler)
    app.on_callback_query(filters.regex("^admin_user_analytics$"))(admin_user_analytics_handler)
    app.on_callback_query(filters.regex("^admin_chat_analytics$"))(admin_chat_analytics_handler)
    app.on_callback_query(filters.regex("^admin_referral_analytics$"))(admin_referral_analytics_handler)
    app.on_callback_query(filters.regex("^admin_growth_analytics$"))(admin_growth_analytics_handler)
    app.on_callback_query(filters.regex("^admin_growth_\\d+$"))(admin_growth_period_handler)
    app.on_callback_query(filters.regex("^admin_feature_analytics$"))(admin_feature_analytics_handler)
    
    logger.info("Admin Analytics handlers registered.")
