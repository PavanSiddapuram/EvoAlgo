# 🧬 EvoAlgo: LLM-Driven Evolutionary Algorithm Discovery System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Active Development](https://img.shields.io/badge/status-pre--alpha-orange.svg)]()

> **"Don't ask an LLM to write a better algorithm. Treat the algorithm as an organism, and use the LLM as the mutation operator."**

EvoAlgo is an evolutionary coding framework where Large Language Models (LLMs) act as guided mutation and crossover operators across an evolving population of algorithmic candidates. Candidates are continuously compiled, executed inside an isolated sandbox, benchmarked against multi-distribution workload suites, and ranked using multi-objective Pareto optimization.

---

## Table of Contents
- [Problem Statement](#-problem-statement)
- [The Core Thesis: First Principles](#-the-core-thesis-first-principles)
- [The Evolutionary Loop](#-the-evolutionary-loop)
- [The Algorithm as an Organism](#-the-algorithm-as-an-organism)
- [Mutation & Crossover Operators](#-mutation--crossover-operators)
- [Population Dynamics & Island Model](#-population-dynamics--island-model)
- [The Evaluator & Pareto Frontier](#-the-evaluator--pareto-frontier)
- [Flagship Pilot Problem: Cache Replacement](#-flagship-pilot-problem-cache-replacement)
- [Generalization: Train vs. Hidden Workloads](#-generalization-train-vs-hidden-workloads)
- [System Architecture](#-system-architecture)
- [Repository Structure](#-repository-structure)
- [Roadmap](#-roadmap)

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
  │    • Pareto Non-Domination       • Multi-Workload Suite │
  │    • Cross-Gen Migration         • Profiling & Counters │
  └────────────────────────────┬────────────────────────────┘
                               │
                               ▼
               Discovered High-Performing Policy
```

1. **The LLM provides semantic-preserving code mutations**: Instead of random token flips, the LLM makes structured edits with full awareness of program logic, invariants, and syntax.
2. **Evolutionary search navigates high-dimensional trade-offs**: By keeping a diverse population across multiple islands, the system avoids local optima and preserves promising sub-heuristics.
3. **The sandbox enforces ground truth**: No hallucinated speedups survive. The evaluator measures exact cache hit rates, CPU cycles, and memory overheads.

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

A single homogeneous population quickly converges to a local optimum (e.g., everyone mutates around standard LRU). EvoAlgo implements an **Island Topology with Speciation**:

```
                       Global Archive / Pareto Front
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
* **Migration Policy**: Every $N$ generations, the top $k$ non-dominated candidates from each island migrate to adjacent islands, breaking local plateaus.

---

## 📊 The Evaluator & Pareto Frontier

Real algorithms involve trade-offs. EvoAlgo evaluates candidates across multiple objectives using **NSGA-II** (Non-dominated Sorting Genetic Algorithm II) principles:

$$\text{Objective Vector } \vec{F} = \Big( \text{Correctness } (\%), \text{Hit Ratio } (\%), -\text{Eviction Latency } (\mu\text{s}), -\text{Memory Overhead } (\text{KB}) \Big)$$

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

A candidate $A$ dominates $B$ ($A \succ B$) if:
$$\forall i \in \{1,\dots,m\}, \quad F_i(A) \ge F_i(B) \quad \land \quad \exists j \in \{1,\dots,m\}, \quad F_j(A) > F_j(B)$$

Candidates on the **Pareto Frontier** are preserved in the Global Archive, guaranteeing diversity across both ultra-low-latency and maximum-efficiency regimes.

---

## ⚡ Flagship Pilot Problem: Cache Replacement

Why Cache Replacement over standard Sorting?
1. **Determinism**: Fully reproducible simulated workloads with discrete step counters.
2. **Clear Baselines**: LRU, FIFO, LFU, 2Q, ARC.
3. **Rich Algorithmic Space**: Frequency, recency, ghost caches, bloom filters, and adaptive decay curves.
4. **Systems Relevance**: Directly mirrors real-world optimization problems solved in systems infrastructure (e.g., Google AlphaEvolve cache policies).

### Workload Suite
- **Workload A (Zipfian)**: Skewed access patterns modeling web traffic and key-value stores.
- **Workload B (Sequential Scan)**: Large linear scans testing cache pollution resistance.
- **Workload C (Cyclic / Loop)**: Working set slightly larger than capacity (tests LRU thrashing).
- **Workload D (Phase Shift)**: Sudden distribution change from one cluster of keys to another.
- **Workload E (Bursty)**: High-frequency bursts of temporal access interspersed with random noise.

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
Candidates with high $\Delta_{\text{gen}}$ are penalized to favor robust, general-purpose policies over brittle overfits.

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
│  • Prompts  │  │  • Sandbox  │  │  • Archive  │
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
│   │   └── population.py
│   ├── evolution/             # Evolutionary operators & dynamics
│   │   ├── selection.py       # Pareto ranking, NSGA-II crowding distance
│   │   ├── mutation.py        # 4 mutation operators + prompt dispatch
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
│   ├── cache_replacement/     # Flagship Pilot Domain
│   │   ├── problem.py
│   │   ├── simulator.py
│   │   ├── workloads.py       # Synthetic and real-world trace generators
│   │   └── baselines/         # FIFO, LRU, LFU, ARC
│   └── sorting/               # Sanity Verification Domain
│       ├── problem.py
│       └── baselines/         # Bubble, Insertion, Quick, Merge
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

## 🗺️ Roadmap

- [x] **Phase 0: Specifications & First Principles**
  - Problem Statement, Architecture Blueprint, and Harness Specifications.
- [ ] **Phase 1: Problem Harness & Simulator Ground Truth**
  - `BaseProblem` abstraction, Cache Replacement simulator, workload generator suite (Zipf, Scans, Phase-shifts), and baseline implementations (FIFO, LRU, LFU).
- [ ] **Phase 2: Evaluator Pipeline & Sandboxed Runner**
  - Subprocess runner with hard CPU/memory/timeout limits, syntax validation, invariant test suite, and fitness metrics calculation.
- [ ] **Phase 3: LLM Mutation Engine & Code Parser**
  - Multi-provider LLM interface (Gemini / Anthropic / OpenAI), 5 mutation prompt operators, and robust code-block AST parser.
- [ ] **Phase 4: Evolutionary Core & Island Topology**
  - Population management, Pareto frontier archive, NSGA-II selection, and multi-island migration loop.
- [ ] **Phase 5: Flagship Experiment & Laboratory Dashboard**
  - Complete 20-generation evolutionary run on cache replacement, lineage tree visualization, and code diff trajectory tracking.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
