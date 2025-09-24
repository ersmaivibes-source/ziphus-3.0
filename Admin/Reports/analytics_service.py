"""
Advanced analytics service for admin panel.
Handles user analytics, chat analytics, referral analytics, and growth metrics.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger

logger = get_logger(__name__)

@dataclass
class UserAnalytics:
    """User analytics data structure."""
    total_users: int
    banned_users: int
    active_users: int
    new_users_today: int
    new_users_week: int
    new_users_month: int
    users_with_accounts: int
    growth_rate: float
    language_distribution: Dict[str, int]

@dataclass
class ChatAnalytics:
    """Chat analytics data structure."""
    total_chats: int
    channels: int
    groups: int
    private_chats: int
    chats_added_today: int
    chats_added_week: int
    chats_added_month: int
    total_members: int
    average_members_per_chat: float
    banned_chats: int

@dataclass
class ReferralAnalytics:
    """Referral analytics data structure."""
    total_referrals: int
    successful_referrals: int
    referrals_today: int
    referrals_week: int
    referrals_month: int
    stars_distributed: int
    top_referrers: List[Dict[str, Any]]
    success_rate: float

@dataclass
class GrowthAnalytics:
    """Growth analytics data structure."""
    period_days: int
    daily_registrations: List[Dict[str, Any]]
    daily_chat_additions: List[Dict[str, Any]]
    total_growth: int
    average_daily_growth: float
    peak_day: Dict[str, Any]

class AnalyticsService:
    """Service for handling advanced analytics operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.cache_timeout = 300  # 5 minutes cache
        self._cache = {}
        self._cache_timestamps = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache_timestamps:
            return False
        return (datetime.now() - self._cache_timestamps[key]).seconds < self.cache_timeout
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Set cache data with timestamp."""
        self._cache[key] = data
        self._cache_timestamps[key] = datetime.now()
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cached data if valid."""
        if self._is_cache_valid(key):
            return self._cache[key]
        return None

    async def get_user_analytics(self) -> UserAnalytics:
        """Get comprehensive user analytics."""
        cache_key = "user_analytics"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Get basic user counts
            total_users = await self.db.get_total_users()
            banned_users = await self.db.get_banned_users_count()
            
            # Get time-based user counts
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)
            
            new_users_today = await self.db.get_users_registered_after(today_start)
            new_users_week = await self.db.get_users_registered_after(week_start)
            new_users_month = await self.db.get_users_registered_after(month_start)
            
            # Get active users (users who logged in within last 7 days)
            active_cutoff = now - timedelta(days=7)
            active_users = await self.db.get_active_users_count(active_cutoff)
            
            # Get users with accounts (have email)
            users_with_accounts = await self.db.get_users_with_accounts_count()
            
            # Calculate growth rate (month over month)
            prev_month_start = month_start - timedelta(days=30)
            prev_month_users = await self.db.get_users_registered_between(prev_month_start, month_start)
            growth_rate = (new_users_month / max(prev_month_users, 1)) * 100 if prev_month_users > 0 else 0
            
            # Get language distribution
            language_distribution = await self.db.get_language_distribution()
            
            analytics = UserAnalytics(
                total_users=total_users,
                banned_users=banned_users,
                active_users=active_users,
                new_users_today=new_users_today,
                new_users_week=new_users_week,
                new_users_month=new_users_month,
                users_with_accounts=users_with_accounts,
                growth_rate=round(growth_rate, 2),
                language_distribution=language_distribution
            )
            
            self._set_cache(cache_key, analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            # Return empty analytics on error
            return UserAnalytics(0, 0, 0, 0, 0, 0, 0, 0.0, {})

    async def get_chat_analytics(self) -> ChatAnalytics:
        """Get comprehensive chat analytics."""
        cache_key = "chat_analytics"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Get total chats
            total_chats = await self.db.get_total_chats()
            banned_chats = await self.db.get_banned_chats_count()
            
            # Get chat type breakdown
            chat_types = await self.db.get_chat_type_breakdown()
            channels = chat_types.get('channel', 0)
            groups = chat_types.get('group', 0) + chat_types.get('supergroup', 0)
            private_chats = chat_types.get('private', 0)
            
            # Get time-based chat counts
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)
            
            chats_added_today = await self.db.get_chats_added_after(today_start)
            chats_added_week = await self.db.get_chats_added_after(week_start)
            chats_added_month = await self.db.get_chats_added_after(month_start)
            
            # Get member statistics
            total_members, average_members = await self.db.get_member_statistics()
            
            analytics = ChatAnalytics(
                total_chats=total_chats,
                channels=channels,
                groups=groups,
                private_chats=private_chats,
                chats_added_today=chats_added_today,
                chats_added_week=chats_added_week,
                chats_added_month=chats_added_month,
                total_members=total_members,
                average_members_per_chat=round(average_members, 2),
                banned_chats=banned_chats
            )
            
            self._set_cache(cache_key, analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting chat analytics: {e}")
            return ChatAnalytics(0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0)

    async def get_referral_analytics(self) -> ReferralAnalytics:
        """Get comprehensive referral analytics."""
        cache_key = "referral_analytics"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Get basic referral counts
            total_referrals = await self.db.get_total_referrals()
            successful_referrals = await self.db.get_successful_referrals_count()
            
            # Get time-based referral counts
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)
            
            referrals_today = await self.db.get_referrals_after(today_start)
            referrals_week = await self.db.get_referrals_after(week_start)
            referrals_month = await self.db.get_referrals_after(month_start)
            
            # Get stars distributed
            stars_distributed = await self.db.get_total_referral_stars()
            
            # Get top referrers
            top_referrers = await self.db.get_top_referrers(limit=10)
            
            # Calculate success rate
            success_rate = (successful_referrals / max(total_referrals, 1)) * 100 if total_referrals > 0 else 0
            
            analytics = ReferralAnalytics(
                total_referrals=total_referrals,
                successful_referrals=successful_referrals,
                referrals_today=referrals_today,
                referrals_week=referrals_week,
                referrals_month=referrals_month,
                stars_distributed=stars_distributed,
                top_referrers=top_referrers,
                success_rate=round(success_rate, 2)
            )
            
            self._set_cache(cache_key, analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting referral analytics: {e}")
            return ReferralAnalytics(0, 0, 0, 0, 0, 0, [], 0.0)

    async def get_growth_analytics(self, days: int = 30) -> GrowthAnalytics:
        """Get growth analytics for specified period."""
        cache_key = f"growth_analytics_{days}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = end_date - timedelta(days=days)
            
            # Get daily registration data
            daily_registrations = await self.db.get_daily_registrations(start_date, end_date)
            
            # Get daily chat additions
            daily_chat_additions = await self.db.get_daily_chat_additions(start_date, end_date)
            
            # Calculate totals and averages
            total_growth = sum(day['count'] for day in daily_registrations)
            average_daily_growth = total_growth / days if days > 0 else 0
            
            # Find peak day
            peak_day = max(daily_registrations, key=lambda x: x['count']) if daily_registrations else {'date': None, 'count': 0}
            
            analytics = GrowthAnalytics(
                period_days=days,
                daily_registrations=daily_registrations,
                daily_chat_additions=daily_chat_additions,
                total_growth=total_growth,
                average_daily_growth=round(average_daily_growth, 2),
                peak_day=peak_day
            )
            
            self._set_cache(cache_key, analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting growth analytics: {e}")
            return GrowthAnalytics(days, [], [], 0, 0.0, {'date': None, 'count': 0})

    async def get_feature_usage_stats(self) -> Dict[str, Any]:
        """Get feature usage statistics."""
        cache_key = "feature_usage_stats"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            stats = await self.db.get_feature_usage_statistics()
            self._set_cache(cache_key, stats)
            return stats
        except Exception as e:
            logger.error(f"Error getting feature usage stats: {e}")
            return {}

    async def refresh_analytics_cache(self) -> bool:
        """Refresh all analytics cache."""
        try:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.info("Analytics cache refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Error refreshing analytics cache: {e}")
            return False

    def format_user_analytics(self, analytics: UserAnalytics, lang_code: str = 'en') -> str:
        """Format user analytics for display."""
        if lang_code == 'fa':
            text = f"📊 **آمار کاربران**\n\n"
            text += f"👥 **کل کاربران:** {analytics.total_users:,}\n"
            text += f"🚫 **کاربران مسدود:** {analytics.banned_users:,}\n"
            text += f"🟢 **کاربران فعال:** {analytics.active_users:,}\n"
            text += f"📈 **کاربران جدید امروز:** {analytics.new_users_today:,}\n"
            text += f"📅 **کاربران جدید هفته:** {analytics.new_users_week:,}\n"
            text += f"🗓️ **کاربران جدید ماه:** {analytics.new_users_month:,}\n"
            text += f"📧 **کاربران با حساب:** {analytics.users_with_accounts:,}\n"
            text += f"📊 **نرخ رشد:** {analytics.growth_rate}%\n\n"
            
            if analytics.language_distribution:
                text += f"🌐 **توزیع زبان:**\n"
                for lang, count in sorted(analytics.language_distribution.items(), key=lambda x: x[1], reverse=True):
                    text += f"• {lang.upper()}: {count:,} کاربر\n"
        else:
            text = f"📊 **User Analytics**\n\n"
            text += f"👥 **Total Users:** {analytics.total_users:,}\n"
            text += f"🚫 **Banned Users:** {analytics.banned_users:,}\n"
            text += f"🟢 **Active Users:** {analytics.active_users:,}\n"
            text += f"📈 **New Users Today:** {analytics.new_users_today:,}\n"
            text += f"📅 **New Users This Week:** {analytics.new_users_week:,}\n"
            text += f"🗓️ **New Users This Month:** {analytics.new_users_month:,}\n"
            text += f"📧 **Users with Accounts:** {analytics.users_with_accounts:,}\n"
            text += f"📊 **Growth Rate:** {analytics.growth_rate}%\n\n"
            
            if analytics.language_distribution:
                text += f"🌐 **Language Distribution:**\n"
                for lang, count in sorted(analytics.language_distribution.items(), key=lambda x: x[1], reverse=True):
                    text += f"• {lang.upper()}: {count:,} users\n"
        
        return text

    def format_chat_analytics(self, analytics: ChatAnalytics, lang_code: str = 'en') -> str:
        """Format chat analytics for display."""
        if lang_code == 'fa':
            text = f"💬 **آمار چت‌ها**\n\n"
            text += f"📊 **کل چت‌ها:** {analytics.total_chats:,}\n"
            text += f"📢 **کانال‌ها:** {analytics.channels:,}\n"
            text += f"👥 **گروه‌ها:** {analytics.groups:,}\n"
            text += f"💬 **چت‌های خصوصی:** {analytics.private_chats:,}\n"
            text += f"🚫 **چت‌های مسدود:** {analytics.banned_chats:,}\n\n"
            text += f"📈 **چت‌های اضافه شده امروز:** {analytics.chats_added_today:,}\n"
            text += f"📅 **چت‌های اضافه شده هفته:** {analytics.chats_added_week:,}\n"
            text += f"🗓️ **چت‌های اضافه شده ماه:** {analytics.chats_added_month:,}\n\n"
            text += f"👤 **کل اعضا:** {analytics.total_members:,}\n"
            text += f"📊 **میانگین اعضا در چت:** {analytics.average_members_per_chat}"
        else:
            text = f"💬 **Chat Analytics**\n\n"
            text += f"📊 **Total Chats:** {analytics.total_chats:,}\n"
            text += f"📢 **Channels:** {analytics.channels:,}\n"
            text += f"👥 **Groups:** {analytics.groups:,}\n"
            text += f"💬 **Private Chats:** {analytics.private_chats:,}\n"
            text += f"🚫 **Banned Chats:** {analytics.banned_chats:,}\n\n"
            text += f"📈 **Chats Added Today:** {analytics.chats_added_today:,}\n"
            text += f"📅 **Chats Added This Week:** {analytics.chats_added_week:,}\n"
            text += f"🗓️ **Chats Added This Month:** {analytics.chats_added_month:,}\n\n"
            text += f"👤 **Total Members:** {analytics.total_members:,}\n"
            text += f"📊 **Average Members per Chat:** {analytics.average_members_per_chat}"
        
        return text

    def format_referral_analytics(self, analytics: ReferralAnalytics, lang_code: str = 'en') -> str:
        """Format referral analytics for display."""
        if lang_code == 'fa':
            text = f"🎯 **آمار معرفی‌ها**\n\n"
            text += f"🔗 **کل معرفی‌ها:** {analytics.total_referrals:,}\n"
            text += f"✅ **معرفی‌های موفق:** {analytics.successful_referrals:,}\n"
            text += f"📊 **نرخ موفقیت:** {analytics.success_rate}%\n\n"
            text += f"📈 **معرفی‌های امروز:** {analytics.referrals_today:,}\n"
            text += f"📅 **معرفی‌های هفته:** {analytics.referrals_week:,}\n"
            text += f"🗓️ **معرفی‌های ماه:** {analytics.referrals_month:,}\n\n"
            text += f"⭐ **ستاره‌های توزیع شده:** {analytics.stars_distributed:,}\n\n"
            
            if analytics.top_referrers:
                text += f"🏆 **برترین معرف‌ها:**\n"
                for i, referrer in enumerate(analytics.top_referrers[:5], 1):
                    name = referrer.get('First_Name', 'ناشناس')
                    count = referrer.get('referral_count', 0)
                    text += f"{i}. {name}: {count} معرفی\n"
        else:
            text = f"🎯 **Referral Analytics**\n\n"
            text += f"🔗 **Total Referrals:** {analytics.total_referrals:,}\n"
            text += f"✅ **Successful Referrals:** {analytics.successful_referrals:,}\n"
            text += f"📊 **Success Rate:** {analytics.success_rate}%\n\n"
            text += f"📈 **Referrals Today:** {analytics.referrals_today:,}\n"
            text += f"📅 **Referrals This Week:** {analytics.referrals_week:,}\n"
            text += f"🗓️ **Referrals This Month:** {analytics.referrals_month:,}\n\n"
            text += f"⭐ **Stars Distributed:** {analytics.stars_distributed:,}\n\n"
            
            if analytics.top_referrers:
                text += f"🏆 **Top Referrers:**\n"
                for i, referrer in enumerate(analytics.top_referrers[:5], 1):
                    name = referrer.get('First_Name', 'Unknown')
                    count = referrer.get('referral_count', 0)
                    text += f"{i}. {name}: {count} referrals\n"
        
        return text

    def format_growth_analytics(self, analytics: GrowthAnalytics, lang_code: str = 'en') -> str:
        """Format growth analytics for display."""
        if lang_code == 'fa':
            text = f"📈 **آمار رشد ({analytics.period_days} روز)**\n\n"
            text += f"👥 **کل رشد:** {analytics.total_growth:,} کاربر\n"
            text += f"📊 **میانگین رشد روزانه:** {analytics.average_daily_growth}\n"
            if analytics.peak_day and analytics.peak_day['date']:
                text += f"🏆 **بهترین روز:** {analytics.peak_day['date']} ({analytics.peak_day['count']} کاربر)\n\n"
            
            if len(analytics.daily_registrations) > 0:
                text += f"📅 **آخرین 7 روز:**\n"
                for day in analytics.daily_registrations[-7:]:
                    text += f"• {day['date']}: {day['count']} کاربر جدید\n"
        else:
            text = f"📈 **Growth Analytics ({analytics.period_days} days)**\n\n"
            text += f"👥 **Total Growth:** {analytics.total_growth:,} users\n"
            text += f"📊 **Average Daily Growth:** {analytics.average_daily_growth}\n"
            if analytics.peak_day and analytics.peak_day['date']:
                text += f"🏆 **Peak Day:** {analytics.peak_day['date']} ({analytics.peak_day['count']} users)\n\n"
            
            if len(analytics.daily_registrations) > 0:
                text += f"📅 **Last 7 Days:**\n"
                for day in analytics.daily_registrations[-7:]:
                    text += f"• {day['date']}: {day['count']} new users\n"
        
        return text