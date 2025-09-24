"""
Hydrogram Bot Client Management
=============================

Consolidated client initialization and configuration management.
Moved from main.py and various service files.
"""

from hydrogram import Client
from hydrogram.errors import FloodWait
import asyncio
from typing import Optional, Any

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config
from general.Logging.logger_manager import get_logger, log_error_with_context
from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService

# Get the general configuration
core_config = get_core_config()

# Initialize logger
logger = get_logger(__name__)

class BotClient:
    """Centralized Hydrogram Client management for the bot."""
    
    def __init__(self):
        """Initialize the bot client."""
        self.app: Optional[Client] = None
        self.db: Optional[DatabaseManager] = None
        self.redis: Optional[RedisService] = None
        self._initialized = False
        self._connected = False
    
    async def initialize(self, db: DatabaseManager, redis: RedisService) -> bool:
        """
        Initialize the Hydrogram client with services.
        
        Args:
            db: Database manager instance
            redis: Redis service instance
            
        Returns:
            bool: Success status
        """
        try:
            self.db = db
            self.redis = redis
            
            # Initialize Hydrogram client using general configuration
            client_params = core_config.telegram.get_client_params()
            self.app = Client(**client_params)
            
            # Attach services to app for handlers to access
            # We'll store them in a way that can be accessed later
            if self.app:
                # Dynamically add attributes to the client instance
                # This is the pattern used in the original code
                self.app.db = self.db  # type: ignore
                self.app.redis = self.redis  # type: ignore
            
            self._initialized = True
            logger.info("Hydrogram client initialized successfully")
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'client_initialization'})
            return False
    
    async def start(self) -> bool:
        """
        Start the Hydrogram client.
        
        Returns:
            bool: Success status
        """
        if not self._initialized:
            logger.error("Client not initialized before start")
            return False
        
        if not self.app:
            logger.error("Client app not initialized")
            return False
        
        try:
            await self.app.start()
            self._connected = True
            
            bot_info = await self.app.get_me()
            logger.info(f"Bot started successfully: @{bot_info.username} ({bot_info.id})")
            return True
            
        except FloodWait as e:
            # Handle the case where e.value might not be a number
            wait_time = getattr(e, 'value', 1)
            try:
                wait_seconds = float(wait_time)
                logger.warning(f"FloodWait on startup: sleeping for {wait_seconds} seconds")
                await asyncio.sleep(wait_seconds)
            except (ValueError, TypeError):
                logger.warning(f"FloodWait on startup: sleeping for 1 second (invalid wait time: {wait_time})")
                await asyncio.sleep(1.0)
            return await self.start()  # Retry
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'client_start'})
            return False
    
    async def stop(self) -> bool:
        """
        Stop the Hydrogram client gracefully.
        
        Returns:
            bool: Success status
        """
        try:
            if self.app and self._connected:
                await self.app.stop()
                self._connected = False
                logger.info("Hydrogram client stopped successfully")
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'client_stop'})
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        if not self.app:
            return False
        try:
            return bool(self._connected and self.app.is_connected)
        except AttributeError:
            return False
    
    @property
    def client(self) -> Optional[Client]:
        """Get the Hydrogram client instance."""
        return self.app
    
    def attach_services(self, **services):
        """Attach additional services to the client."""
        if self.app:
            for name, service in services.items():
                setattr(self.app, name, service)
                logger.debug(f"Attached service '{name}' to client")