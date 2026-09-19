# 🏛️ EvoAlgo: Architecture & Systems Design Document

This document provides the exhaustive architectural specification for **EvoAlgo**, outlining subsystem boundaries, data models, execution isolation protocols, and communication workflows.

---

## 1. System Topology Overview

```
                                    +----------------------------------+
                                    |         User / Dashboard         |
                                    |   (Web UI / CLI / Experimenter)  |
                                    +-----------------+----------------+
                                                      | HTTP / WebSocket
                                                      v
                                    +----------------------------------+
                                    |         FastAPI Gateway          |
                                    +-----------------+----------------+
                                                      |
                                                      v
+---------------------------------------------------------------------------------------------------------+
|                                        EVOLUTION ORCHESTRATOR                                           |
|                                                                                                         |
|    +------------------------+      +-------------------------+      +------------------------------+    |
|    |      Island Manager    |      |     Population Pool     |      |       Pareto Archive         |    |
|    |  (Topology & Migration)|      |  (Individuals per Isle) |      |     (Global Non-Dominated)   |    |
|    +-----------+------------+      +------------+------------+      +--------------+---------------+    |
|                |                                |                                  ^                    |
|                |                                v                                  |                    |
|                |                   +-------------------------+                     |                    |
|                |                   |      NSGA-II Selector   |                     |                    |
|                |                   | (Crowding & Dominance)  |                     |                    |
|                |                   +------------+------------+                     |                    |
|                |                                |                                  |                    |
|                v                                v                                  |                    |
|    +------------------------+      +-------------------------+                     |                    |
|    |     LLM Generator      |      |   Mutation / Crossover  |                     |                    |
|    |   (Multi-Provider API) |◄─────┤   (Operator Dispatcher) |                     |                    |
|    +-----------+------------+      +-------------------------+                     |                    |
|                |                                                                   |                    |
|                v                                                                   |                    |
|    +------------------------+                                                      |                    |
|    |  AST Parser & Cleaner  |                                                      |                    |
|    +-----------+------------+                                                      |                    |
|                |                                                                   |                    |
|                v                                                                   |                    |
|    +--------------------------------------------------------------------------+    |                    |
|    |                           EVALUATOR HARNESS                              |    |                    |
|    |                                                                          |    |                    |
|    |  +--------------------+   +---------------------+   +-----------------+  |    |                    |
|    |  | Tier 1: AST Check  |──►| Tier 2: Invariants  |──►| Tier 3: Workload|  |────+                    |
|    |  |  (Static Linting)  |   |   (Correctness)     |   |   (Simulation)  |  |    |                    |
|    |  +--------------------+   +---------------------+   +--------+--------+  |    |                    |
|    |                                                              |           |    |                    |
|    |                                                              v           |    |                    |
|    |                                                     +-----------------+  |    |                    |
|    |                                                     | Tier 4: Profiler|  |    |                    |
|    |                                                     | (Latency/Memory)|  |    |                    |
|    |                                                     +-----------------+  |    |                    |
+----+--------------------------------------------------------------------------+----+--------------------+
                                                      |
                                                      v
                                    +----------------------------------+
                                    |     Experiment Store (SQLite/PG) |
                                    |   - Individuals & Phenotypes     |
                                    |   - Code Diffs & Lineage DAG     |
                                    |   - Generation Time-Series Logs  |
                                    +----------------------------------+
```

---

## 2. Core Subsystems

### 2.1 Generator & Prompt Dispatcher
The Generator transforms parent algorithm genotypes and performance diagnostics into concrete prompts for LLM providers:
* **Multi-Provider Support**: Pluggable backend adapter (`GeminiProvider`, `AnthropicProvider`, `OpenAIProvider`, `LocalOllamaProvider`).
* **Operator Dispatcher**: Directs the request to one of five prompt templates:
  * `OPTIMIZATION_PROMPT`: Directs local loop tightening, data structure reuse, and branch pruning.
  * `STRUCTURAL_PROMPT`: Directs replacement of backing storage (e.g., hash table + heap vs. ring buffer + bitmaps).
  * `ALGORITHMIC_PROMPT`: Demands a completely different conceptual decision policy.
  * `SIMPLIFICATION_PROMPT`: Strips dead tracking state while maintaining performance invariants.
  * `CROSSOVER_PROMPT`: Merges complementary concepts from two high-ranking parents.
* **Extraction & Sanitization**: Uses Python's `ast` module to strip markdown blocks, validate syntax, and verify interface conformance before handing code to the sandbox.

### 2.2 Sandboxed Evaluator Harness
The evaluator executes arbitrary LLM-generated code under strict isolation. Execution occurs in an isolated subprocess with OS-level resource limits:
* **Linux / Container Target**: `setrlimit` (`RLIMIT_CPU`, `RLIMIT_AS`), Docker container with `--cpus=1.0` and `--memory=256m`, `--net=none`.
* **Windows Host Support**: Subprocess runner with `psutil` process tree monitoring, hard wall-clock timeouts, memory limits, and isolated Python execution environments.
* **Fail-Fast Tiered Pipeline**:
  1. *Tier 1: AST Validation* (< 5ms): Verifies AST syntax and checks that the required class (e.g. `CachePolicy`) and methods (`get`, `put`, `evict`) are implemented.
  2. *Tier 2: Invariant Correctness* (< 50ms): Evaluates small edge-case access patterns (e.g., capacity 1, zero capacity, repeated duplicate keys, immediate evictions) to guarantee safety.
  3. *Tier 3: Workload Simulation* (< 500ms): Feeds 10,000+ access requests across Zipfian, sequential, and cyclic workload traces. Collects hit count, miss count, and eviction count.
  4. *Tier 4: Micro-benchmarking* (< 2000ms): Runs timed operational sweeps to collect p50/p99 operation latencies and peak memory overhead.

### 2.3 Evolutionary Engine & Selection
The engine maintains the population across generational rounds:
* **Individual**: Contains unique ID, source code, genome metadata, parent IDs, mutation operator applied, fitness vector, and validation scores.
* **Population & Islands**: Organizes individuals into $K$ isolated islands (e.g., Island 1: Greedy/Recency, Island 2: Frequency/Count-Min, Island 3: Predictive/Decay).
* **NSGA-II Selection**:
  * **Fast Non-Dominated Sorting**: Partitions candidates into Pareto fronts ($F_1, F_2, \dots, F_k$).
  * **Crowding Distance Assignment**: Calculates the density of solutions surrounding a candidate in objective space, favoring isolated solutions to preserve boundary diversity.
* **Migration**: Every $M$ generations, the top non-dominated candidates from each island migrate to peer islands in a ring or star topology.

### 2.4 Experiment Store & Phylogenetic Lineage
Every generated candidate is immutably stored:
* **Lineage DAG**: Each candidate references its `parent_ids`. This constructs a complete phylogenetic tree of algorithmic evolution over time.
* **Code Diffs**: Generates unified diffs between parent and child programs, enabling visualization of the exact line-by-line discoveries.
* **Workload Breakdown**: Stores hit rates and latencies per workload profile to track generalization progress.

---

## 3. Data Schemas

### 3.1 Individual Model
```python
class Individual(BaseModel):
    id: str                                    # e.g., "cand_g05_i01_042"
    generation: int                            # Generation index
    island_id: str                             # Island identifier
    parent_ids: list[str]                      # Empty if generation 0 baseline
    mutation_operator: str                     # "optimization" | "structural" | "algorithmic" | "crossover" | "baseline"
    code: str                                  # Complete executable Python source code
    genome_metadata: dict[str, Any]            # Abstract strategy, data structures, complexity
    
    # Phenotype / Evaluation Results
    is_valid: bool = False                     # Passed compilation & invariants
    error_message: Optional[str] = None        # Compilation / runtime failure details
    
    # Fitness Vector (Pareto Objectives)
    hit_ratio_train: float = 0.0               # Primary objective (higher is better)
    hit_ratio_val: float = 0.0                 # Generalization check (unseen workloads)
    avg_latency_us: float = 0.0                # Eviction latency in microseconds (lower is better)
    memory_overhead_bytes: int = 0             # Peak tracking structure memory (lower is better)
    
    pareto_rank: int = 0                       # Assigned by NSGA-II
    crowding_distance: float = 0.0             # Assigned by NSGA-II
```

### 3.2 Evaluation Result Schema
```python
class WorkloadMetric(BaseModel):
    workload_name: str
    total_requests: int
    hits: int
    misses: int
    hit_ratio: float
    evictions: int
    elapsed_time_ms: float

class EvaluationResult(BaseModel):
    individual_id: str
    passed_syntax: bool
    passed_invariants: bool
    train_metrics: list[WorkloadMetric]
    validation_metrics: list[WorkloadMetric]
    overall_train_hit_ratio: float
    overall_val_hit_ratio: float
    generalization_gap: float                  # train_hit_ratio - val_hit_ratio
    p99_latency_us: float
    peak_memory_kb: float
```

---

## 4. Workload Trace Specification (Cache Domain)

To guarantee that discovered policies do not overfit:

| Trace Identifier | Profile | Characteristics | Evaluates |
| :--- | :--- | :--- | :--- |
| `zipf_alpha_0.9` | Skewed Web Access | $80\%$ of requests focus on $20\%$ of keys | Basic frequency and temporal locality |
| `sequential_scan` | Database Table Scan | Long monotonic stream: $1, 2, \dots, 2K$ (where $K$ = cache size) | Cache pollution resistance (Bypass mechanism) |
| `cyclic_thrash` | Periodic Loop | Repeated sequence of size $K + 1$ | Resistance to pathological LRU thrashing |
| `bursty_phases` | Multi-Tenant Workload | High-frequency access to Set A, followed by instant shift to Set B | Adaptation speed & frequency decay |
| `val_realworld_trace` | Hidden Validation | Real-world CDN/OLTP access trace (unseen during evolution) | True out-of-distribution algorithmic generalization |

---

## 5. Security and Sandboxing Design

Executing untrusted code generated by an LLM requires strict boundary enforcement:
1. **No External Network Access**: Disallow socket initialization.
2. **Filesystem Restrictions**: Code executes in an isolated temporary directory with read-only access to necessary libraries and no write access to system files.
3. **Hard Process Termination**: If an algorithm enters an infinite loop, the orchestrator issues a `SIGKILL` after a strict timeout ($2.0$ seconds).
4. **Memory Hard Capping**: Memory allocations exceeding $256\,\text{MB}$ immediately trigger an out-of-memory exception and failure marking.
