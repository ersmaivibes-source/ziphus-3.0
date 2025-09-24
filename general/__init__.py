"""
general Module - Basic and General Tasks Consolidation
===================================================

This module consolidates all basic and general task-related code from across the entire
Telegram bot into a single, organized structure. Following the ULTIMATE_ARCHITECTURE_DESIGN
pattern used for Users, Admin, Security, and libhydrogram consolidation.

Components:
-----------
- Common/: Shared utilities and helper functions
- Validation/: Input validation and sanitization 
- Configuration/: Enhanced configuration management
- Logging/: Centralized logging functionality
- Base/: Abstract classes and interfaces
- Decorators/: Common decorators and middleware
- Error/: Centralized error handling
- Database/: general database management (existing)
- Framework/: general framework components (existing)

Consolidated from:
-----------------
- common/base.py
- common/decorators.py  
- Tools/Validators/validation.py
- Tools/Helpers/helpers.py
- Security/Validation/input_validation.py
- Security/Authorization/decorators.py
- Security/Logging/secure_logging.py
- Logs/Security/secure_logging.py
- config.py (enhanced configuration)
- logger_setup.py
- libhydrogram/Utils/ (utilities)
- Errors/general/error_manager.py

Usage:
------
from general.Common import CommonUtils
from general.Validation import InputValidator
from general.Configuration import get_core_config
from general.Logging import get_logger
from general.Base import BaseService
from general.Decorators import admin_required
from general.Error import get_error_manager

Version: 9.9.9.0
Framework: general Consolidation
"""

__version__ = "9.9.9.0"
__author__ = "Ziphus Bot Team"
__framework__ = "general Consolidation"

# general components exports
from .Common import CommonUtils, HelperFunctions
from .Validation import InputValidator
from .Configuration import get_core_config, CoreConfigManager
from .Logging import get_logger, log_user_action, log_error_with_context
from .Base import BaseService, BaseManager, SafeHandlerUtils, SecurityUtils, MessageUtils
from .Decorators import admin_required, check_user_banned, error_handler, rate_limit
from .Error import get_error_manager, handle_error, handle_critical_error

# Database (existing)
from .Database.MySQL.db_manager import DatabaseManager

__all__ = [
    # Common utilities
    'CommonUtils',
    'HelperFunctions',
    
    # Validation
    'InputValidator',
    
    # Configuration
    'get_core_config',
    'CoreConfigManager',
    
    # Logging
    'get_logger',
    'log_user_action', 
    'log_error_with_context',
    
    # Base classes
    'BaseService',
    'BaseManager',
    'SafeHandlerUtils',
    'SecurityUtils',
    'MessageUtils',
    
    # Decorators
    'admin_required',
    'check_user_banned',
    'error_handler',
    'rate_limit',
    
    # Error handling
    'get_error_manager',
    'handle_error',
    'handle_critical_error',
    
    # Database (existing)
    'DatabaseManager'
]