"""
Subscription handlers for user subscription management.
Handles subscription plans, upgrades, downgrades, and billing.
"""

from hydrogram import Client, filters
from hydrogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from hydrogram.handlers import CallbackQueryHandler
import asyncio
from typing import Dict, Optional

from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService
from Users.Subscriptions.subscription_service import UserSubscriptionService
from general.Logging.logger_manager import get_logger, log_user_action, log_error_with_context

# Import the NEW and secure decorator
from general.Decorators.core_decorators import check_user_banned

# Initialize logger
logger = get_logger(__name__)

# Global instances
db: Optional[DatabaseManager] = None
redis: Optional[RedisService] = None
subscription_service: Optional[UserSubscriptionService] = None

@check_user_banned()
async def subscription_menu_handler(client: Client, callback_query: CallbackQuery):
    """Handle subscription menu display."""
    user_id = callback_query.from_user.id
    try:
        if subscription_service is None:
            await callback_query.answer("Service not initialized", show_alert=True)
            return
            
        current_plan = await subscription_service.get_user_subscription_status(user_id)
        
        # Format the subscription status message
        if current_plan:
            plan_type = current_plan.get('Plan_Type', 'free')
        else:
            plan_type = 'free'
        
        message_text = subscription_service.format_subscription_status(current_plan, 'en') if subscription_service else "Service unavailable"
        
        await callback_query.message.edit_text(
            message_text,
            reply_markup=InlineKeyboardMarkup([])  # Empty keyboard for now
        )
        await callback_query.answer()
        
    except Exception as e:
        log_error_with_context(e, {'handler': 'subscription_menu_handler', 'user_id': user_id})
        await callback_query.answer("An error occurred", show_alert=True)

@check_user_banned()
async def view_plans_handler(client: Client, callback_query: CallbackQuery):
    """Handle viewing available subscription plans."""
    user_id = callback_query.from_user.id
    try:
        # TODO: Implement plan viewing
        await callback_query.answer("Feature not implemented yet", show_alert=True)
        
    except Exception as e:
        log_error_with_context(e, {'handler': 'view_plans_handler', 'user_id': user_id})
        await callback_query.answer("An error occurred", show_alert=True)

@check_user_banned()
async def upgrade_plan_handler(client: Client, callback_query: CallbackQuery):
    """Handle plan upgrade request."""
    user_id = callback_query.from_user.id
    try:
        # Extract plan ID from callback data
        if callback_query.data is None:
            await callback_query.answer("Invalid request", show_alert=True)
            return
            
        # Extract plan ID by removing the prefix
        data_str = str(callback_query.data)
        if data_str.startswith('upgrade_plan_'):
            plan_id = data_str[13:]  # Remove 'upgrade_plan_' prefix
        else:
            plan_id = data_str
        
        # TODO: Implement plan upgrade
        await callback_query.answer("Feature not implemented yet", show_alert=True)
        
    except Exception as e:
        log_error_with_context(e, {'handler': 'upgrade_plan_handler', 'user_id': user_id})
        await callback_query.answer("An error occurred", show_alert=True)

def register_handlers(app: Client):
    """Register subscription handlers."""
    global db, redis, subscription_service
    
    # Get instances from app
    db = getattr(app, 'db', None)
    redis = getattr(app, 'redis', None)
    subscription_service = UserSubscriptionService(db) if db else None
    
    # Register callback handlers using the correct pattern
    app.add_handler(CallbackQueryHandler(subscription_menu_handler, filters.regex("^subscription_menu$")))
    app.add_handler(CallbackQueryHandler(view_plans_handler, filters.regex("^view_plans$")))
    app.add_handler(CallbackQueryHandler(upgrade_plan_handler, filters.regex("^upgrade_plan_")))
    
    logger.info("Subscription handlers registered successfully")