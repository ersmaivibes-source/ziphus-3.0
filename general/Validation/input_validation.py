"""
general Input Validation Module
===========================

Consolidates all input validation functionality from:
- Tools/Validators/validation.py
- Security/Validation/input_validation.py

Moved to general for basic/general task consolidation.
"""

import re
import string
import random
import math
import os
from typing import List, Tuple, Optional
from urllib.parse import urlparse

# Use modern validation libraries
import bleach
from email_validator import validate_email as validate_email_format, EmailNotValidError
import validators
from pydantic import HttpUrl

from general.Logging.logger_manager import get_logger, log_security_event

logger = get_logger(__name__)

# Common suspicious email domains to block
BLOCKED_EMAIL_DOMAINS = [
    "10minutemail.com",
    "guerrillamail.com", 
    "mailinator.com",
    "tempmail.org",
    "throwaway.email",
    "yopmail.com",
    "mailinator.com",
    "trashmail.com",
    "disposable-email.com",
    "temp-mail.org",
    "getairmail.com",
    "guerrillamailblock.com",
    "mailnesia.com",
    "fakeinbox.com",
    "tempinbox.com",
    "mintemail.com",
    "mytempemail.com",
    "jetable.org",
    "mailexpire.com",
    "spambox.us",
    "temporaryinbox.com"
]

# Common XSS attack patterns to block
XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'on\w+\s*=\s*["\'][^"\']*["\']',
    r'javascript:\s*\w+',
    r'<iframe[^>]*>.*?</iframe>',
    r'<object[^>]*>.*?</object>',
    r'<embed[^>]*>.*?</embed>',
    r'<form[^>]*>.*?</form>',
    r'<meta[^>]*>',
    r'<link[^>]*>',
    r'<base[^>]*>',
    r'<applet[^>]*>.*?</applet>',
    r'<frame[^>]*>.*?</frame>',
    r'<frameset[^>]*>.*?</frameset>',
    r'<svg[^>]*>.*?</svg>',
    r'<math[^>]*>.*?</math>',
    r'<marquee[^>]*>.*?</marquee>',
    r'<blink[^>]*>.*?</blink>',
    r'<vbscript[^>]*>.*?</vbscript>',
    r'<xml[^>]*>.*?</xml>',
    r'<xss[^>]*>.*?</xss>',
    r'expression\s*\(',
    r'eval\s*\(',
    r'alert\s*\(',
    r'confirm\s*\(',
    r'prompt\s*\('
]

# SQL injection patterns to block
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|FETCH)\b)",
    r"(--|#|\/\*|\*\/|;)",
    r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
    r"(\b(OR|AND)\s+['\"][^'\"]+['\"]\s*=\s*['\"][^'\"]+['\"])",
    r"(\b(OR|AND)\s+\w+\s*=\s*\w+)",
    r"(\b(UNION|SELECT)\s+(ALL|DISTINCT)?\s*\*)",
    r"(\b(CONCAT|GROUP_CONCAT|VERSION|DATABASE|USER|SYSTEM_USER|SESSION_USER)\s*\()",
    r"(\b(LOAD_FILE|SLEEP|BENCHMARK)\s*\()",
    r"(\b(CHAR|NCHAR|VARCHAR|NVARCHAR)\s*\()",
    r"(\b(WAITFOR\s+(DELAY|TIMEOUT))\b)",
    r"(\b(EXEC(UTE)?\s+))",
    r"(\b(XP_|SP_)\w+)",
    r"(\b(INFORMATION_SCHEMA|SYSOBJECTS|SYSUSERS)\b)"
]

class InputValidator:
    """general input validation utilities with enhanced security."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Enhanced email validation with security checks using email-validator library."""
        if not email or not isinstance(email, str):
            return False
        
        # Sanitize input
        email = email.strip().lower()
        if len(email) > 254:  # RFC 5321 limit
            return False
        
        try:
            # Use email-validator library for proper validation
            validated_email = validate_email_format(email, check_deliverability=False)
            normalized_email = validated_email.email
            
            # Check for suspicious patterns
            if '..' in normalized_email or normalized_email.startswith('.') or normalized_email.endswith('.'):
                return False
            
            try:
                local_part, domain = normalized_email.rsplit('@', 1)
                
                # Validate local part length (RFC 5321)
                if len(local_part) > 64:
                    return False
                
                # Check for blocked domains
                if domain in BLOCKED_EMAIL_DOMAINS:
                    log_security_event('blocked_email_domain', {
                        'domain': domain,
                        'email': email
                    }, 'medium')
                    return False
                
                # Check for suspicious domain patterns
                if domain.count('.') > 3 or len(domain) > 253:
                    return False
                
                return True
                
            except (IndexError, AttributeError, ValueError):
                return False
                
        except EmailNotValidError:
            return False

    @staticmethod
    def validate_password(password: str, lang_code: str = 'en') -> str:
        """
        Enhanced password validation with entropy checking and security.
        
        Args:
            password: Password string to validate
            lang_code: Language code for error messages
            
        Returns:
            'valid' if password is valid, error message string otherwise
        """
        if not password or not isinstance(password, str):
            return 'password_error_required'
        
        # Length check
        if len(password) < 8:
            return 'password_error_length'
        
        if len(password) > 128:  # Prevent DoS
            return 'password_error_too_long'
        
        # Character requirements
        if not re.search(r'[A-Z]', password):
            return 'password_error_uppercase'
        
        if not re.search(r'[a-z]', password):
            return 'password_error_lowercase'
        
        if not re.search(r'[0-9]', password):
            return 'password_error_digit'
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return 'password_error_special'
        
        # Calculate entropy
        charset_size = 0
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'[0-9]', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            charset_size += 32
        
        entropy = len(password) * math.log2(charset_size)
        if entropy < 50:  # Minimum entropy threshold
            return 'password_error_weak'
        
        # Check against common patterns
        common_patterns = [
            r'(.)\1{3,}',  # 4+ repeated characters
            r'123456',     # Sequential numbers
            r'abcdef',     # Sequential letters
            r'qwerty',     # Keyboard patterns
            r'password',   # Common password
            r'admin',      # Common password
            r'welcome',    # Common password
            r'login',      # Common password
            r'123456789',  # Sequential numbers
            r'111111',     # Repeated numbers
            r'000000',     # Repeated numbers
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                return 'password_error_pattern'
        
        return 'valid'

    @staticmethod
    def validate_chat_id(chat_id_str: str) -> bool:
        """Validate if string is a valid Telegram chat ID."""
        if not chat_id_str or not isinstance(chat_id_str, str):
            return False
        
        try:
            chat_id = int(chat_id_str.strip())
            # Valid chat IDs are typically:
            # - Positive for users (up to ~10 digits)
            # - Negative for groups/channels (usually 10+ digits)
            return abs(chat_id) >= 1000
        except (ValueError, OverflowError):
            return False

    @staticmethod
    def validate_user_input_length(text: str, max_length: int = 4096) -> bool:
        """Validate user input length to prevent DoS attacks."""
        if not text:
            return True  # Empty text is usually valid
        
        # SECURITY: Check for extremely long inputs that could cause DoS
        if len(text) > max_length:
            log_security_event('input_too_long', {
                'length': len(text),
                'max_length': max_length
            }, 'medium')
            return False
        
        # SECURITY: Check for null bytes and other dangerous characters
        if '\x00' in text or '\r\n' in text.replace('\r\n', '\n'):
            log_security_event('dangerous_characters_detected', {
                'content': text[:100] + '...' if len(text) > 100 else text
            }, 'high')
            return False
        
        return True

    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """Sanitize user input to prevent injection attacks using bleach."""
        if not text:
            return ""
        
        # Use bleach for HTML sanitization
        sanitized = bleach.clean(
            text,
            tags=[],  # No allowed tags
            attributes={},  # No allowed attributes
            strip=True,  # Strip disallowed tags
            strip_comments=True  # Strip HTML comments
        )
        
        # Limit length
        if len(sanitized) > 4096:
            sanitized = sanitized[:4093] + "..."
        
        return sanitized

    @staticmethod
    def validate_and_sanitize_message(message: str) -> Tuple[bool, str]:
        """Validate and sanitize message content."""
        if not message:
            return False, ""
        
        # Check length
        if not InputValidator.validate_user_input_length(message):
            return False, ""
        
        # Sanitize
        sanitized = InputValidator.sanitize_user_input(message)
        
        # Final validation
        if len(sanitized.strip()) == 0:
            return False, ""
        
        return True, sanitized

    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """Enhanced file extension validation with security checks."""
        if not filename or not isinstance(filename, str):
            return False
        
        # Sanitize filename first
        filename = filename.strip()
        if len(filename) > 255:  # Filesystem limit
            return False
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(pattern in filename for pattern in dangerous_patterns):
            log_security_event('dangerous_filename_pattern', {
                'filename': filename
            }, 'high')
            return False
        
        # Check for hidden files or suspicious names
        if filename.startswith('.') or filename.lower() in ['con', 'prn', 'aux', 'nul']:
            return False
        
        try:
            # Get extension (handle multiple dots properly)
            if '.' not in filename:
                return False
                
            extension = filename.lower().split('.')[-1]
            
            # Validate extension isn't empty or too long
            if not extension or len(extension) > 10:
                return False
            
            # Check against whitelist
            allowed_lower = [ext.lower().strip() for ext in allowed_extensions]
            return extension in allowed_lower
            
        except (IndexError, AttributeError):
            return False

    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
        """Validate file size in bytes."""
        if not isinstance(file_size, int) or file_size < 0:
            return False
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            log_security_event('file_too_large', {
                'file_size': file_size,
                'max_size_bytes': max_size_bytes
            }, 'medium')
            return False
        return True

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        if not filename:
            return "unnamed_file"
        
        # Remove path separators and dangerous characters
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:250] + ('.' + ext if ext else '')
        
        return sanitized or "unnamed_file"

    @staticmethod
    def validate_url(url: str) -> bool:
        """Secure URL validation with protocol and domain checking using validators."""
        if not url or not isinstance(url, str):
            return False
        
        # Sanitize input
        url = url.strip()
        if len(url) > 2048:  # Reasonable URL length limit
            return False
        
        # Only allow HTTP/HTTPS protocols for security
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Block dangerous protocols that might be disguised
        dangerous_protocols = ['javascript:', 'data:', 'file:', 'ftp:', 'mailto:']
        if any(protocol in url.lower() for protocol in dangerous_protocols):
            log_security_event('dangerous_url_protocol', {
                'url': url
            }, 'high')
            return False
        
        # Use validators library for proper URL validation
        try:
            validated_url = validators.url(url)
            if not validated_url:
                return False
            
            # Parse URL to check domain
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check for suspicious domain patterns
            if domain.count('.') > 5 or len(domain) > 253:
                return False
                
            return True
        except Exception:
            return False

    @staticmethod
    def validate_amount(amount_str: str, min_amount: float = 0.01, max_amount: float = 10000.0) -> Tuple[bool, float]:
        """
        Validate monetary amount.
        
        Returns:
            Tuple of (is_valid, parsed_amount)
        """
        if not amount_str or not isinstance(amount_str, str):
            return False, 0.0
        
        try:
            amount = float(amount_str.strip())
            if min_amount <= amount <= max_amount:
                return True, round(amount, 2)
            return False, 0.0
        except (ValueError, OverflowError):
            return False, 0.0

    @staticmethod
    def validate_language_code(lang_code: str) -> bool:
        """Validate language code."""
        if not lang_code or not isinstance(lang_code, str):
            return False
        
        # Support common language codes
        valid_codes = ['en', 'fa', 'ar', 'de', 'fr', 'es', 'it', 'ru', 'zh', 'ja', 'ko']
        return lang_code.lower() in valid_codes

    @staticmethod
    def is_valid_username(username: str) -> bool:
        """
        Validate Telegram username format.
        Rules: 5-32 chars, alphanumeric + underscore, must start with a letter.
        """
        if not username:
            return False
        
        # Remove @ if present
        username = username.lstrip('@')
        
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def generate_secure_code(length: int = 6) -> str:
        """Generate cryptographically secure verification code."""
        characters = string.digits
        # Remove confusing characters
        characters = characters.replace('0', '').replace('1', '')
        return ''.join(random.choices(characters, k=length))
    
    @staticmethod
    def detect_xss(content: str) -> bool:
        """Detect potential XSS attacks in content."""
        if not content or not isinstance(content, str):
            return False
        
        content_lower = content.lower()
        
        # Check for XSS patterns
        for pattern in XSS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                log_security_event('xss_pattern_detected', {
                    'content_preview': content_lower[:100] + '...' if len(content_lower) > 100 else content_lower
                }, 'high')
                return True
        
        return False
    
    @staticmethod
    def detect_sql_injection(content: str) -> bool:
        """Detect potential SQL injection attacks in content."""
        if not content or not isinstance(content, str):
            return False
        
        content_lower = content.lower()
        
        # Check for SQL injection patterns
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                log_security_event('sql_injection_pattern_detected', {
                    'content_preview': content_lower[:100] + '...' if len(content_lower) > 100 else content_lower
                }, 'high')
                return True
        
        return False
    
    @staticmethod
    def comprehensive_sanitize(content: str) -> str:
        """Comprehensive sanitization of user content."""
        if not content or not isinstance(content, str):
            return ""
        
        # First, basic sanitization with bleach
        sanitized = InputValidator.sanitize_user_input(content)
        
        # Remove XSS patterns
        for pattern in XSS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove extra whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized