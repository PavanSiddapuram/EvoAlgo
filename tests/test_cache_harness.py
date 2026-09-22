"""
Comprehensive tests for Tier 1 Cache Replacement Problem Harness.
Validates invariant checking, fast gate, simulation accuracy, and baseline dynamics.
"""

import pytest
from problems.cache_replacement.problem import CacheProblem
from problems.cache_replacement.baselines import (
    FIFOCache, FIFO_SOURCE,
    LRUCache, LRU_SOURCE,
    LFUCache, LFU_SOURCE,
    ARCCache, ARC_SOURCE,
)
from problems.cache_replacement.simulator import CacheInvariantChecker, CacheSimulator
from problems.cache_replacement.workloads import (
    generate_zipf_workload,
    generate_sequential_scan_workload,
    generate_cyclic_workload,
    generate_phase_shift_workload,
    generate_bursty_workload,
    generate_adversarial_fuzzer_workload,
    get_training_workloads,
    get_validation_workloads,
)


def test_problem_specification():
    problem = CacheProblem(capacity=50, requests_per_workload=500)
    spec = problem.get_spec()
    assert spec.name == "cache_replacement"
    assert spec.tier == "tier_1_systems"
    assert "hit_ratio" in spec.objective_names
    assert "latency_us" in spec.objective_names


def test_fast_gate_verification():
    problem = CacheProblem(capacity=50)

    # Valid class with get and put
    valid, msg = problem.verify_fast_gate(LRU_SOURCE)
    assert valid is True

    # Invalid syntax
    valid, msg = problem.verify_fast_gate("def broken(: print('hi')")
    assert valid is False
    assert "SyntaxError" in msg

    # Missing methods
    no_methods = "class EmptyPolicy:\n    pass\n"
    valid, msg = problem.verify_fast_gate(no_methods)
    assert valid is False
    assert "must implement both 'get(self, key)' and 'put(self, key)'" in msg


@pytest.mark.parametrize("cache_cls", [FIFOCache, LRUCache, LFUCache, ARCCache])
def test_baseline_invariants(cache_cls):
    passed, reason = CacheInvariantChecker.verify(cache_cls)
    assert passed is True, f"{cache_cls.__name__} failed invariants: {reason}"


def test_broken_cache_invariant_detection():
    # Cache that exceeds capacity
    class BrokenCapacityCache:
        def __init__(self, capacity: int):
            self.capacity = capacity
            self.items = set()

        def get(self, key: int) -> bool:
            return key in self.items

        def put(self, key: int) -> None:
            self.items.add(key)  # never evicts!
            return None

    passed, reason = CacheInvariantChecker.verify(BrokenCapacityCache)
    assert passed is False
    assert "invariant" in reason.lower() or "exceeded" in reason.lower() or "eviction" in reason.lower()


def test_workload_generators():
    zipf = generate_zipf_workload(num_requests=200, num_unique_keys=30, alpha=0.9, seed=42)
    assert len(zipf) == 200
    assert max(zipf) < 30

    scan = generate_sequential_scan_workload(num_requests=300, working_set_size=10, scan_length=50, seed=42)
    assert len(scan) == 300

    cyclic = generate_cyclic_workload(capacity=10, num_requests=100, cycle_offset=1)
    assert len(cyclic) == 100
    assert cyclic[0:11] == list(range(11))

    phase = generate_phase_shift_workload(num_requests=200, num_phases=4, keys_per_phase=20, seed=42)
    assert len(phase) == 200

    bursty = generate_bursty_workload(num_requests=200, num_background_keys=50, seed=42)
    assert len(bursty) == 200

    adv = generate_adversarial_fuzzer_workload(capacity=10, num_requests=200, seed=42)
    assert len(adv) == 200


def test_baseline_simulation_evaluation():
    problem = CacheProblem(capacity=20, requests_per_workload=500)

    # Evaluate LRU
    report_lru = problem.run_training_evaluation(LRUCache, individual_id="baseline_lru")
    assert report_lru.passed_invariants is True
    assert report_lru.overall_train_hit_ratio > 0.0
    assert len(report_lru.train_metrics) == 4

    # Evaluate ARC
    report_arc = problem.run_training_evaluation(ARCCache, individual_id="baseline_arc")
    assert report_arc.passed_invariants is True
    assert report_arc.overall_train_hit_ratio > 0.0

    # Validation evaluation
    val_report = problem.run_validation_evaluation(ARCCache, individual_id="baseline_arc")
    assert val_report.overall_val_hit_ratio > 0.0
    assert len(val_report.validation_metrics) == 4


def test_lru_cyclic_thrashing():
    """
    Validates that a cyclic loop of size (capacity + 1) induces complete thrashing in LRU,
    demonstrating the need for advanced eviction heuristics.
    """
    capacity = 10
    cyclic_trace = generate_cyclic_workload(capacity=capacity, num_requests=110, cycle_offset=1)

    metric = CacheSimulator.run_workload(LRUCache, capacity, "cyclic_thrash", cyclic_trace)
    # LRU will have 0 hits once the loop starts, initial requests miss
    assert metric.hits == 0
    assert metric.hit_ratio == 0.0
