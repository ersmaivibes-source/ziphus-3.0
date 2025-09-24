"""
Enhanced user limiter service for checking feature usage limits.
Consolidated from User/Restrictions/user_limiter.py and User/Limits/user_limiter.py

This module also serves as the consolidated limits functionality from User/Limits/
"""

from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta

from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger, log_error_with_context
from Users.Subscriptions.subscription_service import UserSubscriptionService
from Users.Language.user_translations_en import USER_TRANSLATIONS_EN
from Users.Language.user_translations_fa import USER_TRANSLATIONS_FA

# Initialize logger
logger = get_logger(__name__)

class UserLimiter:
    """Enhanced service for managing user feature usage limits."""
    
    def __init__(self, db: DatabaseManager):
        """Initialize user limiter."""
        self.db = db
        self.subscription_service = UserSubscriptionService(db)
    
    def _get_text(self, key: str, lang_code: str = 'en', **kwargs) -> str:
        """Get localized text for users."""
        translations = USER_TRANSLATIONS_FA if lang_code == 'fa' else USER_TRANSLATIONS_EN
        text = translations.get(key, key)
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text
    
    async def check_limit(self, user_id: int, feature: str,
                        file_size_mb: Optional[float] = None,
                        lang_code: str = 'en') -> Tuple[bool, str]:
        """
        Check if user can use a feature.
        
        Args:
            user_id: User's chat ID
            feature: Feature name to check
            file_size_mb: Optional file size for size-based limits
            lang_code: User's language code
        
        Returns:
            Tuple of (allowed, reason_message)
        """
        try:
            # Get user's current plan limits
            plan_limits = await self.subscription_service.get_user_plan_limits(user_id, feature)
            plan_type = plan_limits.get('plan', 'free')
            feature_limits = plan_limits.get('limits', {})
            
            # If no limits defined, allow usage
            if not feature_limits:
                return True, "Allowed"
            
            # Check file size limits if applicable
            if file_size_mb is not None and 'size_mb' in feature_limits:
                size_limit = feature_limits['size_mb']
                if size_limit != -1 and file_size_mb > size_limit:
                    message = self._get_text('file_size_exceeded', lang_code, 
                                           limit=size_limit, size=file_size_mb)
                    return False, message
            
            # Check usage limits
            if 'daily' in feature_limits:
                allowed, message = await self._check_daily_limit(
                    user_id, feature, feature_limits['daily'], plan_type, lang_code
                )
                if not allowed:
                    return False, message
            
            elif 'monthly' in feature_limits:
                allowed, message = await self._check_monthly_limit(
                    user_id, feature, feature_limits['monthly'], plan_type, lang_code
                )
                if not allowed:
                    return False, message
            
            elif 'hourly' in feature_limits:
                allowed, message = await self._check_hourly_limit(
                    user_id, feature, feature_limits['hourly'], plan_type, lang_code
                )
                if not allowed:
                    return False, message
            
            return True, "Allowed"
            
        except Exception as e:
            logger.error(f"Error checking limits for user {user_id}, feature {feature}: {e}")
            # Allow usage on error to prevent blocking legitimate users
            return True, "Allowed (error checking limits)"
    
    async def _check_daily_limit(self, user_id: int, feature: str, limit: int,
                               plan_type: str, lang_code: str) -> Tuple[bool, str]:
        """Check daily usage limit."""
        if limit == 0:
            message = self._get_text('feature_not_available', lang_code, 
                                   feature=feature, plan=plan_type)
            return False, message
        elif limit == -1:
            return True, "Unlimited usage"
        
        usage = await self.db.get_feature_usage(user_id, feature, 'daily')
        if usage >= limit:
            message = self._get_text('daily_limit_reached', lang_code,
                                   usage=usage, limit=limit, feature=feature)
            return False, message
        
        return True, f"Allowed ({usage}/{limit} daily)"
    
    async def _check_monthly_limit(self, user_id: int, feature: str, limit: int,
                                 plan_type: str, lang_code: str) -> Tuple[bool, str]:
        """Check monthly usage limit."""
        if limit == 0:
            message = self._get_text('feature_not_available', lang_code,
                                   feature=feature, plan=plan_type)
            return False, message
        elif limit == -1:
            return True, "Unlimited usage"
        
        usage = await self.db.get_feature_usage(user_id, feature, 'monthly')
        if usage >= limit:
            message = self._get_text('monthly_limit_reached', lang_code,
                                   usage=usage, limit=limit, feature=feature)
            return False, message
        
        return True, f"Allowed ({usage}/{limit} monthly)"
    
    async def _check_hourly_limit(self, user_id: int, feature: str, limit: int,
                                plan_type: str, lang_code: str) -> Tuple[bool, str]:
        """Check hourly usage limit."""
        if limit == 0:
            message = self._get_text('feature_not_available', lang_code,
                                   feature=feature, plan=plan_type)
            return False, message
        elif limit == -1:
            return True, "Unlimited usage"
        
        usage = await self.db.get_feature_usage(user_id, feature, 'hourly')
        if usage >= limit:
            message = self._get_text('hourly_limit_reached', lang_code,
                                   usage=usage, limit=limit, feature=feature)
            return False, message
        
        return True, f"Allowed ({usage}/{limit} hourly)"
    
    async def get_remaining_usage(self, user_id: int, feature: str, 
                                lang_code: str = 'en') -> Dict[str, Any]:
        """Get remaining usage for a feature."""
        try:
            # Get user's current plan limits
            plan_limits = await self.subscription_service.get_user_plan_limits(user_id, feature)
            plan_type = plan_limits.get('plan', 'free')
            feature_limits = plan_limits.get('limits', {})
            
            if not feature_limits:
                return {
                    'plan': plan_type,
                    'feature': feature,
                    'usage': {},
                    'limits': {},
                    'status': 'unlimited'
                }
            
            usage_info = {
                'plan': plan_type,
                'feature': feature,
                'usage': {},
                'limits': feature_limits,
                'status': 'limited'
            }
            
            # Get usage for different periods
            if 'daily' in feature_limits:
                daily_usage = await self.db.get_feature_usage(user_id, feature, 'daily')
                daily_limit = feature_limits['daily']
                
                usage_info['usage']['daily'] = {
                    'used': daily_usage,
                    'limit': daily_limit,
                    'remaining': max(0, daily_limit - daily_usage) if daily_limit != -1 else -1,
                    'percentage': (daily_usage / daily_limit * 100) if daily_limit > 0 else 0
                }
            
            if 'monthly' in feature_limits:
                monthly_usage = await self.db.get_feature_usage(user_id, feature, 'monthly')
                monthly_limit = feature_limits['monthly']
                
                usage_info['usage']['monthly'] = {
                    'used': monthly_usage,
                    'limit': monthly_limit,
                    'remaining': max(0, monthly_limit - monthly_usage) if monthly_limit != -1 else -1,
                    'percentage': (monthly_usage / monthly_limit * 100) if monthly_limit > 0 else 0
                }
            
            if 'hourly' in feature_limits:
                hourly_usage = await self.db.get_feature_usage(user_id, feature, 'hourly')
                hourly_limit = feature_limits['hourly']
                
                usage_info['usage']['hourly'] = {
                    'used': hourly_usage,
                    'limit': hourly_limit,
                    'remaining': max(0, hourly_limit - hourly_usage) if hourly_limit != -1 else -1,
                    'percentage': (hourly_usage / hourly_limit * 100) if hourly_limit > 0 else 0
                }
            
            # Check if unlimited
            if plan_limits.get('is_unlimited') or any(limit == -1 for limit in feature_limits.values()):
                usage_info['status'] = 'unlimited'
            
            return usage_info
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_remaining_usage',
                'user_id': user_id,
                'feature': feature
            })
            return {
                'plan': 'free',
                'feature': feature,
                'usage': {},
                'limits': {},
                'status': 'error',
                'error': str(e)
            }
    
    async def increment_usage(self, user_id: int, feature: str, 
                            amount: int = 1) -> bool:
        """Increment feature usage for a user."""
        try:
            success = await self.db.increment_feature_usage(user_id, feature, amount)
            
            if success:
                logger.debug(f"Incremented {feature} usage by {amount} for user {user_id}")
            
            return success
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'increment_usage',
                'user_id': user_id,
                'feature': feature,
                'amount': amount
            })
            return False
    
    async def reset_daily_usage(self, user_id: Optional[int] = None) -> bool:
        """Reset daily usage counters (for all users or specific user)."""
        try:
            if user_id:
                query = "DELETE FROM feature_usage WHERE User_ID = %s AND Period = 'daily'"
                params = (user_id,)
            else:
                query = "DELETE FROM feature_usage WHERE Period = 'daily'"
                params = ()
            
            rows_affected = await self.db.execute_update(query, params)
            logger.info(f"Reset daily usage: {rows_affected} records affected")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'reset_daily_usage',
                'user_id': user_id
            })
            return False
    
    async def reset_monthly_usage(self, user_id: Optional[int] = None) -> bool:
        """Reset monthly usage counters (for all users or specific user)."""
        try:
            if user_id:
                query = "DELETE FROM feature_usage WHERE User_ID = %s AND Period = 'monthly'"
                params = (user_id,)
            else:
                query = "DELETE FROM feature_usage WHERE Period = 'monthly'"
                params = ()
            
            rows_affected = await self.db.execute_update(query, params)
            logger.info(f"Reset monthly usage: {rows_affected} records affected")
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'reset_monthly_usage',
                'user_id': user_id
            })
            return False
    
    async def get_user_usage_summary(self, user_id: int, 
                                   lang_code: str = 'en') -> Dict[str, Any]:
        """Get comprehensive usage summary for a user."""
        try:
            # Get user's subscription info
            subscription = await self.subscription_service.get_user_subscription_status(user_id)
            plan_type = 'free'
            
            if subscription and subscription.get('Status') == 'active':
                plan_type = subscription.get('Plan_Type', 'free')
            
            # Get usage for key features
            features = ['media_downloader', 'file_converter', 'bot_addition', 'ai_features']
            usage_summary = {
                'user_id': user_id,
                'plan': plan_type,
                'features': {},
                'overall_status': 'active'
            }
            
            for feature in features:
                feature_usage = await self.get_remaining_usage(user_id, feature, lang_code)
                usage_summary['features'][feature] = feature_usage
            
            return usage_summary
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_user_usage_summary',
                'user_id': user_id
            })
            return {
                'user_id': user_id,
                'plan': 'free',
                'features': {},
                'overall_status': 'error',
                'error': str(e)
            }
    
    def format_usage_message(self, usage_info: Dict[str, Any], 
                           lang_code: str = 'en') -> str:
        """Format usage information into a user-friendly message."""
        try:
            plan = usage_info.get('plan', 'free').title()
            feature = usage_info.get('feature', 'Unknown')
            
            if lang_code == 'fa':
                message = f"📊 **محدودیت {feature}**\n\n"
                message += f"📦 **پلن فعلی:** {plan}\n\n"
            else:
                message = f"📊 **{feature} Limits**\n\n"
                message += f"📦 **Current Plan:** {plan}\n\n"
            
            usage_data = usage_info.get('usage', {})
            
            for period, data in usage_data.items():
                used = data.get('used', 0)
                limit = data.get('limit', 0)
                remaining = data.get('remaining', 0)
                percentage = data.get('percentage', 0)
                
                if lang_code == 'fa':
                    period_name = {'daily': 'روزانه', 'monthly': 'ماهانه', 'hourly': 'ساعتی'}.get(period, period)
                    message += f"📅 **{period_name}:** "
                else:
                    period_name = period.title()
                    message += f"📅 **{period_name}:** "
                
                if limit == -1:
                    unlimited_text = "نامحدود" if lang_code == 'fa' else "Unlimited"
                    message += f"{unlimited_text}\n"
                else:
                    message += f"{used}/{limit} ({percentage:.1f}%)\n"
                    if remaining > 0:
                        remaining_text = "باقی‌مانده" if lang_code == 'fa' else "remaining"
                        message += f"   ↳ {remaining} {remaining_text}\n"
            
            if usage_info.get('status') == 'unlimited':
                unlimited_status = "✅ دسترسی نامحدود" if lang_code == 'fa' else "✅ Unlimited Access"
                message += f"\n{unlimited_status}"
            
            return message
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'format_usage_message',
                'usage_info': usage_info
            })
            return "Error formatting usage information"