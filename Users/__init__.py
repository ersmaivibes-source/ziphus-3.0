"""
Users Module
Consolidated user-related functionality following ULTIMATE_ARCHITECTURE_DESIGN pattern
"""

# Import all user services and components
from .Authentication.user_auth_service import UserAuthService
from .Management.user_management_service import UserManagementService
from .Restrictions.user_limiter import UserLimiter
from .Limits.user_limiter import UserLimiter as UserLimiterAlias  # Alias for backward compatibility
from .Subscriptions import UserSubscriptionService, SubscriptionLimitService
from .Referrals.referral_service import UserReferralService
from .Profiles.user_profile_service import UserProfileService
from .Models.user_models import UserProfile, UserPreferences, UserStatistics
from .Language import user_translations_en, user_translations_fa
from .Keyboard import (
    UserKeyboards, 
    UserMenuKeyboards, 
    UserSettingsKeyboards, 
    UserAccountKeyboards, 
    UserNavigationKeyboards
)

__all__ = [
    # Authentication
    'UserAuthService',
    
    # Management
    'UserManagementService',
    
    # Restrictions & Limits
    'UserLimiter',
    'UserLimiterAlias',
    
    # Subscriptions
    'UserSubscriptionService',
    'SubscriptionLimitService',
    
    # Referrals
    'UserReferralService',
    
    # Profiles
    'UserProfileService',
    
    # Models
    'UserProfile',
    'UserStatistics', 
    'UserPreferences',
    
    # Language
    'user_translations_en',
    'user_translations_fa',
    
    # Keyboards
    'UserKeyboards',
    'UserMenuKeyboards',
    'UserSettingsKeyboards', 
    'UserAccountKeyboards',
    'UserNavigationKeyboards'
]