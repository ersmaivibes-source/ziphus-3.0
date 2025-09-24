"""
Enhanced subscription service for managing user subscriptions and plan comparisons.
Consolidated from User/Subscriptions/subscription_service.py and enhanced.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger, log_error_with_context
from Users.Language.user_translations_en import USER_TRANSLATIONS_EN
from Users.Language.user_translations_fa import USER_TRANSLATIONS_FA

# Initialize logger
logger = get_logger(__name__)

class UserSubscriptionService:
    """Enhanced service for managing user subscriptions and plans."""
    
    def __init__(self, db: DatabaseManager):
        """Initialize subscription service."""
        self.db = db
        self.plan_configs = {
            'free': {
                'price_eur': 0,
                'price_toman': 0,
                'duration_days': 0,
                'features': {
                    'media_downloader': {'daily': 2, 'size_mb': 50},
                    'file_converter': {'daily': 2, 'size_mb': 50},
                    'bot_addition': {'monthly': 3},
                    'ai_features': {'monthly': 1000000},  # 1M tokens
                    'smart_music': {'daily': 2},
                    'fact_checker': {'daily': 2}
                }
            },
            'standard': {
                'price_eur': 4.0,
                'price_toman': 190000,
                'duration_days': 30,
                'features': {
                    'media_downloader': {'daily': 50, 'size_mb': 2000},
                    'file_converter': {'daily': 50, 'size_mb': 2000},
                    'bot_addition': {'monthly': 15},
                    'ai_features': {'monthly': 10000000},  # 10M tokens
                    'smart_music': {'daily': 20},
                    'fact_checker': {'daily': 10}
                }
            },
            'pro': {
                'price_eur': 7.0,
                'price_toman': 390000,
                'duration_days': 30,
                'features': {
                    'media_downloader': {'daily': 200, 'size_mb': 5000},
                    'file_converter': {'daily': 200, 'size_mb': 5000},
                    'bot_addition': {'monthly': 50},
                    'ai_features': {'monthly': 50000000},  # 50M tokens
                    'smart_music': {'daily': 50},
                    'fact_checker': {'daily': 50}
                }
            },
            'ultimate': {
                'price_eur': 12.0,
                'price_toman': 890000,
                'duration_days': 30,
                'features': {
                    'media_downloader': {'daily': -1, 'size_mb': -1},  # Unlimited
                    'file_converter': {'daily': -1, 'size_mb': -1},
                    'bot_addition': {'monthly': -1},
                    'ai_features': {'monthly': 100000000},  # 100M tokens
                    'smart_music': {'daily': 100},
                    'fact_checker': {'daily': 100}
                }
            }
        }
    
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
    
    async def get_user_subscription_status(self, chat_id: int) -> Optional[Dict]:
        """Get user's current subscription status."""
        try:
            return await self.db.get_user_subscription(chat_id)
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_user_subscription_status',
                'chat_id': chat_id
            })
            return None
    
    async def activate_subscription(self, user_id: int, plan_type: str, 
                                  payment_method: str = 'crypto') -> Dict:
        """Activate a subscription for a user."""
        try:
            if plan_type not in self.plan_configs:
                return {
                    'success': False,
                    'message': 'Invalid subscription plan'
                }
            
            plan_config = self.plan_configs[plan_type]
            end_date = datetime.now() + timedelta(days=plan_config['duration_days'])
            
            success = await self.db.create_or_update_subscription(
                user_id=user_id,
                plan_type=plan_type,
                end_date=end_date,
                payment_method=payment_method,
                amount_paid=plan_config.get('price_eur', 0)
            )
            
            if success:
                logger.info(f"Subscription activated: user={user_id}, plan={plan_type}")
                return {
                    'success': True,
                    'message': 'Subscription activated successfully',
                    'plan': plan_type,
                    'end_date': end_date
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to activate subscription'
                }
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'activate_subscription',
                'user_id': user_id,
                'plan_type': plan_type
            })
            return {
                'success': False,
                'message': 'Error activating subscription'
            }
    
    def format_subscription_status(self, subscription: Optional[Dict], lang_code: str) -> str:
        """Format user's subscription status message."""
        if not subscription:
            return self._format_free_plan_status(lang_code)
        
        plan_type = subscription.get('Plan_Type', 'free').title()
        status = subscription.get('Status', 'unknown')
        end_date = subscription.get('End_Date')
        
        # Handle datetime parsing safely
        formatted_end_date = None
        if end_date:
            try:
                if isinstance(end_date, str):
                    parsed_date = datetime.fromisoformat(end_date.replace('Z', ''))
                    formatted_end_date = parsed_date.strftime('%Y-%m-%d')
                elif hasattr(end_date, 'year'):
                    formatted_end_date = end_date.strftime('%Y-%m-%d')
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid End_Date format: {end_date} - {e}")
        
        if lang_code == 'fa':
            message = f"📋 **اشتراک من**\n\n"
            message += f"📦 **پلن فعلی:** {plan_type}\n"
            message += f"⭐ **وضعیت:** {'فعال' if status == 'active' else 'غیرفعال'}\n"
            
            if formatted_end_date:
                message += f"📅 **تاریخ انقضا:** {formatted_end_date}\n"
            
            if status == 'active':
                message += f"\n✅ اشتراک شما فعال است و از تمام امکانات پلن {plan_type} بهره‌مند هستید."
            else:
                message += f"\n❌ اشتراک شما منقضی شده است. برای ادامه استفاده از امکانات، اشتراک خود را تمدید کنید."
        else:
            message = f"📋 **My Subscription**\n\n"
            message += f"📦 **Current Plan:** {plan_type}\n"
            message += f"⭐ **Status:** {'Active' if status == 'active' else 'Inactive'}\n"
            
            if formatted_end_date:
                message += f"📅 **Expires:** {formatted_end_date}\n"
            
            if status == 'active':
                message += f"\n✅ Your subscription is active and you have access to all {plan_type} plan features."
            else:
                message += f"\n❌ Your subscription has expired. Please renew to continue using premium features."
        
        return message
    
    def _format_free_plan_status(self, lang_code: str) -> str:
        """Format free plan status message."""
        if lang_code == 'fa':
            message = f"📋 **اشتراک من**\n\n"
            message += f"📦 **پلن فعلی:** رایگان\n"
            message += f"⭐ **وضعیت:** فعال\n\n"
            message += f"🎯 شما در حال حاضر از پلن رایگان استفاده می‌کنید.\n"
            message += f"برای دسترسی به امکانات بیشتر، پلن خود را ارتقا دهید."
        else:
            message = f"📋 **My Subscription**\n\n"
            message += f"📦 **Current Plan:** Free\n"
            message += f"⭐ **Status:** Active\n\n"
            message += f"🎯 You are currently using the free plan.\n"
            message += f"Upgrade your plan to access more features."
        return message
    
    def get_plan_price_formatted(self, plan_type: str, lang_code: str) -> str:
        """Get formatted price for a plan."""
        if plan_type not in self.plan_configs:
            return "Free" if lang_code == 'en' else "رایگان"
        
        plan_config = self.plan_configs[plan_type]
        
        if lang_code == 'fa':
            toman_price = plan_config['price_toman']
            if toman_price == 0:
                return "رایگان"
            elif toman_price >= 1000:
                thousands = toman_price // 1000
                return f"{thousands} هزار تومان"
            else:
                return f"{toman_price} تومان"
        else:
            eur_price = plan_config['price_eur']
            return "Free" if eur_price == 0 else f"€{eur_price}"
    
    def get_plan_price_display(self, plan_type: str, lang_code: str, 
                              include_duration: bool = True) -> str:
        """Get complete price display with duration."""
        price = self.get_plan_price_formatted(plan_type, lang_code)
        
        if include_duration and plan_type != 'free':
            duration_suffix = "/ماه" if lang_code == 'fa' else "/month"
            return f"{price}{duration_suffix}"
        
        return price
    
    def create_plan_comparison_message(self, lang_code: str) -> str:
        """Create comprehensive plan comparison message."""
        if lang_code == 'fa':
            return self._create_plan_comparison_fa()
        else:
            return self._create_plan_comparison_en()
    
    def _create_plan_comparison_en(self) -> str:
        """Create English plan comparison message."""
        message = f"📊 **Plan Comparison**\n\n"
        message += "🎯 **Choose the right plan for you:**\n\n"
        
        features = [
            ("📥 Media Downloader", "2/day - 50MB", "50/day - 2GB", "200/day - 5GB", "Unlimited"),
            ("🔄 File Format Converter", "2/day - 50MB", "50/day - 2GB", "200/day - 5GB", "Unlimited"),
            ("🔗 Add Bot to Chats", "3/month", "15/month", "50/month", "Unlimited"),
            ("🤖 AI Features", "1M tokens/month", "10M tokens/month", "50M tokens/month", "100M tokens/month"),
            ("🎵 Smart Music Finder", "2/day", "20/day + lyrics", "50/day + lyrics", "100/day + lyrics"),
            ("🔍 Fact Checker", "2/day", "10/day", "50/day", "100/day"),
        ]
        
        labels = ["🆓 Free", "✨ Standard", "🚀 Pro", "💎 Ultimate"]
        
        for feature_name, free, standard, pro, ultimate in features:
            message += f"**{feature_name}**\n"
            message += f"{labels[0]}: {free}\n"
            message += f"{labels[1]}: {standard}\n"
            message += f"{labels[2]}: {pro}\n"
            message += f"{labels[3]}: {ultimate}\n"
            message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        message += f"💰 **Pricing:**\n"
        message += f"✨ **Standard**: {self.get_plan_price_display('standard', 'en')}\n"
        message += f"🚀 **Pro**: {self.get_plan_price_display('pro', 'en')}\n"
        message += f"💎 **Ultimate**: {self.get_plan_price_display('ultimate', 'en')}\n\n"
        
        return message
    
    def _create_plan_comparison_fa(self) -> str:
        """Create Persian plan comparison message."""
        message = f"📊 **مقایسه پلن‌ها**\n\n"
        message += "🎯 **پلن مناسب خود را انتخاب کنید:**\n\n"
        
        features = [
            ("📥 دانلود رسانه", "2/روز - 50MB", "50/روز - 2GB", "200/روز - 5GB", "نامحدود"),
            ("🔄 تبدیل فرمت فایل", "2/روز - 50MB", "50/روز - 2GB", "200/روز - 5GB", "نامحدود"),
            ("🔗 اضافه کردن ربات", "3/ماه", "15/ماه", "50/ماه", "نامحدود"),
            ("🤖 هوش مصنوعی", "1M توکن/ماه", "10M توکن/ماه", "50M توکن/ماه", "100M توکن/ماه"),
            ("🎵 موزیک یاب هوشمند", "2/روز", "20/روز + متن", "50/روز + متن", "100/روز + متن"),
            ("🔍 فکت چکر", "2/روز", "10/روز", "50/روز", "100/روز"),
        ]
        
        labels = ["🆓 رایگان", "✨ استاندارد", "🚀 حرفه‌ای", "💎 نهایی"]
        
        for feature_name, free, standard, pro, ultimate in features:
            message += f"**{feature_name}**\n"
            message += f"{labels[0]}: {free}\n"
            message += f"{labels[1]}: {standard}\n"
            message += f"{labels[2]}: {pro}\n"
            message += f"{labels[3]}: {ultimate}\n"
            message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        message += f"💰 **قیمت‌ها:**\n"
        message += f"✨ **استاندارد**: {self.get_plan_price_display('standard', 'fa')}\n"
        message += f"🚀 **حرفه‌ای**: {self.get_plan_price_display('pro', 'fa')}\n"
        message += f"💎 **نهایی**: {self.get_plan_price_display('ultimate', 'fa')}\n\n"
        
        return message
    
    def get_plan_info(self, plan_type: str) -> Dict[str, Any]:
        """Get information about a specific plan."""
        if plan_type not in self.plan_configs:
            return {}
        
        return self.plan_configs[plan_type].copy()
    
    def get_plan_features(self, plan_type: str) -> Dict[str, Any]:
        """Get features for a specific plan."""
        plan_info = self.get_plan_info(plan_type)
        return plan_info.get('features', {})
    
    async def get_user_plan_limits(self, user_id: int, feature: str) -> Dict[str, Any]:
        """Get user's current plan limits for a specific feature."""
        try:
            subscription = await self.get_user_subscription_status(user_id)
            plan_type = 'free'
            
            if subscription and subscription.get('Status') == 'active':
                end_date = subscription.get('End_Date')
                if end_date:
                    # Check if subscription is still valid
                    if isinstance(end_date, str):
                        end_date = datetime.fromisoformat(end_date.replace('Z', ''))
                    
                    if end_date > datetime.now():
                        plan_type = subscription.get('Plan_Type', 'free')
            
            plan_features = self.get_plan_features(plan_type)
            feature_limits = plan_features.get(feature, {})
            
            return {
                'plan': plan_type,
                'limits': feature_limits,
                'is_unlimited': any(v == -1 for v in feature_limits.values() if isinstance(v, int))
            }
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_user_plan_limits',
                'user_id': user_id,
                'feature': feature
            })
            # Return free plan limits as fallback
            return {
                'plan': 'free',
                'limits': self.get_plan_features('free').get(feature, {}),
                'is_unlimited': False
            }
    
    async def check_feature_access(self, user_id: int, feature: str) -> bool:
        """Check if user has access to a specific feature."""
        try:
            plan_limits = await self.get_user_plan_limits(user_id, feature)
            
            # If feature not defined in any plan, allow access
            if not plan_limits.get('limits'):
                return True
            
            # If unlimited access
            if plan_limits.get('is_unlimited'):
                return True
            
            # Check current usage against limits
            current_usage = await self.db.get_feature_usage(user_id, feature, 'daily')
            daily_limit = plan_limits['limits'].get('daily', 0)
            
            if daily_limit == -1:  # Unlimited
                return True
            
            return current_usage < daily_limit
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'check_feature_access',
                'user_id': user_id,
                'feature': feature
            })
            return True  # Allow access on error