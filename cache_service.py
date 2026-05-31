import json
import os
import time
import redis
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class CacheService:
    """Production-ready cache service with Redis fallback to in-memory"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        
        # Try to connect to Redis
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # Test connection
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis unavailable, using memory cache: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
            else:
                # In-memory fallback with TTL check
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    if time.time() < entry["expires_at"]:
                        return entry["value"]
                    else:
                        del self.memory_cache[key]
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value, default=str))
                return True
            else:
                # In-memory with real TTL
                self.memory_cache[key] = {
                    "value": value,
                    "expires_at": time.time() + ttl
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
                return True
            else:
                self.memory_cache.clear()
                return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False