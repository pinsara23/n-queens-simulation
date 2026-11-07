"""Reference recursive N-Queens backtracking solver."""

from __future__ import annotations

from time import perf_counter
from typing import Iterator

from .base_solver import (
    NQueensSolver,
    SolverEvent,
    SolverEventType,
)


class BacktrackingSolver(NQueensSolver):
    """Place one queen per row and scan prior rows for conflicts."""

    def solve(
        self, *, find_all: bool = False
    ) -> list[tuple[int, ...]]:
        """Run the search without retaining visualization events."""
        solutions: list[tuple[int, ...]] = []
        for event in self.solve_events(find_all=find_all):
            if event.event_type is SolverEventType.SOLUTION_FOUND:
                if event.solution is not None:
                    solutions.append(event.solution)
        return solutions

    def solve_events(
        self,
        *,
        find_all: bool = False,
        max_events: int | None = None,
        time_limit_seconds: float | None = None,
    ) -> Iterator[SolverEvent]:
        """Yield events while recursively exploring candidate positions."""
        if max_events is not None and (
            not isinstance(max_events, int) or max_events < 0
        ):
            raise ValueError("max_events must be a non-negative integer or None")
        if time_limit_seconds is not None and time_limit_seconds <= 0:
            raise ValueError("time_limit_seconds must be positive or None")

        self._statistics.reset()
        self._solution = None
        start = perf_counter()
        board = [-1] * self.size
        event_count = 0
        deadline = (
            start + time_limit_seconds
            if time_limit_seconds is not None
            else None
        )
        timed_out = False

        def emit(event: SolverEvent) -> Iterator[SolverEvent]:
            nonlocal event_count
            if max_events is None or event_count < max_events:
                event_count += 1
                yield event

        def search(row: int) -> Iterator[SolverEvent]:
            nonlocal timed_out
            if deadline is not None and perf_counter() >= deadline:
                timed_out = True
                return
            self._statistics.recursive_calls += 1
            self._statistics.search_nodes += 1
            self._statistics.maximum_recursion_depth = max(
                self._statistics.maximum_recursion_depth, row
            )

            if row == self.size:
                solution = tuple(board)
                self._statistics.solutions_found += 1
                if self._solution is None:
                    self._solution = solution
                yield from emit(
                    SolverEvent(
                        SolverEventType.SOLUTION_FOUND,
                        row=row,
                        solution=solution,
                    )
                )
                return

            for column in range(self.size):
                if deadline is not None and perf_counter() >= deadline:
                    timed_out = True
                    return
                self._statistics.attempted_placements += 1
                if not self._is_safe(board, row, column):
                    yield from emit(
                        SolverEvent(
                            SolverEventType.REJECT_POSITION,
                            row,
                            column,
                            reason=self._conflict_reason(board, row, column),
                        )
                    )
                    continue

                self._statistics.valid_placements += 1
                board[row] = column
                yield from emit(
                    SolverEvent(SolverEventType.PLACE_QUEEN, row, column)
                )

                before = self._statistics.solutions_found
                yield from search(row + 1)
                found_solution = self._statistics.solutions_found > before

                board[row] = -1
                if not found_solution:
                    self._statistics.backtracking_operations += 1
                    yield from emit(
                        SolverEvent(SolverEventType.BACKTRACK, row, column)
                    )
                if found_solution and not find_all:
                    return

        yield from search(0)
        self._statistics.elapsed_time = perf_counter() - start

    @staticmethod
    def _is_safe(board: list[int], row: int, column: int) -> bool:
        """Check column and diagonal conflicts against prior rows."""
        for previous_row in range(row):
            previous_column = board[previous_row]
            if previous_column == column:
                return False
            if abs(previous_row - row) == abs(previous_column - column):
                return False
        return True

    @staticmethod
    def _conflict_reason(
        board: list[int], row: int, column: int
    ) -> str | None:
        """Return the first truthful conflict category for a candidate."""
        for previous_row in range(row):
            previous_column = board[previous_row]
            if previous_column == column:
                return "column"
            if abs(previous_row - row) == abs(previous_column - column):
                return "diagonal"
        return None
