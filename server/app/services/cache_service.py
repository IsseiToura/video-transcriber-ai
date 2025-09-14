"""
Memcached cache service for video information caching.
"""

import logging
from typing import Optional, Dict, Any
from pymemcache.client.base import Client
from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()

class CacheService:
    """Memcached cache service for video data."""
    
    def __init__(self):
        """Initialize cache service with Memcached client."""
        self.client = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Memcached server."""
        try:
            if not settings.ELASTICACHE_MEMCACHED_ENDPOINT:
                logger.warning("ElastiCache endpoint not configured, cache disabled")
                return
            
            # Use the endpoint directly as a string (same as working example)
            endpoint = settings.ELASTICACHE_MEMCACHED_ENDPOINT
            
            # Create Memcached client with timeout settings
            self.client = Client(
                endpoint,
                timeout=5,  # 5 second timeout
                connect_timeout=5  # 5 second connection timeout
            )
            logger.info(f"Connected to Memcached at {endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Memcached: {e}")
            logger.warning("Cache will be disabled. Application will continue without caching.")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if cache is available."""
        return self.client is not None
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/error
        """
        if not self.is_available():
            return None
        
        try:
            data = self.client.get(key)
            if data:
                logger.warning(f"Cache hit for key: {key}")
                return data
            else:
                logger.warning(f"Cache miss for key: {key}")
                return None
        except Exception as e:
            logger.error(f"Error getting from cache for key {key}: {e}")
            # If connection fails, disable cache for this session
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                logger.warning("Cache connection failed, disabling cache for this session")
                self.client = None
            return None
    
    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            ttl = ttl or settings.ELASTICACHE_MEMCACHED_TTL
            # Store data directly (Memcached will handle serialization)
            result = self.client.set(key, data, expire=ttl)
            if result:
                logger.debug(f"Cached data for key: {key} (TTL: {ttl}s)")
            return result
        except Exception as e:
            logger.error(f"Error setting cache for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete data from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            result = self.client.delete(key)
            if result:
                logger.debug(f"Deleted cache key: {key}")
            return result
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def get_video_info_key(self, video_id: str, owner_username: str) -> str:
        """
        Generate cache key for video info.
        
        Args:
            video_id: Video ID
            owner_username: Owner username
            
        Returns:
            Cache key string
        """
        return f"video_info:{owner_username}:{video_id}"
    
    def invalidate_video_info(self, video_id: str, owner_username: str) -> bool:
        """
        Invalidate video info cache.
        
        Args:
            video_id: Video ID
            owner_username: Owner username
            
        Returns:
            True if successful
        """
        key = self.get_video_info_key(video_id, owner_username)
        return self.delete(key)


# Global cache service instance
cache_service = CacheService()
