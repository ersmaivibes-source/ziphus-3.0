"""
Common Utilities Consolidation
==============================

Consolidates all basic utilities from common/base.py and Tools/Helpers/.
Moved from scattered locations for better organization.
"""

import asyncio
import uuid
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, List, Any, Tuple
from pathlib import Path

from general.Logging.logger_manager import get_logger
from general.Error.error_manager import get_error_manager

logger = get_logger(__name__)
error_manager = get_error_manager()


class CommonUtils:
    """Consolidated common utilities for the bot."""
    
    # === SAFE HANDLER UTILITIES ===
    
    @staticmethod
    def inject_user_and_lang(func: Callable) -> Callable:
        """Decorator to inject user data and language code."""
        async def wrapper(*args, **kwargs):
            try:
                # For now, just pass through - can implement user injection later
                return await func(*args, **kwargs)
            except Exception as e:
                await error_manager.handle_error(e, {'decorator': 'inject_user_and_lang'})
                raise
        return wrapper
    
    # === SECURITY UTILITIES ===
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input."""
        if not text:
            return ""
        # Basic sanitization
        return text.strip()[:1000]  # Limit length and strip whitespace
    
    @staticmethod
    def validate_crypto_address(address: str, crypto_type: str) -> bool:
        """Validate cryptocurrency address format."""
        if not address or not isinstance(address, str):
            return False
        
        crypto_patterns = {
            'btc': r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$',
            'eth': r'^0x[a-fA-F0-9]{40}$',
            'usdt': r'^0x[a-fA-F0-9]{40}$|^T[A-Za-z1-9]{33}$'
        }
        
        pattern = crypto_patterns.get(crypto_type.lower())
        if not pattern:
            return False
        
        return bool(re.match(pattern, address))
    
    # === ID GENERATION ===
    
    @staticmethod
    def generate_unique_id(prefix: str = "") -> str:
        """Generate a unique ID with optional prefix."""
        return f"{prefix}{uuid.uuid4().hex[:12].upper()}"
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate short alphanumeric ID."""
        import string
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_verification_code(length: int = 8) -> str:
        """Generate a random verification code."""
        import string
        characters = string.ascii_uppercase + string.digits
        # Exclude similar looking characters to avoid confusion
        characters = characters.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    # === FILE UTILITIES ===
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
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
    def create_backup_filename(original: str) -> str:
        """Create backup filename with timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = original.rsplit('.', 1) if '.' in original else (original, '')
        return f"{name}_backup_{timestamp}.{ext}" if ext else f"{original}_backup_{timestamp}"
    
    @staticmethod
    def create_temp_filename(prefix: str = "temp", extension: str = "tmp") -> str:
        """Create temporary filename."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_id = CommonUtils.generate_short_id(6)
        return f"{prefix}_{timestamp}_{random_id}.{extension}"
    
    # === TEXT UTILITIES ===
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length."""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison."""
        import unicodedata
        text = unicodedata.normalize('NFKD', text)
        text = text.lower()
        text = ' '.join(text.split())
        return text
    
    @staticmethod
    def extract_urls_from_text(text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    # === DATE/TIME UTILITIES ===
    
    @staticmethod
    def parse_duration(duration_str: str) -> Optional[timedelta]:
        """Parse duration string (e.g., '1h', '30m', '5d') to timedelta."""
        pattern = r'^(\d+)([smhdw])$'
        match = re.match(pattern, duration_str.lower())
        
        if not match:
            return None
        
        value, unit = match.groups()
        value = int(value)
        
        unit_mapping = {
            's': 'seconds',
            'm': 'minutes', 
            'h': 'hours',
            'd': 'days',
            'w': 'weeks'
        }
        
        if unit not in unit_mapping:
            return None
        
        return timedelta(**{unit_mapping[unit]: value})
    
    @staticmethod
    def format_datetime(dt: datetime, format_type: str = 'default') -> str:
        """Format datetime with different format types."""
        formats = {
            'default': '%Y-%m-%d %H:%M:%S',
            'date_only': '%Y-%m-%d',
            'time_only': '%H:%M:%S',
            'human': '%B %d, %Y at %H:%M',
            'compact': '%d/%m/%y %H:%M'
        }
        
        return dt.strftime(formats.get(format_type, formats['default']))
    
    @staticmethod
    def is_weekend(date: datetime = None) -> bool:
        """Check if date is weekend."""
        if date is None:
            date = datetime.now()
        return date.weekday() >= 5
    
    @staticmethod
    def get_season(date: datetime = None) -> str:
        """Get season for given date."""
        if date is None:
            date = datetime.now()
        
        month = date.month
        day = date.day
        
        if (month == 12 and day >= 21) or month in [1, 2] or (month == 3 and day < 20):
            return 'Winter'
        elif (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
            return 'Spring'
        elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 22):
            return 'Summer'
        else:
            return 'Autumn'
    
    # === COMMAND PARSING ===
    
    @staticmethod
    def parse_command_args(text: str) -> Tuple[str, List[str]]:
        """Parse command and arguments from text."""
        parts = text.split()
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        return command, args
    
    # === VALIDATION HELPERS ===
    
    @staticmethod
    def is_valid_user_input_length(text: str, max_length: int = 4096) -> bool:
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


class MessageUtils:
    """Message handling utilities."""
    
    @staticmethod
    def split_message(text: str, max_length: int = 4096) -> List[str]:
        """Split a long message into multiple parts."""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current_part = ""
        
        # Split by lines first to preserve formatting
        lines = text.split('\n')
        
        for line in lines:
            # If a single line is too long, split it by words
            if len(line) > max_length:
                words = line.split(' ')
                for word in words:
                    if len(current_part) + len(word) + 1 <= max_length:
                        current_part += (" " if current_part else "") + word
                    else:
                        if current_part:
                            parts.append(current_part)
                            current_part = word
                        else:
                            # Single word longer than max_length
                            parts.append(word[:max_length])
                            current_part = word[max_length:]
            else:
                if len(current_part) + len(line) + 1 <= max_length:
                    current_part += ("\n" if current_part else "") + line
                else:
                    if current_part:
                        parts.append(current_part)
                    current_part = line
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    @staticmethod
    def format_user_mention(user_id: int, name: str = None, use_markdown: bool = True) -> str:
        """Format a user mention."""
        display_name = name or f"User{user_id}"
        if use_markdown:
            return f'[{display_name}](tg://user?id={user_id})'
        else:
            return f'<a href="tg://user?id={user_id}">{display_name}</a>'
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape markdown special characters."""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    @staticmethod
    def strip_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)