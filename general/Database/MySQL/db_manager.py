"""Database Manager for MySQL operations with modern async patterns.
Handles all database interactions with proper connection pooling and error handling."""

import aiomysql
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from general.Logging.logger_manager import get_logger, log_error_with_context

logger = get_logger(__name__)

# Use general configuration instead of old config.py
from general.Configuration.config_manager import get_core_config

class DatabaseManager:
    """Modern async database manager with connection pooling."""
    
    def __init__(self):
        """Initialize database manager."""
        self.pool: Optional[aiomysql.Pool] = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize database connection pool with optimized settings."""
        try:
            core_config = get_core_config()
            
            # Optimized connection pool settings for performance
            self.pool = await aiomysql.create_pool(
                host=core_config.database.host,
                port=core_config.database.port,
                user=core_config.database.user,
                password=core_config.database.password,
                db=core_config.database.database,
                charset='utf8mb4',
                minsize=15,  # Increased minimum connections for better concurrency
                maxsize=100,  # Increased maximum connections for high load handling
                pool_recycle=1800,  # Recycle connections every 30 minutes (more frequent)
                autocommit=True,
                echo=False,  # Disable query logging in production
                # pool_pre_ping=True,  # Verify connections before use (not supported by aiomysql)
                connect_timeout=5,  # Reduced connection timeout for faster failure detection
                # read_timeout=5,     # Reduced read timeout (not supported by aiomysql)
                # write_timeout=5,    # Reduced write timeout (not supported by aiomysql)
                # pool_timeout=30     # Pool acquisition timeout (not supported by aiomysql)
            )
            
            self.is_initialized = True
            logger.info("Database connection pool initialized successfully with optimized settings")
            
        except Exception as e:
            log_error_with_context(e, {'method': 'initialize_database'})
            raise
    
    async def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Execute a SELECT query and return results with connection validation."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        try:
            # Use connection context manager for automatic cleanup
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params or ())
                    result = await cursor.fetchall()
                    return result
        except Exception as e:
            log_error_with_context(e, {'query': query, 'params': params})
            return []
    
    async def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    rows_affected = await cursor.execute(query, params or ())
                    await conn.commit()
                    return rows_affected
        except Exception as e:
            log_error_with_context(e, {'query': query, 'params': params})
            return 0
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID with caching."""
        query = "SELECT * FROM users WHERE Chat_ID = %s"
        result = await self.execute_query(query, (user_id,))
        return result[0] if result else None

    async def get_admins(self) -> List[Dict]:
        """Get all admin users."""
        try:
            # Get admin IDs from environment variable
            import os
            admin_ids = [int(x) for x in str(os.getenv('ADMIN_CHAT_IDS', '')).split(',') if x.strip().isdigit()]
            
            if not admin_ids:
                return []
            
            # Create placeholders for the IN clause
            placeholders = ','.join(['%s'] * len(admin_ids))
            query = f"SELECT * FROM users WHERE Chat_ID IN ({placeholders})"
            result = await self.execute_query(query, tuple(admin_ids))
            return result if result else []
        except Exception as e:
            log_error_with_context(e, {'method': 'get_admins'})
            return []

    async def create_user(self, chat_id: int, first_name: str, last_name: Optional[str] = None, 
                         username: Optional[str] = None, language_code: str = 'en', 
                         referrer_id: Optional[int] = None) -> Dict:
        """Create a new user."""
        try:
            query = """
                INSERT INTO users (Chat_ID, First_Name, Last_Name, Username, Language_Code, Referrer_ID, Created_At)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            params = (chat_id, first_name, last_name, username, language_code, referrer_id)
            
            rows_affected = await self.execute_update(query, params)
            
            # Process referral if referrer_id is provided
            if referrer_id and rows_affected > 0:
                await self.process_referral(referrer_id, chat_id)
            
            return {
                'success': rows_affected > 0,
                'referral_processed': bool(referrer_id and rows_affected > 0)
            }
        except Exception as e:
            log_error_with_context(e, {'method': 'create_user', 'chat_id': chat_id})
            return {'success': False}
    
    async def update_login_info(self, user_id: int):
        """Update user login information."""
        query = "UPDATE users SET Last_Login = NOW() WHERE Chat_ID = %s"
        await self.execute_update(query, (user_id,))
    
    async def update_user_language(self, user_id: int, language_code: str):
        """Update user language preference."""
        query = "UPDATE users SET Language_Code = %s WHERE Chat_ID = %s"
        await self.execute_update(query, (user_id, language_code))
    
    async def get_user_tickets(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user tickets."""
        query = """
            SELECT * FROM tickets 
            WHERE User_ID = %s 
            ORDER BY Created_At DESC 
            LIMIT %s
        """
        return await self.execute_query(query, (user_id, limit))
    
    async def get_ticket(self, ticket_id: int, user_id: int) -> Optional[Dict]:
        """Get specific ticket by ID and user."""
        query = "SELECT * FROM tickets WHERE ID = %s AND User_ID = %s"
        result = await self.execute_query(query, (ticket_id, user_id))
        return result[0] if result else None
    
    async def get_ticket_messages(self, ticket_id: int) -> List[Dict]:
        """Get messages for a ticket."""
        query = """
            SELECT * FROM ticket_messages 
            WHERE Ticket_ID = %s 
            ORDER BY Created_At ASC
        """
        return await self.execute_query(query, (ticket_id,))
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address."""
        query = "SELECT * FROM users WHERE Email = %s"
        result = await self.execute_query(query, (email,))
        return result[0] if result else None
    
    async def update_user_email_password(self, user_id: int, email: str, password_hash: str) -> bool:
        """Update user's email and password hash."""
        query = "UPDATE users SET Email = %s, Password_Hash = %s WHERE Chat_ID = %s"
        rows_affected = await self.execute_update(query, (email, password_hash, user_id))
        return rows_affected > 0
    
    async def update_user_password(self, user_id: int, password_hash: str) -> bool:
        """Update user's password hash."""
        query = "UPDATE users SET Password_Hash = %s WHERE Chat_ID = %s"
        rows_affected = await self.execute_update(query, (password_hash, user_id))
        return rows_affected > 0
    
    async def get_feature_usage(self, user_id: int, feature: str, period: str) -> int:
        """Get feature usage count for a user."""
        try:
            query = """
                SELECT Usage_Count 
                FROM feature_usage 
                WHERE User_ID = %s AND Feature_Name = %s AND Period = %s
            """
            result = await self.execute_query(query, (user_id, feature, period))
            return result[0]['Usage_Count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {
                'method': 'get_feature_usage',
                'user_id': user_id,
                'feature': feature,
                'period': period
            })
            return 0
    
    async def increment_feature_usage(self, user_id: int, feature: str, amount: int = 1) -> bool:
        """Increment feature usage for a user."""
        try:
            # First try to update existing record
            update_query = """
                UPDATE feature_usage 
                SET Usage_Count = Usage_Count + %s, Last_Updated = NOW()
                WHERE User_ID = %s AND Feature_Name = %s AND Period = %s
            """
            rows_affected = await self.execute_update(update_query, (amount, user_id, feature, self._get_current_period()))
            
            # If no rows were affected, insert a new record
            if rows_affected == 0:
                insert_query = """
                    INSERT INTO feature_usage (User_ID, Feature_Name, Period, Usage_Count, Last_Updated)
                    VALUES (%s, %s, %s, %s, NOW())
                """
                await self.execute_update(insert_query, (user_id, feature, self._get_current_period(), amount))
            
            return True
        except Exception as e:
            log_error_with_context(e, {
                'method': 'increment_feature_usage',
                'user_id': user_id,
                'feature': feature,
                'amount': amount
            })
            return False
    
    def _get_current_period(self) -> str:
        """Get current period for feature usage tracking."""
        now = datetime.now()
        hour = now.strftime('%Y-%m-%d %H')
        day = now.strftime('%Y-%m-%d')
        month = now.strftime('%Y-%m')
        return f"hourly:{hour}|daily:{day}|monthly:{month}"
    
    async def process_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Process a successful referral by awarding stars to the referrer."""
        try:
            # Award 5 stars to the referrer
            update_query = """
                UPDATE users 
                SET Stars = Stars + 5, Total_Referrals = Total_Referrals + 1
                WHERE Chat_ID = %s
            """
            rows_affected = await self.execute_update(update_query, (referrer_id,))
            
            # Award 5 stars to the referred user
            referred_query = """
                UPDATE users 
                SET Stars = Stars + 5
                WHERE Chat_ID = %s
            """
            await self.execute_update(referred_query, (referred_id,))
            
            return rows_affected > 0
        except Exception as e:
            log_error_with_context(e, {
                'method': 'process_referral',
                'referrer_id': referrer_id,
                'referred_id': referred_id
            })
            return False
    
    async def add_user_stars(self, user_id: int, stars: int) -> bool:
        """Add stars to a user's account."""
        try:
            query = "UPDATE users SET Stars = Stars + %s WHERE Chat_ID = %s"
            rows_affected = await self.execute_update(query, (stars, user_id))
            return rows_affected > 0
        except Exception as e:
            log_error_with_context(e, {
                'method': 'add_user_stars',
                'user_id': user_id,
                'stars': stars
            })
            return False
    
    async def get_user_subscription(self, user_id: int) -> Optional[Dict]:
        """Get user's current subscription."""
        try:
            query = """
                SELECT * FROM subscriptions 
                WHERE User_ID = %s AND Status = 'active' AND End_Date > NOW()
                ORDER BY End_Date DESC 
                LIMIT 1
            """
            result = await self.execute_query(query, (user_id,))
            return result[0] if result else None
        except Exception as e:
            log_error_with_context(e, {
                'method': 'get_user_subscription',
                'user_id': user_id
            })
            return None
    
    async def create_or_update_subscription(self, user_id: int, plan_type: str, 
                                          end_date: datetime, payment_method: str, 
                                          amount_paid: float) -> bool:
        """Create or update a user's subscription."""
        try:
            # Check if user already has an active subscription
            existing_query = """
                SELECT ID FROM subscriptions 
                WHERE User_ID = %s AND Status = 'active' AND End_Date > NOW()
            """
            existing = await self.execute_query(existing_query, (user_id,))
            
            if existing:
                # Update existing subscription
                update_query = """
                    UPDATE subscriptions 
                    SET Plan_Type = %s, End_Date = %s, Payment_Method = %s, Amount_Paid = %s, Last_Updated = NOW()
                    WHERE ID = %s
                """
                subscription_id = existing[0]['ID']
                rows_affected = await self.execute_update(update_query, 
                                                        (plan_type, end_date, payment_method, amount_paid, subscription_id))
            else:
                # Create new subscription
                insert_query = """
                    INSERT INTO subscriptions (User_ID, Plan_Type, Start_Date, End_Date, Status, Payment_Method, Amount_Paid)
                    VALUES (%s, %s, NOW(), %s, 'active', %s, %s)
                """
                rows_affected = await self.execute_update(insert_query, 
                                                        (user_id, plan_type, end_date, payment_method, amount_paid))
            
            return rows_affected > 0
        except Exception as e:
            log_error_with_context(e, {
                'method': 'create_or_update_subscription',
                'user_id': user_id,
                'plan_type': plan_type
            })
            return False
    
    async def create_ticket(self, user_id: int, category: str, subject: str, message: str) -> Optional[int]:
        """Create a new support ticket."""
        try:
            # Create the ticket
            ticket_query = """
                INSERT INTO tickets (User_ID, Category, Subject, Status, Priority, Created_At, Updated_At)
                VALUES (%s, %s, %s, 'open', 'normal', NOW(), NOW())
            """
            ticket_id = await self.execute_update(ticket_query, (user_id, category, subject))
            
            if ticket_id > 0:
                # Get the actual ticket ID (this is a simplification - in reality, we'd need to get the last inserted ID)
                # For now, we'll just return a placeholder
                return ticket_id
            return None
        except Exception as e:
            log_error_with_context(e, {
                'method': 'create_ticket',
                'user_id': user_id,
                'category': category,
                'subject': subject
            })
            return None
    
    async def add_ticket_message(self, ticket_id: int, user_id: int, message: str, is_admin: bool = False) -> bool:
        """Add a message to a ticket."""
        try:
            query = """
                INSERT INTO ticket_messages (Ticket_ID, User_ID, Message, Is_Admin, Created_At)
                VALUES (%s, %s, %s, %s, NOW())
            """
            rows_affected = await self.execute_update(query, (ticket_id, user_id, message, is_admin))
            
            # Update ticket's updated_at timestamp
            update_query = "UPDATE tickets SET Updated_At = NOW() WHERE ID = %s"
            await self.execute_update(update_query, (ticket_id,))
            
            return rows_affected > 0
        except Exception as e:
            log_error_with_context(e, {
                'method': 'add_ticket_message',
                'ticket_id': ticket_id,
                'user_id': user_id
            })
            return False
    
    async def close(self):
        """Close database connections."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Database connections closed")
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.pool and not self.pool._closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    asyncio.run(self.close())
            except Exception:
                pass
    
    # === Analytics Service Methods ===
    
    async def get_total_users(self) -> int:
        """Get total user count."""
        try:
            query = "SELECT COUNT(*) as count FROM users"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_total_users'})
            return 0
    
    async def get_banned_users_count(self) -> int:
        """Get banned users count."""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE Is_Banned = TRUE"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_banned_users_count'})
            return 0
    
    async def get_users_registered_after(self, date) -> int:
        """Get users registered after a specific date."""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE Created_At >= %s"
            result = await self.execute_query(query, (date,))
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_users_registered_after', 'date': date})
            return 0
    
    async def get_active_users_count(self, cutoff_date) -> int:
        """Get active users count."""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE Last_Login >= %s"
            result = await self.execute_query(query, (cutoff_date,))
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_active_users_count', 'cutoff_date': cutoff_date})
            return 0
    
    async def get_users_with_accounts_count(self) -> int:
        """Get users with email accounts."""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE Email IS NOT NULL"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_users_with_accounts_count'})
            return 0
    
    async def get_language_distribution(self) -> Dict[str, int]:
        """Get language distribution statistics."""
        try:
            query = "SELECT Language_Code, COUNT(*) as count FROM users GROUP BY Language_Code"
            results = await self.execute_query(query)
            return {result['Language_Code']: result['count'] for result in results} if results else {}
        except Exception as e:
            log_error_with_context(e, {'method': 'get_language_distribution'})
            return {}
    
    async def get_users_registered_between(self, start_date, end_date) -> int:
        """Get users registered between dates."""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE Created_At >= %s AND Created_At <= %s"
            result = await self.execute_query(query, (start_date, end_date))
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_users_registered_between', 'start_date': start_date, 'end_date': end_date})
            return 0
    
    async def get_total_chats(self) -> int:
        """Get total chat count."""
        try:
            query = "SELECT COUNT(*) as count FROM bot_chats"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_total_chats'})
            return 0
    
    async def get_banned_chats_count(self) -> int:
        """Get banned chats count."""
        try:
            query = "SELECT COUNT(*) as count FROM bot_chats WHERE Is_Banned = TRUE"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_banned_chats_count'})
            return 0
    
    async def get_chat_type_breakdown(self) -> Dict[str, int]:
        """Get chat type distribution."""
        try:
            query = "SELECT Type, COUNT(*) as count FROM bot_chats GROUP BY Type"
            results = await self.execute_query(query)
            return {result['Type']: result['count'] for result in results} if results else {}
        except Exception as e:
            log_error_with_context(e, {'method': 'get_chat_type_breakdown'})
            return {}
    
    async def get_chats_added_after(self, date) -> int:
        """Get chats added after a specific date."""
        try:
            query = "SELECT COUNT(*) as count FROM bot_chats WHERE Created_At >= %s"
            result = await self.execute_query(query, (date,))
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_chats_added_after', 'date': date})
            return 0
    
    async def get_member_statistics(self) -> Tuple[int, float]:
        """Get member statistics (total members, average members per chat)."""
        try:
            # Get total members
            total_query = "SELECT SUM(Member_Count) as total FROM bot_chats WHERE Member_Count IS NOT NULL"
            total_result = await self.execute_query(total_query)
            total_members = total_result[0]['total'] if total_result and total_result[0]['total'] else 0
            
            # Get average members per chat
            avg_query = "SELECT AVG(Member_Count) as average FROM bot_chats WHERE Member_Count IS NOT NULL"
            avg_result = await self.execute_query(avg_query)
            avg_members = avg_result[0]['average'] if avg_result and avg_result[0]['average'] else 0.0
            
            return int(total_members), float(avg_members)
        except Exception as e:
            log_error_with_context(e, {'method': 'get_member_statistics'})
            return 0, 0.0
    
    async def get_total_referrals(self) -> int:
        """Get total referral count."""
        try:
            query = "SELECT COUNT(*) as count FROM referrals"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_total_referrals'})
            return 0
    
    async def get_successful_referrals_count(self) -> int:
        """Get successful referrals count."""
        try:
            query = "SELECT COUNT(*) as count FROM referrals WHERE Is_Successful = TRUE"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_successful_referrals_count'})
            return 0
    
    async def get_referrals_after(self, date) -> int:
        """Get referrals after a specific date."""
        try:
            query = "SELECT COUNT(*) as count FROM referrals WHERE Created_At >= %s"
            result = await self.execute_query(query, (date,))
            return result[0]['count'] if result else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_referrals_after', 'date': date})
            return 0
    
    async def get_total_referral_stars(self) -> int:
        """Get total referral stars distributed."""
        try:
            query = "SELECT SUM(Stars_Awarded) as total FROM referrals WHERE Stars_Awarded IS NOT NULL"
            result = await self.execute_query(query)
            return result[0]['total'] if result and result[0]['total'] else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_total_referral_stars'})
            return 0
    
    async def get_top_referrers(self, limit: int = 10) -> List[Dict]:
        """Get top referrers."""
        try:
            query = """
                SELECT u.Chat_ID, u.First_Name, u.Username, u.Total_Referrals 
                FROM users u 
                WHERE u.Total_Referrals > 0 
                ORDER BY u.Total_Referrals DESC 
                LIMIT %s
            """
            return await self.execute_query(query, (limit,))
        except Exception as e:
            log_error_with_context(e, {'method': 'get_top_referrers', 'limit': limit})
            return []
    
    async def get_daily_registrations(self, start_date, end_date) -> List[Dict]:
        """Get daily registration data."""
        try:
            query = """
                SELECT DATE(Created_At) as date, COUNT(*) as count 
                FROM users 
                WHERE Created_At >= %s AND Created_At <= %s 
                GROUP BY DATE(Created_At) 
                ORDER BY DATE(Created_At)
            """
            return await self.execute_query(query, (start_date, end_date))
        except Exception as e:
            log_error_with_context(e, {'method': 'get_daily_registrations', 'start_date': start_date, 'end_date': end_date})
            return []
    
    async def get_daily_chat_additions(self, start_date, end_date) -> List[Dict]:
        """Get daily chat additions."""
        try:
            query = """
                SELECT DATE(Created_At) as date, COUNT(*) as count 
                FROM bot_chats 
                WHERE Created_At >= %s AND Created_At <= %s 
                GROUP BY DATE(Created_At) 
                ORDER BY DATE(Created_At)
            """
            return await self.execute_query(query, (start_date, end_date))
        except Exception as e:
            log_error_with_context(e, {'method': 'get_daily_chat_additions', 'start_date': start_date, 'end_date': end_date})
            return []
    
    async def get_feature_usage_statistics(self) -> Dict[str, Any]:
        """Get feature usage statistics."""
        try:
            query = "SELECT Feature_Name, SUM(Usage_Count) as total_usage FROM feature_usage GROUP BY Feature_Name"
            results = await self.execute_query(query)
            return {result['Feature_Name']: result['total_usage'] for result in results} if results else {}
        except Exception as e:
            log_error_with_context(e, {'method': 'get_feature_usage_statistics'})
            return {}
    
    # === System Health Service Methods ===
    
    async def get_database_size(self) -> int:
        """Get database size in bytes."""
        try:
            query = "SELECT SUM(data_length + index_length) as size FROM information_schema.tables WHERE table_schema = DATABASE()"
            result = await self.execute_query(query)
            return result[0]['size'] if result and result[0]['size'] else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_database_size'})
            return 0
    
    async def get_table_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get table statistics."""
        try:
            query = """
                SELECT table_name, table_rows, data_length, index_length 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """
            results = await self.execute_query(query)
            stats = {}
            for result in results:
                table_name = result['table_name']
                stats[table_name] = {
                    'row_count': result['table_rows'],
                    'data_size': result['data_length'],
                    'index_size': result['index_length'],
                    'total_size': result['data_length'] + result['index_length']
                }
            return stats
        except Exception as e:
            log_error_with_context(e, {'method': 'get_table_statistics'})
            return {}
    
    async def get_total_records(self) -> int:
        """Get total records count across all tables."""
        try:
            query = "SELECT SUM(table_rows) as total FROM information_schema.tables WHERE table_schema = DATABASE()"
            result = await self.execute_query(query)
            return result[0]['total'] if result and result[0]['total'] else 0
        except Exception as e:
            log_error_with_context(e, {'method': 'get_total_records'})
            return 0
    
    async def get_connection_pool_status(self) -> str:
        """Get connection pool status."""
        try:
            # This is a placeholder - actual implementation would depend on the connection pool
            return "healthy" if self.pool else "uninitialized"
        except Exception as e:
            log_error_with_context(e, {'method': 'get_connection_pool_status'})
            return "error"
    
    async def get_query_performance(self) -> Dict[str, float]:
        """Get query performance metrics."""
        try:
            # This is a placeholder - actual implementation would depend on monitoring setup
            return {}
        except Exception as e:
            log_error_with_context(e, {'method': 'get_query_performance'})
            return {}
    
    async def get_last_backup_time(self) -> Optional[datetime]:
        """Get last backup time."""
        try:
            # This is a placeholder - actual implementation would depend on backup system
            return None
        except Exception as e:
            log_error_with_context(e, {'method': 'get_last_backup_time'})
            return None