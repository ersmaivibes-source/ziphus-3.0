"""User Authentication Service for secure user management."""

import hashlib
import secrets
import logging
from typing import Dict, Any, Optional
import time

# Use more secure password hashing libraries
import bcrypt
from argon2 import PasswordHasher, exceptions as argon2_exceptions

from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService
from general.Validation.input_validation import InputValidator
from Email.email_service import EmailService
from general.Logging.logger_manager import get_logger, log_user_action, log_error_with_context, log_security_event
from general.Configuration.config_manager import get_core_config

# Initialize logger
logger = get_logger(__name__)

# Get configuration
core_config = get_core_config()

# Initialize password hasher with optimized settings for security
password_hasher = PasswordHasher(
    time_cost=3,       # Number of iterations
    memory_cost=65536, # Memory usage in KB
    parallelism=1,     # Number of parallel threads
    hash_len=32,       # Length of hash in bytes
    salt_len=16        # Length of salt in bytes
)

def validate_email(email: str) -> bool:
    """Validate email format."""
    return InputValidator.validate_email(email)

def validate_password(password: str, lang_code: str = 'en') -> str:
    """Validate password strength."""
    return InputValidator.validate_password(password, lang_code)

def generate_verification_code() -> str:
    """Generate secure verification code."""
    return InputValidator.generate_secure_code(6)

class UserAuthService:
    """Service for user authentication and account management."""
    
    def __init__(self, db: DatabaseManager, redis: RedisService, email_service: EmailService):
        """Initialize authentication service."""
        self.db = db
        self.redis = redis
        self.email_service = email_service
        self._texts = {}  # In a real implementation, this would load language-specific texts
    
    def _get_text(self, key: str, lang_code: str = 'en', **kwargs) -> str:
        """Get localized text."""
        # This is a simplified implementation
        texts = {
            'en': {
                'invalid_email': 'Invalid email address.',
                'email_exists': 'Email address already registered.',
                'email_send_failed': 'Failed to send verification email.',
                'email_code_sent': 'Verification code sent to {email}.',
                'verification_expired': 'Verification code expired.',
                'incorrect_code': 'Incorrect verification code.',
                'email_verified': 'Email verified successfully.',
                'registration_failed': 'Registration failed.',
                'error_occurred': 'An error occurred.',
                'email_not_registered': 'Email not registered.',
                'account_temporarily_locked': 'Account temporarily locked. Try again in {minutes} minutes.',
                'account_locked_due_to_attempts': 'Account locked due to too many failed attempts.',
                'sign_in_failed_attempts_remaining': 'Sign in failed. {remaining} attempts remaining.',
                'sign_in_successful': 'Sign in successful.',
                'user_not_found': 'User not found.',
                'no_password_set': 'No password set for this account.',
                'incorrect_current_password': 'Current password is incorrect.',
                'password_changed_successfully': 'Password changed successfully.',
                'password_change_failed': 'Password change failed.',
                'email_change_code_sent': 'Email change verification code sent.',
                'too_many_requests': 'Too many requests. Please try again later.'
            }
        }
        
        try:
            message = texts.get(lang_code, texts['en']).get(key, key)
            return message.format(**kwargs) if kwargs else message
        except KeyError:
            return key

    async def initiate_email_registration(self, user_id: int, email: str, 
                                        password: str, lang_code: str = 'en') -> Dict[str, Any]:
        """Start email registration process with verification."""
        try:
            # Rate limiting for registration attempts
            if await self._is_rate_limited(f"register:{user_id}", max_calls=5, window_seconds=300):
                log_security_event('registration_rate_limit_exceeded', {
                    'user_id': user_id,
                    'email': email
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('too_many_requests', lang_code)
                }
            
            # Validate email format
            if not validate_email(email):
                return {
                    'success': False,
                    'message': self._get_text('invalid_email', lang_code)
                }
            
            # Validate password strength
            password_validation = validate_password(password, lang_code)
            if password_validation != "valid":
                return {
                    'success': False,
                    'message': password_validation
                }
            
            # Check if email already exists
            existing_email = await self.db.get_user_by_email(email)
            if existing_email:
                return {
                    'success': False,
                    'message': self._get_text('email_exists', lang_code)
                }
            
            # Hash password before storing verification data using Argon2
            password_hash = self._hash_password_argon2(password)
            
            # Generate verification code
            verification_code = generate_verification_code()
            
            # Store verification data in Redis with hashed password
            success = await self.redis.set_verification_code_with_password(
                user_id, verification_code, email, password_hash
            )
            
            if not success:
                return {
                    'success': False,
                    'message': self._get_text('email_send_failed', lang_code)
                }
            
            # Send verification email (fix: removed lang_code parameter)
            email_sent = self.email_service.send_verification_email(email, verification_code)
            
            if email_sent:
                log_user_action(user_id, 'email_verification_sent', {'email': email})
                log_security_event('email_verification_initiated', {
                    'user_id': user_id,
                    'email': email
                }, 'medium')
                return {
                    'success': True,
                    'message': self._get_text('email_code_sent', lang_code, email=email)
                }
            else:
                # Clear verification data if email failed
                await self.redis.clear_verification_data(user_id)
                return {
                    'success': False,
                    'message': self._get_text('email_send_failed', lang_code)
                }
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'initiate_email_registration',
                'user_id': user_id,
                'email': email
            })
            return {
                'success': False,
                'message': self._get_text('error_occurred', lang_code)
            }
    
    async def verify_email_code(self, user_id: int, code: str, 
                               lang_code: str = 'en') -> Dict[str, Any]:
        """Verify email verification code and complete registration."""
        try:
            # Rate limiting for verification attempts
            if await self._is_rate_limited(f"verify:{user_id}", max_calls=10, window_seconds=300):
                log_security_event('verification_rate_limit_exceeded', {
                    'user_id': user_id
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('too_many_requests', lang_code)
                }
            
            # Get verification data
            verification_data = await self.redis.get_verification_data(user_id)
            if not verification_data:
                return {
                    'success': False,
                    'message': self._get_text('verification_expired', lang_code)
                }
            
            # Verify code
            if verification_data.get('code') != code.upper():
                log_security_event('email_verification_failed', {
                    'user_id': user_id,
                    'reason': 'incorrect_code'
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('incorrect_code', lang_code)
                }
            
            # Update user with email and password hash
            email = verification_data.get('email')
            password_hash = verification_data.get('password_hash')
            
            # Check if email and password hash exist
            if not email or not password_hash:
                return {
                    'success': False,
                    'message': self._get_text('verification_expired', lang_code)
                }
            
            success = await self.db.update_user_email_password(
                user_id, email, password_hash
            )
            
            if success:
                # Clear verification data
                await self.redis.clear_verification_data(user_id)
                
                log_user_action(user_id, 'email_verified', {'email': email})
                log_security_event('email_verification_completed', {
                    'user_id': user_id,
                    'email': email
                }, 'low')
                
                return {
                    'success': True,
                    'message': self._get_text('email_verified', lang_code)
                }
            else:
                return {
                    'success': False,
                    'message': self._get_text('registration_failed', lang_code)
                }
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'verify_email_code',
                'user_id': user_id
            })
            return {
                'success': False,
                'message': self._get_text('error_occurred', lang_code)
            }
    
    async def authenticate_user(self, email: str, password: str, 
                               lang_code: str = 'en') -> Dict[str, Any]:
        """Authenticate user with email and password."""
        try:
            # Rate limiting for login attempts
            rate_limit_key = f"login:{email}"
            if await self._is_rate_limited(rate_limit_key, max_calls=10, window_seconds=300):
                log_security_event('login_rate_limit_exceeded', {
                    'email': email
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('too_many_requests', lang_code)
                }
            
            # Get user by email
            user = await self.db.get_user_by_email(email)
            if not user:
                log_security_event('login_failed', {
                    'email': email,
                    'reason': 'email_not_registered'
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('email_not_registered', lang_code)
                }
            
            user_id = user.get('Chat_ID')
            if not user_id:
                log_security_event('login_failed', {
                    'email': email,
                    'reason': 'invalid_user_id'
                }, 'high')
                return {
                    'success': False,
                    'message': self._get_text('email_not_registered', lang_code)
                }
            
            # Check if account is locked
            if await self._is_account_locked(user_id):
                remaining_minutes = await self._get_lockout_remaining_minutes(user_id)
                log_security_event('login_failed', {
                    'user_id': user_id,
                    'email': email,
                    'reason': 'account_locked'
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('account_temporarily_locked', 
                                            lang_code, minutes=remaining_minutes),
                    'locked': True
                }
            
            # Verify password
            stored_password_hash = user.get('Password_Hash')
            if not stored_password_hash or not self._verify_password_argon2(password, stored_password_hash):
                # Increment failed attempts
                await self._increment_failed_attempts(user_id)
                
                # Check if should lock account
                failed_attempts = await self._get_failed_attempts(user_id)
                max_attempts = core_config.security.max_login_attempts
                
                if failed_attempts >= max_attempts:
                    await self._lock_account(user_id)
                    log_security_event('account_locked', {
                        'user_id': user_id,
                        'email': email,
                        'failed_attempts': failed_attempts
                    }, 'high')
                    return {
                        'success': False,
                        'message': self._get_text('account_locked_due_to_attempts', lang_code),
                        'locked': True
                    }
                
                remaining = max_attempts - failed_attempts
                log_security_event('login_failed', {
                    'user_id': user_id,
                    'email': email,
                    'reason': 'incorrect_password',
                    'remaining_attempts': remaining
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('sign_in_failed_attempts_remaining', 
                                            lang_code, remaining=remaining)
                }
            
            # Clear failed attempts on successful login
            await self._clear_failed_attempts(user_id)
            
            # Update last login
            await self.db.update_login_info(user_id)
            
            log_user_action(user_id, 'successful_login', {'email': email})
            log_security_event('login_successful', {
                'user_id': user_id,
                'email': email
            }, 'low')
            
            return {
                'success': True,
                'message': self._get_text('sign_in_successful', lang_code),
                'user': user
            }
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'authenticate_user',
                'email': email
            })
            return {
                'success': False,
                'message': self._get_text('error_occurred', lang_code)
            }
    
    async def change_password(self, user_id: int, current_password: str,
                             new_password: str, lang_code: str = 'en') -> Dict[str, Any]:
        """Change user password."""
        try:
            # Rate limiting for password change attempts
            if await self._is_rate_limited(f"changepass:{user_id}", max_calls=5, window_seconds=300):
                log_security_event('password_change_rate_limit_exceeded', {
                    'user_id': user_id
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('too_many_requests', lang_code)
                }
            
            # Get user
            user = await self.db.get_user(user_id)
            if not user:
                return {
                    'success': False,
                    'message': self._get_text('user_not_found', lang_code)
                }
            
            # Check if password is set
            stored_password_hash = user.get('Password_Hash')
            if not stored_password_hash:
                return {
                    'success': False,
                    'message': self._get_text('no_password_set', lang_code)
                }
            
            # Verify current password
            if not self._verify_password_argon2(current_password, stored_password_hash):
                log_security_event('password_change_failed', {
                    'user_id': user_id,
                    'reason': 'incorrect_current_password'
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('incorrect_current_password', lang_code)
                }
            
            # Validate new password
            password_validation = validate_password(new_password, lang_code)
            if password_validation != "valid":
                return {
                    'success': False,
                    'message': password_validation
                }
            
            # Hash new password
            new_password_hash = self._hash_password_argon2(new_password)
            
            # Update password
            success = await self.db.update_user_password(user_id, new_password_hash)
            
            if success:
                log_user_action(user_id, 'password_changed')
                log_security_event('password_changed', {
                    'user_id': user_id
                }, 'low')
                return {
                    'success': True,
                    'message': self._get_text('password_changed_successfully', lang_code)
                }
            else:
                log_security_event('password_change_failed', {
                    'user_id': user_id,
                    'reason': 'database_update_failed'
                }, 'high')
                return {
                    'success': False,
                    'message': self._get_text('password_change_failed', lang_code)
                }
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'change_password',
                'user_id': user_id
            })
            return {
                'success': False,
                'message': self._get_text('error_occurred', lang_code)
            }
    
    async def change_email(self, user_id: int, new_email: str, 
                          lang_code: str = 'en') -> Dict[str, Any]:
        """Initiate email change process."""
        try:
            # Rate limiting for email change attempts
            if await self._is_rate_limited(f"changeemail:{user_id}", max_calls=5, window_seconds=300):
                log_security_event('email_change_rate_limit_exceeded', {
                    'user_id': user_id
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('too_many_requests', lang_code)
                }
            
            # Validate new email format
            if not validate_email(new_email):
                return {
                    'success': False,
                    'message': self._get_text('invalid_email', lang_code)
                }
            
            # Check if email already exists
            existing_email = await self.db.get_user_by_email(new_email)
            if existing_email:
                log_security_event('email_change_failed', {
                    'user_id': user_id,
                    'new_email': new_email,
                    'reason': 'email_already_exists'
                }, 'medium')
                return {
                    'success': False,
                    'message': self._get_text('email_exists', lang_code)
                }
            
            # Generate verification code
            verification_code = generate_verification_code()
            
            # Store verification data for email change (without password)
            success = await self.redis.set_verification_code(
                user_id, verification_code, new_email
            )
            
            if not success:
                return {
                    'success': False,
                    'message': self._get_text('email_send_failed', lang_code)
                }
            
            # Send verification email to new address
            email_sent = self.email_service.send_verification_email(new_email, verification_code)
            
            if email_sent:
                log_user_action(user_id, 'email_change_initiated', {'new_email': new_email})
                log_security_event('email_change_initiated', {
                    'user_id': user_id,
                    'new_email': new_email
                }, 'medium')
                return {
                    'success': True,
                    'message': self._get_text('email_change_code_sent', lang_code)
                }
            else:
                await self.redis.clear_verification_data(user_id)
                return {
                    'success': False,
                    'message': self._get_text('email_send_failed', lang_code)
                }
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'change_email',
                'user_id': user_id,
                'new_email': new_email
            })
            return {
                'success': False,
                'message': self._get_text('error_occurred', lang_code)
            }
    
    def _hash_password_argon2(self, password: str) -> str:
        """Hash password using Argon2 (most secure option)."""
        try:
            return password_hasher.hash(password)
        except Exception as e:
            log_error_with_context(e, {'operation': 'argon2_hash'})
            # Fallback to bcrypt
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password_argon2(self, password: str, stored_hash: str) -> bool:
        """Verify password against Argon2 hash."""
        try:
            password_hasher.verify(stored_hash, password)
            return True
        except argon2_exceptions.VerifyMismatchError:
            return False
        except Exception:
            # Fallback to bcrypt verification
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except Exception:
                return False
    
    async def _increment_failed_attempts(self, user_id: int) -> None:
        """Increment failed login attempts."""
        if not self.redis.redis:
            return
        key = f"failed_attempts:{user_id}"
        await self.redis.redis.incr(key)
        await self.redis.redis.expire(key, 900)  # 15 minutes
    
    async def _get_failed_attempts(self, user_id: int) -> int:
        """Get number of failed login attempts."""
        if not self.redis.redis:
            return 0
        key = f"failed_attempts:{user_id}"
        attempts = await self.redis.redis.get(key)
        return int(attempts) if attempts else 0
    
    async def _clear_failed_attempts(self, user_id: int) -> None:
        """Clear failed login attempts."""
        if not self.redis.redis:
            return
        key = f"failed_attempts:{user_id}"
        await self.redis.redis.delete(key)
    
    async def _lock_account(self, user_id: int) -> None:
        """Lock user account temporarily."""
        if not self.redis.redis:
            return
        key = f"account_locked:{user_id}"
        lockout_duration = core_config.security.lockout_duration_minutes
        await self.redis.redis.setex(key, lockout_duration * 60, "locked")
    
    async def _is_account_locked(self, user_id: int) -> bool:
        """Check if account is locked."""
        if not self.redis.redis:
            return False
        key = f"account_locked:{user_id}"
        return bool(await self.redis.redis.exists(key))
    
    async def _get_lockout_remaining_minutes(self, user_id: int) -> int:
        """Get remaining lockout time in minutes."""
        if not self.redis.redis:
            return 0
        key = f"account_locked:{user_id}"
        ttl = await self.redis.redis.ttl(key)
        return max(0, ttl // 60) if ttl > 0 else 0
    
    async def _is_rate_limited(self, key: str, max_calls: int, window_seconds: int) -> bool:
        """Check if a key is rate limited."""
        if not self.redis.redis:
            return False
        
        current_count = await self.redis.redis.get(key)
        current_count = int(current_count) if current_count else 0
        
        if current_count >= max_calls:
            return True
        
        # Increment count and set expiration
        await self.redis.redis.incr(key)
        if current_count == 0:
            await self.redis.redis.expire(key, window_seconds)
        
        return False