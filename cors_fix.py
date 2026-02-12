# CORS middleware for all responses with enhanced error handling and logging
import logging
import time
import threading
from functools import wraps
from typing import Dict, Any, Optional, Callable
from collections import OrderedDict
import weakref

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cors_middleware(f: Callable) -> Callable:
    """Enhanced CORS middleware with error handling and logging"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            response = f(*args, **kwargs)
            # Enhanced CORS headers for production use
            response.headers.update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Access-Control-Max-Age": "86400"
            })
            logger.debug(f"CORS headers applied to {f.__name__}")
            return response
        except Exception as e:
            logger.error(f"Error in CORS middleware for {f.__name__}: {str(e)}")
            raise
    return wrapper

class CacheMetrics:
    """Cache performance metrics tracking"""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.errors = 0
        self._lock = threading.Lock()
    
    def record_hit(self):
        with self._lock:
            self.hits += 1
    
    def record_miss(self):
        with self._lock:
            self.misses += 1
    
    def record_eviction(self):
        with self._lock:
            self.evictions += 1
    
    def record_error(self):
        with self._lock:
            self.errors += 1
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

class ThreadSafeCacheManager:
    """Production-ready thread-safe cache with comprehensive error handling"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000, 
                 cleanup_interval: int = 60):
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.metrics = CacheMetrics()
        self._cleanup_timer: Optional[threading.Timer] = None
        self._start_cleanup_timer()
        
        # Weak reference cleanup for proper resource management
        self._finalizer = weakref.finalize(self, self._cleanup_resources)
    
    def get(self, key: str) -> Optional[Any]:
        """Thread-safe cache retrieval with metrics"""
        try:
            with self._lock:
                if key not in self._cache:
                    self.metrics.record_miss()
                    logger.debug(f"Cache miss for key: {key}")
                    return None
                
                entry = self._cache[key]
                current_time = time.time()
                
                if current_time > entry['expires_at']:
                    del self._cache[key]
                    self.metrics.record_miss()
                    logger.debug(f"Cache expired for key: {key}")
                    return None
                
                # Move to end for LRU ordering
                self._cache.move_to_end(key)
                self.metrics.record_hit()
                logger.debug(f"Cache hit for key: {key}")
                return entry['value']
                
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Error retrieving cache key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Thread-safe cache storage with size management"""
        try:
            with self._lock:
                # Evict if at capacity
                while len(self._cache) >= self.max_size:
                    self._evict_lru()
                
                expires_at = time.time() + (ttl or self.default_ttl)
                self._cache[key] = {
                    'value': value,
                    'expires_at': expires_at,
                    'created_at': time.time(),
                    'access_count': 0
                }
                
                logger.debug(f"Cached key: {key}, TTL: {ttl or self.default_ttl}s")
                return True
                
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Error setting cache key {key}: {str(e)}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """Remove specific cache entry"""
        try:
            with self._lock:
                removed = self._cache.pop(key, None) is not None
                if removed:
                    logger.debug(f"Invalidated cache key: {key}")
                return removed
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Error invalidating cache key {key}: {str(e)}")
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        try:
            with self._lock:
                count = len(self._cache)
                self._cache.clear()
                logger.info(f"Cleared {count} cache entries")
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Error clearing cache: {str(e)}")
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self._cache:
            key, _ = self._cache.popitem(last=False)
            self.metrics.record_eviction()
            logger.debug(f"Evicted LRU cache key: {key}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        try:
            with self._lock:
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self._cache.items()
                    if current_time > entry['expires_at']
                ]
                
                for key in expired_keys:
                    del self._cache[key]
                    self.metrics.record_eviction()
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Error during cache cleanup: {str(e)}")
        finally:
            self._start_cleanup_timer()
    
    def _start_cleanup_timer(self) -> None:
        """Start periodic cleanup timer"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        
        self._cleanup_timer = threading.Timer(
            self.cleanup_interval, self._cleanup_expired
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _cleanup_resources(self) -> None:
        """Cleanup resources on destruction"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': self.metrics.get_hit_rate(),
                'hits': self.metrics.hits,
                'misses': self.metrics.misses,
                'evictions': self.metrics.evictions,
                'errors': self.metrics.errors,
                'default_ttl': self.default_ttl
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        try:
            test_key = f"__health_check_{time.time()}"
            test_value = "health_check_value"
            
            # Test set/get operations
            set_success = self.set(test_key, test_value, ttl=1)
            get_result = self.get(test_key)
            cleanup_success = self.invalidate(test_key)
            
            stats = self.get_stats()
            
            return {
                'status': 'healthy' if set_success and get_result == test_value else 'degraded',
                'operations_working': set_success and get_result == test_value and cleanup_success,
                'stats': stats,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }

# Global cache instance with production settings
cache = ThreadSafeCacheManager(
    default_ttl=300,  # 5 minutes
    max_size=10000,   # Increased for production
    cleanup_interval=120  # 2 minutes
)

# Cache decorator for easy function caching
def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                return result
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator

# Export health check endpoint helper
def get_cache_health() -> Dict[str, Any]:
    """Get cache health status for monitoring"""
    return cache.health_check()