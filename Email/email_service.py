"""
Email Service Module
==================

Consolidated email sending functionality.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails using general configuration."""
    
    def __init__(self):
        """Initialize email service with general configuration."""
        self.core_config = get_core_config()
        self._initialized = False
    
    def _get_smtp_config(self):
        """Get SMTP configuration from general configuration."""
        # Get email configuration from environment variables through core config
        import os
        return {
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_SENDER_ADDRESS', ''),
            'password': os.getenv('EMAIL_SENDER_PASSWORD', ''),
            'use_tls': True
        }
    
    def initialize(self) -> bool:
        """Initialize email service."""
        try:
            # In a real implementation, we would validate the email configuration
            # from the general configuration here
            self._initialized = True
            logger.info("Email service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize email service: {e}")
            return False
    
    def send_email(self, to_emails: List[str], subject: str, body: str, 
                   html_body: Optional[str] = None) -> bool:
        """Send an email using general configuration."""
        if not self._initialized:
            logger.error("Email service not initialized")
            return False
        
        try:
            # Get SMTP configuration from general configuration
            smtp_config = self._get_smtp_config()
            
            # Validate required configuration
            if not smtp_config['username'] or not smtp_config['password']:
                logger.error("Email configuration is incomplete")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = smtp_config['username']
            message["To"] = ", ".join(to_emails)
            
            # Add body
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                if smtp_config['use_tls']:
                    server.starttls(context=context)
                server.login(smtp_config['username'], smtp_config['password'])
                server.sendmail(smtp_config['username'], to_emails, message.as_string())
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_verification_email(self, email: str, verification_code: str) -> bool:
        """Send verification email."""
        subject = "Email Verification Code"
        body = f"Your verification code is: {verification_code}"
        
        return self.send_email([email], subject, body)
    
    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset email."""
        subject = "Password Reset Request"
        body = f"Use this token to reset your password: {reset_token}"
        
        return self.send_email([email], subject, body)