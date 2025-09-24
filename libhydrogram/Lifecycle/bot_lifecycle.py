"""
Bot Lifecycle Management
=======================

Consolidates bot start, stop, and session management from main.py.
"""

import asyncio
import signal
from hydrogram import idle
from hydrogram.errors import FloodWait
from typing import Optional, Callable, Dict, Any, List

from general.Logging.logger_manager import get_logger, log_error_with_context
from libhydrogram.Client.bot_client import BotClient
from libhydrogram.Handlers.handler_registry import HandlerRegistry

# Initialize logger
logger = get_logger(__name__)

class BotLifecycle:
    """Manages the complete bot lifecycle."""
    
    def __init__(self, bot_client: BotClient):
        """Initialize lifecycle manager."""
        self.bot_client = bot_client
        self.handler_registry: Optional[HandlerRegistry] = None
        self.running = False
        self._shutdown_callbacks: List[Callable] = []
        self._startup_callbacks: List[Callable] = []
    
    async def initialize(self, db_manager, redis_service) -> bool:
        """
        Initialize the bot lifecycle.
        
        Args:
            db_manager: Database manager instance
            redis_service: Redis service instance
            
        Returns:
            bool: Success status
        """
        try:
            # Initialize bot client
            if not await self.bot_client.initialize(db_manager, redis_service):
                logger.error("Failed to initialize bot client")
                return False
            
            # Initialize handler registry
            client = self.bot_client.client
            if client is None:
                logger.error("Bot client not available for handler registry")
                return False
            self.handler_registry = HandlerRegistry(client)
            
            # Register all handlers
            self.handler_registry.register_all_handlers()
            
            # Validate registration
            if not self.handler_registry.validate_registration():
                logger.error("Handler registration validation failed")
                return False
            
            logger.info("Bot lifecycle initialized successfully")
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'lifecycle_initialization'})
            return False
    
    async def start(self) -> bool:
        """
        Start the bot and all services.
        
        Returns:
            bool: Success status
        """
        try:
            # Execute startup callbacks
            await self._execute_callbacks(self._startup_callbacks, 'startup')
            
            # Start the bot client
            if not await self.bot_client.start():
                logger.error("Failed to start bot client")
                return False
            
            self.running = True
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            client = self.bot_client.client
            if client is not None:
                bot_info = await client.get_me()
                logger.info(f"Bot lifecycle started: @{bot_info.username} ({bot_info.id})")
            
            return True
            
        except FloodWait as e:
            wait_time = getattr(e, 'value', 1)
            try:
                wait_seconds = float(wait_time)
                logger.warning(f"FloodWait during startup: sleeping for {wait_seconds} seconds")
                await asyncio.sleep(wait_seconds)
            except (ValueError, TypeError):
                logger.warning(f"FloodWait during startup: sleeping for 1 second (invalid wait time: {wait_time})")
                await asyncio.sleep(1.0)
            return await self.start()  # Retry
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'lifecycle_start'})
            return False
    
    async def run(self):
        """Run the bot until stopped."""
        try:
            if not self.running:
                logger.error("Bot not started before run")
                return
            
            logger.info("Bot is now running and ready to receive messages")
            
            # Keep the bot running
            await idle()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            log_error_with_context(e, {'operation': 'lifecycle_run'})
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot gracefully."""
        if not self.running:
            return
        
        logger.info("Initiating bot shutdown...")
        self.running = False
        
        try:
            # Execute shutdown callbacks
            await self._execute_callbacks(self._shutdown_callbacks, 'shutdown')
            
            # Stop bot client
            await self.bot_client.stop()
            
            logger.info("Bot lifecycle shutdown complete")
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'lifecycle_stop'})
    
    def add_startup_callback(self, callback: Callable):
        """Add a callback to be executed during startup."""
        self._startup_callbacks.append(callback)
        logger.info(f"Added startup callback: {callback.__name__}")
    
    def add_shutdown_callback(self, callback: Callable):
        """Add a callback to be executed during shutdown."""
        self._shutdown_callbacks.append(callback)
        logger.info(f"Added shutdown callback: {callback.__name__}")
    
    async def _execute_callbacks(self, callbacks: List[Callable], phase: str):
        """Execute a list of callbacks."""
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
                logger.debug(f"Executed {phase} callback: {callback.__name__}")
            except Exception as e:
                log_error_with_context(e, {
                    'operation': f'{phase}_callback',
                    'callback': callback.__name__
                })
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            # Create a task to handle the async stop method
            loop = asyncio.get_event_loop()
            loop.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        logger.info("Signal handlers configured")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current lifecycle status."""
        return {
            'running': self.running,
            'client_connected': self.bot_client.is_connected if self.bot_client else False,
            'handlers_registered': self.handler_registry is not None,
            'startup_callbacks': len(self._startup_callbacks),
            'shutdown_callbacks': len(self._shutdown_callbacks)
        }
    
    async def restart(self):
        """Restart the bot gracefully."""
        logger.info("Initiating bot restart...")
        
        if self.running:
            await self.stop()
        
        # Small delay to ensure clean shutdown
        await asyncio.sleep(1)
        
        await self.start()
        logger.info("Bot restart completed")