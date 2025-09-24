"""
general Base Classes and Interfaces
================================

Consolidated base classes and interfaces from:
- common/base.py
- Various abstract implementations across the codebase

Moved to general for basic/general task consolidation.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass
from datetime import datetime

from general.Logging.logger_manager import get_logger, log_error_with_context

logger = get_logger(__name__)


class BaseService(ABC):
    """Abstract base class for all services."""
    
    def __init__(self, name: str):
        """Initialize base service."""
        self.name = name
        self.is_initialized = False
        self.start_time: Optional[datetime] = None
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup service resources."""
        pass
    
    async def start(self) -> bool:
        """Start the service."""
        try:
            if self.is_initialized:
                self.logger.warning(f"Service {self.name} is already initialized")
                return True
            
            success = await self.initialize()
            if success:
                self.is_initialized = True
                self.start_time = datetime.utcnow()
                self.logger.info(f"Service {self.name} started successfully")
            else:
                self.logger.error(f"Failed to start service {self.name}")
            
            return success
        except Exception as e:
            log_error_with_context(e, {'service': self.name, 'operation': 'start'})
            return False
    
    async def stop(self):
        """Stop the service."""
        try:
            if not self.is_initialized:
                self.logger.warning(f"Service {self.name} is not initialized")
                return
            
            await self.cleanup()
            self.is_initialized = False
            self.start_time = None
            self.logger.info(f"Service {self.name} stopped successfully")
        except Exception as e:
            log_error_with_context(e, {'service': self.name, 'operation': 'stop'})
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information."""
        uptime = None
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'name': self.name,
            'initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime_seconds': uptime
        }


class BaseManager(ABC):
    """Abstract base class for all managers."""
    
    def __init__(self, name: str):
        """Initialize base manager."""
        self.name = name
        self.services: Dict[str, BaseService] = {}
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def register_service(self, service: BaseService):
        """Register a service with the manager."""
        self.services[service.name] = service
        self.logger.info(f"Registered service: {service.name}")
    
    async def start_all_services(self) -> bool:
        """Start all registered services."""
        success_count = 0
        total_count = len(self.services)
        
        for service in self.services.values():
            if await service.start():
                success_count += 1
        
        if success_count == total_count:
            self.logger.info(f"All {total_count} services started successfully")
            return True
        else:
            self.logger.error(f"Only {success_count}/{total_count} services started successfully")
            return False
    
    async def stop_all_services(self):
        """Stop all registered services."""
        for service in self.services.values():
            await service.stop()
        self.logger.info("All services stopped")
    
    def get_services_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered services."""
        return {name: service.get_status() for name, service in self.services.items()}


class SafeHandlerUtils:
    """Utilities for safe handler execution."""
    
    @staticmethod
    def inject_user_and_lang(func: Callable) -> Callable:
        """Decorator to inject user data and language code."""
        async def wrapper(*args, **kwargs):
            try:
                # For now, just pass through - can implement user injection later
                return await func(*args, **kwargs)
            except Exception as e:
                log_error_with_context(e, {'decorator': 'inject_user_and_lang'})
                raise
        return wrapper


class SecurityUtils:
    """Basic security utilities."""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input."""
        if not text:
            return ""
        # Basic sanitization
        return text.strip()[:1000]  # Limit length and strip whitespace
    
    @staticmethod
    def validate_crypto_address(address: str, crypto_type: str) -> bool:
        """Validate cryptocurrency address format."""
        if not address or not isinstance(address, str):
            return False
        
        address = address.strip()
        
        # Basic validation patterns for common cryptocurrencies
        validation_patterns = {
            'btc': {
                'min_length': 26,
                'max_length': 35,
                'starts_with': ['1', '3', 'bc1']
            },
            'eth': {
                'min_length': 42,
                'max_length': 42,
                'starts_with': ['0x']
            },
            'usdt': {
                'min_length': 34,
                'max_length': 42,
                'starts_with': ['0x', '1', '3']
            }
        }
        
        crypto_type = crypto_type.lower()
        if crypto_type not in validation_patterns:
            return False
        
        pattern = validation_patterns[crypto_type]
        
        # Check length
        if not (pattern['min_length'] <= len(address) <= pattern['max_length']):
            return False
        
        # Check prefix
        if not any(address.startswith(prefix) for prefix in pattern['starts_with']):
            return False
        
        return True


class MessageUtils:
    """Message handling utilities."""
    
    @staticmethod
    async def safe_edit_message(message, text: str, reply_markup=None):
        """Safely edit a message with error handling."""
        try:
            await message.edit_text(text, reply_markup=reply_markup)
            return True
        except Exception as e:
            logger.debug(f"Failed to edit message: {e}")
            return False
    
    @staticmethod
    async def safe_send_message(chat_id, text: str, reply_markup=None):
        """Safely send a message with error handling."""
        try:
            # This would need the actual client instance
            # For now, just return False as placeholder
            return False
        except Exception as e:
            logger.debug(f"Failed to send message: {e}")
            return False
    
    @staticmethod
    def split_message(text: str, max_length: int = 4096) -> List[str]:
        """Split a long message into multiple parts."""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current_part = ""
        
        # Split by lines first to preserve formatting
        lines = text.split('\n')
        
        for line in lines:
            # If a single line is too long, split it by words
            if len(line) > max_length:
                words = line.split(' ')
                for word in words:
                    if len(current_part) + len(word) + 1 <= max_length:
                        current_part += (" " if current_part else "") + word
                    else:
                        if current_part:
                            parts.append(current_part)
                            current_part = word
                        else:
                            # Single word longer than max_length
                            parts.append(word[:max_length])
                            current_part = word[max_length:]
            else:
                if len(current_part) + len(line) + 1 <= max_length:
                    current_part += ("\n" if current_part else "") + line
                else:
                    if current_part:
                        parts.append(current_part)
                    current_part = line
        
        if current_part:
            parts.append(current_part)
        
        return parts


class ValidationMixin:
    """Mixin class providing basic validation functionality."""
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that all required fields are present and not empty."""
        for field in required_fields:
            if field not in data or not data[field]:
                logger.warning(f"Missing required field: {field}")
                return False
        return True
    
    def validate_field_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> bool:
        """Validate that fields have the correct types."""
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                logger.warning(f"Field {field} has incorrect type. Expected {expected_type}, got {type(data[field])}")
                return False
        return True


@dataclass
class OperationResult:
    """Standard result structure for operations."""
    success: bool
    message: str = ""
    data: Any = None
    error_code: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    @classmethod
    def success_result(cls, message: str = "Operation successful", data: Any = None) -> 'OperationResult':
        """Create a successful operation result."""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_result(cls, message: str = "Operation failed", error_code: str = None) -> 'OperationResult':
        """Create an error operation result."""
        return cls(success=False, message=message, error_code=error_code)


class AsyncContextManager:
    """Base async context manager."""
    
    async def __aenter__(self):
        """Enter the async context."""
        await self.setup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context."""
        await self.teardown()
    
    async def setup(self):
        """Setup the context (override in subclasses)."""
        pass
    
    async def teardown(self):
        """Teardown the context (override in subclasses)."""
        pass


class Singleton:
    """Singleton metaclass for ensuring only one instance."""
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


class ConfigurableComponent:
    """Base class for components that can be configured."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize configurable component."""
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set_config_value(self, key: str, value: Any):
        """Set a configuration value."""
        self.config[key] = value
        self.logger.debug(f"Config updated: {key} = {value}")
    
    def validate_config(self) -> bool:
        """Validate the configuration (override in subclasses)."""
        return True