"""
User profile service for managing user information and account settings.
Handles user profile management, account history, and preferences."""

import json
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime, timedelta

from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger, log_error_with_context, log_user_action
from Users.Models.user_models import UserProfile, UserStatistics, UserPreferences
from Users.Language.user_translations_en import USER_TRANSLATIONS_EN
from Users.Language.user_translations_fa import USER_TRANSLATIONS_FA

# Initialize logger
logger = get_logger(__name__)

class UserProfileService:
    """Service for managing user profiles and account information."""
    
    def __init__(self, db: DatabaseManager):
        """Initialize user profile service."""
        self.db = db
    
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
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get complete user profile."""
        try:
            user_data = await self.db.get_user(user_id)
            if not user_data:
                return None
            
            return UserProfile.from_db_data(user_data)
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_user_profile',
                'user_id': user_id
            })
            return None
    
    async def update_user_profile(self, user_id: int, 
                                 profile_data: Dict[str, Any]) -> bool:
        """Update user profile information."""
        try:
            # Build update query dynamically
            allowed_fields = [
                'First_Name', 'Last_Name', 'Username', 'Email', 
                'Language_Code', 'Timezone'
            ]
            
            update_fields = []
            params: List[Any] = []
            
            for field, value in profile_data.items():
                if field in allowed_fields and value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                return False
            
            # Add user ID parameter
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE Chat_ID = %s"
            rows_affected = await self.db.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                log_user_action(user_id, 'profile_updated', {
                    'updated_fields': list(profile_data.keys())
                })
                return True
            
            return False
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'update_user_profile',
                'user_id': user_id,
                'profile_data': profile_data
            })
            return False
    
    async def get_user_statistics(self, user_id: int) -> Optional[UserStatistics]:
        """Get user statistics and analytics."""
        try:
            user = await self.db.get_user(user_id)
            if not user:
                return None
            
            # Calculate account age
            created_at = user.get('Created_At')
            account_age_days = 0
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                account_age_days = (datetime.now() - created_at).days
            
            # Get feature usage statistics
            feature_usage_query = """
                SELECT Feature_Name, SUM(Usage_Count) as Total_Usage
                FROM feature_usage 
                WHERE User_ID = %s 
                GROUP BY Feature_Name
            """
            feature_results = await self.db.execute_query(feature_usage_query, (user_id,))
            
            features_used = {}
            for result in feature_results:
                features_used[result['Feature_Name']] = result['Total_Usage']
            
            # Get login count (approximate)
            total_logins = await self._get_user_login_count(user_id)
            
            # Get subscription history
            subscription_history = await self._get_subscription_history(user_id)
            
            return UserStatistics(
                user_id=user_id,
                total_logins=total_logins,
                features_used=features_used,
                last_activity=user.get('Last_Login'),
                account_age_days=account_age_days,
                referrals_made=user.get('Total_Referrals', 0),
                stars_earned=user.get('Stars', 0),
                subscription_history=subscription_history
            )
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_user_statistics',
                'user_id': user_id
            })
            return None
    
    async def _get_user_login_count(self, user_id: int) -> int:
        """Get approximate login count for user."""
        try:
            # This is an approximation - in a real system you'd track this properly
            user = await self.db.get_user(user_id)
            if not user:
                return 0
            
            created_at = user.get('Created_At')
            if not created_at:
                return 1
            
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            # Rough estimate based on account age and activity
            days_since_creation = (datetime.now() - created_at).days
            return max(1, days_since_creation // 3)  # Assume login every 3 days on average
            
        except Exception:
            return 1
    
    async def _get_subscription_history(self, user_id: int) -> List[Dict]:
        """Get user's subscription history."""
        try:
            query = """
                SELECT Plan_Type, Start_Date, End_Date, Status, Payment_Method, Amount_Paid
                FROM subscriptions 
                WHERE User_ID = %s 
                ORDER BY Start_Date DESC
                LIMIT 10
            """
            
            results = await self.db.execute_query(query, (user_id,))
            
            history = []
            for result in results:
                history.append({
                    'plan': result['Plan_Type'],
                    'start_date': result['Start_Date'],
                    'end_date': result['End_Date'],
                    'status': result['Status'],
                    'payment_method': result.get('Payment_Method'),
                    'amount_paid': result.get('Amount_Paid')
                })
            
            return history
            
        except Exception:
            return []
    
    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences and settings."""
        try:
            user = await self.db.get_user(user_id)
            if not user:
                return None
            
            # Get preferences from Raw_Data field
            raw_data = user.get('Raw_Data') or {}
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data) if raw_data else {}
            
            preferences_data = raw_data.get('preferences', {})
            
            return UserPreferences(
                user_id=user_id,
                language_code=user.get('Language_Code', 'en'),
                timezone=preferences_data.get('timezone', 'UTC'),
                notification_settings=preferences_data.get('notification_settings'),
                theme_preference=preferences_data.get('theme_preference', 'default'),
                privacy_settings=preferences_data.get('privacy_settings')
            )
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_user_preferences',
                'user_id': user_id
            })
            return None
    
    async def update_user_preferences(self, user_id: int, 
                                    preferences: UserPreferences) -> bool:
        """Update user preferences."""
        try:
            user = await self.db.get_user(user_id)
            if not user:
                return False
            
            # Get current raw data
            raw_data = user.get('Raw_Data') or {}
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data) if raw_data else {}
            
            # Update preferences
            raw_data['preferences'] = {
                'timezone': preferences.timezone,
                'notification_settings': preferences.notification_settings,
                'theme_preference': preferences.theme_preference,
                'privacy_settings': preferences.privacy_settings
            }
            
            # Update language code in main user record
            update_query = """
                UPDATE users 
                SET Language_Code = %s, Raw_Data = %s 
                WHERE Chat_ID = %s
            """
            
            rows_affected = await self.db.execute_update(
                update_query, 
                (preferences.language_code, json.dumps(raw_data), user_id)
            )
            
            if rows_affected > 0:
                log_user_action(user_id, 'preferences_updated')
                return True
            
            return False
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'update_user_preferences',
                'user_id': user_id
            })
            return False
    
    def format_account_history(self, profile: UserProfile, 
                             statistics: UserStatistics,
                             lang_code: str) -> str:
        """Format account history message."""
        try:
            if lang_code == 'fa':
                message = f"📜 **تاریخچه حساب**\n\n"
                
                # Personal Information
                message += f"👤 **اطلاعات شخصی**\n"
                message += f"• {self._get_text('field_first_name', lang_code)}: {profile.first_name}\n"
                if profile.last_name:
                    message += f"• {self._get_text('field_last_name', lang_code)}: {profile.last_name}\n"
                if profile.username:
                    message += f"• {self._get_text('field_username', lang_code)}: @{profile.username}\n"
                if profile.email:
                    message += f"• {self._get_text('field_email', lang_code)}: {profile.email}\n"
                message += f"• {self._get_text('field_id', lang_code)}: {profile.chat_id}\n"
                message += f"• {self._get_text('field_lang_code', lang_code)}: {profile.language_code}\n\n"
                
                # Account Status
                message += f"⭐ **وضعیت حساب**\n"
                status = "فعال" if profile.is_active else "مسدود"
                message += f"• وضعیت: {status}\n"
                if profile.created_at:
                    created_date = profile.created_at.strftime('%Y-%m-%d') if hasattr(profile.created_at, 'strftime') else str(profile.created_at)
                    message += f"• تاریخ عضویت: {created_date}\n"
                if profile.last_login:
                    login_date = profile.last_login.strftime('%Y-%m-%d %H:%M') if hasattr(profile.last_login, 'strftime') else str(profile.last_login)
                    message += f"• آخرین ورود: {login_date}\n"
                message += f"• سن حساب: {statistics.account_age_days} روز\n\n"
                
                # Rewards and Referrals
                message += f"🎁 **جوایز و ارجاعات**\n"
                message += f"• ستاره‌ها: {profile.stars}\n"
                message += f"• تعداد معرفی‌ها: {profile.total_referrals}\n"
                message += f"• تعداد ورودها: {statistics.total_logins}\n\n"
                
                # Subscription Info
                message += f"💎 **اشتراک**\n"
                message += f"• پلن فعلی: {profile.subscription_plan.title()}\n"
                if profile.subscription_end_date and profile.is_premium:
                    end_date = profile.subscription_end_date.strftime('%Y-%m-%d') if hasattr(profile.subscription_end_date, 'strftime') else str(profile.subscription_end_date)
                    message += f"• تاریخ انقضا: {end_date}\n"
                
            else:
                message = f"📜 **Account History**\n\n"
                
                # Personal Information
                message += f"👤 **Personal Information**\n"
                message += f"• {self._get_text('field_first_name', lang_code)}: {profile.first_name}\n"
                if profile.last_name:
                    message += f"• {self._get_text('field_last_name', lang_code)}: {profile.last_name}\n"
                if profile.username:
                    message += f"• {self._get_text('field_username', lang_code)}: @{profile.username}\n"
                if profile.email:
                    message += f"• {self._get_text('field_email', lang_code)}: {profile.email}\n"
                message += f"• {self._get_text('field_id', lang_code)}: {profile.chat_id}\n"
                message += f"• {self._get_text('field_lang_code', lang_code)}: {profile.language_code}\n\n"
                
                # Account Status
                message += f"⭐ **Account Status**\n"
                status = "Active" if profile.is_active else "Banned"
                message += f"• Status: {status}\n"
                if profile.created_at:
                    created_date = profile.created_at.strftime('%Y-%m-%d') if hasattr(profile.created_at, 'strftime') else str(profile.created_at)
                    message += f"• Joined: {created_date}\n"
                if profile.last_login:
                    login_date = profile.last_login.strftime('%Y-%m-%d %H:%M') if hasattr(profile.last_login, 'strftime') else str(profile.last_login)
                    message += f"• Last Login: {login_date}\n"
                message += f"• Account Age: {statistics.account_age_days} days\n\n"
                
                # Rewards and Referrals
                message += f"🎁 **Rewards & Referrals**\n"
                message += f"• Stars: {profile.stars}\n"
                message += f"• Total Referrals: {profile.total_referrals}\n"
                message += f"• Total Logins: {statistics.total_logins}\n\n"
                
                # Subscription Info
                message += f"💎 **Subscription**\n"
                message += f"• Current Plan: {profile.subscription_plan.title()}\n"
                if profile.subscription_end_date and profile.is_premium:
                    end_date = profile.subscription_end_date.strftime('%Y-%m-%d') if hasattr(profile.subscription_end_date, 'strftime') else str(profile.subscription_end_date)
                    message += f"• Expires: {end_date}\n"
            
            return message
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'format_account_history',
                'user_id': profile.chat_id if profile else None
            })
            return self._get_text('error_occurred', lang_code)
    
    def format_user_profile_summary(self, profile: UserProfile, 
                                  lang_code: str) -> str:
        """Format user profile summary message."""
        try:
            if lang_code == 'fa':
                message = f"👤 **پروفایل کاربری**\n\n"
                message += f"📝 **نام:** {profile.full_name}\n"
                if profile.username:
                    message += f"🏷️ **نام کاربری:** @{profile.username}\n"
                if profile.email:
                    message += f"📧 **ایمیل:** {profile.email}\n"
                message += f"🌐 **زبان:** {profile.language_code.upper()}\n"
                message += f"⭐ **ستاره‌ها:** {profile.stars}\n"
                message += f"👥 **معرفی‌ها:** {profile.total_referrals}\n"
                message += f"💎 **پلن:** {profile.subscription_plan.title()}\n"
                
                status = "فعال" if profile.is_active else "مسدود"
                message += f"📊 **وضعیت:** {status}\n"
            else:
                message = f"👤 **User Profile**\n\n"
                message += f"📝 **Name:** {profile.full_name}\n"
                if profile.username:
                    message += f"🏷️ **Username:** @{profile.username}\n"
                if profile.email:
                    message += f"📧 **Email:** {profile.email}\n"
                message += f"🌐 **Language:** {profile.language_code.upper()}\n"
                message += f"⭐ **Stars:** {profile.stars}\n"
                message += f"👥 **Referrals:** {profile.total_referrals}\n"
                message += f"💎 **Plan:** {profile.subscription_plan.title()}\n"
                
                status = "Active" if profile.is_active else "Banned"
                message += f"📊 **Status:** {status}\n"
            
            return message
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'format_user_profile_summary',
                'user_id': profile.chat_id if profile else None
            })
            return self._get_text('error_occurred', lang_code)
    
    async def delete_user_data(self, user_id: int) -> bool:
        """Delete all user data (for data cleanup/GDPR compliance)."""
        try:
            # Delete from multiple tables
            tables_to_clean = [
                'feature_usage',
                'subscriptions', 
                'tickets',
                'ticket_messages',
                'user_sessions',
                'users'  # Delete user record last
            ]
            
            for table in tables_to_clean:
                if table == 'users':
                    query = f"DELETE FROM {table} WHERE Chat_ID = %s"
                else:
                    query = f"DELETE FROM {table} WHERE User_ID = %s"
                
                await self.db.execute_update(query, (user_id,))
            
            log_user_action(user_id, 'user_data_deleted')
            return True
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'delete_user_data',
                'user_id': user_id
            })
            return False