"""N-Queens solver implementations."""

from .base_solver import SolverEvent, SolverEventType, SolverStatistics
from .backtracking import BacktrackingSolver

__all__ = [
    "BacktrackingSolver",
    "SolverEvent",
    "SolverEventType",
    "SolverStatistics",
]
