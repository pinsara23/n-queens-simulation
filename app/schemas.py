"""Pydantic models for the public API."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.core.registry import ALGORITHMS, MAX_BOARD_SIZE

AlgorithmId = Literal["backtracking", "bitmask", "forward_checking", "min_conflicts"]


class AlgorithmInfo(BaseModel):
    id: str
    name: str
    description: str
    category: Literal["exact", "local_search"]
    finds_all: bool
    max_n: int
    randomized: bool


class _BoardRequest(BaseModel):
    n: Annotated[int, Field(ge=4, le=MAX_BOARD_SIZE)]
    algorithm: AlgorithmId = "backtracking"
    seed: int | None = None

    @model_validator(mode="after")
    def _check_size_for_algorithm(self):
        max_n = ALGORITHMS[self.algorithm]["max_n"]
        if self.n > max_n:
            raise ValueError(f"n must be at most {max_n} for {self.algorithm}")
        return self


class AlgorithmResponse(BaseModel):
    algorithms: list[AlgorithmInfo]


class TraceRequest(_BoardRequest):
    max_steps: Annotated[int, Field(ge=1, le=50000)] = 20000
    stop_after_first_solution: bool = True


class SolveRequest(_BoardRequest):
    max_solutions: Annotated[int, Field(ge=1, le=1000)] = 10


class TraceStep(BaseModel):
    i: int
    type: Literal["place", "reject", "backtrack", "solution", "move", "restart"]
    row: int | None = None
    col: int | None = None
    reason: Literal["column", "diagonal", "dead_end"] | None = None
    blocked_row: int | None = None
    from_col: int | None = None
    conflicts: int | None = None
    board: list[int] | None = None


class SolverStats(BaseModel):
    nodes_explored: int
    placements: int
    rejections: int
    backtracks: int
    solutions_found: int
    moves: int = 0
    restarts: int = 0
    elapsed_ms: float


class TraceResponse(BaseModel):
    n: int
    algorithm: str
    steps: list[TraceStep]
    stats: SolverStats
    truncated: bool


class SolveResponse(BaseModel):
    solutions: list[list[int]]
    count: int
    stats: SolverStats
    truncated: bool
