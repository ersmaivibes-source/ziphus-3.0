"""
general Configuration Management
============================

Enhanced configuration management consolidating functionality from:
- config.py
- libhydrogram/Configuration/bot_configuration.py
- Security/Configuration/security_config.py

Moved to general for basic/general task consolidation.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from general.Logging.logger_manager import get_logger

logger = get_logger(__name__)


@dataclass
class CoreTelegramConfig:
    """general Telegram configuration."""
    api_id: int = 0
    api_hash: str = ""
    bot_token: str = ""
    session_name: str = "ziphus_bot"
    
    def __post_init__(self):
        """Validate Telegram configuration."""
        # Load from environment variables
        self.api_id = int(os.getenv('API_ID', '0')) or self.api_id
        self.api_hash = os.getenv('API_HASH', '') or self.api_hash
        self.bot_token = os.getenv('BOT_TOKEN', '') or self.bot_token
        self.session_name = os.getenv('SESSION_NAME', 'ziphus_bot') or self.session_name
        
        # Validate
        if not self.api_id or self.api_id == 0:
            raise ValueError("API_ID is required and must be non-zero")
        if not self.api_hash:
            raise ValueError("API_HASH is required")
        if not self.bot_token:
            raise ValueError("BOT_TOKEN is required")
        if not self.session_name:
            raise ValueError("SESSION_NAME is required")
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False
    
    def get_client_params(self) -> Dict[str, Any]:
        """Get parameters for Hydrogram Client initialization."""
        return {
            'name': self.session_name,
            'api_id': self.api_id,
            'api_hash': self.api_hash,
            'bot_token': self.bot_token
        }


@dataclass
class CoreDatabaseConfig:
    """general database configuration."""
    host: str = "127.0.0.1"
    port: int = 3306
    database: str = ""
    user: str = ""
    password: str = ""
    charset: str = "utf8mb4"
    pool_size: int = 10
    pool_max_overflow: int = 20
    
    def __post_init__(self):
        """Validate database configuration."""
        # Load from environment variables
        self.host = os.getenv('DB_HOST', '127.0.0.1') or self.host
        self.port = int(os.getenv('DB_PORT', '3306')) or self.port
        self.database = os.getenv('DB_DATABASE', '') or self.database
        self.user = os.getenv('DB_USER', '') or self.user
        self.password = os.getenv('DB_PASSWORD', '') or self.password
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4') or self.charset
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '10')) or self.pool_size
        self.pool_max_overflow = int(os.getenv('DB_POOL_MAX_OVERFLOW', '20')) or self.pool_max_overflow
        
        if not self.database:
            raise ValueError("Database name is required")
        if not self.user:
            raise ValueError("Database user is required")
        if not self.password:
            raise ValueError("Database password is required")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Database port must be between 1 and 65535")
    
    @property
    def connection_string(self) -> str:
        """Generate database connection string."""
        return f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class CoreRedisConfig:
    """general Redis configuration."""
    host: str = "127.0.0.1"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    def __post_init__(self):
        """Validate Redis configuration."""
        # Load from environment variables
        self.host = os.getenv('REDIS_HOST', '127.0.0.1') or self.host
        self.port = int(os.getenv('REDIS_PORT', '6379')) or self.port
        self.db = int(os.getenv('REDIS_DB', '0')) or self.db
        self.password = os.getenv('REDIS_PASSWORD') or self.password
        
        if not self.host:
            raise ValueError("Redis host is required")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Redis port must be between 1 and 65535")
        if self.db < 0 or self.db > 15:
            raise ValueError("Redis DB must be between 0 and 15")


@dataclass
class CoreApplicationConfig:
    """general application configuration."""
    environment: str = "development"
    debug_mode: bool = False
    log_level: str = "INFO"
    verification_code_expiry: int = 600  # 10 minutes
    session_expiry: int = 3600  # 1 hour
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate application configuration."""
        # Load from environment variables
        self.environment = os.getenv('ENVIRONMENT', 'development') or self.environment
        self.debug_mode = os.getenv('DEBUG', 'false').lower() == 'true' or self.debug_mode
        self.log_level = os.getenv('LOG_LEVEL', 'INFO') or self.log_level
        self.verification_code_expiry = int(os.getenv('VERIFICATION_CODE_EXPIRY', '600')) or self.verification_code_expiry
        self.session_expiry = int(os.getenv('SESSION_EXPIRY', '3600')) or self.session_expiry
        self.max_retries = int(os.getenv('MAX_RETRIES', '3')) or self.max_retries
        self.retry_delay = float(os.getenv('RETRY_DELAY', '1.0')) or self.retry_delay
        
        valid_environments = ["development", "staging", "production"]
        if self.environment not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"Log level must be one of: {valid_log_levels}")
        
        if self.verification_code_expiry <= 0:
            raise ValueError("Verification code expiry must be positive")
        
        if self.session_expiry <= 0:
            raise ValueError("Session expiry must be positive")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == 'production'
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == 'development'


@dataclass
class CoreSecurityConfig:
    """general security configuration."""
    max_file_size_mb: int = 50
    allowed_file_extensions: List[str] = field(default_factory=lambda: [
        'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp4', 'mp3'
    ])
    max_text_length: int = 4096
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    def __post_init__(self):
        """Validate security configuration."""
        # Load from environment variables
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '50')) or self.max_file_size_mb
        extensions_str = os.getenv('ALLOWED_FILE_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx,txt,mp4,mp3')
        if extensions_str:
            allowed_extensions = [ext.strip() for ext in extensions_str.split(',') if ext.strip()]
            if allowed_extensions:
                self.allowed_file_extensions = allowed_extensions
        self.max_text_length = int(os.getenv('MAX_TEXT_LENGTH', '4096')) or self.max_text_length
        self.session_timeout_minutes = int(os.getenv('SESSION_TIMEOUT_MINUTES', '60')) or self.session_timeout_minutes
        self.max_login_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')) or self.max_login_attempts
        self.lockout_duration_minutes = int(os.getenv('LOCKOUT_DURATION_MINUTES', '15')) or self.lockout_duration_minutes
        
        if self.max_file_size_mb <= 0:
            raise ValueError("Max file size must be positive")
        if self.max_text_length <= 0:
            raise ValueError("Max text length must be positive")
        if self.session_timeout_minutes <= 0:
            raise ValueError("Session timeout must be positive")
        
        # Normalize file extensions
        self.allowed_file_extensions = [ext.lower().strip() for ext in self.allowed_file_extensions]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


@dataclass
class CoreRateLimitConfig:
    """general rate limiting configuration."""
    commands_per_minute: int = 30
    callbacks_per_minute: int = 60
    messages_per_minute: int = 20
    files_per_hour: int = 10
    
    def __post_init__(self):
        """Validate rate limit configuration."""
        # Load from environment variables
        self.commands_per_minute = int(os.getenv('RATE_LIMIT_COMMANDS', '30')) or self.commands_per_minute
        self.callbacks_per_minute = int(os.getenv('RATE_LIMIT_CALLBACKS', '60')) or self.callbacks_per_minute
        self.messages_per_minute = int(os.getenv('RATE_LIMIT_MESSAGES', '20')) or self.messages_per_minute
        self.files_per_hour = int(os.getenv('RATE_LIMIT_FILES', '10')) or self.files_per_hour
        
        if self.commands_per_minute <= 0:
            raise ValueError("Commands per minute must be positive")
        if self.callbacks_per_minute <= 0:
            raise ValueError("Callbacks per minute must be positive")


class CoreConfigManager:
    """Centralized configuration manager for general functionality."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.telegram = CoreTelegramConfig()
        self.database = self._load_database_config()
        self.redis = self._load_redis_config()
        self.application = self._load_application_config()
        self.security = self._load_security_config()
        self.rate_limits = self._load_rate_limit_config()
        self._environment_loaded = True
    
    def _load_database_config(self) -> CoreDatabaseConfig:
        """Load database configuration from environment."""
        return CoreDatabaseConfig()
    
    def _load_redis_config(self) -> CoreRedisConfig:
        """Load Redis configuration from environment."""
        return CoreRedisConfig()
    
    def _load_application_config(self) -> CoreApplicationConfig:
        """Load application configuration from environment."""
        return CoreApplicationConfig()
    
    def _load_security_config(self) -> CoreSecurityConfig:
        """Load security configuration from environment."""
        return CoreSecurityConfig()
    
    def _load_rate_limit_config(self) -> CoreRateLimitConfig:
        """Load rate limiting configuration from environment."""
        return CoreRateLimitConfig()
    
    def validate_configuration(self) -> bool:
        """Validate all configuration sections."""
        try:
            # Validate all config sections by accessing their properties
            _ = self.telegram.is_valid
            _ = self.database.connection_string
            _ = self.security.max_file_size_bytes
            _ = self.application.is_production
            
            logger.info("general configuration validation successful")
            return True
            
        except Exception as e:
            logger.error(f"general configuration validation failed: {e}")
            return False
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            'telegram': {
                'api_id_set': bool(self.telegram.api_id),
                'api_hash_set': bool(self.telegram.api_hash),
                'bot_token_set': bool(self.telegram.bot_token),
                'session_name': self.telegram.session_name
            },
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'pool_size': self.database.pool_size
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'db': self.redis.db
            },
            'application': {
                'environment': self.application.environment,
                'debug_mode': self.application.debug_mode,
                'log_level': self.application.log_level
            },
            'security': {
                'max_file_size_mb': self.security.max_file_size_mb,
                'max_text_length': self.security.max_text_length,
                'allowed_extensions_count': len(self.security.allowed_file_extensions)
            },
            'rate_limits': {
                'commands_per_minute': self.rate_limits.commands_per_minute,
                'callbacks_per_minute': self.rate_limits.callbacks_per_minute
            },
            'environment_loaded': self._environment_loaded,
            'is_valid': self.validate_configuration()
        }
    
    def reload_configuration(self):
        """Reload configuration from environment variables."""
        logger.info("Reloading general configuration...")
        
        self.telegram = CoreTelegramConfig()
        self.database = self._load_database_config()
        self.redis = self._load_redis_config()
        self.application = self._load_application_config()
        self.security = self._load_security_config()
        self.rate_limits = self._load_rate_limit_config()
        
        logger.info("general configuration reloaded successfully")


# Global configuration manager instance
_config_manager = None

def get_core_config() -> CoreConfigManager:
    """Get the global general configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = CoreConfigManager()
    return _config_manager

def reload_core_config():
    """Reload the global general configuration."""
    global _config_manager
    if _config_manager is not None:
        _config_manager.reload_configuration()
    else:
        _config_manager = CoreConfigManager()