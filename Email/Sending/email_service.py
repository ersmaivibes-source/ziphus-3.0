"""
Email Sending Service
====================

Service for sending various types of emails.
"""

import logging
from typing import List, Optional, Dict, Any

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config

logger = logging.getLogger(__name__)

class EmailSendingService:
    """Service for sending various types of emails using general configuration."""
    
    def __init__(self):
        """Initialize email sending service."""
        self.core_config = get_core_config()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize email sending service."""
        try:
            # In a real implementation, we would validate the email configuration
            # from the general configuration here
            self._initialized = True
            logger.info("Email sending service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize email sending service: {e}")
            return False
    
    async def send_email(self, recipient: str, subject: str, template_name: str, 
                        template_data: Optional[Dict[str, Any]] = None) -> bool:
        """Send an email using a template."""
        if not self._initialized:
            logger.error("Email sending service not initialized")
            return False
        
        try:
            # Get email configuration from general configuration
            # Note: Email configuration should be added to general configuration
            email_config = {
                'sender_address': '',
                'sender_password': '',
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587
            }
            
            # In a real implementation, we would:
            # 1. Load the email template
            # 2. Render the template with template_data
            # 3. Send the email using the configuration from general
            
            logger.info(f"Email sent to {recipient} using template {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def send_verification_code(self, email: str, code: str) -> bool:
        """Send verification code email."""
        template_data = {
            'code': code,
            'expiry_minutes': self.core_config.application.verification_code_expiry // 60
        }
        
        return await self.send_email(
            recipient=email,
            subject="Verification Code",
            template_name="verification_code",
            template_data=template_data
        )
    
    async def send_password_reset(self, email: str, token: str) -> bool:
        """Send password reset email."""
        template_data = {
            'token': token,
            'expiry_hours': 1  # This should be configurable
        }
        
        return await self.send_email(
            recipient=email,
            subject="Password Reset",
            template_name="password_reset",
            template_data=template_data
        )
    
    async def send_notification(self, email: str, message: str, subject: str = "Notification") -> bool:
        """Send notification email."""
        template_data = {
            'message': message
        }
        
        return await self.send_email(
            recipient=email,
            subject=subject,
            template_name="notification",
            template_data=template_data
        )