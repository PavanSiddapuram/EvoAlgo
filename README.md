# 🧬 EvoAlgo: LLM-Driven Evolutionary Algorithm Discovery System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Active Development](https://img.shields.io/badge/status-pre--alpha-orange.svg)]()

> **"Don't ask an LLM to write a better algorithm. Treat the algorithm as an organism, and use the LLM as the mutation operator."**

EvoAlgo is an evolutionary coding framework where Large Language Models (LLMs) act as guided mutation and crossover operators across an evolving population of algorithmic candidates. Candidates are continuously compiled, executed inside an isolated sandbox, benchmarked against multi-distribution workload suites, and ranked using multi-objective Pareto optimization and MAP-Elites quality-diversity archives.

The engine spans both **Systems Infrastructure** (cache eviction, job scheduling, memory managers) and **Frontier AI/ML & LLM Systems** (KV-cache compression, MoE token routing, speculative decoding verification, and symbolic optimizers).

---

## Table of Contents
- [Problem Statement](#-problem-statement)
- [The Core Thesis: First Principles](#-the-core-thesis-first-principles)
- [The Evolutionary Loop](#-the-evolutionary-loop)
- [Frontier Capabilities](#-frontier-capabilities)
- [Research Wedges: Systems & AI/ML Systems](#-research-wedges-systems--aiml-systems)
- [The Algorithm as an Organism](#-the-algorithm-as-an-organism)
- [Mutation & Crossover Operators](#-mutation--crossover-operators)
- [Population Dynamics & Island Model](#-population-dynamics--island-model)
- [The Evaluator & Pareto Frontier](#-the-evaluator--pareto-frontier)
- [Flagship Pilot Problem: Cache Replacement](#-flagship-pilot-problem-cache-replacement)
- [Generalization: Train vs. Hidden Workloads](#-generalization-train-vs-hidden-workloads)
- [System Architecture](#-system-architecture)
- [Repository Structure](#-repository-structure)
- [Phased Roadmap](#-phased-roadmap)

---

## 🎯 Problem Statement

Direct prompt-based algorithm synthesis (*"Write an optimal algorithm for X"*) suffers from three fatal limitations:
1. **Regressing to the Pretraining Mean**: LLMs output textbook solutions (QuickSort, LRU, standard DP) because those are the highest-probability sequences in their training distribution. They cannot autonomously break into novel algorithmic territory through single-shot prompting.
2. **Hallucinatory Optimality**: An LLM cannot execute its own code or observe hardware caches, branch predictors, or memory layouts. Without an empirical execution loop, algorithmic claims are ungrounded.
3. **Premature Convergence & Fragility**: Classical Genetic Programming (GP) relies on random AST node mutations or bit-flips, producing an overwhelming majority of non-compiling or semantically broken programs ($99\%+$ mortality).

### The Scientific Question
> *Can an LLM-guided evolutionary search discover non-trivial, human-competitive algorithmic heuristics that generalize across unseen workloads, outperforming both raw LLM zero-shot generation and classical genetic programming?*

---

## 💡 The Core Thesis: First Principles

$$\text{Algorithmic Discovery} = \text{LLM Semantic Prior} \times \text{Evolutionary Search Space} \times \text{Empirical Sandbox Feedback}$$

```
                ┌──────────────────────────────┐
                │   LLM Generative Prior       │
                │  (Semantic AST mutations)    │
                └──────────────┬───────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │                 EvoAlgo Discovery Engine                │
  │                                                         │
  │   [Evolutionary Topology]       [Empirical Ground Truth]│
  │    • Multi-Island Speciation     • Subprocess Sandbox   │
  │    • MAP-Elites Quality Diversity• Multi-Workload Suite │
  │    • Pareto Non-Domination       • Co-Evolving Fuzzers  │
  │    • Cross-Gen Migration         • Profiling & Counters │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
               Discovered High-Performing Policy
```

1. **The LLM provides semantic-preserving code mutations**: Instead of random token flips, the LLM makes structured edits with full awareness of program logic, invariants, and syntax.
2. **Evolutionary search navigates high-dimensional trade-offs**: By keeping a diverse population across multiple islands and behavioral niches, the system avoids local optima.
3. **The sandbox enforces ground truth**: No hallucinated speedups survive. The evaluator measures exact cache hit rates, CPU cycles, and memory overheads.

---

## 🚀 Frontier Capabilities

EvoAlgo incorporates 5 frontier evolutionary and systems design patterns:

### 1. 🗺️ MAP-Elites Behavioral Archive (Multi-Dimensional Diversity)
Instead of collapsing all candidates into a single scalar or 1D leaderboard, EvoAlgo constructs a multi-dimensional behavioral feature grid (e.g. *Memory Overhead $\times$ Code Complexity $\times$ Strategy Family*). Each niche cell stores only the highest-fitness individual for that specific behavior, ensuring the population never converges prematurely.

### 2. 🦹 Co-Evolutionary Adversarial Workload Fuzzing
Humans write predictable benchmarks (pure Zipfian, linear scans). EvoAlgo co-evolves a secondary population of **Adversarial Access Traces** that specifically mutate to maximize miss rates against the current elite algorithms, hunting down pathological thrashing edge cases.

### 3. 🎯 Multi-Armed Bandit (MAB) Adaptive Mutation Router
Rather than uniform mutation probabilities, a Thompson Sampling / MAB controller tracks which mutation operators (Optimization, Structural, Algorithmic, Crossover) yield surviving offspring at generation $g$ and dynamically adapts selection probabilities.

### 4. ⚡ Fast-Path Pre-Execution Filtering (<10ms Gating)
Before launching full subprocess sandbox simulations, a lightweight static and AST analyzer verifies interface adherence, checks cyclic invariants, and filters out dead or trivial algorithms.

### 5. ⚙️ Native Code Compilation / Export Pipeline (Python $\to$ C++20)
Symbolic algorithms are discovered in readable Python, but top Pareto/MAP-Elites performers are exported and compiled directly to C++20 for microsecond-scale production deployment (e.g., Redis, RocksDB, or custom storage engines).

---

## 🔬 Research Wedges: Systems & AI/ML Systems

EvoAlgo's discovery engine is designed to span both core systems and AI/ML infrastructure:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                EVOALGO RESEARCH WEDGES                                  │
├─────────────────────────────────────────┬───────────────────────────────────────────────┤
│        Track A: Systems Infrastructure  │         Track B: AI/ML & LLM Systems          │
├─────────────────────────────────────────┼───────────────────────────────────────────────┤
│ • Cache Replacement Policies (LRU/ARC)  │ • LLM KV Cache Eviction & Compression         │
│ • Task & Thread Scheduling (Work stealing)│ • Mixture-of-Experts (MoE) Token Routing    │
│ • Storage & Buffer Pool Managers        │ • Speculative Decoding Acceptance Trees       │
│ • Lockless Memory Allocators            │ • Symbolic Optimizers & LR Schedulers (Lion)  │
│ • Compression Dictionary Selectors      │ • Dynamic Sparse Attention Skip-Masks         │
└─────────────────────────────────────────┴───────────────────────────────────────────────┘
```

---

## 🔄 The Evolutionary Loop

```
                         ┌───────────────────┐
                         │   Problem Spec    │
                         │   "Optimize X"    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Problem Analyzer  │
                         │  - constraints    │
                         │  - objectives     │
                         │  - test harness   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                   ┌─────────────────────────────┐
                   │     Initial Population      │
                   │  Baselines + LLM Seeds      │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                       ┌───────────────────┐
                       │    COMPILER       │
                       │ syntax/type/AST   │
                       └─────────┬─────────┘
                                 │
                         ┌───────┴────────┐
                         │                │
                       FAIL              PASS
                         │                │
                         ▼                ▼
                      Discard       Correctness
                                      Testing
                                         │
                                         ▼
                                   Workload Sim
                                  & Benchmarking
                                         │
                                         ▼
                               ┌────────────────┐
                               │   Evaluator    │
                               │  - correctness │
                               │  - hit/speedup │
                               │  - memory      │
                               │  - latency     │
                               └───────┬────────┘
                                       │
                                       ▼
                               ┌────────────────┐
                               │   Population   │
                               │    Archive     │
                               │ (Pareto Front) │
                               └───────┬────────┘
                                       │
                                       ▼
                                   SELECTION
                               (NSGA-II Crowding)
                                       │
                                       ▼
                              ┌──────────────────┐
                              │     MUTATION     │
                              │  - Optimization  │
                              │  - Structural    │
                              │  - Algorithmic   │
                              │  - Crossover     │
                              └────────┬─────────┘
                                       │
                                       ▼
                                    REPEAT
```

---

## 🧬 The Algorithm as an Organism

EvoAlgo decouples an algorithm into its internal representation (**Genotype**) and its real-world execution characteristics (**Phenotype**):

```
                   Algorithm Individual
                            │
         ┌──────────────────┴──────────────────┐
         ▼                                     ▼
      Genotype                              Phenotype
 ┌─────────────────┐                   ┌─────────────────┐
 │ • Source Code   │                   │ • Hit Ratio     │
 │ • AST Structure │ ──[ Evaluator ]──►│ • Latency (p99) │
 │ • Heuristic DNA │                   │ • Memory Footprint│
 │ • Data Structs  │                   │ • CPU Cycles    │
 └─────────────────┘                   └─────────────────┘
```

### The Algorithm Genome Specification
```json
{
  "id": "cand_gen14_isl2_008",
  "generation": 14,
  "island": "heuristic_decay",
  "strategy": "frequency_decay_with_ghost_cache",
  "data_structures": ["doubly_linked_list", "hash_map", "bloom_filter"],
  "heuristics": ["exponential_recency_decay", "reuse_distance_prediction"],
  "complexity": {
    "lookup": "O(1)",
    "eviction": "O(1)",
    "space": "O(K)"
  }
}
```

---

## 🔬 Mutation & Crossover Operators

The LLM is prompted via targeted operator templates rather than generic open-ended instructions:

| Operator | Target | Description |
| :--- | :--- | :--- |
| **Mutation A — Optimization** | Performance | Streamlines loops, reduces dictionary allocations, and eliminates redundant branches without changing algorithmic logic. |
| **Mutation B — Algorithmic** | Strategy | Discovers a fundamentally different algorithmic approach (e.g., swapping a static frequency counter for an adaptive windowed decay). |
| **Mutation C — Structural** | Data Structures | Replaces the core backing collections (e.g., replaces an $O(N)$ linear search with an $O(\log K)$ segmented LRU or count-min sketch). |
| **Mutation D — Simplification** | Maintainability | Prunes redundant edge-case branches and dead state while enforcing zero regression in fitness. |
| **Mutation E — Crossover** | Synthesis | Recombines two high-performing parents (e.g., Parent A's scan resistance + Parent B's frequency tracking) into a novel hybrid child. |

---

## 🏝️ Population Dynamics & Island Model

A single homogeneous population quickly converges to a local optimum. EvoAlgo implements an **Island Topology with Speciation**:

```
                       Global Archive / MAP-Elites Grid
                                     ▲
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
                 ▼                   ▼                   ▼
          ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
          │  Island A   │◄───►│  Island B   │◄───►│  Island C   │
          │ Recency-led │     │Frequency-led│     │ Adaptive/ML │
          └─────────────┘     └─────────────┘     └─────────────┘
                 ▲                   ▲                   ▲
                 │                   │                   │
          [Greedy Mut.]       [Sketch Mut.]       [Hybrid Mut.]
```

* **Speciation**: Each island is seeded with distinct paradigms and guided by specialized prompts.
* **Migration Policy**: Every $N$ generations, top non-dominated candidates from each island migrate to adjacent islands.

---

## 📊 The Evaluator & Pareto Frontier

EvoAlgo evaluates candidates across multiple objectives using **NSGA-II** principles:

$$\vec{F} = \Big( \text{Correctness } (\%), \text{Hit Ratio } (\%), -\text{Eviction Latency } (\mu\text{s}), -\text{Memory Overhead } (\text{KB}) \Big)$$

```
Eviction Latency
   ▲
   │        ● Candidate A (Fastest latency, moderate hit rate)
   │
   │            ● Candidate B (Balanced)
   │
   │                    ● Candidate C (Highest hit rate, complex metadata)
   └─────────────────────────────────────► Cache Hit Ratio
```

Candidates on the **Pareto Frontier** and **MAP-Elites cells** are preserved in the Global Archive, guaranteeing diversity across both ultra-low-latency and maximum-efficiency regimes.

---

## ⚡ Flagship Pilot Problem: Cache Replacement (Tier 1)

Why Cache Replacement over standard Sorting?
1. **Determinism**: Fully reproducible simulated workloads with discrete step counters.
2. **Clear Baselines**: LRU, FIFO, LFU, 2Q, ARC.
3. **Rich Algorithmic Space**: Frequency, recency, ghost caches, bloom filters, and adaptive decay curves.
4. **Systems Relevance**: Direct bridge into systems infrastructure and downstream LLM KV-cache eviction.

### Workload Suite
- **Workload A (Zipfian)**: Skewed access patterns modeling web traffic and key-value stores.
- **Workload B (Sequential Scan)**: Large linear scans testing cache pollution resistance.
- **Workload C (Cyclic / Loop)**: Working set slightly larger than capacity (tests LRU thrashing).
- **Workload D (Phase Shift)**: Sudden distribution change from one cluster of keys to another.
- **Workload E (Bursty)**: High-frequency bursts of temporal access interspersed with random noise.
- **Workload F (Adversarial Fuzzer)**: Co-evolved synthetic access patterns designed to induce thrashing.

---

## 🛡️ Generalization: Train vs. Hidden Workloads

To prevent the LLM from overfitting or hardcoding heuristics to a specific synthetic trace:

```
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│       TRAINING WORKLOADS             │       │      HIDDEN VALIDATION WORKLOADS     │
│   (Used during evolutionary loop)    │       │     (Evaluated post-generation)      │
├──────────────────────────────────────┤       ├──────────────────────────────────────┤
│ • Zipfian Trace (alpha = 0.8)        │  ──►  │ • Zipfian Trace (alpha = 1.2)        │
│ • Sequential Scan (2x Cache Size)    │       │ • Multi-tenant Interleaved Scans     │
│ • Fixed Cyclic Loop                  │       │ • Dynamic Phase Shift Workload       │
└──────────────────────────────────────┘       └──────────────────────────────────────┘
```

The system measures the **Generalization Gap**:
$$\Delta_{\text{gen}} = \text{Fitness}_{\text{train}} - \text{Fitness}_{\text{val}}$$

---

## 🏗️ System Architecture

```
                                 ┌──────────────────┐
                                 │   Web Dashboard  │
                                 │  Next.js / React │
                                 └────────┬─────────┘
                                          │ WebSocket / REST
                                          ▼
                                 ┌──────────────────┐
                                 │   API Gateway    │
                                 │     FastAPI      │
                                 └────────┬─────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        │                                   │
                        ▼                                   ▼
             ┌─────────────────────┐             ┌─────────────────────┐
             │  Evolution Engine   │             │   Experiment Store  │
             │ (Async Orchestrator)│             │  PostgreSQL / SQLite│
             └──────────┬──────────┘             └─────────────────────┘
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Generator  │  │  Evaluator  │  │  Selector   │
│  • LLM API  │  │  • Runner   │  │  • NSGA-II  │
│  • Prompts  │  │  • Sandbox  │  │  • MAP-Elite│
│  • Parsers  │  │  • Profiler │  │  • Migrator │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## 📁 Repository Structure

```
EvoAlgo/
├── engine/
│   ├── core/                  # Genotype, Phenotype, Individual, Population
│   │   ├── genome.py
│   │   ├── individual.py
│   │   ├── map_elites.py      # Quality-diversity feature grid
│   │   └── population.py
│   ├── evolution/             # Evolutionary operators & dynamics
│   │   ├── selection.py       # Pareto ranking, NSGA-II crowding distance
│   │   ├── mutation.py        # 4 mutation operators + prompt dispatch
│   │   ├── bandit.py          # Thompson Sampling mutation router
│   │   ├── crossover.py       # Two-parent hybrid synthesis
│   │   └── islands.py         # Multi-island topology & migration schedules
│   ├── evaluator/             # Multi-tier verification & execution harness
│   │   ├── runner.py          # Secure subprocess runner with limits
│   │   ├── correctness.py     # Invariant tests & smoke checks
│   │   ├── fitness.py         # Multi-objective scoring
│   │   └── profiler.py        # Micro-benchmarks, latency, memory profiling
│   ├── generator/             # LLM interface & prompt engineering
│   │   ├── llm_client.py      # Multi-provider client (Gemini, Claude, OpenAI)
│   │   ├── prompts.py         # Operator-specific prompt templates
│   │   └── parser.py          # AST extraction and code sanitization
│   └── storage/               # Persistent lineage and experiment logs
│       ├── database.py
│       └── models.py
├── problems/
│   ├── base.py                # Abstract BaseProblem interface
│   ├── cache_replacement/     # Flagship Pilot Domain (Tier 1)
│   │   ├── problem.py
│   │   ├── simulator.py
│   │   ├── workloads.py       # Synthetic, trace, and adversarial generators
│   │   └── baselines/         # FIFO, LRU, LFU, ARC
│   └── llm_kv_cache/          # LLM Systems Domain (Tier 2)
│       ├── problem.py
│       ├── attention_trace.py # Attention score traces from LLaMA/Mistral
│       └── baselines/         # StreamingLLM, H2O, SnapKV
├── experiments/
│   ├── configs/               # YAML experiment definitions
│   └── runs/                  # Artifact logs and metrics
├── docs/
│   ├── ARCHITECTURE.md        # In-depth architectural design specification
│   └── HARNESS_SPEC.md        # Evaluator sandbox & benchmark harness protocol
├── pyproject.toml
└── README.md
```

---

## 🗺️ Phased Roadmap

- [x] **Phase 0: Specifications & First Principles**
  - Problem Statement, Architecture Blueprint, Frontier Capabilities, AI/ML Wedges, and Harness Specifications.
- [ ] **Phase 1: Tier 1 Problem Harness (Cache Replacement Ground Truth)**
  - `BaseProblem` abstraction, Cache Replacement simulator, multi-distribution workload suite, adversarial fuzzer, and baselines (FIFO, LRU, LFU, ARC).
- [ ] **Phase 2: Evaluator Pipeline & Sandboxed Runner**
  - Subprocess runner with hard CPU/memory/timeout limits, syntax validation, invariant test suite, and fitness metrics calculation.
- [ ] **Phase 3: LLM Mutation Engine & Code Parser**
  - Multi-provider LLM interface (Gemini / Anthropic / OpenAI), 5 mutation prompt operators, Thompson Sampling bandit dispatcher, and robust code-block AST parser.
- [ ] **Phase 4: Evolutionary Core, MAP-Elites & Island Topology**
  - Population management, Pareto frontier archive, MAP-Elites behavioral grid, NSGA-II selection, and multi-island migration loop.
- [ ] **Phase 5: Tier 1 Flagship Experiment & Laboratory Dashboard**
  - Complete 20-generation evolutionary run on cache replacement, lineage tree visualization, and code diff trajectory tracking.
- [ ] **Phase 6: Tier 2 AI/ML Wedge (LLM KV-Cache Eviction Discovery)**
  - Dynamic token retention heuristic discovery tested against real attention weight matrices.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
