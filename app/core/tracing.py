"""Adapt the solver's event stream to the public API contract."""

from __future__ import annotations

from time import perf_counter

from algorithms.backtracking import BacktrackingSolver
from algorithms.base_solver import SolverEventType

from .config import solver_time_limit_seconds
from .registry import ALGORITHMS
from app.schemas import SolveResponse, SolverStats, TraceResponse, TraceStep


def _stats(solver: BacktrackingSolver, elapsed_ms: float) -> SolverStats:
    values = solver.get_statistics()
    return SolverStats(
        nodes_explored=values.search_nodes,
        placements=values.valid_placements,
        rejections=values.attempted_placements - values.valid_placements,
        backtracks=values.backtracking_operations,
        solutions_found=values.solutions_found,
        elapsed_ms=round(elapsed_ms, 3),
    )


def trace_solution(
    n: int,
    algorithm: str,
    max_steps: int,
    stop_after_first_solution: bool,
) -> TraceResponse:
    solver = ALGORITHMS[algorithm]["solver"](n)
    steps: list[TraceStep] = []
    started = perf_counter()
    truncated = False
    events = solver.solve_events(
        find_all=not stop_after_first_solution,
        time_limit_seconds=solver_time_limit_seconds(),
    )
    try:
        for event in events:
            if event.event_type is SolverEventType.PLACE_QUEEN:
                step = TraceStep(
                    i=len(steps), type="place", row=event.row, col=event.column
                )
            elif event.event_type is SolverEventType.REJECT_POSITION:
                step = TraceStep(
                    i=len(steps),
                    type="reject",
                    row=event.row,
                    col=event.column,
                    reason=event.reason,
                )
            elif event.event_type is SolverEventType.BACKTRACK:
                step = TraceStep(
                    i=len(steps),
                    type="backtrack",
                    row=event.row,
                    col=event.column,
                )
            elif event.event_type is SolverEventType.SOLUTION_FOUND:
                step = TraceStep(
                    i=len(steps),
                    type="solution",
                    board=list(event.solution or ()),
                )
            else:
                continue
            steps.append(step)
            if len(steps) >= max_steps:
                truncated = True
                break
    finally:
        events.close()
    if not truncated and perf_counter() - started >= solver_time_limit_seconds():
        truncated = True
    return TraceResponse(
        n=n,
        algorithm=algorithm,
        steps=steps,
        stats=_stats(solver, (perf_counter() - started) * 1000),
        truncated=truncated,
    )


def solve(
    n: int, algorithm: str, max_solutions: int
) -> SolveResponse:
    solver = ALGORITHMS[algorithm]["solver"](n)
    solutions: list[list[int]] = []
    started = perf_counter()
    truncated = False
    events = solver.solve_events(
        find_all=True,
        time_limit_seconds=solver_time_limit_seconds(),
    )
    try:
        for event in events:
            if event.event_type is SolverEventType.SOLUTION_FOUND:
                solutions.append(list(event.solution or ()))
                if len(solutions) >= max_solutions:
                    truncated = True
                    break
    finally:
        events.close()
    if not truncated and perf_counter() - started >= solver_time_limit_seconds():
        truncated = True
    return SolveResponse(
        solutions=solutions,
        count=len(solutions),
        stats=_stats(solver, (perf_counter() - started) * 1000),
        truncated=truncated,
    )
