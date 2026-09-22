"""
Adaptive Replacement Cache (ARC) Baseline.
Reference: Nimrod Megiddo and Dharmendra S. Modha (FAST 2003).
Self-tuning cache algorithm balancing recency and frequency.
"""

from collections import OrderedDict
from typing import Optional
from problems.cache_replacement.problem import BaseCache


class ARCCache(BaseCache):
    """
    Adaptive Replacement Cache (ARC).
    Maintains two double-lists (T1, T2) and two ghost lists (B1, B2),
    adapting target size parameter p in response to workload phase shifts.
    """

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.p: float = 0.0  # Target size for T1
        self.t1: OrderedDict[int, bool] = OrderedDict()  # Recent entries
        self.t2: OrderedDict[int, bool] = OrderedDict()  # Frequent entries
        self.b1: OrderedDict[int, bool] = OrderedDict()  # Ghost recent entries
        self.b2: OrderedDict[int, bool] = OrderedDict()  # Ghost frequent entries

    def get(self, key: int) -> bool:
        if key in self.t1:
            # Move from T1 to T2 (promoted to frequent)
            del self.t1[key]
            self.t2[key] = True
            return True
        elif key in self.t2:
            self.t2.move_to_end(key)
            return True
        return False

    def _replace(self, key: int) -> Optional[int]:
        evicted = None
        len_t1 = len(self.t1)
        if len_t1 > 0 and ((key in self.b2 and len_t1 == int(self.p)) or (len_t1 > self.p)):
            evicted, _ = self.t1.popitem(last=False)
            self.b1[evicted] = True
            if len(self.b1) > self.capacity:
                self.b1.popitem(last=False)
        else:
            if len(self.t2) > 0:
                evicted, _ = self.t2.popitem(last=False)
                self.b2[evicted] = True
                if len(self.b2) > self.capacity:
                    self.b2.popitem(last=False)
        return evicted

    def put(self, key: int) -> Optional[int]:
        # Case 1: Key is already in T1 or T2
        if key in self.t1:
            del self.t1[key]
            self.t2[key] = True
            return None
        if key in self.t2:
            self.t2.move_to_end(key)
            return None

        # Case 2: Key is in ghost list B1
        if key in self.b1:
            delta = 1.0 if len(self.b1) >= len(self.b2) else len(self.b2) / max(1, len(self.b1))
            self.p = min(float(self.capacity), self.p + delta)
            evicted = self._replace(key)
            del self.b1[key]
            self.t2[key] = True
            return evicted

        # Case 3: Key is in ghost list B2
        if key in self.b2:
            delta = 1.0 if len(self.b2) >= len(self.b1) else len(self.b1) / max(1, len(self.b2))
            self.p = max(0.0, self.p - delta)
            evicted = self._replace(key)
            del self.b2[key]
            self.t2[key] = True
            return evicted

        # Case 4: Cache miss completely (not in T1, T2, B1, B2)
        len_l1 = len(self.t1) + len(self.b1)
        len_l2 = len(self.t2) + len(self.b2)

        if len_l1 == self.capacity:
            if len(self.t1) < self.capacity:
                if self.b1:
                    self.b1.popitem(last=False)
                evicted = self._replace(key)
            else:
                evicted, _ = self.t1.popitem(last=False)
        elif len_l1 < self.capacity and (len_l1 + len_l2 >= self.capacity):
            if len_l1 + len_l2 == 2 * self.capacity and self.b2:
                self.b2.popitem(last=False)
            evicted = self._replace(key)
        else:
            evicted = None

        self.t1[key] = True
        return evicted


ARC_SOURCE = '''from collections import OrderedDict

class ARCCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.p = 0.0
        self.t1 = OrderedDict()
        self.t2 = OrderedDict()
        self.b1 = OrderedDict()
        self.b2 = OrderedDict()

    def get(self, key: int) -> bool:
        if key in self.t1:
            del self.t1[key]
            self.t2[key] = True
            return True
        elif key in self.t2:
            self.t2.move_to_end(key)
            return True
        return False

    def _replace(self, key: int):
        evicted = None
        len_t1 = len(self.t1)
        if len_t1 > 0 and ((key in self.b2 and len_t1 == int(self.p)) or (len_t1 > self.p)):
            evicted, _ = self.t1.popitem(last=False)
            self.b1[evicted] = True
            if len(self.b1) > self.capacity:
                self.b1.popitem(last=False)
        else:
            if len(self.t2) > 0:
                evicted, _ = self.t2.popitem(last=False)
                self.b2[evicted] = True
                if len(self.b2) > self.capacity:
                    self.b2.popitem(last=False)
        return evicted

    def put(self, key: int):
        if key in self.t1:
            del self.t1[key]
            self.t2[key] = True
            return None
        if key in self.t2:
            self.t2.move_to_end(key)
            return None

        if key in self.b1:
            delta = 1.0 if len(self.b1) >= len(self.b2) else len(self.b2) / max(1, len(self.b1))
            self.p = min(float(self.capacity), self.p + delta)
            evicted = self._replace(key)
            del self.b1[key]
            self.t2[key] = True
            return evicted

        if key in self.b2:
            delta = 1.0 if len(self.b2) >= len(self.b1) else len(self.b1) / max(1, len(self.b2))
            self.p = max(0.0, self.p - delta)
            evicted = self._replace(key)
            del self.b2[key]
            self.t2[key] = True
            return evicted

        len_l1 = len(self.t1) + len(self.b1)
        len_l2 = len(self.t2) + len(self.b2)

        if len_l1 == self.capacity:
            if len(self.t1) < self.capacity:
                if self.b1:
                    self.b1.popitem(last=False)
                evicted = self._replace(key)
            else:
                evicted, _ = self.t1.popitem(last=False)
        elif len_l1 < self.capacity and (len_l1 + len_l2 >= self.capacity):
            if len_l1 + len_l2 == 2 * self.capacity and self.b2:
                self.b2.popitem(last=False)
            evicted = self._replace(key)
        else:
            evicted = None

        self.t1[key] = True
        return evicted
'''
