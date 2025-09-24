"""Subscription limit service for displaying user limits and usage.
Helps users understand their current subscription limits.
Enhanced and consolidated from User/Subscriptions/subscription_limit_service.py
"""

from typing import Dict, Any, Optional
from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger, log_error_with_context
from Users.Restrictions.user_limiter import UserLimiter
from Users.Language.user_translations_en import USER_TRANSLATIONS_EN
from Users.Language.user_translations_fa import USER_TRANSLATIONS_FA

# Initialize logger
logger = get_logger(__name__)

class SubscriptionLimitService:
    """Enhanced service for checking and displaying subscription limits."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.user_limiter = UserLimiter(db)
    
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
    
    async def get_bot_addition_status(self, user_id: int, lang_code: str = 'en') -> str:
        """Get user's bot addition status and limits."""
        try:
            # Get remaining usage for bot addition
            usage_info = await self.user_limiter.get_remaining_usage(user_id, 'bot_addition', lang_code)
            
            if not usage_info or 'usage' not in usage_info:
                return self._get_text('limit_info_not_found', lang_code)
            
            plan = usage_info.get('plan', 'free')
            
            if lang_code == 'fa':
                text = f"🔗 **محدودیت اضافه کردن ربات**\n\n"
                text += f"📦 **پلن فعلی:** {plan.title()}\n"
                
                if 'monthly' in usage_info['usage']:
                    monthly = usage_info['usage']['monthly']
                    if monthly['limit'] == -1:
                        text += f"✅ **وضعیت:** نامحدود\n"
                        text += f"💡 شما می‌توانید ربات را به تعداد نامحدود چت اضافه کنید."
                    else:
                        text += f"📊 **استفاده ماهانه:** {monthly['used']}/{monthly['limit']}\n"
                        text += f"⏳ **باقی‌مانده:** {monthly['remaining']}\n\n"
                        
                        if monthly['remaining'] > 0:
                            text += f"✅ شما می‌توانید ربات را به {monthly['remaining']} چت دیگر اضافه کنید."
                        else:
                            text += f"🚫 محدودیت ماهانه شما تمام شده است.\n"
                            text += f"💎 برای اضافه کردن ربات به چت‌های بیشتر، اشتراک خود را ارتقا دهید."
                else:
                    text += f"ℹ️ اطلاعات استفاده در دسترس نیست."
            else:
                text = f"🔗 **Bot Addition Limits**\n\n"
                text += f"📦 **Current Plan:** {plan.title()}\n"
                
                if 'monthly' in usage_info['usage']:
                    monthly = usage_info['usage']['monthly']
                    if monthly['limit'] == -1:
                        text += f"✅ **Status:** Unlimited\n"
                        text += f"💡 You can add the bot to unlimited chats."
                    else:
                        text += f"📊 **Monthly Usage:** {monthly['used']}/{monthly['limit']}\n"
                        text += f"⏳ **Remaining:** {monthly['remaining']}\n\n"
                        
                        if monthly['remaining'] > 0:
                            text += f"✅ You can add the bot to {monthly['remaining']} more chats."
                        else:
                            text += f"🚫 You have reached your monthly limit.\n"
                            text += f"💎 Please upgrade your subscription to add the bot to more chats."
                else:
                    text += f"ℹ️ Usage information not available."
            
            return text
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_bot_addition_status',
                'user_id': user_id
            })
            return self._get_text('error_retrieving_limits', lang_code)
    
    async def get_comprehensive_limits_status(self, user_id: int, lang_code: str = 'en') -> str:
        """Get comprehensive overview of all user limits."""
        try:
            # Get user subscription using the subscription service
            from Users.Subscriptions.subscription_service import UserSubscriptionService
            subscription_service = UserSubscriptionService(self.db)
            subscription = await subscription_service.get_user_subscription_status(user_id)
            plan_type = subscription['Plan_Type'] if subscription else 'free'
            
            if lang_code == 'fa':
                text = f"📊 **محدودیت‌های اشتراک من**\n\n"
                text += f"📦 **پلن فعلی:** {plan_type.title()}\n\n"
                
                # Key features overview
                key_features = {
                    'bot_addition': 'اضافه کردن ربات',
                    'media_downloader': 'دانلود رسانه', 
                    'file_converter': 'تبدیل فرمت',
                    'smart_music_finder': 'موزیک یاب هوشمند',
                    'ai_features': 'هوش مصنوعی'
                }
            else:
                text = f"📊 **My Subscription Limits**\n\n"
                text += f"📦 **Current Plan:** {plan_type.title()}\n\n"
                
                # Key features overview
                key_features = {
                    'bot_addition': 'Bot Addition',
                    'media_downloader': 'Media Downloads',
                    'file_converter': 'File Conversion',
                    'smart_music_finder': 'Smart Music Finder',
                    'ai_features': 'AI Features'
                }
            
            # Get usage for key features
            for feature, display_name in key_features.items():
                try:
                    usage_info = await self.user_limiter.get_remaining_usage(user_id, feature, lang_code)
                    
                    if usage_info and 'usage' in usage_info:
                        if 'monthly' in usage_info['usage']:
                            monthly = usage_info['usage']['monthly']
                            if monthly['limit'] == -1:
                                status = "♾️ نامحدود" if lang_code == 'fa' else "♾️ Unlimited"
                            else:
                                percentage = monthly.get('percentage', 0)
                                status = f"{monthly['used']}/{monthly['limit']} ({percentage:.1f}%)"
                        elif 'daily' in usage_info['usage']:
                            daily = usage_info['usage']['daily']
                            if daily['limit'] == -1:
                                status = "♾️ نامحدود" if lang_code == 'fa' else "♾️ Unlimited"
                            else:
                                percentage = daily.get('percentage', 0)
                                status = f"{daily['used']}/{daily['limit']} ({percentage:.1f}%)"
                        else:
                            status = "N/A"
                    else:
                        status = "N/A"
                    
                    text += f"• **{display_name}:** {status}\n"
                    
                except Exception as feature_error:
                    logger.error(f"Error getting usage for {feature}: {feature_error}")
                    text += f"• **{display_name}:** Error\n"
            
            if lang_code == 'fa':
                text += f"\n💡 برای مشاهده جزئیات بیشتر یا ارتقای اشتراک، از منوی اشتراک استفاده کنید."
            else:
                text += f"\n💡 Use the subscription menu for more details or to upgrade your plan."
            
            return text
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_comprehensive_limits_status',
                'user_id': user_id
            })
            return self._get_text('error_retrieving_limits', lang_code)
    
    async def get_feature_usage_details(self, user_id: int, feature: str, 
                                      lang_code: str = 'en') -> str:
        """Get detailed usage information for a specific feature."""
        try:
            usage_info = await self.user_limiter.get_remaining_usage(user_id, feature, lang_code)
            
            if not usage_info:
                return self._get_text('feature_not_found', lang_code, feature=feature)
            
            plan = usage_info.get('plan', 'free')
            feature_name = feature.replace('_', ' ').title()
            
            if lang_code == 'fa':
                text = f"📊 **جزئیات استفاده از {feature_name}**\n\n"
                text += f"📦 **پلن:** {plan.title()}\n"
            else:
                text = f"📊 **{feature_name} Usage Details**\n\n"
                text += f"📦 **Plan:** {plan.title()}\n"
            
            usage_data = usage_info.get('usage', {})
            
            for period, data in usage_data.items():
                used = data.get('used', 0)
                limit = data.get('limit', 0)
                remaining = data.get('remaining', 0)
                percentage = data.get('percentage', 0)
                
                period_name = {
                    'daily': 'روزانه' if lang_code == 'fa' else 'Daily',
                    'monthly': 'ماهانه' if lang_code == 'fa' else 'Monthly',
                    'hourly': 'ساعتی' if lang_code == 'fa' else 'Hourly'
                }.get(period, period)
                
                text += f"\n📅 **{period_name}:**\n"
                
                if limit == -1:
                    unlimited_text = "نامحدود" if lang_code == 'fa' else "Unlimited"
                    text += f"   ✅ {unlimited_text}\n"
                else:
                    text += f"   📊 استفاده: {used}/{limit} ({percentage:.1f}%)\n" if lang_code == 'fa' else f"   📊 Usage: {used}/{limit} ({percentage:.1f}%)\n"
                    if remaining > 0:
                        remaining_text = "باقی‌مانده" if lang_code == 'fa' else "remaining"
                        text += f"   ⏳ {remaining} {remaining_text}\n"
                    else:
                        limit_reached = "محدودیت رسیده" if lang_code == 'fa' else "Limit reached"
                        text += f"   🚫 {limit_reached}\n"
            
            return text
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_feature_usage_details',
                'user_id': user_id,
                'feature': feature
            })
            return self._get_text('error_retrieving_feature_details', lang_code)
    
    async def get_plan_upgrade_suggestions(self, user_id: int, 
                                         lang_code: str = 'en') -> str:
        """Get personalized plan upgrade suggestions based on usage patterns."""
        try:
            # Get current subscription using the subscription service
            from Users.Subscriptions.subscription_service import UserSubscriptionService
            subscription_service = UserSubscriptionService(self.db)
            subscription = await subscription_service.get_user_subscription_status(user_id)
            current_plan = subscription['Plan_Type'] if subscription else 'free'
            
            # Get usage summary
            usage_summary = await self.user_limiter.get_user_usage_summary(user_id, lang_code)
            
            if lang_code == 'fa':
                text = f"💡 **پیشنهادات ارتقای پلن**\n\n"
                text += f"📦 **پلن فعلی:** {current_plan.title()}\n\n"
            else:
                text = f"💡 **Plan Upgrade Suggestions**\n\n"
                text += f"📦 **Current Plan:** {current_plan.title()}\n\n"
            
            # Analyze usage patterns and suggest upgrades
            high_usage_features = []
            for feature, data in usage_summary.get('features', {}).items():
                usage_info = data.get('usage', {})
                for period, period_data in usage_info.items():
                    percentage = period_data.get('percentage', 0)
                    if percentage > 80:  # High usage threshold
                        high_usage_features.append(feature)
            
            if high_usage_features:
                if lang_code == 'fa':
                    text += f"🔍 **تحلیل استفاده شما:**\n"
                    text += f"شما از امکانات زیر به شدت استفاده می‌کنید:\n"
                    for feature in high_usage_features:
                        feature_name = feature.replace('_', ' ')
                        text += f"• {feature_name}\n"
                    text += f"\n💎 **توصیه:** ارتقا به پلن بالاتر برای استفاده بهتر\n"
                else:
                    text += f"🔍 **Usage Analysis:**\n"
                    text += f"You have high usage of these features:\n"
                    for feature in high_usage_features:
                        feature_name = feature.replace('_', ' ').title()
                        text += f"• {feature_name}\n"
                    text += f"\n💎 **Recommendation:** Upgrade to a higher plan for better usage\n"
            else:
                if lang_code == 'fa':
                    text += f"✅ استفاده شما در محدوده مناسب است.\n"
                else:
                    text += f"✅ Your usage is within reasonable limits.\n"
            
            return text
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_plan_upgrade_suggestions',
                'user_id': user_id
            })
            return self._get_text('error_generating_suggestions', lang_code)