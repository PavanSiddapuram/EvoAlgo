# 🧪 EvoAlgo: Problem Harness & Evaluation Specification

This specification defines the contract between the **EvoAlgo Core Engine** and any **Problem Domain**, outlining the harness protocols for:
1. **Tier 1: Systems Cache Replacement Policy Discovery**
2. **Tier 2: LLM KV-Cache Eviction & Compression Discovery**
3. **Co-Evolutionary Adversarial Workload Fuzzing**
4. **Fast-Path Pre-Execution Filtering**

---

## 1. The `BaseProblem` Interface

Every domain in EvoAlgo must subclass `BaseProblem` to provide a uniform abstraction:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel

class ProblemSpec(BaseModel):
    name: str
    tier: str                                  # "tier_1_systems" | "tier_2_ai_systems"
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
        """Returns reference implementations (e.g. {'LRU': code, 'FIFO': code, 'ARC': code})."""
        pass

    @abstractmethod
    def verify_fast_gate(self, code: str) -> Tuple[bool, str]:
        """Tier 1: Fast AST inspection and complexity check (<10ms)."""
        pass

    @abstractmethod
    def verify_invariants(self, candidate_class: Any) -> Tuple[bool, str]:
        """Tier 2: Sanity tests against candidate class to verify behavioral contracts."""
        pass

    @abstractmethod
    def run_training_evaluation(self, candidate_class: Any) -> Dict[str, Any]:
        """Tier 3: Executes candidate against training workload distributions."""
        pass

    @abstractmethod
    def run_validation_evaluation(self, candidate_class: Any) -> Dict[str, Any]:
        """Tier 3 (Held-out): Executes candidate against unseen validation distributions."""
        pass
```

---

## 2. Tier 1: Cache Replacement Policy Contract

For `cache_replacement`, all evolved algorithms must implement the `BaseCache` class interface:

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

1. **Capacity Invariant**: At no point may the number of items stored exceed `capacity`.
2. **Hit Correctness Invariant**: If key `X` was inserted and has not been evicted, `get(X)` must return `True`.
3. **Eviction Validity Invariant**: When `put(Y)` causes an eviction, the returned evicted key `E` must have actually resided in the cache prior to eviction.
4. **Zero / Unity Edge Cases**: Behavior on `capacity = 1` must remain deterministic without crashing or infinite loops.
5. **Idempotence**: Accessing an existing key multiple times must not inflate cache size or corrupt internal links.

---

## 4. Adversarial Workload Fuzzing Contract

In addition to standard synthetic traces (Zipfian, Sequential, Cyclic), the harness includes an **Adversarial Trace Fuzzer**:

```python
class AdversarialWorkloadGenerator:
    """
    Generates dynamic adversarial access patterns to induce cache thrashing.
    Mutates loop length, stride step, and phase shift frequency.
    """
    def generate_adversarial_trace(
        self,
        capacity: int,
        length: int,
        adversarial_seed: int
    ) -> List[int]: ...
```

---

## 5. Tier 2: LLM KV-Cache Eviction & Compression Interface

For `llm_kv_cache`, algorithms implement the `BaseKVCachePolicy` interface:

```python
class BaseKVCachePolicy(ABC):
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens

    @abstractmethod
    def step(
        self,
        token_id: int,
        layer_idx: int,
        attention_vector: List[float]
    ) -> int | None:
        """
        Called on each generated token.
        `attention_vector`: Attention weights from the current query to all stored tokens.
        Returns the token index to evict if cache is at capacity, else None.
        """
        pass
```
