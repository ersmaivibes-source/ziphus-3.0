"""
Admin Keyboard Module
Consolidated admin keyboard interfaces and components following ULTIMATE_ARCHITECTURE_DESIGN pattern.
"""

from .admin_keyboards import AdminKeyboards
from .admin_menu_keyboards import AdminMenuKeyboards
from .admin_user_keyboards import AdminUserKeyboards
from .admin_analytics_keyboards import AdminAnalyticsKeyboards
from .admin_system_keyboards import AdminSystemKeyboards
from .admin_ticket_keyboards import AdminTicketKeyboards

__all__ = [
    'AdminKeyboards',
    'AdminMenuKeyboards', 
    'AdminUserKeyboards',
    'AdminAnalyticsKeyboards',
    'AdminSystemKeyboards',
    'AdminTicketKeyboards'
]