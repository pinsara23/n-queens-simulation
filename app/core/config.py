"""Environment-backed application settings."""

from __future__ import annotations

import os


def allowed_origins() -> list[str]:
    value = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def rate_limit() -> str:
    return os.getenv("RATE_LIMIT", "60/minute")


def solver_time_limit_seconds() -> float:
    value = os.getenv("SOLVER_TIME_LIMIT_SECONDS", "5")
    try:
        limit = float(value)
    except ValueError as exc:
        raise ValueError("SOLVER_TIME_LIMIT_SECONDS must be numeric") from exc
    if limit <= 0:
        raise ValueError("SOLVER_TIME_LIMIT_SECONDS must be positive")
    return limit
