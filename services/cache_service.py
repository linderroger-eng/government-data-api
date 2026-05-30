import json
import os
from typing import Optional, Any

class CacheService:
    """Simple in-memory cache service (would use Redis in production)"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            return self.cache[key]["value"]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        self.cache[key] = {
            "value": value,
            "ttl": ttl  # In production, would implement actual TTL logic
        }
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        self.cache.clear()
        return True