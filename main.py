"""
Main entry point for Ziphus Bot.
Consolidated Hydrogram initialization using libhydrogram architecture.
"""

import asyncio
import signal
import sys
from general.Logging.logger_manager import get_logger, log_error_with_context
from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService

# === libhydrogram IMPORTS - Consolidated Hydrogram Management ===
from libhydrogram.Client.bot_client import BotClient
from libhydrogram.Lifecycle.bot_lifecycle import BotLifecycle
# Using general configuration instead of libhydrogram configuration
# from libhydrogram.Configuration.bot_configuration import BotConfiguration

# Import the new general configuration
from general.Configuration.config_manager import get_core_config

# Initialize logger
logger = get_logger(__name__)

class ZiphusBot:
    """Main bot application class using libhydrogram architecture."""
    
    def __init__(self):
        """Initialize the bot application."""
        # Use general configuration instead of libhydrogram configuration
        self.config = get_core_config()
        self.bot_client = BotClient()
        self.lifecycle = BotLifecycle(self.bot_client)
        self.db = None
        self.redis = None
        self.running = False
        self.shutdown_event = asyncio.Event()
        
    async def initialize(self):
        """Initialize all services and connections using libhydrogram architecture."""
        try:
            # Validate configuration using general configuration
            if not self.config.validate_configuration():
                logger.error("Configuration validation failed")
                return False
            
            logger.info("Configuration validated successfully")
            
            # Initialize database
            self.db = DatabaseManager()
            await self.db.initialize()
            logger.info("Database initialized successfully")
            
            # Initialize Redis
            self.redis = RedisService()
            await self.redis.initialize()
            logger.info("Redis initialized successfully")
            
            # Initialize bot lifecycle with libhydrogram architecture
            if not await self.lifecycle.initialize(self.db, self.redis):
                logger.error("Bot lifecycle initialization failed")
                return False
            
            logger.info("Bot initialized successfully using libhydrogram architecture")
            return True
            
        except Exception as e:
            log_error_with_context(e, {'phase': 'initialization'})
            return False
    
    async def start(self):
        """Start the bot using libhydrogram lifecycle management."""
        try:
            if not await self.lifecycle.start():
                logger.error("Failed to start bot lifecycle")
                return False
            
            self.running = True
            logger.info("Bot started successfully using libhydrogram architecture")
            return True
            
        except Exception as e:
            log_error_with_context(e, {'phase': 'startup'})
            return False
    
    async def run(self):
        """Run the bot using libhydrogram lifecycle."""
        try:
            # Use a more robust approach to keep the bot running
            while self.running and not self.shutdown_event.is_set():
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Bot run loop cancelled")
        except Exception as e:
            log_error_with_context(e, {'phase': 'runtime'})
    
    async def stop(self):
        """Stop the bot gracefully using libhydrogram lifecycle."""
        logger.info("Shutting down bot...")
        self.running = False
        self.shutdown_event.set()
        
        try:
            # Stop libhydrogram lifecycle
            await self.lifecycle.stop()
            
            # Close database connections
            if self.db:
                await self.db.close()
                logger.info("Database connections closed")
            
            # Close Redis connection
            if self.redis:
                await self.redis.close()
                logger.info("Redis connection closed")
                
        except Exception as e:
            log_error_with_context(e, {'phase': 'shutdown'})
        
        logger.info("Bot shutdown complete")


def setup_signal_handlers(bot):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        bot.shutdown_event.set()
        # Create task to handle async shutdown
        asyncio.create_task(bot.stop())
    
    # Handle SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point using libhydrogram architecture."""
    bot = ZiphusBot()
    
    try:
        if not await bot.initialize():
            logger.error("Failed to initialize bot. Exiting.")
            sys.exit(1)
        
        setup_signal_handlers(bot)
        
        logger.info("Starting Ziphus Bot with libhydrogram architecture...")
        if not await bot.start():
            logger.error("Failed to start bot. Exiting.")
            sys.exit(1)
        
        logger.info("Bot startup completed - ready to receive messages")
        
        # Run the bot
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        log_error_with_context(e, {'phase': 'main'})
        sys.exit(1)
    finally:
        if bot.running:
            await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        log_error_with_context(e, {'phase': 'entry_point'})
        sys.exit(1)