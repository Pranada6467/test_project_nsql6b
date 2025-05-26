import hashlib
import logging
from typing import Dict, Optional
from config.config import FEW_SHOT_CONFIG

logger = logging.getLogger(__name__)

class QueryCache:
    def __init__(self, max_size: int = None):
        self.max_size = max_size or FEW_SHOT_CONFIG['max_cache_size']
        self.cache: Dict[str, str] = {}
        self.access_order = []  # For LRU eviction
    
    def _generate_key(self, question: str, schema: str) -> str:
        """Generate a cache key from question and schema"""
        combined = f"{question}|{schema}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, question: str, schema: str) -> Optional[str]:
        """Get cached SQL query"""
        if not FEW_SHOT_CONFIG['cache_enabled']:
            return None
        
        key = self._generate_key(question, schema)
        
        if key in self.cache:
            # Move to end for LRU
            self.access_order.remove(key)
            self.access_order.append(key)
            logger.info(f"Cache hit for question: {question[:50]}...")
            return self.cache[key]
        
        return None
    
    def set(self, question: str, schema: str, sql: str):
        """Cache a SQL query"""
        if not FEW_SHOT_CONFIG['cache_enabled']:
            return
        
        key = self._generate_key(question, schema)
        
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
            logger.info("Evicted oldest cache entry")
        
        self.cache[key] = sql
        if key not in self.access_order:
            self.access_order.append(key)
        
        logger.info(f"Cached SQL for question: {question[:50]}...")
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.access_order.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

# Global cache instance
query_cache = QueryCache()
