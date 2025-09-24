"""
Email Sending Service
Consolidated email sending functionality with retry and error handling
"""

import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

from general.Logging.logger_manager import get_logger, log_error_with_context
from .email_validation import EmailValidation

# Initialize logger
logger = get_logger(__name__)


class EmailSending:
    """Email sending service with retry logic and error handling."""
    
    def __init__(self, config, redis_service=None):
        """Initialize email sending service."""
        self.config = config
        self.redis_service = redis_service
        self.validator = EmailValidation()
    
    async def send_with_retry(self, recipient: str, subject: str, body: str, 
                            is_html: bool = True, retries: Optional[int] = None) -> bool:
        """Send email with retry logic."""
        max_retries = retries if retries is not None else self.config.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                success = await self._send_single_email(recipient, subject, body, is_html)
                if success:
                    return True
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Email send attempt {attempt + 1} failed, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                
            except Exception as e:
                log_error_with_context(e, {
                    'operation': 'send_with_retry',
                    'attempt': attempt + 1,
                    'recipient': self.validator.normalize_email(recipient)
                })
                
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
        
        return False
    
    async def _send_single_email(self, recipient: str, subject: str, body: str, is_html: bool) -> bool:
        """Send a single email."""
        try:
            # Validate recipient
            if not self.validator.validate_email(recipient):
                logger.error(f"Invalid email address: {recipient}")
                return False
            
            # Create message
            message = MIMEMultipart('alternative')
            message["From"] = self.config.sender_address
            message["To"] = recipient
            message["Subject"] = subject
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Attach body
            mime_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, mime_type, "utf-8"))
            
            # Send email
            smtp_config = self.config.get_smtp_config()
            await aiosmtplib.send(message, **smtp_config)
            
            logger.info(f"Email sent successfully to {self._sanitize_email(recipient)}")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': '_send_single_email',
                'recipient': self._sanitize_email(recipient)
            })
            return False
    
    def _sanitize_email(self, email: str) -> str:
        """Sanitize email for logging."""
        if not email or '@' not in email:
            return '[invalid_email]'
        username, domain = email.split('@', 1)
        sanitized = username[:2] + '*' * max(0, len(username) - 2)
        return f"{sanitized}@{domain}"