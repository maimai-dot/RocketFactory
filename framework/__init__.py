"""
Σ (Sigma) — PDCA 多智能体协同框架

Backward-compatible re-exports from the sigma package.
框架已解耦为独立 pip 包 (D:\\sigma\\)，此处保留兼容导出。
"""

from sigma.state import SharedState, StateManager, ConsensusEstimate, ComplexityTier, ComplexityAssessment
from sigma.convergence import ConvergenceJudge, Verdict
from sigma.triggers import TriggerSystem, Trigger
from sigma.cost_tracker import CostTracker
from sigma.protocol import SigmaProtocol
from sigma.orchestrator import SigmaOrchestrator

__all__ = [
    "SharedState",
    "StateManager",
    "ConsensusEstimate",
    "ComplexityTier",
    "ComplexityAssessment",
    "ConvergenceJudge",
    "Verdict",
    "TriggerSystem",
    "Trigger",
    "CostTracker",
    "SigmaProtocol",
    "SigmaOrchestrator",
]
