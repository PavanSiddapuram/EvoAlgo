# 🧪 EvoAlgo: Problem Harness & Evaluation Specification

This specification defines the contract between the **EvoAlgo Core Engine** and any **Problem Domain**, focusing on the flagship domain: **Cache Replacement Policy Discovery**.

---

## 1. The `BaseProblem` Interface

Every domain in EvoAlgo must subclass `BaseProblem` to provide a uniform abstraction for problem specification, baseline provision, verification, and evaluation.

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel

class ProblemSpec(BaseModel):
    name: str
    description: str
    target_interface: str                      # Expected class name and signature
    objective_names: List[str]                 # e.g., ["hit_ratio", "latency_us", "memory_kb"]
    objective_directions: List[str]            # e.g., ["maximize", "minimize", "minimize"]

class BaseProblem(ABC):
    @abstractmethod
    def get_spec(self) -> ProblemSpec:
        """Returns metadata, interface contract, and objective definitions."""
        pass

    @abstractmethod
    def get_baselines(self) -> Dict[str, str]:
        """Returns reference human-written implementations (e.g., {'LRU': code, 'FIFO': code})."""
        pass

    @abstractmethod
    def verify_invariants(self, candidate_class: Any) -> Tuple[bool, str]:
        """Runs fast sanity tests against candidate class to verify behavioral contracts."""
        pass

    @abstractmethod
    def run_training_evaluation(self, candidate_class: Any) -> Dict[str, Any]:
        """Executes candidate against training workload distributions."""
        pass

    @abstractmethod
    def run_validation_evaluation(self, candidate_class: Any) -> Dict[str, Any]:
        """Executes candidate against held-out/unseen validation distributions."""
        pass
```

---

## 2. Cache Replacement Policy Contract

For the flagship domain `cache_replacement`, all evolved algorithms must implement the `BaseCache` class interface:

```python
class BaseCache(ABC):
    def __init__(self, capacity: int):
        """
        Initialize the cache with fixed capacity K.
        Must raise ValueError if capacity <= 0.
        """
        self.capacity = capacity

    @abstractmethod
    def get(self, key: int) -> bool:
        """
        Record access to `key`.
        Returns True if cache hit, False if cache miss.
        May update internal recency/frequency/metadata state.
        """
        pass

    @abstractmethod
    def put(self, key: int) -> int | None:
        """
        Insert `key` into cache.
        If key already exists, update state and return None.
        If cache is at capacity, select an existing key to evict,
        remove it, insert `key`, and return the evicted key.
        If cache is not full, insert `key` and return None.
        """
        pass
```

---

## 3. Invariant Verification Rules (Tier 2 Sanity Checks)

Before running computationally expensive workloads, the harness executes deterministic invariant tests:
1. **Capacity Invariant**: The cache must never store more than `capacity` items at any point in time.
2. **Hit Correctness Invariant**: If key `X` was inserted and has not been evicted, `get(X)` must return `True`.
3. **Eviction Validity Invariant**: When `put(Y)` causes an eviction, the returned evicted key `E` must have actually resided in the cache prior to eviction.
4. **Zero / Unity Edge Cases**: Behavior on `capacity = 1` must remain deterministic without crashing or infinite loops.
5. **Idempotence**: Accessing an existing key multiple times must not inflate cache size or corrupt internal links.

---

## 4. Workload Simulator Protocol

Workload execution feeds an array of keys into the candidate cache instance:

```python
def simulate_trace(cache: BaseCache, trace: List[int]) -> SimulationMetrics:
    hits = 0
    misses = 0
    evictions = 0
    
    start_time = time.perf_counter_ns()
    
    for key in trace:
        is_hit = cache.get(key)
        if is_hit:
            hits += 1
        else:
            misses += 1
            evicted = cache.put(key)
            if evicted is not None:
                evictions += 1
                
    total_time_ns = time.perf_counter_ns() - start_time
    total = hits + misses
    hit_ratio = hits / total if total > 0 else 0.0
    avg_latency_us = (total_time_ns / total) / 1000.0 if total > 0 else 0.0
    
    return SimulationMetrics(
        hits=hits,
        misses=misses,
        evictions=evictions,
        hit_ratio=hit_ratio,
        avg_latency_us=avg_latency_us
    )
```

---

## 5. Benchmarking & Noise Mitigation

To ensure reliable, non-noisy metrics:
* **Micro-benchmarks use synthetic traces with fixed seeds**: Trace generation uses `random.Random(42)` and `numpy.random.default_rng(42)`.
* **Execution Environment Warmup**: An initial dummy trace of 500 items is run to warm up JIT/bytecode compilation paths before recording latency metrics.
* **Aggregated Statistics**: High-resolution latency profiling executes 5 repeated passes; metrics report the **median** and **p99** latency to discard OS context-switch spikes.
