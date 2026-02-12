# CORS middleware for all responses
from functools import wraps
import time
from typing import Dict, Any, Optional

def cors_middleware(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    return wrapper

# Improved dependency caching mechanism
class CacheManager:
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry['expires_at']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        expires_at = time.time() + (ttl or self.default_ttl)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
    
    def invalidate(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None
    
    def clear(self) -> None:
        self._cache.clear()
    
    def _evict_oldest(self) -> None:
        if not self._cache:
            return
        oldest_key = min(self._cache.keys(), 
                        key=lambda k: self._cache[k]['created_at'])
        del self._cache[oldest_key]

# Global cache instance
cache = CacheManager()