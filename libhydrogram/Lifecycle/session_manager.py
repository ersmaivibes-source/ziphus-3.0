"""
Session Management for Bot Operations
====================================

Advanced session management and bot state tracking.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)


class SessionManager:
    """Manages bot sessions and operational state."""
    
    def __init__(self):
        """Initialize session manager."""
        self.session_start_time: Optional[datetime] = None
        self.session_id: Optional[str] = None
        self.active_users: Set[int] = set()
        self.session_stats = {
            'messages_processed': 0,
            'callbacks_processed': 0,
            'errors_encountered': 0,
            'uptime_seconds': 0
        }
        self._last_activity: Optional[datetime] = None
    
    def start_session(self, session_id: Optional[str] = None):
        """Start a new bot session."""
        self.session_start_time = datetime.now()
        self.session_id = session_id or f"session_{int(self.session_start_time.timestamp())}"
        self.active_users.clear()
        self.session_stats = {
            'messages_processed': 0,
            'callbacks_processed': 0,
            'errors_encountered': 0,
            'uptime_seconds': 0
        }
        self._last_activity = self.session_start_time
        
        logger.info(f"Bot session started: {self.session_id}")
    
    def end_session(self):
        """End the current bot session."""
        if self.session_start_time:
            session_duration = datetime.now() - self.session_start_time
            self.session_stats['uptime_seconds'] = int(session_duration.total_seconds())
            
            logger.info(f"Bot session ended: {self.session_id}")
            logger.info(f"Session statistics: {self.session_stats}")
            
            # Reset session data
            self.session_start_time = None
            self.session_id = None
            self.active_users.clear()
    
    def record_message_processed(self, user_id: int):
        """Record a message being processed."""
        self.session_stats['messages_processed'] += 1
        self.active_users.add(user_id)
        self._last_activity = datetime.now()
    
    def record_callback_processed(self, user_id: int):
        """Record a callback being processed."""
        self.session_stats['callbacks_processed'] += 1
        self.active_users.add(user_id)
        self._last_activity = datetime.now()
    
    def record_error(self):
        """Record an error occurrence."""
        self.session_stats['errors_encountered'] += 1
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        if not self.session_start_time:
            return {'active': False}
        
        current_time = datetime.now()
        uptime = current_time - self.session_start_time
        
        return {
            'active': True,
            'session_id': self.session_id,
            'start_time': self.session_start_time.isoformat(),
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': str(uptime),
            'active_users_count': len(self.active_users),
            'active_users': list(self.active_users),
            'last_activity': self._last_activity.isoformat() if self._last_activity else None,
            'statistics': self.session_stats.copy()
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics."""
        if not self.session_start_time:
            return {}
        
        uptime_hours = (datetime.now() - self.session_start_time).total_seconds() / 3600
        
        if uptime_hours == 0:
            return {'uptime_hours': 0}
        
        return {
            'uptime_hours': uptime_hours,
            'messages_per_hour': self.session_stats['messages_processed'] / uptime_hours,
            'callbacks_per_hour': self.session_stats['callbacks_processed'] / uptime_hours,
            'errors_per_hour': self.session_stats['errors_encountered'] / uptime_hours,
            'error_rate_percent': (self.session_stats['errors_encountered'] / 
                                 max(1, self.session_stats['messages_processed'] + 
                                     self.session_stats['callbacks_processed'])) * 100
        }
    
    def is_healthy(self) -> bool:
        """Check if the session is healthy."""
        if not self.session_start_time:
            return False
        
        # Check if last activity was within acceptable time
        if self._last_activity:
            time_since_activity = datetime.now() - self._last_activity
            if time_since_activity > timedelta(hours=1):  # No activity for 1 hour
                return False
        
        # Check error rate
        metrics = self.get_performance_metrics()
        if metrics.get('error_rate_percent', 0) > 10:  # More than 10% error rate
            return False
        
        return True
    
    def cleanup_old_users(self, max_age_hours: int = 24):
        """Clean up old user records (would need user activity tracking)."""
        # This is a placeholder - real implementation would track user last seen times
        logger.info(f"Cleaned up old user records (placeholder)")
    
    async def generate_session_report(self) -> Dict[str, Any]:
        """Generate a comprehensive session report."""
        try:
            session_info = self.get_session_info()
            performance_metrics = self.get_performance_metrics()
            
            return {
                'session': session_info,
                'performance': performance_metrics,
                'health_status': self.is_healthy(),
                'report_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'generate_session_report'})
            return {'error': 'Failed to generate session report'}