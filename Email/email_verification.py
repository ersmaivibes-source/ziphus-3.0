"""
Email Verification Service
Consolidated email verification functionality
"""

import secrets
import string
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)


class EmailVerification:
    """Email verification code management."""
    
    def __init__(self, redis_service=None):
        """Initialize verification service."""
        self.redis_service = redis_service
    
    def generate_verification_code(self, length: int = 6) -> str:
        """Generate a secure verification code."""
        # Use only digits for better UX
        characters = string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def generate_reset_token(self, length: int = 32) -> str:
        """Generate a secure reset token."""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    async def store_verification_code(self, user_id: int, email: str, code: str, 
                                    expiry_minutes: int = 10) -> bool:
        """Store verification code in Redis."""
        if not self.redis_service:
            return False
        
        try:
            verification_data = {
                'email': email,
                'code': code,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(minutes=expiry_minutes)).isoformat()
            }
            
            key = f"email_verification:{user_id}"
            return await self.redis_service.set_json(key, verification_data, ex=expiry_minutes * 60)
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'store_verification_code',
                'user_id': user_id
            })
            return False
    
    async def verify_code(self, user_id: int, submitted_code: str) -> Dict[str, Any]:
        """Verify submitted code against stored code."""
        if not self.redis_service:
            return {'success': False, 'message': 'Verification service unavailable'}
        
        try:
            key = f"email_verification:{user_id}"
            verification_data = await self.redis_service.get_json(key)
            
            if not verification_data:
                return {'success': False, 'message': 'No verification code found or expired'}
            
            stored_code = verification_data.get('code')
            if not stored_code or stored_code != submitted_code:
                return {'success': False, 'message': 'Invalid verification code'}
            
            # Check expiry
            expires_at = datetime.fromisoformat(verification_data.get('expires_at'))
            if datetime.now() > expires_at:
                await self.redis_service.delete(key)
                return {'success': False, 'message': 'Verification code expired'}
            
            # Success - return email and clear code
            email = verification_data.get('email')
            await self.redis_service.delete(key)
            
            return {
                'success': True,
                'email': email,
                'message': 'Email verified successfully'
            }
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'verify_code',
                'user_id': user_id
            })
            return {'success': False, 'message': 'Verification error occurred'}
    
    async def clear_verification_data(self, user_id: int) -> bool:
        """Clear verification data for user."""
        if not self.redis_service:
            return False
        
        try:
            key = f"email_verification:{user_id}"
            return await self.redis_service.delete(key)
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'clear_verification_data',
                'user_id': user_id
            })
            return False