import redis.asyncio as redis
import json
import datetime
import secrets
import socket
from typing import Optional, Any, Dict, List
from datetime import timedelta

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config
from general.Logging.logger_manager import get_logger, log_error_with_context, log_security_event

logger = get_logger(__name__)

# Get the general configuration
core_config = get_core_config()

class RedisService:
    """Manages Redis connections and operations with enhanced security and performance."""
    
    def __init__(self):
        """Initialize Redis service."""
        self.redis: Optional[redis.Redis] = None
        
    async def initialize(self):
        """Create Redis connection with optimized settings."""
        try:
            redis_kwargs = {
                'host': core_config.redis.host,
                'port': core_config.redis.port,
                'db': core_config.redis.db,
                'decode_responses': True,
                'socket_keepalive': True,
                'socket_connect_timeout': 3,  # Reduced connection timeout for faster failure detection
                'socket_timeout': 3,          # Reduced read/write timeout
                'retry_on_timeout': True,     # Retry on timeout
                'health_check_interval': 15,  # More frequent health checks
                'max_connections': 100,       # Increased maximum connections for high load
                'single_connection_client': False,  # Use connection pool
                'socket_keepalive_options': {  # TCP keepalive options
                    socket.TCP_KEEPIDLE: 60,
                    socket.TCP_KEEPINTVL: 30,
                    socket.TCP_KEEPCNT: 3
                } if hasattr(socket, 'TCP_KEEPIDLE') else {}
            }
            
            # Only add password if it's actually set
            if core_config.redis.password:
                redis_kwargs['password'] = core_config.redis.password
            
            self.redis = await redis.Redis(**redis_kwargs)
            
            # Test connection
            if self.redis:
                await self.redis.ping()
            logger.info("Redis connection established successfully with optimized settings")
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'redis_initialize'})
            raise
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    # User State Management
    
    async def set_user_state(self, user_id: int, state: str, data: Optional[Dict] = None) -> bool:
        """Set user state with optional data and security token."""
        try:
            # Check Redis connection before operations
            if not self.redis:
                logger.error("Redis connection not initialized")
                return False
            
            key = f"state:{user_id}"
            # SECURITY: Add session token to prevent session hijacking
            session_token = secrets.token_urlsafe(32)
            value = {
                'state': state,
                'data': data or {},
                'session_token': session_token,
                'created_at': datetime.datetime.now().isoformat()
            }
            
            # Test connection before setting data
            await self.redis.ping()
            
            await self.redis.setex(
                key,
                timedelta(seconds=core_config.application.session_expiry),
                json.dumps(value, separators=(',', ':'))  # Compact JSON for performance
            )
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'set_user_state', 'user_id': user_id})
            return False
    
    async def get_user_state(self, user_id: int) -> Optional[Dict]:
        """Get user state and data."""
        try:
            if not self.redis:
                return None
                
            key = f"state:{user_id}"
            value = await self.redis.get(key)
            
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'get_user_state', 'user_id': user_id})
            return None
    
    async def clear_user_state(self, user_id: int) -> bool:
        """Clear user state."""
        try:
            if not self.redis:
                return False
                
            key = f"state:{user_id}"
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'clear_user_state', 'user_id': user_id})
            return False
    
    # Verification Codes
    
    async def set_verification_code(self, user_id: int, code: str, 
                                  email: str) -> bool:
        """Store verification code with associated data. No password is stored."""
        try:
            if not self.redis:
                return False
                
            key = f"verify:{user_id}"
            value = {
                'code': code,
                'email': email
            }
            
            await self.redis.setex(
                key,
                timedelta(seconds=core_config.application.verification_code_expiry),
                json.dumps(value, separators=(',', ':'))  # Compact JSON for performance
            )
            log_security_event('verification_code_set', {
                'user_id': user_id,
                'email': email
            }, 'low')
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'set_verification_code'})
            return False
    
    async def set_verification_code_with_password(self, user_id: int, code: str, 
                                  email: str, password_hash: str) -> bool:
        """Store verification code with associated data including hashed password."""
        try:
            if not self.redis:
                return False
                
            key = f"verify:{user_id}"
            value = {
                'code': code,
                'email': email,
                'password_hash': password_hash
            }
            
            await self.redis.setex(
                key,
                timedelta(seconds=core_config.application.verification_code_expiry),
                json.dumps(value, separators=(',', ':'))  # Compact JSON for performance
            )
            log_security_event('verification_code_with_password_set', {
                'user_id': user_id,
                'email': email
            }, 'medium')
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'set_verification_code_with_password'})
            return False
    
    async def get_verification_data(self, user_id: int) -> Optional[Dict]:
        """Get verification data."""
        try:
            if not self.redis:
                return None
                
            key = f"verify:{user_id}"
            value = await self.redis.get(key)
            
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'get_verification_data'})
            return None
    
    async def clear_verification_data(self, user_id: int) -> bool:
        """Clear verification data."""
        try:
            if not self.redis:
                return False
                
            key = f"verify:{user_id}"
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'clear_verification_data'})
            return False
    
    # Payment Sessions
    
    async def set_payment_session(self, user_id: int, session_data: Dict) -> bool:
        """Store payment session data."""
        try:
            if not self.redis:
                return False
                
            key = f"payment:{user_id}"
            await self.redis.setex(
                key,
                timedelta(hours=1),
                json.dumps(session_data, separators=(',', ':'))  # Compact JSON for performance
            )
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'set_payment_session'})
            return False
    
    async def get_payment_session(self, user_id: int) -> Optional[Dict]:
        """Get payment session data."""
        try:
            if not self.redis:
                return None
                
            key = f"payment:{user_id}"
            value = await self.redis.get(key)
            
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'get_payment_session'})
            return None
    
    async def clear_payment_session(self, user_id: int) -> bool:
        """Clear payment session."""
        try:
            if not self.redis:
                return False
                
            key = f"payment:{user_id}"
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'clear_payment_session'})
            return False
    
    # Secure Session Management
    
    async def create_secure_session(self, user_id: int, session_data: Optional[Dict] = None) -> Optional[str]:
        """Create a secure session with a unique token."""
        try:
            if not self.redis:
                return None
                
            # Generate a secure session token
            session_token = secrets.token_urlsafe(32)
            key = f"session:{session_token}"
            
            # Store session data
            value = {
                'user_id': user_id,
                'created_at': datetime.datetime.now().isoformat(),
                'last_accessed': datetime.datetime.now().isoformat(),
                'data': session_data or {}
            }
            
            # Store session with expiration
            await self.redis.setex(
                key,
                timedelta(seconds=core_config.application.session_expiry),
                json.dumps(value, separators=(',', ':'))  # Compact JSON for performance
            )
            
            log_security_event('session_created', {
                'user_id': user_id,
                'session_token': session_token[:8] + '...'  # Log only partial token
            }, 'low')
            
            return session_token
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'create_secure_session', 'user_id': user_id})
            return None
    
    async def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate a session token and update last accessed time."""
        try:
            if not self.redis or not session_token:
                return None
                
            key = f"session:{session_token}"
            value = await self.redis.get(key)
            
            if not value:
                log_security_event('session_validation_failed', {
                    'reason': 'session_not_found',
                    'session_token': session_token[:8] + '...'  # Log only partial token
                }, 'medium')
                return None
            
            session_data = json.loads(value)
            
            # Update last accessed time
            session_data['last_accessed'] = datetime.datetime.now().isoformat()
            
            # Update expiration
            await self.redis.setex(
                key,
                timedelta(seconds=core_config.application.session_expiry),
                json.dumps(session_data, separators=(',', ':'))  # Compact JSON for performance
            )
            
            log_security_event('session_validated', {
                'user_id': session_data.get('user_id'),
                'session_token': session_token[:8] + '...'  # Log only partial token
            }, 'low')
            
            return session_data
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'validate_session'})
            return None
    
    async def destroy_session(self, session_token: str) -> bool:
        """Destroy a session."""
        try:
            if not self.redis or not session_token:
                return False
                
            key = f"session:{session_token}"
            await self.redis.delete(key)
            
            log_security_event('session_destroyed', {
                'session_token': session_token[:8] + '...'  # Log only partial token
            }, 'low')
            
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'destroy_session'})
            return False
    
    async def get_user_sessions(self, user_id: int) -> List[str]:
        """Get all active session tokens for a user (simplified implementation)."""
        try:
            # In a real implementation, you would track user sessions in a separate key
            # For now, we'll return an empty list
            return []
        except Exception as e:
            log_error_with_context(e, {'operation': 'get_user_sessions', 'user_id': user_id})
            return []
    
    async def destroy_user_sessions(self, user_id: int) -> int:
        """Destroy all sessions for a user (simplified implementation)."""
        try:
            # In a real implementation, you would track and destroy all user sessions
            # For now, we'll return 0
            return 0
        except Exception as e:
            log_error_with_context(e, {'operation': 'destroy_user_sessions', 'user_id': user_id})
            return 0
    
    # Temporary Data Storage Methods for Admin Menu Tracker
    
    async def set_temp_data(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store temporary data with TTL."""
        try:
            if not self.redis:
                return False
                
            await self.redis.setex(key, ttl, str(value))
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'set_temp_data', 'key': key})
            return False
    
    async def get_temp_data(self, key: str) -> Optional[str]:
        """Get temporary data."""
        try:
            if not self.redis:
                return None
                
            value = await self.redis.get(key)
            return value
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'get_temp_data', 'key': key})
            return None
    
    async def delete_temp_data(self, key: str) -> bool:
        """Delete temporary data."""
        try:
            if not self.redis:
                return False
                
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'delete_temp_data', 'key': key})
            return False
