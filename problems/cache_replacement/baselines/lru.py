"""
Least Recently Used (LRU) Baseline Cache.
"""

from collections import OrderedDict
from typing import Optional
from problems.cache_replacement.problem import BaseCache


class LRUCache(BaseCache):
    """Standard Least Recently Used eviction policy."""

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.cache: OrderedDict[int, bool] = OrderedDict()

    def get(self, key: int) -> bool:
        if key in self.cache:
            self.cache.move_to_end(key)
            return True
        return False

    def put(self, key: int) -> Optional[int]:
        if key in self.cache:
            self.cache.move_to_end(key)
            return None

        evicted = None
        if len(self.cache) >= self.capacity:
            evicted, _ = self.cache.popitem(last=False)

        self.cache[key] = True
        return evicted


LRU_SOURCE = '''from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> bool:
        if key in self.cache:
            self.cache.move_to_end(key)
            return True
        return False

    def put(self, key: int) -> int | None:
        if key in self.cache:
            self.cache.move_to_end(key)
            return None
        evicted = None
        if len(self.cache) >= self.capacity:
            evicted, _ = self.cache.popitem(last=False)
        self.cache[key] = True
        return evicted
'''
