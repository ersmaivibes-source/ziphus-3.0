"""Enhanced referral service for managing referral notifications and rewards.
Consolidated from User/Referrals/referral_service.py and enhanced."""

import json
from typing import Optional, Dict, List
from hydrogram import Client
from general.Database.MySQL.db_manager import DatabaseManager
from general.Logging.logger_manager import get_logger, log_error_with_context, log_user_action
from Users.Language.user_translations_en import USER_TRANSLATIONS_EN
from Users.Language.user_translations_fa import USER_TRANSLATIONS_FA

# Initialize logger
logger = get_logger(__name__)

class UserReferralService:
    """Enhanced service for managing user referrals and rewards."""
    
    def __init__(self, db: DatabaseManager, client: Client):
        """Initialize referral service."""
        self.db = db
        self.client = client
        self.milestone_rewards = {
            50: {'stars': 50, 'plan': None},
            100: {'stars': 100, 'plan': 'standard'},
            200: {'stars': 200, 'plan': 'pro'},
            500: {'stars': 500, 'plan': 'ultimate'},
            1000: {'stars': 1000, 'plan': 'ultimate'}
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
    
    async def send_referral_notifications(self, referrer_chat_id: int, 
                                        referred_chat_id: int) -> bool:
        """Send notifications to both referrer and referred user about successful referral."""
        try:
            # Get referrer info
            referrer_data = await self.db.get_user(referrer_chat_id)
            referrer_lang = referrer_data.get('Language_Code', 'en') if referrer_data else 'en'
            
            # Get referred user info  
            referred_data = await self.db.get_user(referred_chat_id)
            referred_lang = referred_data.get('Language_Code', 'en') if referred_data else 'en'
            
            referrer_name = referrer_data.get('First_Name', 'Friend') if referrer_data else 'Friend'
            referred_name = referred_data.get('First_Name', 'Friend') if referred_data else 'Friend'
            
            # Notify referred user about the bonus
            referred_message = self._get_text(
                'referral_new_user', 
                referred_lang,
                referrer_name=referrer_name,
                stars_amount=5
            )
            
            try:
                await self.client.send_message(referred_chat_id, referred_message)
                log_user_action(referred_chat_id, 'received_referral_notification', {
                    'referrer_id': referrer_chat_id,
                    'stars_awarded': 5
                })
            except Exception as e:
                logger.error(f"Failed to send referral notification to referred user {referred_chat_id}: {e}")
            
            # Notify referrer about successful referral
            referrer_message = self._get_text(
                'referral_referrer',
                referrer_lang,
                new_user_name=referred_name
            )
            
            try:
                await self.client.send_message(referrer_chat_id, referrer_message)
                log_user_action(referrer_chat_id, 'successful_referral_notification', {
                    'referred_user_id': referred_chat_id,
                    'referred_user_name': referred_name
                })
            except Exception as e:
                logger.error(f"Failed to send referral notification to referrer {referrer_chat_id}: {e}")
                
            logger.info(f"Referral notifications sent successfully: referrer={referrer_chat_id}, referred={referred_chat_id}")
            return True
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'send_referral_notifications',
                'referrer_id': referrer_chat_id,
                'referred_id': referred_chat_id
            })
            return False
    
    def generate_referral_link(self, bot_username: str, user_id: int) -> str:
        """Generate referral link for user."""
        return f"https://t.me/{bot_username}?start={user_id}"
    
    async def process_successful_referral(self, referrer_id: int, referred_id: int) -> Dict:
        """Process a successful referral with notifications and rewards."""
        try:
            # Process referral in database (awards stars and records referral)
            success = await self.db.process_referral(referrer_id, referred_id)
            
            if success:
                # Send notifications to both users
                await self.send_referral_notifications(referrer_id, referred_id)
                
                # Check and send milestone notifications
                await self.send_milestone_notifications(referrer_id)
                
                logger.info(f"Referral processed successfully: {referrer_id} -> {referred_id}")
                return {
                    'success': True,
                    'message': 'Referral processed successfully'
                }
            else:
                logger.warning(f"Referral processing failed: {referrer_id} -> {referred_id}")
                return {
                    'success': False,
                    'message': 'Failed to process referral'
                }
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'process_successful_referral',
                'referrer_id': referrer_id,
                'referred_id': referred_id
            })
            return {
                'success': False,
                'message': 'Error processing referral'
            }
    
    async def send_milestone_notifications(self, user_id: int) -> bool:
        """Send any pending milestone notifications to user."""
        try:
            logger.info(f"Checking for milestone notifications for user {user_id}")
            user = await self.db.get_user(user_id)
            if not user:
                return False
            
            raw_data = user.get('Raw_Data') or {}
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data) if raw_data else {}
            elif raw_data is None:
                raw_data = {}
            
            pending_notifications = raw_data.get('pending_notifications', [])
            milestone_notifications = [n for n in pending_notifications if n.get('type') == 'milestone']
            
            logger.info(f"Found {len(milestone_notifications)} milestone notifications for user {user_id}")
            
            if milestone_notifications:
                lang_code = user.get('Language_Code', 'en')
                
                for notification in milestone_notifications:
                    milestone = notification['milestone']
                    total_stars = notification['total_stars']
                    activated_plan = notification.get('activated_plan')
                    
                    # Map milestone to language key
                    milestone_key = {
                        50: 'milestone_10_stars',   # Level 1: 50 stars 
                        100: 'milestone_15_stars',  # Level 2: 100 stars
                        200: 'milestone_20_stars',  # Level 3: 200 stars
                        500: 'milestone_25_stars',
                        1000: 'milestone_30_stars'
                    }.get(milestone)
                    
                    if milestone_key:
                        message = self._get_text(milestone_key, lang_code)
                        message += f"\n\n⭐ **Total Stars:** {total_stars}"
                        
                        # Add plan activation notification if applicable
                        if activated_plan:
                            if lang_code == 'fa':
                                plan_message = f"\n\n🎁 **جایزه ویژه:** پلن {activated_plan.title()} برای 1 ماه فعال شد!"
                                plan_message += f"\n✨ اکنون می‌توانید از تمام امکانات پیشرفته استفاده کنید!"
                            else:
                                plan_message = f"\n\n🎁 **Special Reward:** {activated_plan.title()} plan activated for 1 month!"
                                plan_message += f"\n✨ You now have access to all premium features!"
                            message += plan_message
                        
                        await self.client.send_message(user_id, message)
                        logger.info(f"Sent milestone notification to {user_id}: {milestone} stars" + 
                                  (f" with {activated_plan} plan activation" if activated_plan else ""))
                
                # Clear processed notifications
                raw_data['pending_notifications'] = [n for n in pending_notifications if n.get('type') != 'milestone']
                await self.db.execute_update(
                    "UPDATE users SET Raw_Data = %s WHERE Chat_Id = %s",
                    (json.dumps(raw_data), user_id)
                )
                
                return True
            return True  # Return True even if no notifications to send
                
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'send_milestone_notifications',
                'user_id': user_id
            })
            return False
    
    async def get_user_referral_stats(self, user_id: int) -> Dict:
        """Get user's referral statistics."""
        try:
            user = await self.db.get_user(user_id)
            if not user:
                return {
                    'total_referrals': 0,
                    'total_stars': 0,
                    'current_level': 1,
                    'next_milestone': 50
                }
            
            total_referrals = user.get('Total_Referrals', 0)
            total_stars = user.get('Stars', 0)
            
            # Calculate current level and next milestone
            current_level = 1
            next_milestone = 50
            
            for milestone in sorted(self.milestone_rewards.keys()):
                if total_stars >= milestone:
                    current_level += 1
                else:
                    next_milestone = milestone
                    break
            
            return {
                'total_referrals': total_referrals,
                'total_stars': total_stars,
                'current_level': current_level,
                'next_milestone': next_milestone,
                'stars_to_next_milestone': max(0, next_milestone - total_stars)
            }
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_user_referral_stats',
                'user_id': user_id
            })
            return {
                'total_referrals': 0,
                'total_stars': 0,
                'current_level': 1,
                'next_milestone': 50
            }
    
    async def award_stars(self, user_id: int, stars: int, reason: str = 'referral') -> bool:
        """Award stars to a user."""
        try:
            success = await self.db.add_user_stars(user_id, stars)
            
            if success:
                log_user_action(user_id, 'stars_awarded', {
                    'stars': stars,
                    'reason': reason
                })
                
                # Check for milestone achievement
                await self._check_milestone_achievement(user_id)
                
            return success
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'award_stars',
                'user_id': user_id,
                'stars': stars
            })
            return False
    
    async def _check_milestone_achievement(self, user_id: int) -> None:
        """Check if user achieved any milestones and queue notifications."""
        try:
            user = await self.db.get_user(user_id)
            if not user:
                return
            
            current_stars = user.get('Stars', 0)
            
            # Check achieved milestones
            for milestone, reward in self.milestone_rewards.items():
                if current_stars >= milestone:
                    # Check if already notified
                    raw_data = user.get('Raw_Data') or {}
                    if isinstance(raw_data, str):
                        raw_data = json.loads(raw_data) if raw_data else {}
                    
                    achieved_milestones = raw_data.get('achieved_milestones', [])
                    
                    if milestone not in achieved_milestones:
                        # Add to achieved milestones
                        achieved_milestones.append(milestone)
                        raw_data['achieved_milestones'] = achieved_milestones
                        
                        # Queue milestone notification
                        pending_notifications = raw_data.get('pending_notifications', [])
                        pending_notifications.append({
                            'type': 'milestone',
                            'milestone': milestone,
                            'total_stars': current_stars,
                            'activated_plan': reward.get('plan')
                        })
                        raw_data['pending_notifications'] = pending_notifications
                        
                        # Update user data
                        await self.db.execute_update(
                            "UPDATE users SET Raw_Data = %s WHERE Chat_ID = %s",
                            (json.dumps(raw_data), user_id)
                        )
                        
                        logger.info(f"Milestone {milestone} achieved by user {user_id}")
                        
        except Exception as e:
            log_error_with_context(e, {
                'operation': '_check_milestone_achievement',
                'user_id': user_id
            })
    
    async def get_referral_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top referrers leaderboard."""
        try:
            query = """
                SELECT Chat_ID, First_Name, Username, Total_Referrals, Stars
                FROM users 
                WHERE Total_Referrals > 0 
                ORDER BY Total_Referrals DESC, Stars DESC 
                LIMIT %s
            """
            
            results = await self.db.execute_query(query, (limit,))
            
            leaderboard = []
            for i, user in enumerate(results, 1):
                leaderboard.append({
                    'rank': i,
                    'user_id': user['Chat_ID'],
                    'name': user['First_Name'],
                    'username': user.get('Username'),
                    'referrals': user['Total_Referrals'],
                    'stars': user['Stars']
                })
            
            return leaderboard
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'get_referral_leaderboard'
            })
            return []
    
    def format_referral_link_message(self, bot_username: str, user_id: int, 
                                   lang_code: str, current_stars: int = 0) -> str:
        """Format referral link message with user stats."""
        referral_link = self.generate_referral_link(bot_username, user_id)
        
        return self._get_text(
            'referral_link_text',
            lang_code,
            link=referral_link,
            stars=current_stars
        )


def create_referral_service(db: DatabaseManager, client: Client) -> UserReferralService:
    """Factory function to create UserReferralService."""
    return UserReferralService(db, client)