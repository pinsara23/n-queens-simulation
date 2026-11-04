"""Validation helpers shared by solvers, tests, and future GUI code."""

from __future__ import annotations

from collections.abc import Sequence


def validate_board_size(size: int) -> None:
    """Raise ``ValueError`` unless size is a positive integer."""
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        raise ValueError("board size must be a positive integer")


def is_valid_solution(solution: Sequence[int], size: int | None = None) -> bool:
    """Return whether a row-to-column solution satisfies N-Queens constraints."""
    board_size = len(solution) if size is None else size
    if board_size < 1 or len(solution) != board_size:
        return False
    if any(not isinstance(column, int) or isinstance(column, bool) for column in solution):
        return False
    if any(column < 0 or column >= board_size for column in solution):
        return False
    if len(set(solution)) != board_size:
        return False
    return all(
        abs(first_row - second_row)
        != abs(solution[first_row] - solution[second_row])
        for first_row in range(board_size)
        for second_row in range(first_row + 1, board_size)
    )
