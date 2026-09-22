"""
EvoAlgo Base Problem Abstraction.
Defines contracts for all benchmark domains, objectives, and evaluation reports.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class ProblemSpec(BaseModel):
    name: str
    tier: str = Field(description="Category tier, e.g. tier_1_systems or tier_2_ai_systems")
    description: str
    target_interface: str
    objective_names: List[str]
    objective_directions: List[str]  # "maximize" or "minimize"


class WorkloadMetric(BaseModel):
    workload_name: str
    total_requests: int
    hits: int
    misses: int
    hit_ratio: float
    evictions: int
    elapsed_time_ms: float
    avg_latency_us: float


class EvaluationReport(BaseModel):
    individual_id: str
    domain: str
    passed_fast_gate: bool = True
    passed_invariants: bool = False
    error_message: Optional[str] = None
    train_metrics: List[WorkloadMetric] = Field(default_factory=list)
    validation_metrics: List[WorkloadMetric] = Field(default_factory=list)
    overall_train_hit_ratio: float = 0.0
    overall_val_hit_ratio: float = 0.0
    generalization_gap: float = 0.0  # train_hit_ratio - val_hit_ratio
    p99_latency_us: float = 0.0
    peak_memory_kb: float = 0.0


class BaseProblem(ABC):
    """Abstract base class that all discovery domains must implement."""

    @abstractmethod
    def get_spec(self) -> ProblemSpec:
        """Returns metadata, interface contract, and objective definitions."""
        pass

    @abstractmethod
    def get_baselines(self) -> Dict[str, str]:
        """Returns baseline source code implementations (e.g. {'LRU': code, 'FIFO': code})."""
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
    def run_training_evaluation(self, candidate_class: Any, individual_id: str = "unknown") -> EvaluationReport:
        """Tier 3: Executes candidate against training workload distributions."""
        pass

    @abstractmethod
    def run_validation_evaluation(self, candidate_class: Any, individual_id: str = "unknown") -> EvaluationReport:
        """Tier 3 (Held-out): Executes candidate against unseen validation distributions."""
        pass
