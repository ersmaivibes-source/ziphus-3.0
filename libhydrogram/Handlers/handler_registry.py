"""
Centralized Handler Registration System
======================================

Consolidates all Hydrogram handler registration logic from across the codebase.
Moved from main.py and various handler modules.
"""

from hydrogram import Client
from typing import Dict, List, Callable, Any
from general.Logging.logger_manager import get_logger, log_error_with_context

# Initialize logger
logger = get_logger(__name__)

class HandlerRegistry:
    """Centralized registry for all Hydrogram handlers."""
    
    def __init__(self, client: Client):
        """Initialize handler registry."""
        self.client = client
        self._registered_modules: List[str] = []
        self._handler_count = 0
        
    def register_all_handlers(self):
        """Register all handlers from all modules."""
        try:
            logger.info("Starting comprehensive handler registration...")
            
            # Register Admin handlers
            self._register_admin_handlers()
            
            # Register User-facing handlers  
            self._register_user_handlers()
            
            # Register System handlers
            self._register_system_handlers()
            
            # Register Central dispatcher
            self._register_dispatcher()
            
            logger.info(f"Handler registration complete. Total handlers: {self._handler_count}")
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'register_all_handlers'})
    
    def _register_admin_handlers(self):
        """Register all admin-related handlers."""
        logger.info("Registering admin handlers...")
        
        try:
            # Admin Reports
            from Admin.Reports import admin_analytics
            admin_analytics.register_handlers(self.client)
            self._registered_modules.append('admin_analytics')
            
            # Admin System Settings
            from Admin.System_Settings import admin_system_health
            admin_system_health.register_handlers(self.client)
            self._registered_modules.append('admin_system_health')
            
            # Admin User Management
            from Admin.User_Management import admin_tickets, admin_user_management
            admin_tickets.register_handlers(self.client)
            admin_user_management.register_handlers(self.client)
            self._registered_modules.extend(['admin_tickets', 'admin_user_management'])
            
            # Create and attach admin menu tracker
            # Check if client has redis attribute (attached by bot_client)
            if hasattr(self.client, 'redis'):
                from Admin.Dashboard.admin_menu_tracker import create_admin_menu_tracker
                # Dynamically add menu_tracker attribute to client
                self.client.menu_tracker = create_admin_menu_tracker(self.client.redis, self.client)  # type: ignore
            else:
                logger.warning("Client does not have redis attribute, skipping menu tracker creation")
            
            logger.info("Admin handlers registered successfully")
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'register_admin_handlers'})
    
    def _register_user_handlers(self):
        """Register all user-facing handlers."""
        logger.info("Registering user-facing handlers...")
        
        try:
            # Message handlers
            # Navigation and onboarding handlers are registered via decorators
            from Users.Support import ticket_handlers
            ticket_handlers.register_handlers(self.client)
            
            # Callback handlers
            from Users.Subscriptions import subscription_handlers
            subscription_handlers.register_handlers(self.client)
            
            self._registered_modules.extend([
                'ticket_handlers', 'subscription_handlers'
            ])
            
            logger.info("User-facing handlers registered successfully")
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'register_user_handlers'})
    
    def _register_system_handlers(self):
        """Register system-level handlers."""
        logger.info("Registering system handlers...")
        
        try:
            # System handlers registration (chat member handler removed)
            logger.info("System handlers registered successfully")
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'register_system_handlers'})
    
    def _register_dispatcher(self):
        """Register the central message dispatcher."""
        logger.info("Registering central dispatcher...")
        
        try:
            # Register central dispatcher LAST to handle text messages based on user state
            from general.Handlers import dispatcher
            dispatcher.register_dispatcher(self.client)
            
            self._registered_modules.append('dispatcher')
            
            logger.info("Central dispatcher registered successfully")
            
        except Exception as e:
            log_error_with_context(e, {'operation': 'register_dispatcher'})
    
    def get_registration_summary(self) -> Dict[str, Any]:
        """Get registration summary."""
        return {
            'total_modules': len(self._registered_modules),
            'registered_modules': self._registered_modules,
            'total_handlers': self._handler_count,
            'registration_complete': len(self._registered_modules) > 0
        }
    
    def validate_registration(self) -> bool:
        """Validate that all required handlers are registered."""
        required_modules = [
            'admin_analytics', 'admin_system_health', 'admin_tickets', 
            'admin_user_management', 'ticket_handlers', 'subscription_handlers', 'dispatcher'
        ]
        
        missing_modules = [module for module in required_modules if module not in self._registered_modules]
        
        if missing_modules:
            logger.warning(f"Missing handler modules: {missing_modules}")
            return False
        
        logger.info("All required handler modules registered successfully")
        return True