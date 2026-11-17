"""Shared contracts for N-Queens solvers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterator


class SolverEventType(str, Enum):
    """Events emitted while a solver explores the search space."""

    PLACE_QUEEN = "place"
    REJECT_POSITION = "reject"
    BACKTRACK = "backtrack"
    SOLUTION_FOUND = "solution"
    MOVE_QUEEN = "move"
    RESTART = "restart"

    # Compatibility aliases for callers of the original solver contract.
    TRY_POSITION = "place"
    REMOVE_QUEEN = "backtrack"
    SEARCH_COMPLETED = "solution"


@dataclass(frozen=True)
class SolverEvent:
    """A single visualization-friendly search event."""

    event_type: SolverEventType
    row: int
    column: int | None = None
    solution: tuple[int, ...] | None = None
    reason: str | None = None
    from_column: int | None = None
    blocked_row: int | None = None
    conflicts: int | None = None


@dataclass
class SolverStatistics:
    """Counters collected consistently by every solver."""

    recursive_calls: int = 0
    attempted_placements: int = 0
    valid_placements: int = 0
    backtracking_operations: int = 0
    search_nodes: int = 0
    maximum_recursion_depth: int = 0
    solutions_found: int = 0
    moves: int = 0
    restarts: int = 0
    elapsed_time: float = 0.0

    def reset(self) -> None:
        """Reset all counters before a new search."""
        for field_name in self.__dataclass_fields__:
            setattr(self, field_name, 0)


class NQueensSolver(ABC):
    """Abstract interface used by algorithms and future benchmarks."""

    def __init__(self, size: int) -> None:
        if not isinstance(size, int) or isinstance(size, bool) or size < 1:
            raise ValueError("board size must be a positive integer")
        self.size = size
        self._solution: tuple[int, ...] | None = None
        self._statistics = SolverStatistics()

    def solve(self, *, find_all: bool = False) -> list[tuple[int, ...]]:
        """Run the search without retaining visualization events."""
        return [
            event.solution
            for event in self.solve_events(find_all=find_all)
            if event.event_type is SolverEventType.SOLUTION_FOUND
            and event.solution is not None
        ]

    @abstractmethod
    def solve_events(
        self,
        *,
        find_all: bool = False,
        max_events: int | None = None,
        time_limit_seconds: float | None = None,
    ) -> Iterator[SolverEvent]:
        """Yield search events without coupling the solver to a GUI."""

    @staticmethod
    def _validate_limits(
        max_events: int | None, time_limit_seconds: float | None
    ) -> None:
        if max_events is not None and (
            not isinstance(max_events, int) or max_events < 0
        ):
            raise ValueError("max_events must be a non-negative integer or None")
        if time_limit_seconds is not None and time_limit_seconds <= 0:
            raise ValueError("time_limit_seconds must be positive or None")

    def solve_one(self) -> tuple[int, ...] | None:
        """Return the first solution, if one exists."""
        solutions = self.solve(find_all=False)
        return solutions[0] if solutions else None

    def solve_all(self) -> list[tuple[int, ...]]:
        """Return every solution for the current board size."""
        return self.solve(find_all=True)

    def get_statistics(self) -> SolverStatistics:
        """Return a snapshot of the latest search statistics."""
        return SolverStatistics(**vars(self._statistics))

    def get_solution(self) -> tuple[int, ...] | None:
        """Return the most recently found first solution."""
        return self._solution

    def get_execution_time(self) -> float:
        """Return the latest search duration in seconds."""
        return self._statistics.elapsed_time
