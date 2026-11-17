"""Min-conflicts local search for finding a single solution quickly."""

from __future__ import annotations

import random
from time import perf_counter
from typing import Iterator

from .base_solver import NQueensSolver, SolverEvent, SolverEventType


class MinConflictsSolver(NQueensSolver):
    """Repair a full board until no queens attack each other.

    1. Place one queen per row, greedily choosing a least-attacked column
       (``place`` events).
    2. Repeatedly pick a random attacked queen and move it within its row to a
       least-attacked column (``move`` events carry ``from_column`` and the
       board's remaining attacking-pair count in ``conflicts``).
    3. If a round runs out of moves, clear the board and start again
       (a ``restart`` event).

    This scales to very large boards, but it is incomplete: it finds at most
    one solution, may differ from run to run unless ``seed`` is given, and can
    never prove that a board has no solution. Sizes 2 and 3, which have none,
    are answered immediately instead of searched.
    """

    def __init__(
        self,
        size: int,
        *,
        seed: int | None = None,
        max_restarts: int = 50,
        moves_per_restart: int | None = None,
    ) -> None:
        super().__init__(size)
        self.seed = seed
        self.max_restarts = max_restarts
        self.moves_per_restart = moves_per_restart or max(100, 4 * size)

    def solve_events(
        self,
        *,
        find_all: bool = False,
        max_events: int | None = None,
        time_limit_seconds: float | None = None,
    ) -> Iterator[SolverEvent]:
        # find_all is accepted for interface compatibility; local search can
        # only produce one solution.
        self._validate_limits(max_events, time_limit_seconds)
        self._statistics.reset()
        self._solution = None
        start = perf_counter()
        deadline = start + time_limit_seconds if time_limit_seconds else None
        size = self.size
        rng = random.Random(self.seed)
        stats = self._statistics
        event_count = 0

        def emit(event: SolverEvent) -> Iterator[SolverEvent]:
            nonlocal event_count
            if max_events is None or event_count < max_events:
                event_count += 1
                yield event

        def finish() -> None:
            stats.elapsed_time = perf_counter() - start

        if size in (2, 3):
            finish()
            return

        for attempt in range(self.max_restarts + 1):
            if attempt:
                stats.restarts += 1
                yield from emit(SolverEvent(SolverEventType.RESTART, 0))

            board = [-1] * size
            cols = [0] * size
            diag_down = [0] * (2 * size - 1)  # row - col + size - 1
            diag_up = [0] * (2 * size - 1)  # row + col
            pairs = 0  # number of attacking queen pairs on the board

            def attacks(row: int, column: int) -> int:
                return (
                    cols[column]
                    + diag_down[row - column + size - 1]
                    + diag_up[row + column]
                )

            def add(row: int, column: int) -> None:
                nonlocal pairs
                pairs += attacks(row, column)
                cols[column] += 1
                diag_down[row - column + size - 1] += 1
                diag_up[row + column] += 1
                board[row] = column

            def remove(row: int) -> None:
                nonlocal pairs
                column = board[row]
                cols[column] -= 1
                diag_down[row - column + size - 1] -= 1
                diag_up[row + column] -= 1
                pairs -= attacks(row, column)
                board[row] = -1

            for row in range(size):
                if deadline is not None and perf_counter() >= deadline:
                    finish()
                    return
                column = self._least_attacked(rng, size, lambda c: attacks(row, c))
                add(row, column)
                stats.search_nodes += 1
                stats.attempted_placements += 1
                stats.valid_placements += 1
                yield from emit(SolverEvent(SolverEventType.PLACE_QUEEN, row, column))

            for _ in range(self.moves_per_restart + 1):
                if pairs == 0:
                    solution = tuple(board)
                    self._solution = solution
                    stats.solutions_found = 1
                    yield from emit(
                        SolverEvent(
                            SolverEventType.SOLUTION_FOUND, size, solution=solution
                        )
                    )
                    finish()
                    return
                if deadline is not None and perf_counter() >= deadline:
                    finish()
                    return

                # A queen is attacked when another queen shares one of its lines.
                attacked_rows = [
                    r for r in range(size) if attacks(r, board[r]) > 3
                ]
                row = rng.choice(attacked_rows)
                old_column = board[row]
                remove(row)
                column = self._least_attacked(
                    rng, size, lambda c: attacks(row, c), avoid=old_column
                )
                add(row, column)
                stats.search_nodes += 1
                if column != old_column:
                    stats.moves += 1
                    yield from emit(
                        SolverEvent(
                            SolverEventType.MOVE_QUEEN,
                            row,
                            column,
                            from_column=old_column,
                            conflicts=pairs,
                        )
                    )

        finish()

    @staticmethod
    def _least_attacked(
        rng: random.Random, size: int, cost, avoid: int | None = None
    ) -> int:
        """Pick a random column of minimum cost.

        Among equally good columns, ``avoid`` (the queen's old column) is only
        chosen when nothing else ties, so the search keeps moving across
        plateaus instead of stalling in place.
        """
        best_cost = None
        best: list[int] = []
        for column in range(size):
            value = cost(column)
            if best_cost is None or value < best_cost:
                best_cost, best = value, [column]
            elif value == best_cost:
                best.append(column)
        if avoid is not None and len(best) > 1 and avoid in best:
            best.remove(avoid)
        return rng.choice(best)
