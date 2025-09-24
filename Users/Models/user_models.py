"""
Enhanced user-related data models for Users domain.
Consolidated and moved from general/Framework/Models/user_models.py
"""

from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserProfile:
    """User profile data class."""
    chat_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    language_code: str = 'en'
    is_banned: bool = False
    role: str = 'user'
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    stars: int = 0
    total_referrals: int = 0
    subscription_plan: str = 'free'
    subscription_end_date: Optional[datetime] = None
    
    @classmethod
    def from_db_data(cls, data: Dict) -> 'UserProfile':
        """Create UserProfile from database data."""
        return cls(
            chat_id=data.get('Chat_ID'),
            first_name=data.get('First_Name'),
            last_name=data.get('Last_Name'),
            username=data.get('Username'),
            email=data.get('Email'),
            language_code=data.get('Language_Code', 'en'),
            is_banned=data.get('Is_Banned', False),
            role=data.get('Role', 'user'),
            created_at=data.get('Created_At'),
            last_login=data.get('Last_Login'),
            stars=data.get('Stars', 0),
            total_referrals=data.get('Total_Referrals', 0),
            subscription_plan=data.get('Subscription_Plan', 'free'),
            subscription_end_date=data.get('Subscription_End_Date')
        )
    
    def to_dict(self) -> Dict:
        """Convert user profile to dictionary."""
        return {
            'Chat_ID': self.chat_id,
            'First_Name': self.first_name,
            'Last_Name': self.last_name,
            'Username': self.username,
            'Email': self.email,
            'Language_Code': self.language_code,
            'Is_Banned': self.is_banned,
            'Role': self.role,
            'Created_At': self.created_at,
            'Last_Login': self.last_login,
            'Stars': self.stars,
            'Total_Referrals': self.total_referrals,
            'Subscription_Plan': self.subscription_plan,
            'Subscription_End_Date': self.subscription_end_date
        }
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def display_name(self) -> str:
        """Get user's display name (username or full name)."""
        if self.username:
            return f"@{self.username}"
        return self.full_name
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription."""
        if not self.subscription_end_date:
            return False
        return datetime.now() < self.subscription_end_date
    
    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return not self.is_banned


class User:
    """User model for the Telegram bot (legacy compatibility)."""
    
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
        self.email = data.get('Email')
        self.stars = data.get('Stars', 0)
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return {
            'Chat_ID': self.chat_id,
            'First_Name': self.first_name,
            'Last_Name': self.last_name,
            'Username': self.username,
            'Email': self.email,
            'Language_Code': self.language_code,
            'Is_Banned': self.is_banned,
            'Role': self.role,
            'Created_At': self.created_at,
            'Last_Login': self.last_login,
            'Stars': self.stars
        }
    
    def to_profile(self) -> UserProfile:
        """Convert to UserProfile object."""
        return UserProfile.from_db_data(self.to_dict())


@dataclass
class UserStatistics:
    """User statistics and analytics data."""
    user_id: int
    total_logins: int = 0
    features_used: Dict[str, int] = None
    last_activity: Optional[datetime] = None
    account_age_days: int = 0
    referrals_made: int = 0
    stars_earned: int = 0
    subscription_history: List[Dict] = None
    
    def __post_init__(self):
        if self.features_used is None:
            self.features_used = {}
        if self.subscription_history is None:
            self.subscription_history = []


@dataclass
class UserSession:
    """User session information."""
    user_id: int
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    
    @property
    def duration_minutes(self) -> int:
        """Get session duration in minutes."""
        return int((self.last_activity - self.created_at).total_seconds() / 60)
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired (inactive for 60+ minutes)."""
        inactive_minutes = int((datetime.now() - self.last_activity).total_seconds() / 60)
        return inactive_minutes >= 60


@dataclass
class UserPreferences:
    """User preferences and settings."""
    user_id: int
    language_code: str = 'en'
    timezone: str = 'UTC'
    notification_settings: Dict[str, bool] = None
    theme_preference: str = 'default'
    privacy_settings: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.notification_settings is None:
            self.notification_settings = {
                'email_notifications': True,
                'push_notifications': True,
                'marketing_emails': False,
                'referral_notifications': True
            }
        if self.privacy_settings is None:
            self.privacy_settings = {
                'show_in_leaderboard': True,
                'allow_referral_tracking': True,
                'share_analytics': False
            }