"""Pydantic models for the public API."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

AlgorithmId = Literal["backtracking"]


class AlgorithmInfo(BaseModel):
    id: str
    name: str
    description: str


class AlgorithmResponse(BaseModel):
    algorithms: list[AlgorithmInfo]


class TraceRequest(BaseModel):
    n: Annotated[int, Field(ge=4, le=12)]
    algorithm: AlgorithmId = "backtracking"
    max_steps: Annotated[int, Field(ge=1, le=50000)] = 20000
    stop_after_first_solution: bool = True


class SolveRequest(BaseModel):
    n: Annotated[int, Field(ge=4, le=12)]
    algorithm: AlgorithmId = "backtracking"
    max_solutions: Annotated[int, Field(ge=1, le=1000)] = 10


class TraceStep(BaseModel):
    i: int
    type: Literal["place", "reject", "backtrack", "solution"]
    row: int | None = None
    col: int | None = None
    reason: Literal["column", "diagonal"] | None = None
    board: list[int] | None = None


class SolverStats(BaseModel):
    nodes_explored: int
    placements: int
    rejections: int
    backtracks: int
    solutions_found: int
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
