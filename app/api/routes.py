"""HTTP endpoints for solver visualization and results."""

from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import rate_limit
from app.core.registry import ALGORITHMS
from app.core.tracing import solve, trace_solution
from app.schemas import (
    AlgorithmResponse,
    SolveRequest,
    SolveResponse,
    TraceRequest,
    TraceResponse,
)

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)


@router.get("/algorithms", response_model=AlgorithmResponse)
@limiter.limit(rate_limit())
def algorithms(request: Request) -> AlgorithmResponse:
    return AlgorithmResponse(
        algorithms=[
            {"id": key, "name": value["name"], "description": value["description"]}
            for key, value in ALGORITHMS.items()
        ]
    )


@router.post(
    "/trace", response_model=TraceResponse, response_model_exclude_none=True
)
@limiter.limit(rate_limit())
def trace(request: Request, payload: TraceRequest) -> TraceResponse:
    return trace_solution(
        payload.n,
        payload.algorithm,
        payload.max_steps,
        payload.stop_after_first_solution,
    )


@router.post("/solve", response_model=SolveResponse)
@limiter.limit(rate_limit())
def solve_endpoint(request: Request, payload: SolveRequest) -> SolveResponse:
    return solve(payload.n, payload.algorithm, payload.max_solutions)
