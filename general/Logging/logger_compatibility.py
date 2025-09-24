"""
Logger Compatibility Layer
========================

Provides backward compatibility for files still using logger_setup.py
by redirecting to the new general logger implementation.
"""

from general.Logging.logger_manager import get_logger, log_error_with_context, log_user_action, log_admin_action

# Create a logger instance for backward compatibility
logger = get_logger("ziphus_compatibility")

# Export the same functions that were in logger_setup.py
# These are already imported above, so we just need to make them available
# in the module's namespace for imports like "from logger_setup import logger, log_error_with_context"