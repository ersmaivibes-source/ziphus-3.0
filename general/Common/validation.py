"""
Validation utilities for user input validation.
Extracted from the original utils.py for better modularity.
"""

from general.Validation.input_validation import InputValidator
from general.Logging.logger_manager import get_logger

# Re-export all functions for backward compatibility
validate_email = InputValidator.validate_email
validate_password = InputValidator.validate_password
generate_verification_code = InputValidator.generate_secure_code

# For backward compatibility, re-export the functions
__all__ = ['validate_email', 'validate_password', 'generate_verification_code']

import re
import string
import random
from typing import List

logger = get_logger(__name__)

# Common suspicious email domains to block
BLOCKED_EMAIL_DOMAINS = [
    "10minutemail.com",
    "guerrillamail.com", 
    "mailinator.com",
    "tempmail.org",
    "throwaway.email"
]

def validate_email(email: str) -> bool:
    """Enhanced email validation with security checks."""
    if not email or not isinstance(email, str):
        return False
    
    # Sanitize input
    email = email.strip().lower()
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    # Enhanced email regex validation
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$"
    if not re.match(email_regex, email):
        return False
    
    # Check for suspicious patterns
    if '..' in email or email.startswith('.') or email.endswith('.'):
        return False
    
    try:
        local_part, domain = email.rsplit('@', 1)
        
        # Validate local part length (RFC 5321)
        if len(local_part) > 64:
            return False
        
        # Check for blocked domains
        if domain in BLOCKED_EMAIL_DOMAINS:
            return False
        
        # Check for suspicious domain patterns
        if domain.count('.') > 3 or len(domain) > 253:
            return False
        
        return True
        
    except (IndexError, AttributeError, ValueError):
        return False

def validate_password(password: str, lang_code: str = 'en') -> str:
    """
    Enhanced password validation with entropy checking and security.
    
    Args:
        password: Password string to validate
        lang_code: Language code for error messages
        
    Returns:
        'valid' if password is valid, error message string otherwise
    """
    import math
    from general.Language.Translations import get_text_sync
    
    if not password or not isinstance(password, str):
        return get_text_sync('password_error_empty', lang_code or "en")
    
    # Increased minimum length for better security
    if len(password) < 12:
        return get_text_sync('password_error_length', lang_code or "en")
    
    if len(password) > 128:
        return get_text_sync('password_error_too_long', lang_code or "en")
    
    # Check for null bytes and other dangerous characters
    if '\x00' in password or any(ord(c) < 32 for c in password if c not in '\t\n\r'):
        return get_text_sync('password_error_chars', lang_code or "en")
    
    # Character set validation
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))  
    has_digit = bool(re.search(r"[0-9]", password))
    has_special = bool(re.search(r"[\?\!\@\$\*\(\)\-\_\.\+\=\#\%\^\&]", password))
    
    # Require at least 3 of 4 character types
    char_types = sum([has_upper, has_lower, has_digit, has_special])
    if char_types < 3:
        return get_text_sync('password_error_complexity', lang_code or "en")
    
    # Calculate password entropy for strength assessment
    char_space = 0
    if has_lower: char_space += 26
    if has_upper: char_space += 26  
    if has_digit: char_space += 10
    if has_special: char_space += 20
    
    entropy = len(password) * math.log2(char_space) if char_space > 0 else 0
    if entropy < 50:  # Require minimum entropy
        return get_text_sync('password_error_weak', lang_code or "en")
    
    # Enhanced weak password detection
    password_lower = password.lower()
    weak_patterns = [
        'password', '12345678', 'qwerty123', 'abc123', 'password123',
        '123456789', 'welcome123', 'admin123', 'user123', 'letmein',
        'monkey123', 'dragon123', 'master123', 'superman123'
    ]
    
    # Check for weak patterns in password
    for weak in weak_patterns:
        if weak in password_lower:
            return get_text_sync('password_error_weak', lang_code or "en")
    
    # Check for repeated character patterns
    if re.search(r'(.)\1{2,}', password):  # 3+ consecutive same chars
        return get_text_sync('password_error_repetitive', lang_code or "en")
    
    # Check for sequential patterns
    sequential_patterns = ['123', '234', '345', '456', '789', 'abc', 'bcd', 'cde']
    for pattern in sequential_patterns:
        if pattern in password_lower:
            return get_text_sync('password_error_sequential', lang_code or "en")
    
    return "valid"

def generate_verification_code(length: int = 8) -> str:
    """Generate a random verification code."""
    characters = string.ascii_uppercase + string.digits
    # Exclude similar looking characters to avoid confusion
    characters = characters.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(random.choices(characters, k=length))

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

def validate_user_input_length(text: str, max_length: int = 4096) -> bool:
    """Validate user input length to prevent DoS attacks."""
    if not text:
        return True  # Empty text is usually valid
    
    # SECURITY: Check for extremely long inputs that could cause DoS
    if len(text) > max_length:
        return False
    
    # SECURITY: Check for null bytes and other dangerous characters
    if '\x00' in text or '\r\n' in text.replace('\r\n', '\n'):
        return False
    
    return True

def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove null bytes and control characters except newlines and tabs
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Limit length
    if len(sanitized) > 4096:
        sanitized = sanitized[:4093] + "..."
    
    return sanitized

def validate_and_sanitize_message(message: str) -> tuple[bool, str]:
    """Validate and sanitize message content."""
    if not message:
        return False, ""
    
    # Check length
    if not validate_user_input_length(message):
        return False, ""
    
    # Sanitize
    sanitized = sanitize_user_input(message)
    
    # Final validation
    if len(sanitized.strip()) == 0:
        return False, ""
    
    return True, sanitized

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

def validate_file_security(file_path: str, allowed_extensions: List[str], check_content: bool = True) -> bool:
    """Comprehensive file validation including content checking."""
    import os
    
    if not file_path or not os.path.exists(file_path):
        return False
    
    filename = os.path.basename(file_path)
    
    # Basic extension validation
    if not validate_file_extension(filename, allowed_extensions):
        return False
    
    # File size check
    try:
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            return False
        if file_size == 0:  # Empty files are suspicious
            return False
    except OSError:
        return False
    
    if not check_content:
        return True
    
    # Simplified file validation
    try:
        extension = filename.lower().split('.')[-1]
        
        # Define expected MIME types
        mime_mapping = {
            'jpg': b'\xff\xd8\xff',
            'jpeg': b'\xff\xd8\xff', 
            'png': b'\x89\x50\x4e\x47',
            'gif': b'\x47\x49\x46\x38',
            'pdf': b'\x25\x50\x44\x46',
            'txt': None,  # Text files have no specific header
            'json': None,
            'xml': None
        }
        
        expected_header = mime_mapping.get(extension)
        if expected_header is not None:
            with open(file_path, 'rb') as f:
                file_header = f.read(len(expected_header))
                if not file_header.startswith(expected_header):
                    return False
        
        # Additional checks for potentially dangerous content
        if extension in ['txt', 'json', 'xml']:
            with open(file_path, 'rb') as f:
                content = f.read(8192)  # Read first 8KB
                
                # Check for binary content in text files
                if b'\x00' in content:  # Null bytes indicate binary
                    return False
                
                # Suspicious patterns detection
                suspicious_patterns = [
                    b'<script', b'javascript:', b'vbscript:', 
                    b'onload=', b'onerror=', b'eval(',
                    b'<?php', b'<%', b'${', b'#{',  # Server-side code
                    b'\x00', b'\xff\xfe', b'\xfe\xff'  # Binary markers
                ]
                content_lower = content.lower()
                if any(pattern in content_lower for pattern in suspicious_patterns):
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"File security validation failed: {e}")
        return False

def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
    """Validate file size in bytes."""
    if not isinstance(file_size, int) or file_size < 0:
        return False
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes

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

def validate_url(url: str) -> bool:
    """Secure URL validation with protocol and domain checking."""
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
        return False
    
    # Enhanced URL pattern validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP address
        r'(?::\d+)?'  # optional port
        r'(?:/[^\s]*)?$', re.IGNORECASE  # path (fixed regex)
    )
    
    if not url_pattern.match(url):
        return False
    
    # Block suspicious/malicious domains
    suspicious_domains = [
        'bit.ly', 'tinyurl.com', 'short.link', 'tiny.one',
        'rebrand.ly', 'is.gd', 'ow.ly', 'buff.ly'
    ]
    
    try:
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Check against suspicious domains
        if any(suspicious in domain for suspicious in suspicious_domains):
            return False
        
        # Check for suspicious patterns
        if domain.count('.') > 4:  # Too many subdomains
            return False
        
        # Check for IP addresses in suspicious ranges
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
            octets = [int(x) for x in domain.split('.')]
            # Block common malicious IP ranges
            if octets[0] in [0, 127, 169, 224, 240] or octets[0] >= 240:
                return False
        
        return True
        
    except Exception:
        return False

def validate_amount(amount_str: str, min_amount: float = 0.01, max_amount: float = 10000.0) -> tuple[bool, float]:
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

def validate_language_code(lang_code: str) -> bool:
    """Validate language code."""
    if not lang_code or not isinstance(lang_code, str):
        return False
    
    # Support common language codes
    valid_codes = ['en', 'fa', 'ar', 'de', 'fr', 'es', 'it', 'ru', 'zh', 'ja', 'ko']
    return lang_code.lower() in valid_codes

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

def validate_phone_number(phone: str) -> bool:
    """Basic phone number validation."""
    if not phone:
        return False
        
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits and has a reasonable length
    return phone.isdigit() and 7 <= len(phone) <= 15

def is_valid_email_domain(email: str, allowed_domains: List[str]) -> bool:
    """Check if the email domain is in the allowed list."""
    if not email or '@' not in email:
        return False
    
    domain = email.split('@')[-1].lower()
    return domain in [d.lower() for d in allowed_domains]