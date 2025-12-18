import time
import json
from typing import Any, Optional

class CacheService:
    """
    Simple in-memory cache fallback for development when Redis is not available.
    Supports: set, get, is_rate_limited, reset
    """
    def __init__(self):
        # Storage for cached values: key → (value, expiry_timestamp)
        self.cache = {}
        # Storage for rate limiting: key → (count, expiry_timestamp)
        self.rate_limits = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if exists and not expired"""
        entry = self.cache.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.time() > expiry:
            del self.cache[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value with TTL in seconds"""
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)

    def is_rate_limited(self, key: str, limit: int = 10, window: int = 60) -> bool:
        """Simple rate limiting"""
        now = time.time()
        entry = self.rate_limits.get(key)

        if entry is None:
            self.rate_limits[key] = (1, now + window)
            return False

        count, expiry = entry
        if now > expiry:
            self.rate_limits[key] = (1, now + window)
            return False

        if count >= limit:
            return True

        self.rate_limits[key] = (count + 1, expiry)
        return False

    def reset(self, key: str):
        """Reset rate limit for key"""
        self.rate_limits.pop(key, None)