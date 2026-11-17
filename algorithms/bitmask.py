"""Bitmask backtracking: the same search, with O(1) conflict tests."""

from __future__ import annotations

from time import perf_counter
from typing import Iterator

from .base_solver import NQueensSolver, SolverEvent, SolverEventType


class BitmaskSolver(NQueensSolver):
    """Row-by-row backtracking that tracks attacked squares in three integers.

    ``cols``, ``diag_left`` and ``diag_right`` hold one bit per column of the
    current row. Their union is every attacked square, so the free squares are
    ``~(cols | diag_left | diag_right)`` and attacked columns are never tried.
    That is why this solver emits no ``reject`` events: it skips them instead.
    Columns are tried from 0 upward, so the first solution matches
    ``BacktrackingSolver``.
    """

    def solve_events(
        self,
        *,
        find_all: bool = False,
        max_events: int | None = None,
        time_limit_seconds: float | None = None,
    ) -> Iterator[SolverEvent]:
        self._validate_limits(max_events, time_limit_seconds)
        self._statistics.reset()
        self._solution = None
        start = perf_counter()
        deadline = start + time_limit_seconds if time_limit_seconds else None
        size = self.size
        full = (1 << size) - 1
        board = [-1] * size
        event_count = 0

        def emit(event: SolverEvent) -> Iterator[SolverEvent]:
            nonlocal event_count
            if max_events is None or event_count < max_events:
                event_count += 1
                yield event

        def search(
            row: int, cols: int, diag_left: int, diag_right: int
        ) -> Iterator[SolverEvent]:
            stats = self._statistics
            stats.recursive_calls += 1
            stats.search_nodes += 1
            stats.maximum_recursion_depth = max(stats.maximum_recursion_depth, row)

            if row == size:
                solution = tuple(board)
                stats.solutions_found += 1
                if self._solution is None:
                    self._solution = solution
                yield from emit(
                    SolverEvent(SolverEventType.SOLUTION_FOUND, row, solution=solution)
                )
                return

            free = full & ~(cols | diag_left | diag_right)
            while free:
                if deadline is not None and perf_counter() >= deadline:
                    return
                bit = free & -free  # lowest free column
                free ^= bit
                column = bit.bit_length() - 1
                stats.attempted_placements += 1
                stats.valid_placements += 1
                board[row] = column
                yield from emit(SolverEvent(SolverEventType.PLACE_QUEEN, row, column))

                before = stats.solutions_found
                yield from search(
                    row + 1,
                    cols | bit,
                    ((diag_left | bit) << 1) & full,
                    (diag_right | bit) >> 1,
                )
                found = stats.solutions_found > before
                board[row] = -1
                if not found:
                    stats.backtracking_operations += 1
                    yield from emit(
                        SolverEvent(SolverEventType.BACKTRACK, row, column)
                    )
                elif not find_all:
                    return

        yield from search(0, 0, 0, 0)
        self._statistics.elapsed_time = perf_counter() - start
