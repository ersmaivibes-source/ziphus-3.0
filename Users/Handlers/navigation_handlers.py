"""
Navigation Handlers
==================

Handlers for navigation-related commands and callbacks.
"""

from hydrogram import Client, filters
from hydrogram.types import Message, CallbackQuery
import logging

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config
from general.Keyboard.combined_keyboards import keyboards
from general.Decorators.core_decorators import check_user_banned, error_handler
from general.Database.MySQL.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
core_config = get_core_config()

@Client.on_message(filters.command("start"))
@check_user_banned
@error_handler
async def start_command(client: Client, message: Message):
    """Handle /start command."""
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name or "User"
        
        # Create or update user in database
        await DatabaseManager.create_user(
            chat_id=user_id,
            first_name=first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code
        )
        
        # Update login info
        await DatabaseManager.update_login_info(user_id)
        
        # Send welcome message with keyboard
        welcome_text = f"Welcome, {first_name}! 👋\n\n"
        welcome_text += "I'm your personal assistant bot. How can I help you today?"
        
        await message.reply_text(
            welcome_text,
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply_text("Sorry, an error occurred. Please try again.")

@Client.on_message(filters.command("help"))
@check_user_banned
@error_handler
async def help_command(client: Client, message: Message):
    """Handle /help command."""
    try:
        help_text = (
            "🤖 **Bot Help**\n\n"
            "Here are the available commands:\n\n"
            "• /start - Start the bot\n"
            "• /help - Show this help message\n"
            "• /settings - Open settings menu\n"
            "• /profile - View your profile\n\n"
            "For more information, please contact support."
        )
        
        await message.reply_text(
            help_text,
            reply_markup=keyboards.get_back_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await message.reply_text("Sorry, an error occurred. Please try again.")

@Client.on_callback_query(filters.regex("^main_menu$"))
@check_user_banned
@error_handler
async def main_menu_callback(client: Client, callback_query: CallbackQuery):
    """Handle main menu callback."""
    try:
        await callback_query.answer()
        
        welcome_text = "🏠 **Main Menu**\n\n"
        welcome_text += "Please select an option below:"
        
        await callback_query.message.edit_text(
            welcome_text,
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in main menu callback: {e}")
        await callback_query.answer("An error occurred!", show_alert=True)

@Client.on_callback_query(filters.regex("^back$"))
@check_user_banned
@error_handler
async def back_callback(client: Client, callback_query: CallbackQuery):
    """Handle back callback."""
    try:
        await callback_query.answer()
        
        # For now, just go back to main menu
        # In a real implementation, you might want to track navigation history
        welcome_text = "🏠 **Main Menu**\n\n"
        welcome_text += "Please select an option below:"
        
        await callback_query.message.edit_text(
            welcome_text,
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in back callback: {e}")
        await callback_query.answer("An error occurred!", show_alert=True)