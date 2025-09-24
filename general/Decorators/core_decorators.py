import functools
import asyncio
import os
import time
from typing import List, Optional, Callable, Any, Dict
from datetime import datetime, timedelta

from general.Logging.logger_manager import get_logger, log_error_with_context, log_security_event
from general.Database.MySQL.db_manager import DatabaseManager

logger = get_logger(__name__)


class CoreDecorators:
    """general decorator utilities for the bot with enhanced security and performance."""
    
    @staticmethod
    def check_user_banned():
        """Decorator to check if user is banned before executing handler."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Extract user ID from different possible argument structures
                    user_id = None
                    if len(args) >= 2:
                        # For handlers like (client, callback_query/message)
                        if hasattr(args[1], 'from_user'):
                            user_id = args[1].from_user.id
                        elif hasattr(args[1], 'chat'):
                            user_id = args[1].chat.id
                    
                    # Check if user is banned in database
                    if user_id and len(args) >= 1:
                        # Assuming the app instance is available in args[0] (client)
                        if hasattr(args[0], 'db'):
                            db: DatabaseManager = args[0].db
                            user = await db.get_user(user_id)
                            if user and user.get('Is_Banned', 0) == 1:
                                log_security_event('banned_user_access_attempt', {
                                    'user_id': user_id,
                                    'function': func.__name__
                                }, 'medium')
                                logger.info(f"Banned user {user_id} attempted to access {func.__name__}")
                                return  # Silently ignore or could send a message
                        
                    return await func(*args, **kwargs)
                except Exception as e:
                    log_error_with_context(e, {'decorator': 'check_user_banned'})
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def inject_user_and_lang(func: Callable) -> Callable:
        """Decorator to inject user data and language code."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Extract user information
                user_id = None
                if len(args) >= 2 and hasattr(args[1], 'from_user'):
                    user_id = args[1].from_user.id
                
                # Inject user data and language if user_id is available
                if user_id and len(args) >= 1:
                    if hasattr(args[0], 'db'):
                        db: DatabaseManager = args[0].db
                        user = await db.get_user(user_id)
                        if user:
                            # Inject user data and language code into kwargs
                            kwargs['user_data'] = user
                            kwargs['lang_code'] = user.get('Language_Code', 'en')
                
                return await func(*args, **kwargs)
            except Exception as e:
                log_error_with_context(e, {'decorator': 'inject_user_and_lang'})
                raise
        return wrapper
    
    @staticmethod
    def admin_required(admin_ids: Optional[List[int]] = None):
        """Decorator to ensure only admins can access a function."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Extract user ID from different possible argument structures
                    user_id = None
                    
                    # Check common patterns for user ID extraction
                    if len(args) >= 2:
                        # For handlers like (client, callback_query/message)
                        if hasattr(args[1], 'from_user'):
                            user_id = args[1].from_user.id
                    
                    # Check if user is admin
                    if user_id:
                        # If specific admin IDs provided, check against them
                        if admin_ids and user_id not in admin_ids:
                            log_security_event('unauthorized_admin_access', {
                                'user_id': user_id,
                                'function': func.__name__,
                                'reason': 'not_in_specific_admin_list'
                            }, 'high')
                            logger.warning(f"Unauthorized admin access attempt by user {user_id}")
                            return None
                        # If no specific admin IDs, check against config
                        elif not admin_ids:
                            admin_list = [int(x) for x in str(os.getenv('ADMIN_CHAT_IDS', '')).split(',') if x.strip().isdigit()]
                            if user_id not in admin_list:
                                log_security_event('unauthorized_admin_access', {
                                    'user_id': user_id,
                                    'function': func.__name__,
                                    'reason': 'not_in_config_admin_list'
                                }, 'high')
                                logger.warning(f"Unauthorized admin access attempt by user {user_id}")
                                return None
                    
                    return await func(*args, **kwargs)
                except Exception as e:
                    log_error_with_context(e, {'decorator': 'admin_required'})
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def error_handler(func):
        """Decorator for consistent error handling."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log_error_with_context(e, {'function': func.__name__})
                # Re-raise the exception to allow proper error propagation
                raise
        return wrapper
    
    @staticmethod
    def security_audit_log(action: str):
        """Decorator to log security-sensitive actions."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Extract user info for logging
                    user_id = None
                    if len(args) >= 2 and hasattr(args[1], 'from_user'):
                        user_id = args[1].from_user.id
                    
                    # Log the action
                    logger.info(f"Security action: {action}", extra={
                        'user_id': user_id,
                        'action': action,
                        'function': func.__name__
                    })
                    
                    result = await func(*args, **kwargs)
                    
                    # Log successful completion
                    logger.info(f"Security action completed: {action}", extra={
                        'user_id': user_id,
                        'action': action,
                        'function': func.__name__
                    })
                    
                    return result
                    
                except Exception as e:
                    log_error_with_context(e, {'decorator': 'security_audit_log'})
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def input_validation(validate_func: Callable):
        """Decorator to validate input parameters."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Extract user ID for security logging
                    user_id = None
                    if len(args) >= 2 and hasattr(args[1], 'from_user'):
                        user_id = args[1].from_user.id
                    
                    # Execute the validation function
                    if validate_func:
                        validation_result = await validate_func(*args, **kwargs)
                        if not validation_result:
                            log_security_event('input_validation_failed', {
                                'user_id': user_id,
                                'function': func.__name__
                            }, 'medium')
                            logger.warning(f"Input validation failed for {func.__name__}")
                            # Return a proper response instead of None
                            return await func(*args, **kwargs)  # Let the function handle the validation failure
                    
                    return await func(*args, **kwargs)
                except Exception as e:
                    log_error_with_context(e, {'decorator': 'input_validation'})
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def require_permissions(permissions: List[str]):
        """Decorator to check user permissions."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Extract user ID
                    user_id = None
                    if len(args) >= 2 and hasattr(args[1], 'from_user'):
                        user_id = args[1].from_user.id
                    
                    # Check permissions (simplified implementation)
                    if user_id and permissions:
                        # In a real implementation, this would check the user's permissions in the database
                        # For now, we'll assume admin users have all permissions
                        admin_list = [int(x) for x in str(os.getenv('ADMIN_CHAT_IDS', '')).split(',') if x.strip().isdigit()]
                        if user_id not in admin_list:
                            log_security_event('insufficient_permissions', {
                                'user_id': user_id,
                                'function': func.__name__,
                                'required_permissions': permissions
                            }, 'medium')
                            logger.warning(f"User {user_id} lacks required permissions: {permissions}")
                            # Return a proper response instead of None
                            return await func(*args, **kwargs)  # Let the function handle the permission failure
                    
                    return await func(*args, **kwargs)
                except Exception as e:
                    log_error_with_context(e, {'decorator': 'require_permissions'})
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def rate_limit(max_calls: int = 30, window_seconds: int = 60):
        """Add rate limiting to a handler function with enhanced security logging."""
        def decorator(func: Callable):
            # Store rate limit data per function
            rate_limit_data = {}
            
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract user ID for rate limiting
                user_id = None
                if len(args) >= 2 and hasattr(args[1], 'from_user'):
                    user_id = args[1].from_user.id
                
                if user_id and len(args) >= 1:
                    if hasattr(args[0], 'redis'):
                        try:
                            from general.Caching.redis_service import RedisService
                            redis: RedisService = args[0].redis
                            
                            # Create a unique key for this user and function
                            key = f"rate_limit:{func.__name__}:{user_id}"
                            
                            # Get current count
                            current_count = await redis.redis.get(key) if redis.redis else None
                            current_count = int(current_count) if current_count else 0
                            
                            # Check if user has exceeded rate limit
                            if current_count >= max_calls:
                                log_security_event('rate_limit_exceeded', {
                                    'user_id': user_id,
                                    'function': func.__name__,
                                    'current_count': current_count,
                                    'max_calls': max_calls
                                }, 'medium')
                                logger.warning(f"Rate limit exceeded for user {user_id} on function {func.__name__}")
                                # Could send a message to the user here
                                return  # Silently ignore or could raise exception
                            
                            # Increment count and set expiration
                            if redis.redis:
                                await redis.redis.incr(key)
                                if current_count == 0:
                                    await redis.redis.expire(key, window_seconds)
                            
                        except Exception as e:
                            # If Redis is unavailable, we'll allow the request to proceed
                            log_error_with_context(e, {'decorator': 'rate_limit'})
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def secure_endpoint(require_auth: bool = True, 
                       require_admin: bool = False,
                       rate_limit_per_minute: int = 60,
                       validate_input: bool = True):
        """Comprehensive security decorator combining multiple security checks."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Extract user information
                    user_id = None
                    if len(args) >= 2 and hasattr(args[1], 'from_user'):
                        user_id = args[1].from_user.id
                    
                    # Log access attempt
                    logger.info(f"Secure endpoint access: {func.__name__}", extra={
                        'user_id': user_id,
                        'function': func.__name__,
                        'require_auth': require_auth,
                        'require_admin': require_admin
                    })
                    
                    # Authentication check if required
                    if require_auth and user_id:
                        if len(args) >= 1 and hasattr(args[0], 'db'):
                            db: DatabaseManager = args[0].db
                            user = await db.get_user(user_id)
                            if not user:
                                log_security_event('unauthenticated_access_attempt', {
                                    'user_id': user_id,
                                    'function': func.__name__
                                }, 'high')
                                logger.warning(f"Unauthenticated access attempt to {func.__name__} by user {user_id}")
                                return None
                    
                    # Admin check if required
                    if require_admin and user_id:
                        admin_list = [int(x) for x in str(os.getenv('ADMIN_CHAT_IDS', '')).split(',') if x.strip().isdigit()]
                        if user_id not in admin_list:
                            log_security_event('non_admin_access_to_admin_endpoint', {
                                'user_id': user_id,
                                'function': func.__name__
                            }, 'high')
                            logger.warning(f"Non-admin user {user_id} attempted to access admin endpoint {func.__name__}")
                            return None
                    
                    # Rate limiting
                    if rate_limit_per_minute > 0 and user_id and len(args) >= 1:
                        if hasattr(args[0], 'redis'):
                            from general.Caching.redis_service import RedisService
                            redis: RedisService = args[0].redis
                            
                            key = f"rate_limit:{func.__name__}:{user_id}"
                            current_count = await redis.redis.get(key) if redis.redis else None
                            current_count = int(current_count) if current_count else 0
                            
                            if current_count >= rate_limit_per_minute:
                                log_security_event('rate_limit_exceeded_on_secure_endpoint', {
                                    'user_id': user_id,
                                    'function': func.__name__,
                                    'current_count': current_count,
                                    'rate_limit': rate_limit_per_minute
                                }, 'medium')
                                logger.warning(f"Rate limit exceeded for user {user_id} on secure endpoint {func.__name__}")
                                return None
                            
                            if redis.redis:
                                await redis.redis.incr(key)
                                if current_count == 0:
                                    await redis.redis.expire(key, 60)  # 1 minute window
                    
                    result = await func(*args, **kwargs)
                    
                    # Log successful access
                    logger.info(f"Secure endpoint success: {func.__name__}", extra={
                        'user_id': user_id,
                        'function': func.__name__
                    })
                    
                    return result
                    
                except Exception as e:
                    log_error_with_context(e, {'decorator': 'secure_endpoint'})
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def retry(max_attempts: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
        """Decorator to retry function execution on failure."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        if attempt < max_attempts - 1:
                            wait_time = delay * (backoff_factor ** attempt)
                            logger.warning(
                                f"Function {func.__name__} failed (attempt {attempt + 1}/{max_attempts}), "
                                f"retrying in {wait_time}s: {str(e)}"
                            )
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(
                                f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}"
                            )
                
                # Re-raise the last exception
                if last_exception:
                    raise last_exception
                # Fallback in case last_exception is None (shouldn't happen)
                raise Exception(f"Function {func.__name__} failed after {max_attempts} attempts")
            
            return wrapper
        return decorator
    
    @staticmethod
    def timeout(seconds: float):
        """Decorator to add timeout to async functions."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
                except asyncio.TimeoutError:
                    logger.warning(f"Function {func.__name__} timed out after {seconds} seconds")
                    raise
                except Exception as e:
                    log_error_with_context(e, {'decorator': 'timeout'})
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def performance_monitor(threshold_ms: float = 1000):
        """Decorator to monitor function performance and log slow executions."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
                    
                    # Log if execution time exceeds threshold
                    if execution_time > threshold_ms:
                        logger.warning(
                            f"Slow function execution: {func.__name__} took {execution_time:.2f}ms "
                            f"(threshold: {threshold_ms}ms)"
                        )
                    
                    return result
                except Exception as e:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    logger.error(
                        f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}"
                    )
                    raise
            return wrapper
        return decorator


# Convenience aliases for common decorators
check_user_banned = CoreDecorators.check_user_banned
inject_user_and_lang = CoreDecorators.inject_user_and_lang
admin_required = CoreDecorators.admin_required
error_handler = CoreDecorators.error_handler
security_audit_log = CoreDecorators.security_audit_log
input_validation = CoreDecorators.input_validation
require_permissions = CoreDecorators.require_permissions
rate_limit = CoreDecorators.rate_limit
secure_endpoint = CoreDecorators.secure_endpoint
retry = CoreDecorators.retry
timeout = CoreDecorators.timeout
performance_monitor = CoreDecorators.performance_monitor