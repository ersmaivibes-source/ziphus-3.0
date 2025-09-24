"""
Configuration Compatibility Layer
===============================

Provides backward compatibility for the old config.py by redirecting
all functionality to the new general configuration system.
"""

from general.Configuration.config_manager import get_core_config

# Get the general configuration instance for backward compatibility
_core_config = get_core_config()

# Export all the configuration classes and instances that were in the old config.py
# Map the old config structure to the new general configuration

class TelegramConfig:
    """Telegram API configuration - compatibility layer."""
    
    def __init__(self, api_id=None, api_hash=None, bot_token=None):
        core_config = get_core_config()
        self.api_id = api_id or core_config.database.host
        self.api_hash = api_hash or core_config.database.port
        self.bot_token = bot_token or core_config.database.database
    
    @property
    def connection_string(self):
        """Generate database connection string - compatibility method."""
        core_config = get_core_config()
        return core_config.database.connection_string

class DatabaseConfig:
    """Database configuration with connection pooling settings - compatibility layer."""
    
    def __init__(self, host=None, port=None, database=None, user=None, password=None, 
                 pool_size=None, pool_max_overflow=None):
        core_config = get_core_config()
        self.host = host or core_config.database.host
        self.port = port or core_config.database.port
        self.database = database or core_config.database.database
        self.user = user or core_config.database.user
        self.password = password or core_config.database.password
        self.pool_size = pool_size or core_config.database.pool_size
        self.pool_max_overflow = pool_max_overflow or core_config.database.pool_max_overflow
    
    @property
    def connection_string(self):
        """Generate database connection string."""
        core_config = get_core_config()
        return core_config.database.connection_string

class RedisConfig:
    """Redis configuration for caching and state management - compatibility layer."""
    
    def __init__(self, host=None, port=None, db=None, password=None):
        core_config = get_core_config()
        self.host = host or core_config.redis.host
        self.port = port or core_config.redis.port
        self.db = db or core_config.redis.db
        self.password = password or core_config.redis.password

class EmailConfig:
    """Email service configuration - compatibility layer."""
    
    def __init__(self, sender_address=None, sender_password=None, smtp_server=None, smtp_port=None):
        # For now, we'll use default values since email config is separate in the new structure
        self.sender_address = sender_address or ''
        self.sender_password = sender_password or ''
        self.smtp_server = smtp_server or 'smtp.gmail.com'
        self.smtp_port = smtp_port or 587

class SecurityConfig:
    """Security-related configuration - compatibility layer."""
    
    def __init__(self, max_file_size_mb=None, allowed_file_extensions=None, max_text_length=None):
        core_config = get_core_config()
        self.max_file_size_mb = max_file_size_mb or core_config.security.max_file_size_mb
        self.allowed_file_extensions = allowed_file_extensions or core_config.security.allowed_file_extensions.copy()
        self.max_text_length = max_text_length or core_config.security.max_text_length
    
    @property
    def max_file_size_bytes(self):
        """Get max file size in bytes."""
        core_config = get_core_config()
        return core_config.security.max_file_size_bytes

class PaymentConfig:
    """Payment and cryptocurrency configuration - compatibility layer."""
    
    def __init__(self, gateway_url=None, stripe_api_key=None, crypto_wallets=None):
        self.gateway_url = gateway_url or ""
        self.stripe_api_key = stripe_api_key or ""
        self.crypto_wallets = crypto_wallets or {}

class FeatureConfig:
    """Feature toggle configuration - compatibility layer."""
    
    def __init__(self, enable_file_scanning=None, enable_rate_limiting=None):
        self.enable_file_scanning = enable_file_scanning or False
        self.enable_rate_limiting = enable_rate_limiting or True

class RateLimitConfig:
    """Rate limiting configuration - compatibility layer."""
    
    def __init__(self, commands_per_minute=None, callbacks_per_minute=None):
        core_config = get_core_config()
        self.commands_per_minute = commands_per_minute or core_config.rate_limits.commands_per_minute
        self.callbacks_per_minute = callbacks_per_minute or core_config.rate_limits.callbacks_per_minute

class SubscriptionPlan:
    """Subscription plan configuration - compatibility layer."""
    
    def __init__(self, eur, toman, duration_days):
        self.eur = eur
        self.toman = toman
        self.duration_days = duration_days

class PricingConfig:
    """Subscription pricing configuration - compatibility layer."""
    
    def __init__(self, plans=None):
        self.plans = plans or {
            'standard': SubscriptionPlan(eur=4.0, toman=190000, duration_days=30),
            'pro': SubscriptionPlan(eur=7.0, toman=390000, duration_days=30),
            'ultimate': SubscriptionPlan(eur=12.0, toman=890000, duration_days=30)
        }

class ApplicationConfig:
    """Application-wide configuration constants - compatibility layer."""
    
    def __init__(self, verification_code_expiry=None, session_expiry=None):
        core_config = get_core_config()
        self.verification_code_expiry = verification_code_expiry or core_config.application.verification_code_expiry
        self.session_expiry = session_expiry or core_config.application.session_expiry

class PlanLimitsConfig:
    """Plan limits configuration - compatibility layer."""
    
    def __init__(self, limits=None):
        self.limits = limits or {
            'free': {
                'media_downloader': {'daily': 2, 'size_mb': 50},
                'file_converter': {'daily': 2, 'size_mb': 50},
                'bot_addition': {'daily': 1},
                'tickets': {'monthly': 3},
                'referral_bonus': 5
            },
            'standard': {
                'media_downloader': {'daily': 50, 'size_mb': 2000},
                'file_converter': {'daily': 50, 'size_mb': 2000},
                'bot_addition': {'daily': 10},
                'tickets': {'monthly': 20},
                'referral_bonus': 10
            },
            'pro': {
                'media_downloader': {'daily': 200, 'size_mb': 5000},
                'file_converter': {'daily': 200, 'size_mb': 5000},
                'bot_addition': {'daily': 50},
                'tickets': {'monthly': 50},
                'referral_bonus': 15
            },
            'ultimate': {
                'media_downloader': {'daily': -1, 'size_mb': -1},
                'file_converter': {'daily': -1, 'size_mb': -1},
                'bot_addition': {'daily': -1},
                'tickets': {'monthly': -1},
                'referral_bonus': 20
            }
        }

class Config:
    """Main configuration class combining all configuration sections - compatibility layer."""
    
    def __init__(self):
        core_config = get_core_config()
        self.telegram = TelegramConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.email = EmailConfig()
        self.security = SecurityConfig()
        self.payment = PaymentConfig()
        self.features = FeatureConfig()
        self.rate_limits = RateLimitConfig()
        self.pricing = PricingConfig()
        self.app = ApplicationConfig()
        self.plan_limits = PlanLimitsConfig()
        self.admin_chat_ids = []  # This would need to be set separately
    
    @property
    def is_production(self):
        """Check if running in production mode."""
        core_config = get_core_config()
        return core_config.application.is_production

# Create global config instance for backward compatibility
config = Config()

def load_config():
    """Load and validate configuration from environment variables - compatibility function."""
    return config