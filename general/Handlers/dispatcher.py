"""
Central dispatcher for handling messages and callbacks based on user state.
Routes messages to appropriate handlers using registry pattern to avoid conflicts.
"""

from hydrogram import Client, filters
from hydrogram.types import Message, CallbackQuery
from typing import Dict, Callable, Any

from general.Caching.redis_service import RedisService
from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger, log_error_with_context

logger = get_logger(__name__)
from Language.Translations import get_text, get_text_sync
from common.base import ErrorHandler, MessageUtils

# Global instances
db: DatabaseManager = None
redis: RedisService = None

# Central handler registries
HANDLER_REGISTRY: Dict[str, Callable] = {}
CALLBACK_REGISTRY: Dict[str, Callable] = {}
STATE_PATTERNS: Dict[str, str] = {}

def register_text_handler(states: list, handler_func: Callable, module_name: str = None):
    """Register a text handler for specific states."""
    for state in states:
        HANDLER_REGISTRY[state] = handler_func
        if module_name:
            STATE_PATTERNS[state] = module_name
    logger.info(f"Registered text handler for states: {states}")

def register_callback_handler(prefixes: list, handler_func: Callable, module_name: str = None):
    """Register a callback handler for specific prefixes."""
    for prefix in prefixes:
        CALLBACK_REGISTRY[prefix] = handler_func
        if module_name:
            STATE_PATTERNS[prefix] = module_name
    logger.info(f"Registered callback handler for prefixes: {prefixes}")

# Initialize handler registries
def initialize_handler_registries():
    """Initialize all handler registries with current handlers."""
    try:
        # Import handlers dynamically to avoid circular imports
        from Users.Handlers.onboarding_handlers import handle_onboarding_text
        from Users.Support.ticket_handlers import handle_ticket_text
        
        # Register text handlers by state
        register_text_handler(
            ['awaiting_email', 'awaiting_password', 'awaiting_verification', 
             'signin_email', 'signin_password', 'changing_email', 
             'verify_current_password', 'enter_new_password', 'verify_email_change'],
            handle_onboarding_text,
            'onboarding'
        )
        
        register_text_handler(
            ['ticket_subject_input', 'ticket_message_input'],
            handle_ticket_text,
            'ticket'
        )
        
        logger.info("Handler registries initialized successfully")
        
    except Exception as e:
        log_error_with_context(e, {'context': 'initialize_handler_registries'})

async def message_dispatcher(client: Client, message: Message):
    """
    Central dispatcher for text messages based on user state using registry pattern.
    """
    user_id = message.chat.id
    
    try:
        text = message.text.strip() if message.text else ""
        
        # Handle forwarded messages for admin processing
        if message.forward_from_chat:
            forwarded_chat_id = message.forward_from_chat.id
            if not text:
                text = str(forwarded_chat_id)
            else:
                text += f" (Forwarded from: {forwarded_chat_id})"
        
        logger.debug(f"Message received from {user_id}: '{text[:100]}...'")
        
        # Get user's current state
        state_data = await redis.get_user_state(user_id) if redis else None
        
        if not state_data or not state_data.get('state'):
            logger.debug(f"No state found for user {user_id}, skipping dispatcher")
            return

        state = state_data['state']
        logger.debug(f"Routing state '{state}' for user {user_id}")

        # Get user language
        user = await db.get_user(user_id) if db else None
        lang_code = user.get('Language_Code', 'en') if user else 'en'

        # Route to appropriate handler using registry
        handler_func = None
        
        # Check exact state match first
        if state in HANDLER_REGISTRY:
            handler_func = HANDLER_REGISTRY[state]
        # Check pattern matches for admin states
        elif state.startswith('admin_'):
            # Find the most specific admin handler that matches this state
            best_match = None
            best_match_length = 0
            
            for registered_state, func in HANDLER_REGISTRY.items():
                if registered_state.startswith('admin_'):
                    if (state.startswith(registered_state) or 
                        registered_state in ['admin_user_search', 'admin_ban_reason', 
                                           'admin_broadcast_message', 'admin_analytics_query', 
                                           'admin_chat_search']):
                        if len(registered_state) > best_match_length:
                            best_match = func
                            best_match_length = len(registered_state)
            
            handler_func = best_match
        
        if handler_func:
            logger.debug(f"Calling handler for state '{state}'")
            await handler_func(client, message, user_id, text, lang_code, state_data)
        else:
            logger.warning(f"No handler registered for state: {state} (user {user_id})")
            # Clear invalid state
            if redis:
                await redis.clear_user_state(user_id)
            
    except Exception as e:
        log_error_with_context(e, {
            'handler': 'message_dispatcher', 
            'user_id': user_id,
            'state': state_data.get('state') if 'state_data' in locals() and state_data else None
        })

async def callback_dispatcher(client: Client, callback_query: CallbackQuery):
    """
    Central dispatcher for callback queries based on callback data patterns.
    """
    user_id = callback_query.from_user.id
    callback_data = callback_query.data
    
    try:
        logger.debug(f"Callback received from {user_id}: '{callback_data}'")
        
        # Find appropriate handler based on callback prefix
        handler_func = None
        matched_prefix = None
        
        for prefix, func in CALLBACK_REGISTRY.items():
            if callback_data and callback_data.startswith(prefix):
                handler_func = func
                matched_prefix = prefix
                break
        
        if handler_func:
            logger.debug(f"Calling callback handler for prefix '{matched_prefix}'")
            await handler_func(client, callback_query)
        else:
            logger.debug(f"No callback handler found for: {callback_data}")
            # Let other handlers process it
            
    except Exception as e:
        log_error_with_context(e, {
            'handler': 'callback_dispatcher',
            'user_id': user_id,
            'callback_data': callback_data
        })

def register_dispatcher(app: Client):
    """Register the central dispatchers."""
    global db, redis
    
    # Get instances from app
    db = app.db
    redis = app.redis
    
    # Initialize handler registries
    initialize_handler_registries()
    
    # Register message dispatcher for text messages
    app.add_handler(filters.text & filters.private)(message_dispatcher)
    
    logger.info("Central dispatcher registered successfully")