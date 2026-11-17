"""Registry of algorithms implemented by this project."""

from __future__ import annotations

from algorithms.backtracking import BacktrackingSolver
from algorithms.bitmask import BitmaskSolver
from algorithms.forward_checking import ForwardCheckingSolver
from algorithms.min_conflicts import MinConflictsSolver

# Fields besides "solver" are published by GET /api/algorithms:
#   category   "exact" (complete search) or "local_search" (one solution)
#   finds_all  whether the solver can enumerate every solution
#   max_n      largest board the API accepts for this algorithm
#   randomized whether results vary between runs (pass "seed" to fix them)
ALGORITHMS = {
    "backtracking": {
        "name": "Backtracking",
        "description": "Recursive row-by-row backtracking search.",
        "category": "exact",
        "finds_all": True,
        "max_n": 12,
        "randomized": False,
        "solver": BacktrackingSolver,
    },
    "bitmask": {
        "name": "Bitmask Backtracking",
        "description": (
            "Row-by-row backtracking that tracks attacked columns and diagonals "
            "as bitmasks, so attacked squares are skipped instead of rejected."
        ),
        "category": "exact",
        "finds_all": True,
        "max_n": 12,
        "randomized": False,
        "solver": BitmaskSolver,
    },
    "forward_checking": {
        "name": "Forward Checking + MRV",
        "description": (
            "Constraint search that prunes attacked squares from later rows, "
            "rejects moves that leave a row empty, and fills the most "
            "constrained row next."
        ),
        "category": "exact",
        "finds_all": True,
        "max_n": 12,
        "randomized": False,
        "solver": ForwardCheckingSolver,
    },
    "min_conflicts": {
        "name": "Min-Conflicts",
        "description": (
            "Local search that fills the board, then moves attacked queens to "
            "their least-attacked square until no conflicts remain. Finds one "
            "solution and scales to large boards."
        ),
        "category": "local_search",
        "finds_all": False,
        "max_n": 200,
        "randomized": True,
        "solver": MinConflictsSolver,
    },
}

MAX_BOARD_SIZE = max(entry["max_n"] for entry in ALGORITHMS.values())


def create_solver(algorithm: str, n: int, seed: int | None = None):
    entry = ALGORITHMS[algorithm]
    if entry["randomized"]:
        return entry["solver"](n, seed=seed)
    return entry["solver"](n)
