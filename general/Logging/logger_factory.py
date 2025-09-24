"""
📊 Logs - Logger Factory (Compatibility Layer)
Enterprise-grade logging factory for Ziphus Bot v3.2

Provides backward compatibility by redirecting to the new general logging system.
"""

from general.Logging.logger_manager import get_logger, CoreLoggerManager

class LoggerFactory:
    """
    Logger Factory (Compatibility Layer)
    
    Provides backward compatibility by redirecting to the new general logging system.
    """
    
    _loggers = {}
    _configured = True  # Already configured by general logger
    
    @classmethod
    def configure(cls, log_level: str = "INFO", log_dir: str = None):
        """Configure the logging system (backward compatibility)."""
        # Configuration is handled by general logger, so this is a no-op
        pass
    
    @classmethod
    def get_logger(cls, name: str):
        """Get or create a logger for the specified name."""
        if name not in cls._loggers:
            # Use the general logger manager
            cls._loggers[name] = get_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, name: str, level: str):
        """Set the logging level for a specific logger."""
        logger = cls.get_logger(name)
        # general logger uses different method for setting level
        # This is a simplified implementation for backward compatibility
        pass
    
    @classmethod
    def get_all_loggers(cls):
        """Get all created loggers."""
        return cls._loggers.copy()
