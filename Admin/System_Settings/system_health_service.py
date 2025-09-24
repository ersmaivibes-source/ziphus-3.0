"""
System health monitoring service for admin panel.
Handles system monitoring, database health, and performance metrics.
"""

import asyncio
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from general.Database.MySQL.db_manager import DatabaseManager
from general.Caching.redis_service import RedisService
from general.Logging.logger_manager import get_logger

# Initialize logger
logger = get_logger(__name__)

# TODO: Fix import paths for these modules
# from Language.Translations import get_text, get_text_sync

@dataclass
class SystemHealthMetrics:
    """System health metrics data structure."""
    timestamp: datetime
    database_status: str
    database_size: int
    table_stats: Dict[str, Dict[str, Any]]
    active_connections: int
    redis_status: str
    redis_memory_usage: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: int
    last_24h_activity: Dict[str, int]
    error_count: int

@dataclass
class DatabaseHealth:
    """Database health information."""
    status: str
    size_mb: float
    table_count: int
    total_records: int
    tables: Dict[str, Dict[str, Any]]
    last_backup: Optional[datetime]
    connection_pool_status: str
    query_performance: Dict[str, float]

class SystemHealthService:
    """Service for monitoring system health and performance."""
    
    def __init__(self, db_manager: DatabaseManager, redis_service: Optional[RedisService] = None):
        self.db = db_manager
        self.redis = redis_service
        self.start_time = datetime.now()
        # Using optimized language system - no manager instance needed
    
    async def get_system_health(self) -> SystemHealthMetrics:
        """Get comprehensive system health metrics."""
        try:
            # Get database health
            db_health = await self.get_database_health()
            
            # Get Redis status
            redis_status = await self._get_redis_status()
            
            # Get system resources
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get 24h activity
            activity_24h = await self._get_24h_activity()
            
            # Get error count from logs (last 24h)
            error_count = await self._get_recent_error_count()
            
            # Calculate uptime
            uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            
            metrics = SystemHealthMetrics(
                timestamp=datetime.now(),
                database_status=db_health.status,
                database_size=int(db_health.size_mb * 1024 * 1024),  # Convert back to bytes
                table_stats=db_health.tables,
                active_connections=await self._get_active_db_connections(),
                redis_status=redis_status['status'],
                redis_memory_usage=redis_status['memory_usage'],
                cpu_usage=round(cpu_usage, 2),
                memory_usage=round(memory.percent, 2),
                disk_usage=round(disk.percent, 2),
                uptime=uptime_seconds,
                last_24h_activity=activity_24h,
                error_count=error_count
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealthMetrics(
                timestamp=datetime.now(),
                database_status="error",
                database_size=0,
                table_stats={},
                active_connections=0,
                redis_status="error",
                redis_memory_usage=0,
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                uptime=0,
                last_24h_activity={},
                error_count=0
            )
    
    async def get_database_health(self) -> DatabaseHealth:
        """Get detailed database health information."""
        try:
            # Get database size
            db_size = await self.db.get_database_size()
            
            # Get table statistics
            table_stats = await self.db.get_table_statistics()
            
            # Count total records
            total_records = await self.db.get_total_records()
            
            # Get connection pool status
            pool_status = await self.db.get_connection_pool_status()
            
            # Get query performance metrics
            query_performance = await self.db.get_query_performance()
            
            # Check last backup (if backup system exists)
            last_backup = await self.db.get_last_backup_time()
            
            health = DatabaseHealth(
                status="healthy" if db_size > 0 else "error",
                size_mb=db_size / (1024 * 1024) if db_size > 0 else 0,
                table_count=len(table_stats),
                total_records=total_records,
                tables=table_stats,
                last_backup=last_backup,
                connection_pool_status=pool_status,
                query_performance=query_performance
            )
            
            return health
            
        except Exception as e:
            logger.error(f"Error getting database health: {e}")
            return DatabaseHealth("error", 0, 0, 0, {}, None, "error", {})
    
    async def _get_redis_status(self) -> Dict[str, Any]:
        """Get Redis status and memory usage."""
        try:
            if not self.redis or not self.redis.redis:
                return {"status": "not_configured", "memory_usage": 0}
            
            # Test Redis connection
            await self.redis.redis.ping()
            
            # Get memory usage (if Redis info is available)
            memory_usage = 0
            try:
                info = await self.redis.redis.info()
                memory_usage = info.get('used_memory', 0)
            except Exception:
                pass
            
            return {
                "status": "healthy",
                "memory_usage": memory_usage
            }
            
        except Exception as e:
            logger.error(f"Error checking Redis status: {e}")
            return {"status": "error", "memory_usage": 0}
    
    async def _get_24h_activity(self) -> Dict[str, int]:
        """Get 24-hour activity metrics."""
        try:
            from datetime import datetime, timedelta
            
            # Calculate cutoff time for 24 hours ago
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # Get new users in the last 24 hours
            new_users = await self.db.get_users_registered_after(cutoff_time)
            
            # Get new chats in the last 24 hours
            new_chats = await self.db.get_chats_added_after(cutoff_time)
            
            # Get active users (logged in within last 24 hours)
            active_users = await self.db.get_active_users_count(cutoff_time)
            
            # For messages and tickets, we would need additional methods
            # For now, we'll use placeholders
            activity = {
                'new_users': new_users,
                'new_chats': new_chats,
                'active_users': active_users,
                'messages_sent': 0,  # Placeholder
                'tickets_created': 0  # Placeholder
            }
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting 24h activity: {e}")
            return {}
    
    async def _get_recent_error_count(self, hours: int = 24) -> int:
        """Get error count from recent logs."""
        try:
            # This would typically read from log files or error tracking system
            # For now, return a placeholder
            return 0
        except Exception:
            return 0
    
    async def _get_active_db_connections(self) -> int:
        """Get number of active database connections."""
        try:
            # This would require a specific implementation based on the database
            # For now, we'll return a placeholder or implement a proper method
            return 0
        except Exception:
            return 0
    
    async def _get_connection_pool_status(self) -> str:
        """Get database connection pool status."""
        try:
            return await self.db.get_connection_pool_status()
        except Exception:
            return 'unknown'
    
    async def _get_query_performance(self) -> Dict[str, float]:
        """Get database query performance metrics."""
        try:
            return await self.db.get_query_performance()
        except Exception:
            return {}
    
    async def _get_last_backup_time(self) -> Optional[datetime]:
        """Get last database backup time."""
        try:
            return await self.db.get_last_backup_time()
        except Exception:
            return None
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        try:
            # Database connectivity check
            try:
                # Using execute_query as a ping method
                await self.db.execute_query("SELECT 1")
                results['checks']['database'] = 'healthy'
            except Exception as e:
                results['checks']['database'] = 'error'
                results['errors'].append(f"Database: {str(e)}")
                results['overall_status'] = 'critical'
            
            # Redis connectivity check
            if self.redis and self.redis.redis:
                try:
                    await self.redis.redis.ping()
                    results['checks']['redis'] = 'healthy'
                except Exception as e:
                    results['checks']['redis'] = 'error'
                    results['errors'].append(f"Redis: {str(e)}")
                    if results['overall_status'] == 'healthy':
                        results['overall_status'] = 'warning'
            
            # System resources check
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # CPU check
            if cpu_usage > 90:
                results['warnings'].append(f"High CPU usage: {cpu_usage}%")
                if results['overall_status'] == 'healthy':
                    results['overall_status'] = 'warning'
            results['checks']['cpu'] = 'healthy' if cpu_usage < 80 else 'warning'
            
            # Memory check
            if memory.percent > 90:
                results['warnings'].append(f"High memory usage: {memory.percent}%")
                if results['overall_status'] == 'healthy':
                    results['overall_status'] = 'warning'
            results['checks']['memory'] = 'healthy' if memory.percent < 80 else 'warning'
            
            # Disk check
            if disk.percent > 90:
                results['warnings'].append(f"High disk usage: {disk.percent}%")
                if results['overall_status'] == 'healthy':
                    results['overall_status'] = 'warning'
            results['checks']['disk'] = 'healthy' if disk.percent < 80 else 'warning'
            
            # Database size check
            db_health = await self.get_database_health()
            if db_health.size_mb > 1000:  # 1GB
                results['warnings'].append(f"Large database size: {db_health.size_mb:.1f}MB")
            
            results['checks']['database_size'] = 'healthy'
            
        except Exception as e:
            results['overall_status'] = 'critical'
            results['errors'].append(f"Health check error: {str(e)}")
            logger.error(f"Error running health check: {e}")
        
        return results
    
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old data from database."""
        try:
            cleanup_date = datetime.now() - timedelta(days=days)
            
            results = {
                'cleaned_logs': 0,
                'cleaned_sessions': 0,
                'cleaned_temp_data': 0,
                'total_freed_mb': 0,
                'errors': []
            }
            
            # Using placeholders since these methods don't exist
            results['errors'].append("Cleanup methods not implemented in current DatabaseManager")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {'errors': [str(e)]}
    
    def format_system_health(self, metrics: SystemHealthMetrics, lang_code: str = 'en') -> str:
        """Format system health metrics for display with real-time data."""
        from datetime import datetime
        
        # Get current time
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Build text with real data
        text = f"System Health\n"
        text += f"⏰ Check Time: {current_time}\n\n"
        
        # Database section
        db_emoji = "✅" if metrics.database_status == "healthy" else "❌"
        db_status = "Healthy" if metrics.database_status == "healthy" else "Unhealthy"
        db_size_mb = metrics.database_size / (1024 * 1024)  # Convert to MB
        text += f"{db_emoji} Database: {db_status}\n"
        text += f"Database Size: {db_size_mb:.1f} MB\n"
        text += f"Active Connections: {metrics.active_connections}\n\n"
        
        # Redis section  
        redis_emoji = "✅" if metrics.redis_status == "healthy" else "❌"
        redis_status = "Healthy" if metrics.redis_status == "healthy" else "Unhealthy"
        text += f"{redis_emoji} Redis: {redis_status}\n"
        if metrics.redis_memory_usage > 0:
            redis_memory_mb = metrics.redis_memory_usage / (1024 * 1024)
            text += f"Redis Memory: {redis_memory_mb:.1f} MB\n\n"
        
        # System resources
        text += f"System Resources:\n"
        text += f"CPU Usage: {metrics.cpu_usage:.1f}%\n"
        text += f"Memory Usage: {metrics.memory_usage:.1f}%\n"
        text += f"Disk Usage: {metrics.disk_usage:.1f}%\n\n"
        
        # Uptime
        uptime_hours = metrics.uptime // 3600
        uptime_days = uptime_hours // 24
        remaining_hours = uptime_hours % 24
        text += f"⏱️ Uptime: {uptime_days} days, {remaining_hours} hours\n\n"
        
        # 24h activity
        if metrics.last_24h_activity:
            text += f"📊 24-Hour Activity:\n"
            for key, value in metrics.last_24h_activity.items():
                activity_label = key.replace('_', ' ').title()
                text += f"• {activity_label}: {value:,}\n"
        
        if metrics.error_count > 0:
            text += f"\n⚠️ Recent Errors: {metrics.error_count}"
        
        return text
    
    def format_database_health(self, health: DatabaseHealth, lang_code: str = 'en') -> str:
        """Format database health information for display with real-time data."""
        
        # Build text with real data
        text = f"Database Health\n\n"
        
        # Status section
        status_emoji = "✅" if health.status == "healthy" else "❌"
        status_text = "Healthy" if health.status == "healthy" else "Unhealthy"
        text += f"{status_emoji} Status: {status_text}\n"
        
        # Size and table info
        text += f"Database Size: {health.size_mb:.1f} MB\n"
        text += f"Table Count: {health.table_count}\n"
        text += f"Total Records: {health.total_records}\n"
        
        # Connection pool status
        pool_status = "Healthy" if health.connection_pool_status == "healthy" else "Unhealthy"
        text += f"Connection Pool: {pool_status}\n\n"
        
        # Table statistics
        if health.tables:
            text += f"Table Statistics:\n"
            for table_name, stats in list(health.tables.items())[:8]:  # Show top 8 tables
                row_count = stats.get('row_count', 0)
                table_size_mb = stats.get('size_mb', 0)
                text += f"• {table_name}: {row_count:,} rows, {table_size_mb:.1f} MB\n"
        
        # Last backup info
        if health.last_backup:
            text += f"\nLast Backup: {health.last_backup}"
        
        return text