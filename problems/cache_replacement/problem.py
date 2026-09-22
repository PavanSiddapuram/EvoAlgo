"""
Cache Replacement Problem Domain Definition.
"""

import ast
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Type
from problems.base import BaseProblem, EvaluationReport, ProblemSpec
from problems.cache_replacement.simulator import CacheInvariantChecker, CacheSimulator
from problems.cache_replacement.workloads import get_training_workloads, get_validation_workloads


class BaseCache(ABC):
    """
    The abstract interface that all evolved cache replacement policies must implement.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError(f"Capacity must be positive integer, got {capacity}")
        self.capacity = capacity

    @abstractmethod
    def get(self, key: int) -> bool:
        """
        Lookup key in cache.
        Returns True if cache hit, False if cache miss.
        May update internal recency/frequency/decay state.
        """
        pass

    @abstractmethod
    def put(self, key: int) -> Optional[int]:
        """
        Insert key into cache.
        If key already exists, updates internal state and returns None.
        If cache is full, evicts a key according to the policy, inserts the new key,
        and returns the evicted key.
        If cache is not full, inserts key and returns None.
        """
        pass


class CacheProblem(BaseProblem):
    """
    Tier 1 Systems Problem: Cache Replacement Policy Discovery.
    Evaluates policies on hit ratio, eviction latency, memory overhead, and generalization.
    """

    def __init__(self, capacity: int = 50, requests_per_workload: int = 4000):
        self.capacity = capacity
        self.requests_per_workload = requests_per_workload
        self.train_workloads = get_training_workloads(capacity, requests_per_workload)
        self.validation_workloads = get_validation_workloads(capacity, requests_per_workload)

    def get_spec(self) -> ProblemSpec:
        return ProblemSpec(
            name="cache_replacement",
            tier="tier_1_systems",
            description=(
                "Discover optimal cache replacement policies that maximize hit ratio "
                "across skewed, sequential, cyclic, and adversarial workload traces "
                "while minimizing eviction latency and memory overhead."
            ),
            target_interface="BaseCache(capacity: int)",
            objective_names=["hit_ratio", "latency_us", "generalization_gap"],
            objective_directions=["maximize", "minimize", "minimize"],
        )

    def get_baselines(self) -> Dict[str, str]:
        from problems.cache_replacement.baselines.fifo import FIFO_SOURCE
        from problems.cache_replacement.baselines.lru import LRU_SOURCE
        from problems.cache_replacement.baselines.lfu import LFU_SOURCE
        from problems.cache_replacement.baselines.arc import ARC_SOURCE

        return {
            "FIFO": FIFO_SOURCE,
            "LRU": LRU_SOURCE,
            "LFU": LFU_SOURCE,
            "ARC": ARC_SOURCE,
        }

    def verify_fast_gate(self, code: str) -> Tuple[bool, str]:
        """Tier 1: AST static inspection (<10ms)."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"SyntaxError: {e.msg} at line {e.lineno}"

        # Find classes in the module
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if not classes:
            return False, "No class definition found in code."

        # Find target class implementing get and put
        target_class = None
        for cls in classes:
            method_names = {
                n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            if "get" in method_names and "put" in method_names:
                target_class = cls
                break

        if target_class is None:
            return False, "Candidate class must implement both 'get(self, key)' and 'put(self, key)' methods."

        return True, f"Fast-gate verified class '{target_class.name}'."

    def verify_invariants(self, candidate_class: Type[Any]) -> Tuple[bool, str]:
        """Tier 2: Rigorous invariant tests."""
        return CacheInvariantChecker.verify(candidate_class)

    def run_training_evaluation(
        self, candidate_class: Type[Any], individual_id: str = "unknown"
    ) -> EvaluationReport:
        """Tier 3: Run training workload suite."""
        CacheSimulator.warmup(candidate_class, self.capacity)
        train_metrics = []

        for name, trace in self.train_workloads.items():
            metric = CacheSimulator.run_workload(candidate_class, self.capacity, name, trace)
            train_metrics.append(metric)

        overall_train_hit = (
            sum(m.hits for m in train_metrics) / sum(m.total_requests for m in train_metrics)
            if train_metrics
            else 0.0
        )
        avg_latencies = [m.avg_latency_us for m in train_metrics]
        p99_latency = max(avg_latencies) if avg_latencies else 0.0

        return EvaluationReport(
            individual_id=individual_id,
            domain="cache_replacement",
            passed_fast_gate=True,
            passed_invariants=True,
            train_metrics=train_metrics,
            overall_train_hit_ratio=round(overall_train_hit, 4),
            p99_latency_us=round(p99_latency, 3),
        )

    def run_validation_evaluation(
        self, candidate_class: Type[Any], individual_id: str = "unknown"
    ) -> EvaluationReport:
        """Tier 3 (Held-out): Run unseen validation workload suite."""
        val_metrics = []
        for name, trace in self.validation_workloads.items():
            metric = CacheSimulator.run_workload(candidate_class, self.capacity, name, trace)
            val_metrics.append(metric)

        overall_val_hit = (
            sum(m.hits for m in val_metrics) / sum(m.total_requests for m in val_metrics)
            if val_metrics
            else 0.0
        )
        return EvaluationReport(
            individual_id=individual_id,
            domain="cache_replacement",
            passed_fast_gate=True,
            passed_invariants=True,
            validation_metrics=val_metrics,
            overall_val_hit_ratio=round(overall_val_hit, 4),
        )
