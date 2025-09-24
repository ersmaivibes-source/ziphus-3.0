"""Ticket handlers for user-facing support ticket interactions.
Handles ticket creation, viewing, and user responses.
"""

from hydrogram import Client, filters
from hydrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from hydrogram.handlers import CallbackQueryHandler
import asyncio
from typing import Dict, Optional

from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService
from Admin.Support.ticket_service import TicketService
from general.Keyboard.combined_keyboards import keyboards
from general.Logging.logger_manager import get_logger, log_user_action, log_error_with_context
from general.Language.Translations import get_text_sync
from Users.Support.conversation_cleanup import create_cleanup_service

# Import the NEW and secure decorator
from general.Decorators.core_decorators import check_user_banned
# Import the NEW and optimized utility
from general.Base.base_classes import SafeHandlerUtils, SecurityUtils

# Initialize logger
logger = get_logger(__name__)

# Global instances
db: Optional[DatabaseManager] = None
redis: Optional[RedisService] = None
ticket_service: Optional[TicketService] = None
cleanup_service = None
# Using global keyboards instance from combined_keyboards

@check_user_banned()
@SafeHandlerUtils.inject_user_and_lang
async def support_tickets_handler(client: Client, callback_query: CallbackQuery, user: Optional[Dict], lang_code: str, **kwargs):
    """Handle support tickets main menu."""
    user_id = callback_query.from_user.id
    try:
        log_user_action(user_id, 'accessed_support_tickets')
        await callback_query.message.edit_text(
            get_text_sync('support_tickets_main_text', lang_code),
            reply_markup=keyboards.user_kb.settings_account_menu(lang_code)  # Using settings_account_menu as fallback
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'support_tickets_handler', 'user_id': user_id})
        await callback_query.answer(get_text_sync('error_occurred', lang_code), show_alert=True)

@check_user_banned()
@SafeHandlerUtils.inject_user_and_lang
async def create_ticket_handler(client: Client, callback_query: CallbackQuery, user: Optional[Dict], lang_code: str, **kwargs):
    """Handle ticket creation initiation."""
    user_id = callback_query.from_user.id
    try:
        # Create a simple ticket category keyboard as fallback
        buttons = [
            [InlineKeyboardButton(get_text_sync('general_inquiry', lang_code), callback_data='ticket_category_general')],
            [InlineKeyboardButton(get_text_sync('technical_support', lang_code), callback_data='ticket_category_technical')],
            [InlineKeyboardButton(get_text_sync('billing_issue', lang_code), callback_data='ticket_category_billing')],
            [keyboards.user_kb.back_button_inline(lang_code, 'support_tickets')]
        ]
        
        await callback_query.message.edit_text(
            get_text_sync('select_ticket_category', lang_code),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'create_ticket_handler', 'user_id': user_id})
        await callback_query.answer(get_text_sync('error_occurred', lang_code), show_alert=True)

@check_user_banned()
@SafeHandlerUtils.inject_user_and_lang
async def my_tickets_handler(client: Client, callback_query: CallbackQuery, user: Optional[Dict], lang_code: str, **kwargs):
    """Handle my tickets display."""
    user_id = callback_query.from_user.id
    try:
        if db is None:
            raise RuntimeError("Database not initialized")
            
        tickets = await db.get_user_tickets(user_id, 10)
        
        if not tickets:
            await callback_query.message.edit_text(
                get_text_sync('no_tickets_found', lang_code),
                reply_markup=keyboards.user_kb.settings_account_menu(lang_code)
            )
            await callback_query.answer()
            return
        
        message = f"🎫 **{get_text_sync('your_tickets', lang_code)}**\n\n"
        buttons = []
        
        for ticket in tickets:
            status_emoji = {'open': '🟢', 'in_progress': '🟡', 'closed': '🔴'}.get(ticket['Status'], '⚪')
            buttons.append([InlineKeyboardButton(
                f"{status_emoji} #{ticket['ID']} - {ticket['Subject'][:30]}",
                callback_data=f"view_ticket_{ticket['ID']}"
            )])
        
        buttons.append([InlineKeyboardButton(get_text_sync('create_new_ticket', lang_code), callback_data='create_ticket')])
        buttons.append([keyboards.user_kb.back_button_inline(lang_code, 'support_tickets')])
        
        await callback_query.message.edit_text(message, reply_markup=InlineKeyboardMarkup(buttons))
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'my_tickets_handler', 'user_id': user_id})
        await callback_query.answer(get_text_sync('error_occurred', lang_code), show_alert=True)

async def handle_ticket_text(client: Client, message: Message, user_id: int, text: str, lang_code: str, state_data: dict):
    """Handle text input for ticket operations."""
    state = state_data.get('state')
    
    if state == 'ticket_subject_input':
        await handle_ticket_subject_input(client, message, user_id, text, lang_code)
    elif state == 'ticket_message_input':
        await handle_ticket_message_input(client, message, user_id, text, lang_code)

async def handle_ticket_subject_input(client: Client, message: Message, user_id: int, subject: str, lang_code: str):
    """Handle ticket subject input."""
    try:
        if cleanup_service is None:
            raise RuntimeError("Cleanup service not initialized")
            
        await cleanup_service.track_user_message(user_id, message)
        
        if not (5 <= len(subject.strip()) <= 100):
            error_key = 'subject_too_short' if len(subject.strip()) < 5 else 'subject_too_long'
            error_msg = await message.reply_text(get_text_sync(error_key, lang_code))
            await cleanup_service.handle_input_error(
                user_id, error_msg, get_text_sync('enter_ticket_subject', lang_code),
                reply_markup=keyboards.user_kb.cancel_button(lang_code, 'support_tickets')
            )
            return

        if redis is None:
            raise RuntimeError("Redis service not initialized")
            
        state_data = await redis.get_user_state(user_id)
        if state_data is None:
            category = 'general'
        else:
            category = state_data.get('category', 'general')
        
        # Create ticket
        if db is None:
            raise RuntimeError("Database not initialized")
            
        if ticket_service is None:
            raise RuntimeError("Ticket service not initialized")
            
        ticket_id = await db.create_ticket(user_id, category, subject, subject)
        
        if ticket_id:
            await cleanup_service.complete_conversation(user_id)
            success_msg = get_text_sync('ticket_created_successfully', lang_code, ticket_id=ticket_id)
            await message.reply_text(success_msg, reply_markup=keyboards.user_kb.settings_account_menu(lang_code))
            log_user_action(user_id, 'ticket_created', {'ticket_id': ticket_id, 'category': category})
        else:
            error_msg = await message.reply_text(get_text_sync('ticket_creation_failed', lang_code))
            await cleanup_service.handle_input_error(
                user_id, error_msg, get_text_sync('enter_ticket_subject', lang_code),
                reply_markup=keyboards.user_kb.cancel_button(lang_code, 'support_tickets')
            )
            
    except Exception as e:
        log_error_with_context(e, {'handler': 'handle_ticket_subject_input', 'user_id': user_id})

async def handle_ticket_message_input(client: Client, message: Message, user_id: int, text: str, lang_code: str):
    """Handle ticket message input."""
    try:
        if cleanup_service is None:
            raise RuntimeError("Cleanup service not initialized")
            
        await cleanup_service.track_user_message(user_id, message)
        
        if not (10 <= len(text.strip()) <= 1000):
            error_key = 'message_too_short' if len(text.strip()) < 10 else 'message_too_long'
            error_msg = await message.reply_text(get_text_sync(error_key, lang_code))
            await cleanup_service.handle_input_error(
                user_id, error_msg, get_text_sync('enter_ticket_message', lang_code),
                reply_markup=keyboards.user_kb.cancel_button(lang_code, 'my_tickets')
            )
            return

        if redis is None:
            raise RuntimeError("Redis service not initialized")
            
        state_data = await redis.get_user_state(user_id)
        if state_data is None:
            ticket_id = None
        else:
            ticket_id = state_data.get('ticket_id')
        
        if not ticket_id:
            await message.reply_text(get_text_sync('invalid_ticket', lang_code))
            return
        
        # Add message to ticket
        if db is None:
            raise RuntimeError("Database not initialized")
            
        success = await db.add_ticket_message(ticket_id, user_id, text, False)
        
        if success:
            await cleanup_service.complete_conversation(user_id)
            success_msg = get_text_sync('message_added_successfully', lang_code)
            await message.reply_text(success_msg, reply_markup=keyboards.user_kb.settings_account_menu(lang_code))
            log_user_action(user_id, 'ticket_message_added', {'ticket_id': ticket_id})
        else:
            error_msg = await message.reply_text(get_text_sync('message_add_failed', lang_code))
            await cleanup_service.handle_input_error(
                user_id, error_msg, get_text_sync('enter_ticket_message', lang_code),
                reply_markup=keyboards.user_kb.cancel_button(lang_code, 'my_tickets')
            )
            
    except Exception as e:
        log_error_with_context(e, {'handler': 'handle_ticket_message_input', 'user_id': user_id})

def register_handlers(app: Client):
    """Register ticket handlers."""
    global db, redis, ticket_service, cleanup_service
    
    # Get instances from app (assuming they're attached to the app object)
    db = getattr(app, 'db', None)
    redis = getattr(app, 'redis', None)
    ticket_service = TicketService(db) if db is not None else None
    cleanup_service = create_cleanup_service(redis, app)
    
    # Register callback handlers using the correct syntax
    app.add_handler(CallbackQueryHandler(support_tickets_handler, filters.regex("support_tickets")))
    app.add_handler(CallbackQueryHandler(create_ticket_handler, filters.regex("create_ticket")))
    app.add_handler(CallbackQueryHandler(my_tickets_handler, filters.regex("my_tickets")))
    
    logger.info("Ticket handlers registered successfully")