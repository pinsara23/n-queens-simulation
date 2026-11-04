import pytest

from algorithms.backtracking import BacktrackingSolver
from algorithms.base_solver import SolverEventType
from utils.validation import is_valid_solution


@pytest.mark.parametrize(
    ("size", "expected_count"),
    [(1, 1), (2, 0), (3, 0), (4, 2), (5, 10), (6, 4), (7, 40), (8, 92)],
)
def test_known_solution_counts(size: int, expected_count: int) -> None:
    solver = BacktrackingSolver(size)
    solutions = solver.solve_all()
    assert len(solutions) == expected_count
    assert all(is_valid_solution(solution, size) for solution in solutions)


def test_solve_one_returns_valid_solution() -> None:
    solver = BacktrackingSolver(8)
    solution = solver.solve_one()
    assert solution is not None
    assert is_valid_solution(solution, 8)
    assert solver.get_solution() == solution


def test_events_include_search_lifecycle() -> None:
    events = list(BacktrackingSolver(4).solve_events())
    event_types = [event.event_type for event in events]
    assert event_types[0] is SolverEventType.TRY_POSITION
    assert SolverEventType.SOLUTION_FOUND in event_types
    assert event_types[-1] is SolverEventType.SEARCH_COMPLETED


def test_event_limit_does_not_change_solution_statistics() -> None:
    solver = BacktrackingSolver(4)
    events = list(solver.solve_events(find_all=True, max_events=3))
    assert len(events) == 3
    assert solver.get_statistics().solutions_found == 2


@pytest.mark.parametrize("size", [0, -1, True, 1.5])
def test_invalid_board_size(size: object) -> None:
    with pytest.raises(ValueError):
        BacktrackingSolver(size)  # type: ignore[arg-type]


def test_invalid_event_limit() -> None:
    with pytest.raises(ValueError):
        list(BacktrackingSolver(4).solve_events(max_events=-1))
