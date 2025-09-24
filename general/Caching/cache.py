"""
Secure caching layer for the Ziphus Bot.
Provides in-memory caching with TTL support and security features.
"""

import time
import asyncio
import hashlib
import json
from typing import Any, Optional, Dict, Set, List
from threading import Lock
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from general.Logging.logger_manager import get_logger

# Initialize logger
logger = get_logger(__name__)

# TODO: Fix import path for ErrorHandler
# from common.base import ErrorHandler

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: float
    ttl: int
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    is_sensitive: bool = False
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() > (self.created_at + self.ttl)
    
    def touch(self):
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


class SecureCache:
    """
    Thread-safe in-memory cache with TTL, security features, and statistics.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize secure cache.
        
        Args:
            max_size: Maximum number of entries in cache
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sensitive_keys': 0
        }
        self._sensitive_prefixes: Set[str] = {
            'user_session:', 'auth_token:', 'password:', 'api_key:', 'secret:'
        }
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task."""
        try:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(self._periodic_cleanup())
        except RuntimeError:
            # No event loop running, cleanup will be manual
            pass
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired entries."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                self.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Using our own logger instead of ErrorHandler
                logger.error(f"Cache cleanup error: {e}", extra={'context': 'cache_cleanup'})
    
    def _generate_key(self, key: str) -> str:
        """Generate secure cache key with hash if necessary."""
        # Check if key contains sensitive data
        if any(prefix in key.lower() for prefix in self._sensitive_prefixes):
            # Hash sensitive keys for security
            return hashlib.sha256(key.encode()).hexdigest()[:16]
        return key
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if key contains sensitive data."""
        return any(prefix in key.lower() for prefix in self._sensitive_prefixes)
    
    def _evict_lru(self):
        """Evict least recently used entries when cache is full."""
        if len(self._cache) < self.max_size:
            return
        
        # Find LRU entry
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].last_accessed)
        
        # Remove sensitive data securely
        if self._cache[lru_key].is_sensitive:
            self._cache[lru_key].value = None
        
        del self._cache[lru_key]
        self._stats['evictions'] += 1
        logger.debug(f"Cache evicted LRU entry: {lru_key[:16]}...")
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None, 
        is_sensitive: Optional[bool] = None
    ) -> bool:
        """
        Set cache entry with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            is_sensitive: Mark as sensitive data (auto-detected if None)
        
        Returns:
            True if set successfully
        """
        try:
            with self._lock:
                cache_key = self._generate_key(key)
                ttl = ttl or self.default_ttl
                
                if is_sensitive is None:
                    is_sensitive = self._is_sensitive_key(key)
                
                # Evict if cache is full
                if len(self._cache) >= self.max_size:
                    self._evict_lru()
                
                # Create cache entry
                entry = CacheEntry(
                    value=value,
                    created_at=time.time(),
                    ttl=ttl,
                    is_sensitive=is_sensitive
                )
                
                self._cache[cache_key] = entry
                
                if is_sensitive:
                    self._stats['sensitive_keys'] += 1
                
                logger.debug(f"Cache set: {key[:32]}... (TTL: {ttl}s, Sensitive: {is_sensitive})")
                return True
                
        except Exception as e:
            logger.error(f"Cache set error: {e}", extra={'context': 'cache_set', 'key': key[:32]})
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cache entry if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        try:
            with self._lock:
                cache_key = self._generate_key(key)
                
                if cache_key not in self._cache:
                    self._stats['misses'] += 1
                    return None
                
                entry = self._cache[cache_key]
                
                if entry.is_expired():
                    # Clean up expired entry
                    if entry.is_sensitive:
                        entry.value = None
                    del self._cache[cache_key]
                    self._stats['misses'] += 1
                    return None
                
                # Update access info
                entry.touch()
                self._stats['hits'] += 1
                
                logger.debug(f"Cache hit: {key[:32]}... (Age: {time.time() - entry.created_at:.1f}s)")
                return entry.value
                
        except Exception as e:
            logger.error(f"Cache get error: {e}", extra={'context': 'cache_get', 'key': key[:32]})
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._lock:
                cache_key = self._generate_key(key)
                
                if cache_key not in self._cache:
                    return False
                
                entry = self._cache[cache_key]
                
                # Secure deletion for sensitive data
                if entry.is_sensitive:
                    entry.value = None
                
                del self._cache[cache_key]
                logger.debug(f"Cache deleted: {key[:32]}...")
                return True
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}", extra={'context': 'cache_delete', 'key': key[:32]})
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        try:
            with self._lock:
                cache_key = self._generate_key(key)
                
                if cache_key not in self._cache:
                    return False
                
                entry = self._cache[cache_key]
                
                if entry.is_expired():
                    # Clean up expired entry
                    if entry.is_sensitive:
                        entry.value = None
                    del self._cache[cache_key]
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Cache exists error: {e}", extra={'context': 'cache_exists', 'key': key[:32]})
            return False
    
    def clear(self, pattern: Optional[str] = None):
        """
        Clear cache entries, optionally by pattern.
        
        Args:
            pattern: Optional pattern to match keys (simple string contains)
        """
        try:
            with self._lock:
                if pattern is None:
                    # Clear all entries securely
                    for entry in self._cache.values():
                        if entry.is_sensitive:
                            entry.value = None
                    
                    self._cache.clear()
                    logger.info("Cache cleared completely")
                else:
                    # Clear entries matching pattern
                    to_delete = []
                    for cache_key in self._cache.keys():
                        if pattern in cache_key:
                            to_delete.append(cache_key)
                    
                    for cache_key in to_delete:
                        entry = self._cache[cache_key]
                        if entry.is_sensitive:
                            entry.value = None
                        del self._cache[cache_key]
                    
                    logger.info(f"Cache cleared {len(to_delete)} entries matching pattern: {pattern}")
                
        except Exception as e:
            logger.error(f"Cache clear error: {e}", extra={'context': 'cache_clear', 'pattern': pattern})
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired entries.
        
        Returns:
            Number of entries cleaned up
        """
        try:
            with self._lock:
                expired_keys = []
                current_time = time.time()
                
                for cache_key, entry in self._cache.items():
                    if current_time > (entry.created_at + entry.ttl):
                        expired_keys.append(cache_key)
                
                # Remove expired entries
                for cache_key in expired_keys:
                    entry = self._cache[cache_key]
                    if entry.is_sensitive:
                        entry.value = None
                    del self._cache[cache_key]
                
                if expired_keys:
                    logger.info(f"Cache cleanup removed {len(expired_keys)} expired entries")
                
                return len(expired_keys)
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}", extra={'context': 'cache_cleanup'})
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            current_time = time.time()
            entry_ages = [current_time - entry.created_at for entry in self._cache.values()]
            avg_age = sum(entry_ages) / len(entry_ages) if entry_ages else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': f"{hit_rate:.2f}%",
                'evictions': self._stats['evictions'],
                'sensitive_keys': self._stats['sensitive_keys'],
                'average_age_seconds': f"{avg_age:.2f}",
                'memory_usage_estimate': len(self._cache) * 1024  # Rough estimate
            }
    
    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get list of cache keys, optionally filtered by pattern.
        
        Args:
            pattern: Optional pattern to filter keys
            
        Returns:
            List of cache keys (sensitive keys are masked)
        """
        try:
            with self._lock:
                keys = []
                for cache_key, entry in self._cache.items():
                    if pattern is None or pattern in cache_key:
                        # Mask sensitive keys
                        if entry.is_sensitive:
                            keys.append(f"<sensitive:{cache_key[:8]}...>")
                        else:
                            keys.append(cache_key)
                
                return keys
                
        except Exception as e:
            logger.error(f"Cache get keys error: {e}", extra={'context': 'cache_get_keys', 'pattern': pattern})
            return []
    
    def stop(self):
        """Stop background tasks and clean up."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        
        # Secure cleanup of sensitive data
        with self._lock:
            for entry in self._cache.values():
                if entry.is_sensitive:
                    entry.value = None
            self._cache.clear()
        
        logger.info("SecureCache stopped and cleaned up")


# Global cache instances
user_cache = SecureCache(max_size=2000, default_ttl=1800)  # 30 minutes
session_cache = SecureCache(max_size=500, default_ttl=3600)  # 1 hour
analytics_cache = SecureCache(max_size=100, default_ttl=7200)  # 2 hours


def get_user_cache() -> SecureCache:
    """Get user data cache instance."""
    return user_cache


def get_session_cache() -> SecureCache:
    """Get session cache instance."""
    return session_cache


def get_analytics_cache() -> SecureCache:
    """Get analytics cache instance."""
    return analytics_cache