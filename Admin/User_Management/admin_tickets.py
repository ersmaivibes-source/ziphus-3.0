"""
Admin handlers for support ticket management.
Handles viewing, replying to, and managing the status of tickets.
"""

from hydrogram import Client, filters
from hydrogram.types import CallbackQuery, Message
import re
from typing import cast

from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService
from Admin.Support.ticket_service import TicketService
from general.Keyboard.combined_keyboards import CombinedKeyboards
from general.Logging.logger_manager import get_logger, log_error_with_context
from general.Language.Translations import get_text_sync
from Users.Support.conversation_cleanup import ConversationCleanup
from general.Decorators.core_decorators import admin_required

# Initialize logger
logger = get_logger(__name__)

# Global instances to be initialized by register_handlers
db: DatabaseManager
redis: RedisService
cleanup_service: ConversationCleanup
ticket_service: TicketService
keyboards: CombinedKeyboards = CombinedKeyboards()

# --- Entry Point Handlers (Triggered by Callbacks) ---

@admin_required()
async def admin_tickets_handler(client: Client, callback_query: CallbackQuery):
    """Handles the main support tickets menu for admins."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        await callback_query.message.edit_text(
            get_text_sync('admin_support_ticket_management', lang_code),
            reply_markup=keyboards.admin_tickets_menu(lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_tickets_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_open_tickets_handler(client: Client, callback_query: CallbackQuery):
    """Displays a list of open tickets."""
    try:
        admin_id = callback_query.from_user.id
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        # TODO: Implement get_open_tickets method in DatabaseManager
        open_tickets = []  # Placeholder until method is implemented
        
        # Formatting logic should be moved to a formatter if it gets complex
        if not open_tickets:
            message = get_text_sync('admin_open_tickets_title', lang_code)
        else:
            message = get_text_sync('admin_open_tickets_list', lang_code).format(count=len(open_tickets))
            for ticket in open_tickets[:5]: # Show first 5
                message += f"\n- `#{ticket['ID']}`: {ticket['Subject']}"

        await callback_query.message.edit_text(
            message,
            reply_markup=keyboards.admin_back_button(lang_code, 'admin_tickets')
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_open_tickets_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_view_ticket_handler(client: Client, callback_query: CallbackQuery):
    """Displays the details of a specific ticket."""
    try:
        admin_id = callback_query.from_user.id
        # Fix type issue: check if callback_query.data is not None before splitting
        if callback_query.data is None:
            raise ValueError("Callback data is None")
        # Use regex to extract ticket ID instead of split
        match = re.search(r'admin_view_ticket_(\d+)', cast(str, callback_query.data))
        if not match:
            raise ValueError("Invalid callback data format")
        ticket_id = int(match.group(1))
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        # TODO: Fix get_ticket method call - it requires user_id parameter
        ticket = await db.get_ticket(ticket_id, admin_id)  # Placeholder fix
        if not ticket:
            await callback_query.answer("Ticket not found.", show_alert=True)
            return

        messages = await db.get_ticket_messages(ticket_id)
        
        # Formatting logic (can be moved to a formatter)
        ticket_text = f"**Ticket #{ticket_id}**\n\n"
        ticket_text += f"**User:** `{ticket['User_Chat_Id']}`\n"
        ticket_text += f"**Subject:** {ticket['Subject']}\n"
        ticket_text += f"**Status:** {ticket['Status']}\n\n**Messages:**\n"
        for msg in messages:
            sender = "Admin" if msg.get('Is_Admin') else "User"
            ticket_text += f"- **{sender}**: {msg['Message']}\n"

        # Use existing keyboard method
        await callback_query.message.edit_text(
            ticket_text,
            reply_markup=keyboards.admin_ticket_view_keyboard(ticket_id, lang_code)
        )
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_view_ticket_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_reply_ticket_handler(client: Client, callback_query: CallbackQuery):
    """Initiates a reply to a ticket."""
    try:
        admin_id = callback_query.from_user.id
        # Fix type issue: check if callback_query.data is not None before splitting
        if callback_query.data is None:
            raise ValueError("Callback data is None")
        # Use regex to extract ticket ID instead of split
        match = re.search(r'admin_reply_ticket_(\d+)', cast(str, callback_query.data))
        if not match:
            raise ValueError("Invalid callback data format")
        ticket_id = int(match.group(1))
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'
        
        await cleanup_service.start_conversation(admin_id, f'admin_replying_to_ticket_{ticket_id}')
        
        bot_message = await callback_query.message.edit_text(
            get_text_sync('reply_to_ticket_prefix', lang_code) + f" #{ticket_id}\n" + get_text_sync('type_your_reply_message', lang_code),
            reply_markup=keyboards.admin_back_button(lang_code, f'admin_view_ticket_{ticket_id}')
        )
        await cleanup_service.track_bot_message(admin_id, bot_message)
        await callback_query.answer()
    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_reply_ticket_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

@admin_required()
async def admin_close_ticket_handler(client: Client, callback_query: CallbackQuery):
    """Closes a support ticket."""
    try:
        admin_id = callback_query.from_user.id
        # Fix type issue: check if callback_query.data is not None before splitting
        if callback_query.data is None:
            raise ValueError("Callback data is None")
        # Use regex to extract ticket ID instead of split
        match = re.search(r'admin_close_ticket_(\d+)', cast(str, callback_query.data))
        if not match:
            raise ValueError("Invalid callback data format")
        ticket_id = int(match.group(1))
        user = await db.get_user(admin_id)
        lang_code = user.get('Language_Code', 'en') if user else 'en'

        # TODO: Implement close_ticket method in DatabaseManager
        success = False  # Placeholder until method is implemented
        if success:
            logger.info(f'Admin {admin_id} closed ticket {ticket_id}')
            await callback_query.answer(get_text_sync('ticket_closed_successfully', lang_code), show_alert=True)
            # Optionally notify the user
        else:
            await callback_query.answer(get_text_sync('failed_to_close_ticket', lang_code), show_alert=True)

    except Exception as e:
        log_error_with_context(e, {'handler': 'admin_close_ticket_handler'})
        await callback_query.answer(get_text_sync('error_occurred', 'en'), show_alert=True)

# --- Text Input Processor ---

async def handle_ticket_reply(client: Client, message: Message, admin_id: int, 
                            ticket_id: int, reply_text: str, lang_code: str):
    """Processes an admin's reply to a ticket."""
    try:
        await cleanup_service.track_user_message(admin_id, message)
        
        # TODO: Fix get_ticket method call - it requires user_id parameter
        ticket = await db.get_ticket(ticket_id, admin_id)  # Placeholder fix
        if not ticket:
            await message.reply_text("Ticket not found.")
            await cleanup_service.cancel_conversation(admin_id)
            return

        # TODO: Implement add_ticket_message method in DatabaseManager
        success = False  # Placeholder until method is implemented
        
        if success:
            logger.info(f'Admin {admin_id} replied to ticket {ticket_id}')
            # Notify the user about the reply
            # TODO: Fix notify_user_reply method call
            # await ticket_service.notify_user_reply(client, ticket_id, ticket['User_Chat_Id'], reply_text)
            await message.reply_text(get_text_sync('reply_sent_success', lang_code))
        else:
            await message.reply_text("Failed to send reply.")

        await cleanup_service.complete_conversation(admin_id)
    except Exception as e:
        log_error_with_context(e, {'handler': 'handle_ticket_reply'})
        await cleanup_service.cancel_conversation(admin_id)

# --- Registration ---

def register_handlers(app: Client):
    """Registers all handlers for admin ticket management."""
    global db, redis, cleanup_service, ticket_service
    db = app.db  # type: ignore
    redis = app.redis  # type: ignore
    
    from Users.Support.conversation_cleanup import create_cleanup_service
    cleanup_service = create_cleanup_service(redis, app)
    ticket_service = TicketService(db, redis)

    # Register callback handlers
    app.on_callback_query(filters.regex("^admin_tickets$"))(admin_tickets_handler)
    app.on_callback_query(filters.regex("^admin_open_tickets$"))(admin_open_tickets_handler)
    app.on_callback_query(filters.regex("^admin_view_ticket_\\d+$"))(admin_view_ticket_handler)
    app.on_callback_query(filters.regex("^admin_reply_ticket_\\d+$"))(admin_reply_ticket_handler)
    app.on_callback_query(filters.regex("^admin_close_ticket_\\d+$"))(admin_close_ticket_handler)
    # Remove the undefined handler reference
    # app.on_callback_query(filters.regex("^ticket_mark_closed:(.+)$"))(ticket_mark_closed_handler)
    
    logger.info("Admin Ticket Management handlers registered.")