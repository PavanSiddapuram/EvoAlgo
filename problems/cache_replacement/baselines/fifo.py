"""
First-In, First-Out (FIFO) Baseline Cache.
"""

from collections import deque
from typing import Optional
from problems.cache_replacement.problem import BaseCache


class FIFOCache(BaseCache):
    """Simple FIFO eviction policy."""

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.queue: deque[int] = deque()
        self.lookup: set[int] = set()

    def get(self, key: int) -> bool:
        return key in self.lookup

    def put(self, key: int) -> Optional[int]:
        if key in self.lookup:
            return None

        evicted = None
        if len(self.lookup) >= self.capacity:
            evicted = self.queue.popleft()
            self.lookup.remove(evicted)

        self.queue.append(key)
        self.lookup.add(key)
        return evicted


FIFO_SOURCE = '''class FIFOCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.queue = []
        self.lookup = set()

    def get(self, key: int) -> bool:
        return key in self.lookup

    def put(self, key: int) -> int | None:
        if key in self.lookup:
            return None
        evicted = None
        if len(self.lookup) >= self.capacity:
            evicted = self.queue.pop(0)
            self.lookup.remove(evicted)
        self.queue.append(key)
        self.lookup.add(key)
        return evicted
'''
