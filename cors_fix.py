# CORS middleware for all responses with performance optimizations
from functools import wraps, lru_cache
import time
import threading
from typing import Dict, Any, Optional

# High-performance dependency cache with LRU eviction
@lru_cache(maxsize=1024)
def _get_cached_cors_headers(origin: str = "*") -> Dict[str, str]:
    """Cached CORS headers generation for hot path optimization"""
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "86400"  # 24 hours cache
    }

class DependencyCache:
    """Thread-safe dependency caching with performance monitoring"""
    
    def __init__(self, max_size: int = 512):
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str, factory_func=None) -> Optional[Any]:
        """Get cached value with O(1) lookup performance"""
        with self._lock:
            if key in self._cache:
                self._hits += 1
                self._access_times[key] = time.time()
                return self._cache[key]
            
            self._misses += 1
            if factory_func:
                value = factory_func()
                self._set(key, value)
                return value
            return None
    
    def _set(self, key: str, value: Any) -> None:
        """Internal set with LRU eviction"""
        if len(self._cache) >= self._max_size:
            # Evict least recently used
            lru_key = min(self._access_times.keys(), key=self._access_times.get)
            del self._cache[lru_key]
            del self._access_times[lru_key]
        
        self._cache[key] = value
        self._access_times[key] = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Performance statistics for monitoring"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": len(self._cache)
        }

# Global cache instance for dependency management
_dependency_cache = DependencyCache()

def cors_middleware(f):
    """Optimized CORS middleware with caching for hot path performance"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Use cached headers for maximum performance
        cached_headers = _get_cached_cors_headers()
        for header, value in cached_headers.items():
            response.headers[header] = value
        
        return response
    return wrapper

def benchmark_cors_middleware(iterations: int = 10000) -> Dict[str, float]:
    """Benchmark CORS middleware performance"""
    import time
    
    class MockResponse:
        def __init__(self):
            self.headers = {}
    
    @cors_middleware
    def mock_handler():
        return MockResponse()
    
    # Warm up cache
    for _ in range(100):
        mock_handler()
    
    # Benchmark
    start_time = time.perf_counter()
    for _ in range(iterations):
        mock_handler()
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_time_ms = (total_time / iterations) * 1000
    
    return {
        "total_time_seconds": round(total_time, 4),
        "average_time_ms": round(avg_time_ms, 6),
        "requests_per_second": round(iterations / total_time, 2),
        "cache_stats": _dependency_cache.get_stats()
    }

# Dependency caching utilities
def cache_dependency(key: str, factory_func):
    """Cache expensive dependency computations"""
    return _dependency_cache.get(key, factory_func)

def get_cache_stats() -> Dict[str, Any]:
    """Get dependency cache performance statistics"""
    return _dependency_cache.get_stats()
