"""
Helper utilities for the Ziphus Bot.
Contains common utility functions used across the application.
"""

import re
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple

from general.Logging.logger_manager import get_logger

logger = get_logger(__name__)

def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:12].upper()}"

def generate_short_id(length: int = 8) -> str:
    """Generate short alphanumeric ID."""
    import string
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_float = float(size_bytes)  # Convert to float for division
    while size_float >= 1024 and i < len(size_names) - 1:
        size_float /= 1024.0
        i += 1
    
    return f"{size_float:.1f} {size_names[i]}"

def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

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

def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date."""
    today = datetime.now().date()
    if isinstance(birth_date, datetime):
        birth_date_obj = birth_date.date()
    else:
        birth_date_obj = birth_date
    
    age = today.year - birth_date_obj.year
    if today.month < birth_date_obj.month or (today.month == birth_date_obj.month and today.day < birth_date_obj.day):
        age -= 1
    
    return age

def extract_chat_id_from_text(text: str) -> Optional[int]:
    """Extract chat ID from text (handles both positive and negative IDs)."""
    pattern = r'(-?\d{10,})'
    matches = re.findall(pattern, text)
    
    if matches:
        try:
            return int(matches[0])
        except ValueError:
            pass
    
    return None

def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    import html
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = html.unescape(clean_text)
    return clean_text.strip()

def escape_markdown(text: str) -> str:
    """Escape markdown special characters."""
    special_chars = ['\\', '*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage with zero division protection."""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with default."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with default."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def time_ago(dt: datetime) -> str:
    """Format datetime as 'time ago' string."""
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    days = diff.days
    
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds >= 3600:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds >= 60:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a text progress bar."""
    if total == 0:
        filled_length = length
    else:
        filled_length = int(length * current // total)
        
    bar = "█" * filled_length + "░" * (length - filled_length)
    percentage = calculate_percentage(current, total)
    
    return f"[{bar}] {percentage}%"

def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None

def rate_limit_key(user_id: int, action: str) -> str:
    """Generate rate limit key."""
    return f"rate_limit:{user_id}:{action}"

def create_file_hash(file_path: str) -> Optional[str]:
    """Create SHA256 hash of file."""
    try:
        import hashlib
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error creating file hash: {e}")
        return None

def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def is_image_file(filename: str) -> bool:
    """Check if file is an image based on extension."""
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    return get_file_extension(filename) in image_extensions

def is_video_file(filename: str) -> bool:
    """Check if file is a video based on extension."""
    video_extensions = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v']
    return get_file_extension(filename) in video_extensions

def is_audio_file(filename: str) -> bool:
    """Check if file is audio based on extension."""
    audio_extensions = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma']
    return get_file_extension(filename) in audio_extensions

def is_document_file(filename: str) -> bool:
    """Check if file is a document based on extension."""
    doc_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx']
    return get_file_extension(filename) in doc_extensions

def get_mime_type(filename: str) -> str:
    """Get MIME type based on file extension."""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'

def create_backup_filename(original: str) -> str:
    """Create backup filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = original.rsplit('.', 1) if '.' in original else (original, '')
    return f"{name}_backup_{timestamp}.{ext}" if ext else f"{original}_backup_{timestamp}"

def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    import unicodedata
    text = unicodedata.normalize('NFKD', text)
    text = text.lower()
    text = ' '.join(text.split())
    return text

def parse_command_args(text: str) -> Tuple[str, List[str]]:
    """Parse command and arguments from text."""
    parts = text.split()
    command = parts[0] if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return command, args

def is_weekend(date: Optional[datetime] = None) -> bool:
    """Check if date is weekend."""
    if date is None:
        date = datetime.now()
    return date.weekday() >= 5

def get_season(date: Optional[datetime] = None) -> str:
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

def create_temp_filename(prefix: str = "temp", extension: str = "tmp") -> str:
    """Create temporary filename."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_id = generate_short_id(6)
    return f"{prefix}_{timestamp}_{random_id}.{extension}"

class Timer:
    """Simple timer context manager."""
    
    def __init__(self, name: str = "Timer"):
        self.name = name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        if self.start_time:
            duration = self.end_time - self.start_time
            logger.debug(f"{self.name} took {duration.total_seconds():.3f} seconds")
    
    @property
    def elapsed(self) -> timedelta:
        """Get elapsed time."""
        if self.start_time is None:
            return timedelta(0)
        end = self.end_time or datetime.now()
        if self.start_time:
            return end - self.start_time
        return timedelta(0)