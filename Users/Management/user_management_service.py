"""
Comprehensive user management service.
Central service for all user-related operations and coordination.
"""

from typing import Dict, Optional, List, Any
from hydrogram import Client

from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService
from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)


class UserManagementService:
    """Central service for comprehensive user management."""
    
    def __init__(self, db: DatabaseManager, redis: RedisService, 
                 email_service, client: Client):
        """Initialize user management service."""
        self.db = db
        self.redis = redis
        self.email_service = email_service
        self.client = client
        
        # Initialize sub-services
        self.auth_service = None
        self.subscription_service = None
        self.referral_service = None
        self.limiter = None
        self.profile_service = None
    
    # User Management Methods
    async def ban_user(self, user_id: int, reason: str = 'violation') -> bool:
        """Ban a user."""
        try:
            query = "UPDATE users SET Is_Banned = TRUE WHERE Chat_ID = %s"
            rows_affected = await self.db.execute_update(query, (user_id,))
            
            if rows_affected > 0:
                logger.info(f"User {user_id} banned. Reason: {reason}")
                return True
            
            return False
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'ban_user',
                'user_id': user_id,
                'reason': reason
            })
            return False
    
    async def unban_user(self, user_id: int) -> bool:
        """Unban a user."""
        try:
            query = "UPDATE users SET Is_Banned = FALSE WHERE Chat_ID = %s"
            rows_affected = await self.db.execute_update(query, (user_id,))
            
            if rows_affected > 0:
                logger.info(f"User {user_id} unbanned")
                return True
            
            return False
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'unban_user',
                'user_id': user_id
            })
            return False
    
    async def search_users(self, search_term: str, limit: int = 10) -> List[Dict]:
        """Search users by name, email, or ID."""
        try:
            # Search by multiple criteria
            query = """
                SELECT Chat_ID, First_Name, Last_Name, Username, Email, 
                       Language_Code, Is_Banned, Stars, Total_Referrals, Created_At
                FROM users 
                WHERE (
                    LOWER(First_Name) LIKE LOWER(%s) OR 
                    LOWER(Last_Name) LIKE LOWER(%s) OR 
                    LOWER(Username) LIKE LOWER(%s) OR 
                    LOWER(Email) LIKE LOWER(%s) OR 
                    Chat_ID = %s
                )
                ORDER BY Created_At DESC
                LIMIT %s
            """
            
            search_pattern = f"%{search_term}%"
            
            # Try to parse as integer for ID search
            try:
                search_id = int(search_term)
            except ValueError:
                search_id = 0
            
            params = (search_pattern, search_pattern, search_pattern, 
                     search_pattern, search_id, limit)
            
            results = await self.db.execute_query(query, params)
            
            users = []
            for result in results:
                users.append({
                    'user_id': result['Chat_ID'],
                    'name': f"{result['First_Name']} {result.get('Last_Name', '')}".strip(),
                    'username': result.get('Username'),
                    'email': result.get('Email'),
                    'language': result.get('Language_Code'),
                    'is_banned': result.get('Is_Banned', False),
                    'stars': result.get('Stars', 0),
                    'referrals': result.get('Total_Referrals', 0),
                    'created_at': result.get('Created_At')
                })
            
            return users
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'search_users',
                'search_term': search_term
            })
            return []
    
    async def get_user_analytics(self) -> Dict[str, Any]:
        """Get comprehensive user analytics."""
        try:
            analytics = {}
            
            # Total users
            total_query = "SELECT COUNT(*) as total FROM users"
            total_result = await self.db.execute_query(total_query)
            analytics['total_users'] = total_result[0]['total'] if total_result else 0
            
            # Active users (not banned)
            active_query = "SELECT COUNT(*) as active FROM users WHERE Is_Banned = FALSE"
            active_result = await self.db.execute_query(active_query)
            analytics['active_users'] = active_result[0]['active'] if active_result else 0
            
            # Users with email
            email_query = "SELECT COUNT(*) as with_email FROM users WHERE Email IS NOT NULL"
            email_result = await self.db.execute_query(email_query)
            analytics['users_with_email'] = email_result[0]['with_email'] if email_result else 0
            
            # Language distribution
            lang_query = """
                SELECT Language_Code, COUNT(*) as count 
                FROM users 
                GROUP BY Language_Code
            """
            lang_results = await self.db.execute_query(lang_query)
            analytics['language_distribution'] = {
                result['Language_Code']: result['count'] for result in lang_results
            }
            
            # Recent registrations (last 7 days)
            recent_query = """
                SELECT COUNT(*) as recent 
                FROM users 
                WHERE Created_At >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """
            recent_result = await self.db.execute_query(recent_query)
            analytics['recent_registrations'] = recent_result[0]['recent'] if recent_result else 0
            
            # Top referrers
            referrer_query = """
                SELECT Chat_ID, First_Name, Username, Total_Referrals 
                FROM users 
                WHERE Total_Referrals > 0 
                ORDER BY Total_Referrals DESC 
                LIMIT 5
            """
            referrer_results = await self.db.execute_query(referrer_query)
            analytics['top_referrers'] = [
                {
                    'user_id': r['Chat_ID'],
                    'name': r['First_Name'],
                    'username': r.get('Username'),
                    'referrals': r['Total_Referrals']
                }
                for r in referrer_results
            ]
            
            return analytics
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'get_user_analytics'})
            return {}
    
    async def cleanup_inactive_users(self, days_inactive: int = 365) -> int:
        """Clean up users inactive for specified days."""
        try:
            # Mark users as inactive (don't delete immediately)
            query = """
                UPDATE users 
                SET Is_Banned = TRUE 
                WHERE Last_Login < DATE_SUB(NOW(), INTERVAL %s DAY)
                AND Is_Banned = FALSE
            """
            
            rows_affected = await self.db.execute_update(query, (days_inactive,))
            logger.info(f"Marked {rows_affected} inactive users as banned")
            
            return rows_affected
            
        except Exception as e:
            log_error_with_context(e, {
                'operation': 'cleanup_inactive_users',
                'days_inactive': days_inactive
            })
            return 0
    
    # Utility Methods
    async def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language."""
        try:
            user = await self.db.get_user(user_id)
            return user.get('Language_Code', 'en') if user else 'en'
        except Exception:
            return 'en'
    
    async def update_last_activity(self, user_id: int) -> bool:
        """Update user's last activity timestamp."""
        try:
            query = "UPDATE users SET Last_Login = NOW() WHERE Chat_ID = %s"
            rows_affected = await self.db.execute_update(query, (user_id,))
            return rows_affected > 0
        except Exception:
            return False


def create_user_management_service(db: DatabaseManager, redis: RedisService,
                                 email_service, 
                                 client: Client) -> UserManagementService:
    """Factory function to create UserManagementService."""
    return UserManagementService(db, redis, email_service, client)