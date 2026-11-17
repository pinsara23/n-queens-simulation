"""Backtracking with forward checking and the MRV heuristic."""

from __future__ import annotations

from time import perf_counter
from typing import Iterator

from .base_solver import NQueensSolver, SolverEvent, SolverEventType


class ForwardCheckingSolver(NQueensSolver):
    """Constraint-satisfaction search over per-row domains.

    Each unassigned row keeps a bitmask *domain* of columns that are still
    safe. Placing a queen removes the squares it attacks from every other
    unassigned row. A candidate is rejected with reason ``dead_end`` when that
    would leave some row (``blocked_row``) with no squares, without recursing
    into the subtree.

    The next row to fill is the unassigned row with the fewest legal columns
    (minimum remaining values, ties broken by the lowest row index). This means
    rows are **not** filled top to bottom, unlike the other exact solvers.
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

        def prune(
            domains: dict[int, int], row: int, column: int
        ) -> tuple[dict[int, int], int | None]:
            """Return domains after placing (row, column) and any emptied row."""
            pruned: dict[int, int] = {}
            for other, domain in domains.items():
                distance = abs(other - row)
                attacked = 1 << column
                if column - distance >= 0:
                    attacked |= 1 << (column - distance)
                if column + distance < size:
                    attacked |= 1 << (column + distance)
                remaining = domain & ~attacked
                if not remaining:
                    return pruned, other
                pruned[other] = remaining
            return pruned, None

        def search(domains: dict[int, int], depth: int) -> Iterator[SolverEvent]:
            stats = self._statistics
            stats.recursive_calls += 1
            stats.search_nodes += 1
            stats.maximum_recursion_depth = max(stats.maximum_recursion_depth, depth)

            if not domains:
                solution = tuple(board)
                stats.solutions_found += 1
                if self._solution is None:
                    self._solution = solution
                yield from emit(
                    SolverEvent(SolverEventType.SOLUTION_FOUND, depth, solution=solution)
                )
                return

            row = min(domains, key=lambda r: (domains[r].bit_count(), r))
            free = domains[row]
            rest = {r: d for r, d in domains.items() if r != row}
            while free:
                if deadline is not None and perf_counter() >= deadline:
                    return
                bit = free & -free
                free ^= bit
                column = bit.bit_length() - 1
                stats.attempted_placements += 1

                pruned, blocked = prune(rest, row, column)
                if blocked is not None:
                    yield from emit(
                        SolverEvent(
                            SolverEventType.REJECT_POSITION,
                            row,
                            column,
                            reason="dead_end",
                            blocked_row=blocked,
                        )
                    )
                    continue

                stats.valid_placements += 1
                board[row] = column
                yield from emit(SolverEvent(SolverEventType.PLACE_QUEEN, row, column))

                before = stats.solutions_found
                yield from search(pruned, depth + 1)
                found = stats.solutions_found > before
                if found and not find_all:
                    return
                # Rows are visited out of order, so a viewer cannot infer which
                # queens were lifted. Always report the removal, even after a
                # solution, unlike the row-ordered solvers.
                board[row] = -1
                stats.backtracking_operations += 1
                yield from emit(SolverEvent(SolverEventType.BACKTRACK, row, column))

        yield from search({row: full for row in range(size)}, 0)
        self._statistics.elapsed_time = perf_counter() - start
