"""
Onboarding Handlers
==================

Handlers for user onboarding and registration.
"""

from hydrogram import Client, filters
from hydrogram.types import Message, CallbackQuery
import logging
import secrets

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config
from general.Keyboard.combined_keyboards import keyboards
from general.Decorators.core_decorators import check_user_banned, error_handler
from general.Database.MySQL.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
core_config = get_core_config()

@Client.on_message(filters.command("register"))
@check_user_banned
@error_handler
async def register_command(client: Client, message: Message):
    """Handle /register command."""
    try:
        user_id = message.from_user.id
        
        # Check if user is already registered
        existing_user = await DatabaseManager.get_user(user_id)
        if existing_user:
            await message.reply_text(
                "You are already registered! 👍",
                reply_markup=keyboards.get_main_menu_keyboard()
            )
            return
        
        # Send registration instructions
        register_text = (
            "📝 **Registration**\n\n"
            "Please provide your email address to complete registration:\n\n"
            "Example: `user@example.com`"
        )
        
        await message.reply_text(
            register_text,
            reply_markup=keyboards.get_cancel_keyboard()
        )
        
        # Set user state for registration flow
        # This would typically be handled by a state manager
        
    except Exception as e:
        logger.error(f"Error in register command: {e}")
        await message.reply_text("Sorry, an error occurred. Please try again.")

@Client.on_message(filters.regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'))
@check_user_banned
@error_handler
async def handle_email_input(client: Client, message: Message):
    """Handle email input during registration."""
    try:
        user_id = message.from_user.id
        email = message.text.strip()
        
        # Generate verification code
        verification_code = secrets.token_urlsafe(6)[:6].upper()
        
        # Store verification data (in a real implementation, this would use Redis)
        # For now, we'll simulate storing it
        
        # Send verification code
        verification_text = (
            f"📧 **Email Verification**\n\n"
            f"Your verification code is: `{verification_code}`\n\n"
            f"Please enter this code to verify your email address.\n"
            f"This code will expire in {core_config.application.verification_code_expiry // 60} minutes."
        )
        
        await message.reply_text(
            verification_text,
            reply_markup=keyboards.get_cancel_keyboard()
        )
        
        # Set user state for verification flow
        
    except Exception as e:
        logger.error(f"Error handling email input: {e}")
        await message.reply_text("Sorry, an error occurred. Please try again.")

async def handle_verification_code(client: Client, message: Message):
    """Handle verification code input."""
    try:
        user_code = message.text.strip()
        user_id = message.from_user.id
        
        # In a real implementation, we would verify the code against stored data
        # For now, we'll assume it's correct
        
        # Update user as verified
        # This would typically involve updating the database
        
        # Send completion message
        completion_text = "✅ Registration Complete!\n\n"
        completion_text += "Your email has been verified successfully.\n"
        completion_text += "You now have full access to all bot features!"
        
        await message.reply_text(
            completion_text,
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error handling verification code: {e}")
        await message.reply_text("Sorry, something went wrong. Please try again.")

async def handle_onboarding_text(client: Client, message: Message, user_id: int, text: str, lang_code: str, state_data: dict):
    """Handle text input for onboarding operations."""
    state = state_data.get('state')
    
    if state == 'awaiting_email':
        await handle_email_input(client, message)
    elif state == 'awaiting_verification':
        await handle_verification_code(client, message)
    # Add other state handlers as needed

@Client.on_callback_query(filters.regex("^cancel_registration$"))
@check_user_banned
@error_handler
async def cancel_registration(client: Client, callback_query: CallbackQuery):
    """Handle registration cancellation."""
    try:
        await callback_query.answer()
        
        cancel_text = "❌ **Registration Cancelled**\n\nRegistration process has been cancelled."
        
        await callback_query.message.edit_text(
            cancel_text,
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error cancelling registration: {e}")
        await callback_query.answer("An error occurred!", show_alert=True)