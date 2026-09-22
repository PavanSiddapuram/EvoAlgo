# Baselines package
from problems.cache_replacement.baselines.fifo import FIFOCache, FIFO_SOURCE
from problems.cache_replacement.baselines.lru import LRUCache, LRU_SOURCE
from problems.cache_replacement.baselines.lfu import LFUCache, LFU_SOURCE
from problems.cache_replacement.baselines.arc import ARCCache, ARC_SOURCE

__all__ = [
    "FIFOCache", "FIFO_SOURCE",
    "LRUCache", "LRU_SOURCE",
    "LFUCache", "LFU_SOURCE",
    "ARCCache", "ARC_SOURCE",
]
