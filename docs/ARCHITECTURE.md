# 🏛️ EvoAlgo: Architecture & Systems Design Document

This document provides the exhaustive architectural specification for **EvoAlgo**, detailing subsystem boundaries, data models, execution isolation protocols, MAP-Elites archives, bandit dispatchers, and domain extensions across Systems and AI/ML Infrastructure.

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
|                |                   +-------------------------+      +--------------+---------------+    |
|                |                   |      NSGA-II Selector   |      |       MAP-Elites Grid        |    |
|                |                   | (Crowding & Dominance)  |      |   (Behavioral Niche Cells)   |    |
|                |                   +------------+------------+      +------------------------------+    |
|                |                                |                                                       |
|                v                                v                                                       |
|    +------------------------+      +-------------------------+                                          |
|    |     LLM Generator      |      |   Bandit Mutation Router|                                          |
|    |   (Multi-Provider API) |◄─────┤   (Thompson Sampling)   |                                          |
|    +-----------+------------+      +-------------------------+                                          |
|                |                                                                                        |
|                v                                                                                        |
|    +------------------------+                                                                           |
|    |  AST Parser & Cleaner  |                                                                           |
|    +-----------+------------+                                                                           |
|                |                                                                                        |
|                v                                                                                        |
|    +--------------------------------------------------------------------------+                         |
|    |                           EVALUATOR HARNESS                              |                         |
|    |                                                                          |                         |
|    |  +--------------------+   +---------------------+   +-----------------+  |                         |
|    |  | Tier 1: Fast Gate  |──►| Tier 2: Invariants  |──►| Tier 3: Workload|  |                         |
|    |  | (AST Complexity    |   |   (Correctness)     |   |   (Simulation)  |  |                         |
|    |  |   & Linting <10ms) |   +---------------------+   +--------+--------+  |                         |
|    |  +--------------------+                                      |           |                         |
|    |                                                              v           |                         |
|    |                                                     +-----------------+  |                         |
|    |                                                     | Tier 4: Profiler|  |                         |
|    |                                                     | (Latency/Memory)|  |                         |
|    |                                                     +-----------------+  |                         |
+----+--------------------------------------------------------------------------+-------------------------+
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

### 2.1 Generator & Thompson Sampling Bandit Dispatcher
The Generator transforms parent algorithm genotypes into concrete prompts for LLM providers:
* **Multi-Provider Adapter**: Pluggable backend adapter (`GeminiProvider`, `AnthropicProvider`, `OpenAIProvider`, `LocalOllamaProvider`).
* **Adaptive Multi-Armed Bandit (MAB)**: Rather than fixed probabilities, operator dispatch uses **Thompson Sampling** over Beta distributions:
  $$\theta_k \sim \text{Beta}(\alpha_k, \beta_k)$$
  Where $\alpha_k$ is the count of successful offspring (achieving non-domination) from operator $k$, and $\beta_k$ is the count of rejected offspring.
* **Operator Suite**:
  * `OPTIMIZATION_PROMPT`: Directs local loop tightening, data structure reuse, and branch pruning.
  * `STRUCTURAL_PROMPT`: Directs replacement of backing storage (e.g., hash table + heap vs. ring buffer + bitmaps).
  * `ALGORITHMIC_PROMPT`: Demands a completely different conceptual decision policy.
  * `SIMPLIFICATION_PROMPT`: Strips dead tracking state while maintaining performance invariants.
  * `CROSSOVER_PROMPT`: Merges complementary concepts from two high-ranking parents.
* **Extraction & Sanitization**: Uses Python's `ast` module to strip markdown blocks, validate syntax, and verify interface conformance before handing code to the sandbox.

### 2.2 Quality Diversity: MAP-Elites Behavioral Archive
In addition to NSGA-II Pareto sorting, the engine maintains a **Multi-dimensional Archive of Phenotypic Elites (MAP-Elites)**:
* **Feature Dimensions**:
  * Dimension 1: Memory Footprint per Key (Low: $<32$B, Medium: $32-96$B, High: $>96$B).
  * Dimension 2: Algorithmic Strategy Family (Recency, Frequency, Adaptive-decay, Ghost-cache, Hybrid).
  * Dimension 3: AST Branch / Decision Complexity (Shallow $\le 3$, Medium $4-7$, Deep $\ge 8$).
* **Occupancy Rule**: When a candidate is evaluated, it is mapped to cell $(d_1, d_2, d_3)$. If the cell is empty, the candidate becomes the cell elite. If occupied, the candidate replaces the incumbent only if its primary fitness (hit ratio) exceeds the incumbent.

### 2.3 Sandboxed Evaluator Harness
The evaluator executes arbitrary LLM-generated code under strict isolation:
* **Execution Safety**: Subprocess runner with hard wall-clock timeouts (default $2.0$s), memory capping ($256$MB), and clean process tree teardown via `psutil`.
* **Fail-Fast Tiered Pipeline**:
  1. *Tier 1: Fast Gate (<10ms)*: AST check, recursion depth validation, and signature verification.
  2. *Tier 2: Invariant Correctness (<50ms)*: Edge-case tests (capacity 1, repeated keys, full eviction validity).
  3. *Tier 3: Workload Simulation (<500ms)*: Multi-workload simulation across training traces and co-evolved adversarial traces.
  4. *Tier 4: Micro-benchmarking (<2000ms)*: High-resolution timing sweeps to collect p50/p99 operation latencies and memory high-water mark.

### 2.4 Research Domains (Tier 1 Systems & Tier 2 AI/ML)
* **Tier 1: Systems Cache Replacement**: Evaluates algorithms implementing `BaseCache(capacity)` on keys and eviction decisions.
* **Tier 2: LLM KV-Cache Compression**: Evaluates algorithms implementing `KVCachePolicy(max_tokens)` on token sequences, attention weights, and dynamic eviction/compression decisions.

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
    
    # Behavioral Niche Coordinates (MAP-Elites)
    niche_coordinates: tuple[int, int, int] = (0, 0, 0)
    
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
