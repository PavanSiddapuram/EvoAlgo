"""
Least Frequently Used (LFU) Baseline Cache.
"""

from collections import defaultdict, OrderedDict
from typing import Optional
from problems.cache_replacement.problem import BaseCache


class LFUCache(BaseCache):
    """Least Frequently Used eviction policy with O(1) operations."""

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.key_to_freq: dict[int, int] = {}
        self.freq_to_keys: defaultdict[int, OrderedDict[int, bool]] = defaultdict(OrderedDict)
        self.min_freq: int = 0

    def _increment_freq(self, key: int) -> None:
        freq = self.key_to_freq[key]
        self.key_to_freq[key] = freq + 1

        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq] and self.min_freq == freq:
            self.min_freq += 1

        self.freq_to_keys[freq + 1][key] = True

    def get(self, key: int) -> bool:
        if key not in self.key_to_freq:
            return False
        self._increment_freq(key)
        return True

    def put(self, key: int) -> Optional[int]:
        if key in self.key_to_freq:
            self._increment_freq(key)
            return None

        evicted = None
        if len(self.key_to_freq) >= self.capacity:
            evicted, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_freq[evicted]

        self.key_to_freq[key] = 1
        self.freq_to_keys[1][key] = True
        self.min_freq = 1
        return evicted


LFU_SOURCE = '''from collections import defaultdict, OrderedDict

class LFUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.key_to_freq = {}
        self.freq_to_keys = defaultdict(OrderedDict)
        self.min_freq = 0

    def _increment(self, key: int):
        freq = self.key_to_freq[key]
        self.key_to_freq[key] = freq + 1
        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq] and self.min_freq == freq:
            self.min_freq += 1
        self.freq_to_keys[freq + 1][key] = True

    def get(self, key: int) -> bool:
        if key not in self.key_to_freq:
            return False
        self._increment(key)
        return True

    def put(self, key: int) -> int | None:
        if key in self.key_to_freq:
            self._increment(key)
            return None
        evicted = None
        if len(self.key_to_freq) >= self.capacity:
            evicted, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_freq[evicted]
        self.key_to_freq[key] = 1
        self.freq_to_keys[1][key] = True
        self.min_freq = 1
        return evicted
'''
