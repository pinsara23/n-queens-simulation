"""Registry of algorithms implemented by this project."""

from __future__ import annotations

from algorithms.backtracking import BacktrackingSolver

ALGORITHMS = {
    "backtracking": {
        "name": "Backtracking",
        "description": "Recursive row-by-row backtracking search.",
        "solver": BacktrackingSolver,
    }
}
