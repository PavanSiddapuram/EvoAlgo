"""
EvoAlgo Workload Generator Suite for Cache Replacement.
Provides multi-distribution synthetic traces, phase shifts, cyclic loops,
and adversarial fuzzing patterns to test algorithmic performance and generalization.
"""

from typing import Dict, List
import numpy as np


def generate_zipf_workload(
    num_requests: int = 5000,
    num_unique_keys: int = 200,
    alpha: float = 0.9,
    seed: int = 42,
) -> List[int]:
    """
    Generates a Zipfian distributed access sequence.
    Models skewed database/web cache access where a small fraction of keys receive most traffic.
    """
    rng = np.random.default_rng(seed)
    # Ranks 1 to num_unique_keys
    ranks = np.arange(1, num_unique_keys + 1)
    probabilities = 1.0 / np.power(ranks, alpha)
    probabilities /= np.sum(probabilities)

    # Sample keys from 0 to num_unique_keys - 1
    sampled = rng.choice(num_unique_keys, size=num_requests, p=probabilities)
    return [int(x) for x in sampled]


def generate_sequential_scan_workload(
    num_requests: int = 5000,
    working_set_size: int = 30,
    scan_length: int = 150,
    seed: int = 42,
) -> List[int]:
    """
    Generates a workload interleaving repeated access to a hot working set
    with long, cold linear scans.
    Tests resistance to cache pollution (does a scan flush hot items?).
    """
    rng = np.random.default_rng(seed)
    trace: List[int] = []
    scan_counter = 1000  # Offset cold scan keys

    while len(trace) < num_requests:
        # Access hot working set repeatedly (e.g. 50 requests)
        hot_chunk_len = min(60, num_requests - len(trace))
        hot_keys = rng.choice(working_set_size, size=hot_chunk_len)
        trace.extend(int(k) for k in hot_keys)

        if len(trace) >= num_requests:
            break

        # Linear scan of cold keys
        scan_chunk_len = min(scan_length, num_requests - len(trace))
        for _ in range(scan_chunk_len):
            trace.append(scan_counter)
            scan_counter += 1

    return trace[:num_requests]


def generate_cyclic_workload(
    capacity: int = 50,
    num_requests: int = 5000,
    cycle_offset: int = 2,
) -> List[int]:
    """
    Generates a strictly periodic access sequence of length (capacity + cycle_offset).
    This is a pathological pattern for classic LRU, which experiences a 100% miss rate (thrashing).
    """
    cycle_length = capacity + cycle_offset
    full_cycles = (num_requests // cycle_length) + 1
    repeated = list(range(cycle_length)) * full_cycles
    return repeated[:num_requests]


def generate_phase_shift_workload(
    num_requests: int = 5000,
    num_phases: int = 5,
    keys_per_phase: int = 40,
    seed: int = 42,
) -> List[int]:
    """
    Generates a workload where the active working set abruptly shifts from one key cluster to another.
    Tests how quickly an algorithm decays obsolete historical frequency/recency state.
    """
    rng = np.random.default_rng(seed)
    trace: List[int] = []
    requests_per_phase = num_requests // num_phases

    for phase in range(num_phases):
        offset = phase * (keys_per_phase // 2)  # Partial overlap between adjacent phases
        keys = np.arange(offset, offset + keys_per_phase)
        phase_requests = rng.choice(keys, size=requests_per_phase)
        trace.extend(int(k) for k in phase_requests)

    # Pad if remainder exists
    if len(trace) < num_requests:
        trace.extend([int(x) for x in rng.choice(keys_per_phase, size=num_requests - len(trace))])

    return trace[:num_requests]


def generate_bursty_workload(
    num_requests: int = 5000,
    num_background_keys: int = 250,
    burst_keys_count: int = 15,
    burst_length: int = 40,
    seed: int = 42,
) -> List[int]:
    """
    Generates background random traffic punctuated by intense temporal bursts on a tiny subset.
    Tests the algorithm's agility in recognizing sudden temporal spikes.
    """
    rng = np.random.default_rng(seed)
    trace: List[int] = []

    while len(trace) < num_requests:
        # Background traffic
        bg_len = min(80, num_requests - len(trace))
        trace.extend(int(k) for k in rng.choice(num_background_keys, size=bg_len))

        if len(trace) >= num_requests:
            break

        # Temporal burst
        burst_len = min(burst_length, num_requests - len(trace))
        burst_keys = rng.choice(burst_keys_count, size=burst_len)
        # Offset burst keys into a dedicated range
        trace.extend(int(k + 500) for k in burst_keys)

    return trace[:num_requests]


def generate_adversarial_fuzzer_workload(
    capacity: int = 50,
    num_requests: int = 5000,
    seed: int = 42,
) -> List[int]:
    """
    Co-evolutionary adversarial fuzzer trace.
    Combines thrashing cyclic loops, interleaved stride scans, and deceptive bursts
    specifically crafted to exploit deterministic eviction policies.
    """
    rng = np.random.default_rng(seed)
    trace: List[int] = []
    thrash_cycle = list(range(capacity + 1))
    cold_key = 9000

    while len(trace) < num_requests:
        action = rng.integers(0, 3)
        if action == 0:
            # Inject thrash cycle
            chunk = thrash_cycle * 2
            trace.extend(chunk)
        elif action == 1:
            # Inject short cold scan
            scan_len = min(capacity * 2, num_requests - len(trace))
            for _ in range(scan_len):
                trace.append(cold_key)
                cold_key += 1
        else:
            # Temporal trap: re-access one key from the cycle then switch
            trace.extend([0, 0, 0, 1, 1, 2])

    return trace[:num_requests]


def get_training_workloads(capacity: int = 50, num_requests: int = 4000) -> Dict[str, List[int]]:
    """Standard training workload suite used during the evolutionary cycle."""
    return {
        "zipf_skewed_train": generate_zipf_workload(
            num_requests=num_requests, num_unique_keys=capacity * 4, alpha=0.95, seed=101
        ),
        "scan_pollution_train": generate_sequential_scan_workload(
            num_requests=num_requests, working_set_size=capacity // 2, scan_length=capacity * 2, seed=102
        ),
        "cyclic_thrash_train": generate_cyclic_workload(
            capacity=capacity, num_requests=num_requests, cycle_offset=1
        ),
        "phase_shift_train": generate_phase_shift_workload(
            num_requests=num_requests, num_phases=4, keys_per_phase=capacity, seed=103
        ),
    }


def get_validation_workloads(capacity: int = 50, num_requests: int = 4000) -> Dict[str, List[int]]:
    """
    Held-out validation suite evaluated post-generation to check out-of-distribution generalization.
    Uses higher Zipf alpha, different phase boundaries, bursty distributions, and adversarial fuzzing.
    """
    return {
        "zipf_skewed_val": generate_zipf_workload(
            num_requests=num_requests, num_unique_keys=capacity * 6, alpha=1.2, seed=201
        ),
        "bursty_temporal_val": generate_bursty_workload(
            num_requests=num_requests, num_background_keys=capacity * 5, seed=202
        ),
        "cyclic_offset_val": generate_cyclic_workload(
            capacity=capacity, num_requests=num_requests, cycle_offset=3
        ),
        "adversarial_fuzzer_val": generate_adversarial_fuzzer_workload(
            capacity=capacity, num_requests=num_requests, seed=203
        ),
    }
