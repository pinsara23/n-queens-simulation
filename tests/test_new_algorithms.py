import pytest

from algorithms.backtracking import BacktrackingSolver
from algorithms.base_solver import SolverEventType
from algorithms.bitmask import BitmaskSolver
from algorithms.forward_checking import ForwardCheckingSolver
from algorithms.min_conflicts import MinConflictsSolver
from utils.validation import is_valid_solution

KNOWN_COUNTS = [(1, 1), (2, 0), (3, 0), (4, 2), (5, 10), (6, 4), (7, 40), (8, 92), (9, 352)]
EXACT_SOLVERS = [BitmaskSolver, ForwardCheckingSolver]


@pytest.mark.parametrize("solver_cls", EXACT_SOLVERS)
@pytest.mark.parametrize(("size", "expected_count"), KNOWN_COUNTS)
def test_exact_solvers_count_all_solutions(solver_cls, size, expected_count) -> None:
    solutions = solver_cls(size).solve_all()
    assert len(solutions) == expected_count
    assert len(set(solutions)) == expected_count
    assert all(is_valid_solution(s, size) for s in solutions)


@pytest.mark.parametrize("solver_cls", EXACT_SOLVERS)
def test_exact_solvers_find_same_solution_set_as_backtracking(solver_cls) -> None:
    assert set(solver_cls(8).solve_all()) == set(BacktrackingSolver(8).solve_all())


def test_bitmask_first_solution_matches_backtracking() -> None:
    assert BitmaskSolver(8).solve_one() == BacktrackingSolver(8).solve_one()


def test_bitmask_never_rejects_and_explores_same_tree() -> None:
    bitmask, plain = BitmaskSolver(8), BacktrackingSolver(8)
    events = list(bitmask.solve_events(find_all=True))
    list(plain.solve_events(find_all=True))
    assert not any(e.event_type is SolverEventType.REJECT_POSITION for e in events)
    assert bitmask.get_statistics().valid_placements == plain.get_statistics().valid_placements


def test_forward_checking_prunes_search() -> None:
    fc, plain = ForwardCheckingSolver(8), BacktrackingSolver(8)
    events = list(fc.solve_events())
    plain.solve_one()
    assert fc.get_statistics().valid_placements < plain.get_statistics().valid_placements
    dead_ends = [e for e in events if e.event_type is SolverEventType.REJECT_POSITION]
    assert dead_ends and all(
        e.reason == "dead_end" and e.blocked_row is not None for e in dead_ends
    )


def test_forward_checking_board_is_consistent_during_trace() -> None:
    board: dict[int, int] = {}
    for event in ForwardCheckingSolver(6).solve_events(find_all=True):
        if event.event_type is SolverEventType.PLACE_QUEEN:
            assert event.row not in board
            board[event.row] = event.column
            assert all(
                c != event.column and abs(r - event.row) != abs(c - event.column)
                for r, c in board.items()
                if r != event.row
            )
        elif event.event_type is SolverEventType.BACKTRACK:
            assert board.pop(event.row) == event.column
        elif event.event_type is SolverEventType.SOLUTION_FOUND:
            assert tuple(board[r] for r in range(6)) == event.solution


@pytest.mark.parametrize("size", [1, 4, 5, 8, 12, 50, 200])
def test_min_conflicts_finds_valid_solution(size) -> None:
    solver = MinConflictsSolver(size, seed=1)
    solution = solver.solve_one()
    assert solution is not None and is_valid_solution(solution, size)
    assert solver.get_statistics().solutions_found == 1


@pytest.mark.parametrize("size", [2, 3])
def test_min_conflicts_unsolvable_sizes(size) -> None:
    assert MinConflictsSolver(size).solve_all() == []


def test_min_conflicts_seed_is_reproducible() -> None:
    first = list(MinConflictsSolver(30, seed=7).solve_events())
    second = list(MinConflictsSolver(30, seed=7).solve_events())
    assert first == second


def test_min_conflicts_replaying_events_reaches_solution() -> None:
    board: list[int] = [-1] * 20
    final = None
    for event in MinConflictsSolver(20, seed=3).solve_events():
        if event.event_type is SolverEventType.RESTART:
            board = [-1] * 20
        elif event.event_type is SolverEventType.PLACE_QUEEN:
            board[event.row] = event.column
        elif event.event_type is SolverEventType.MOVE_QUEEN:
            assert board[event.row] == event.from_column
            board[event.row] = event.column
        elif event.event_type is SolverEventType.SOLUTION_FOUND:
            final = event.solution
    assert final == tuple(board)


@pytest.mark.parametrize("solver_cls", [*EXACT_SOLVERS, MinConflictsSolver])
def test_invalid_limits(solver_cls) -> None:
    with pytest.raises(ValueError):
        list(solver_cls(4).solve_events(max_events=-1))
