"""
User-related data models.
"""

from typing import Dict, Optional
from datetime import datetime

class User:
    """User model for the Telegram bot."""
    
    def __init__(self, data: Dict):
        self.chat_id = data.get('Chat_ID')
        self.first_name = data.get('First_Name')
        self.last_name = data.get('Last_Name')
        self.username = data.get('Username')
        self.language_code = data.get('Language_Code', 'en')
        self.is_banned = data.get('Is_Banned', False)
        self.role = data.get('Role', 'user')
        self.created_at = data.get('Created_At')
        self.last_login = data.get('Last_Login')
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            'Chat_ID': self.chat_id,
            'First_Name': self.first_name,
            'Last_Name': self.last_name,
            'Username': self.username,
            'Language_Code': self.language_code,
            'Is_Banned': self.is_banned,
            'Role': self.role,
            'Created_At': self.created_at,
            'Last_Login': self.last_login
        }