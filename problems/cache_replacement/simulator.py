"""
High-throughput Cache Trace Simulator and Tier 2 Invariant Verifier.
"""

import time
from typing import Any, List, Optional, Tuple, Type
from problems.base import WorkloadMetric


class CacheInvariantChecker:
    """
    Tier 2 Verification: Executes strict behavioral invariant checks
    on candidate cache implementations before expensive simulation.
    """

    @staticmethod
    def verify(cache_cls: Type[Any]) -> Tuple[bool, str]:
        """
        Runs comprehensive behavioral tests. Returns (passed, failure_reason).
        """
        try:
            # 1. Negative or zero capacity check
            try:
                cache_cls(0)
                return False, "Failed invariant: Cache did not raise ValueError for capacity=0"
            except (ValueError, AssertionError):
                pass
            except Exception as e:
                return False, f"Unexpected exception on capacity=0: {type(e).__name__}: {e}"

            # 2. Capacity = 1 Edge Case
            c1 = cache_cls(1)
            hit = c1.get(10)
            if hit:
                return False, "Failed invariant: Empty cache returned hit for key=10"
            evicted = c1.put(10)
            if evicted is not None:
                return False, "Failed invariant: First put in empty cache returned an eviction"
            hit = c1.get(10)
            if not hit:
                return False, "Failed invariant: Key=10 not hit immediately after put"
            evicted = c1.put(20)
            if evicted != 10:
                return False, f"Failed invariant: In capacity=1, expected eviction of 10, got {evicted}"
            if not c1.get(20):
                return False, "Failed invariant: Key=20 not present after eviction of 10"
            if c1.get(10):
                return False, "Failed invariant: Evicted key=10 still present in cache"

            # 3. Capacity > 1 Invariants and Idempotence
            cap = 3
            c = cache_cls(cap)
            keys = [1, 2, 3]
            for k in keys:
                ev = c.put(k)
                if ev is not None:
                    return False, f"Premature eviction {ev} when cache was not yet full"

            # Check that all 3 keys are present
            for k in keys:
                if not c.get(k):
                    return False, f"Key {k} was inserted into capacity=3 cache but get returned False"

            # Duplicate put (should update state without evicting)
            ev = c.put(2)
            if ev is not None:
                return False, f"Duplicate put(2) caused an unexpected eviction of {ev}"
            if not c.get(2):
                return False, "Key 2 missing after duplicate put(2)"

            # Eviction validity test: next distinct key must evict one of the existing keys {1, 2, 3}
            ev = c.put(4)
            if ev not in {1, 2, 3}:
                return False, f"Evicted key {ev} was not among stored keys {1, 2, 3}"
            if not c.get(4):
                return False, "Newly inserted key 4 missing from cache"
            if c.get(ev):
                return False, f"Evicted key {ev} still reported as hit in cache"

            # 4. Stress invariant test (random access, strictly enforcing capacity bound)
            c_stress = cache_cls(5)
            active_keys = set()
            for key in [10, 20, 30, 10, 40, 50, 60, 20, 70, 80, 50, 90]:
                if key in active_keys:
                    c_stress.get(key)
                    c_stress.put(key)
                else:
                    ev = c_stress.put(key)
                    if len(active_keys) >= 5:
                        if ev is None or ev not in active_keys:
                            return False, f"Invalid eviction {ev} during stress test"
                        active_keys.remove(ev)
                    active_keys.add(key)

                if len(active_keys) > 5:
                    return False, f"Active keys exceeded capacity 5: size={len(active_keys)}"

            return True, "All invariant checks passed."

        except Exception as exc:
            return False, f"Exception during invariant verification: {type(exc).__name__}: {str(exc)}"


class CacheSimulator:
    """High-speed trace simulator for evaluating cache replacement policies."""

    @staticmethod
    def warmup(cache_cls: Type[Any], capacity: int = 20) -> None:
        """Executes a short dummy run to ensure bytecode compilation and cache warmup."""
        c = cache_cls(capacity)
        for i in range(200):
            if not c.get(i % 50):
                c.put(i % 50)

    @classmethod
    def run_workload(
        cls,
        cache_cls: Type[Any],
        capacity: int,
        workload_name: str,
        trace: List[int],
    ) -> WorkloadMetric:
        """Simulates a workload trace on a fresh instance of cache_cls(capacity)."""
        cache = cache_cls(capacity)
        hits = 0
        misses = 0
        evictions = 0

        # Execute simulation and time it with high resolution
        start_ns = time.perf_counter_ns()
        for key in trace:
            if cache.get(key):
                hits += 1
            else:
                misses += 1
                evicted = cache.put(key)
                if evicted is not None:
                    evictions += 1

        elapsed_ns = time.perf_counter_ns() - start_ns
        elapsed_ms = elapsed_ns / 1_000_000.0
        total_requests = hits + misses
        hit_ratio = hits / total_requests if total_requests > 0 else 0.0
        avg_latency_us = (elapsed_ns / total_requests) / 1000.0 if total_requests > 0 else 0.0

        return WorkloadMetric(
            workload_name=workload_name,
            total_requests=total_requests,
            hits=hits,
            misses=misses,
            hit_ratio=round(hit_ratio, 4),
            evictions=evictions,
            elapsed_time_ms=round(elapsed_ms, 3),
            avg_latency_us=round(avg_latency_us, 3),
        )
