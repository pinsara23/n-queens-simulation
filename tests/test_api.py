from fastapi.testclient import TestClient

from app.main import app
from utils.validation import is_valid_solution


client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_algorithms() -> None:
    response = client.get("/api/algorithms")
    assert response.status_code == 200
    assert response.json()["algorithms"][0]["id"] == "backtracking"


def test_trace_and_stats() -> None:
    response = client.post(
        "/api/trace",
        json={
            "n": 4,
            "algorithm": "backtracking",
            "max_steps": 500,
            "stop_after_first_solution": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert all(step["type"] in {"place", "reject", "backtrack", "solution"} for step in body["steps"])
    assert all(
        is_valid_solution(step["board"], 4)
        for step in body["steps"]
        if step["type"] == "solution"
    )
    stats = body["stats"]
    assert stats["placements"] == sum(step["type"] == "place" for step in body["steps"])
    assert stats["rejections"] == sum(step["type"] == "reject" for step in body["steps"])
    assert stats["backtracks"] == sum(step["type"] == "backtrack" for step in body["steps"])
    assert stats["solutions_found"] == sum(step["type"] == "solution" for step in body["steps"])


def test_trace_truncation() -> None:
    response = client.post("/api/trace", json={"n": 8, "max_steps": 1})
    assert response.status_code == 200
    assert response.json()["truncated"] is True


def test_validation_errors() -> None:
    assert client.post("/api/trace", json={"n": 3}).status_code == 422
    assert client.post("/api/trace", json={"n": 8, "max_steps": 50001}).status_code == 422
    assert client.post("/api/solve", json={"n": 8, "max_solutions": 1001}).status_code == 422


def test_cors_header() -> None:
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_time_limit_behavior(monkeypatch) -> None:
    monkeypatch.setenv("SOLVER_TIME_LIMIT_SECONDS", "0.000001")
    response = client.post("/api/trace", json={"n": 12, "max_steps": 50000})
    assert response.status_code == 200
    assert response.json()["truncated"] is True
