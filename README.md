# N-Queens Interactive Simulation and Performance Analyzer

A modular Python application for solving and visualizing the N-Queens problem.
The current release includes a responsive Pygame simulation of the standard
recursive Backtracking algorithm. Optimized Backtracking, Branch and Bound,
Genetic Algorithm, and benchmark reporting are planned for later phases.

## Features

- Interactive chessboard visualization with resizable Pygame window
- Board sizes from 1x1 through 20x20
- Animated queen placement, rejected positions, removal, and backtracking
- Start, pause, resume, reset, and single-step execution
- Real-time search statistics
- Worker-thread computation so the Pygame interface stays responsive
- GUI-independent solver events suitable for future visualizations
- One-solution and all-solutions solver modes
- Automated correctness tests with known N-Queens solution counts

## Project structure

```text
N-Queens/
├── algorithms/
│   ├── base_solver.py       # Shared solver interface, events, and statistics
│   └── backtracking.py      # Standard recursive Backtracking solver
├── simulation/
│   └── controller.py        # Worker-thread simulation controller
├── visualization/
│   ├── board.py             # Board state and rendering
│   └── ui_components.py     # Reusable Pygame controls
├── utils/
│   └── validation.py        # Board-size and solution validation
├── tests/
│   └── test_backtracking.py
├── main.py                  # Application entry point
├── environment.yml          # Conda environment definition
└── requirements.txt         # Python packages
```

## Development environment

The supported Python version is **3.11**. The project uses a Conda environment
named `nqueens`; it does not use `venv`.

### Create the environment

Using the checked-in environment definition:

```powershell
conda env create -f environment.yml
conda activate nqueens
```

If the environment already exists, update it with:

```powershell
conda env update -n nqueens -f environment.yml --prune
conda activate nqueens
```

The direct equivalent is:

```powershell
conda create -n nqueens python=3.11 -y
conda activate nqueens
pip install -r requirements.txt
```

## Current implementation

### Implemented

- Phase 1: Conda environment and dependency setup
- Phase 2: Standard recursive Backtracking solver
- Phase 6: Common solver event and statistics contract
- Phase 7–8: Pygame board and interactive Backtracking simulation

The reference solver in [`algorithms/backtracking.py`](algorithms/backtracking.py)
places one queen per row and checks each candidate against previously placed
queens. It supports finding one solution or all solutions, emits
GUI-independent search events, collects statistics, and supports configurable
event limits.

The shared interface is defined in
[`algorithms/base_solver.py`](algorithms/base_solver.py), and solution
validation is provided by [`utils/validation.py`](utils/validation.py).

### Not yet implemented

- Optimized Backtracking
- Branch and Bound
- Genetic Algorithm
- Performance benchmarking and CSV export
- Matplotlib performance charts
- Multiple-solution browsing in the GUI

## Installation

From the project directory, create and activate the Conda environment:

```powershell
conda env create -f environment.yml
conda activate nqueens
```

For an existing environment:

```powershell
conda env update -n nqueens -f environment.yml --prune
conda activate nqueens
```

The project requires Python 3.11 and does not use `venv`.

## Run the tests

```powershell
conda activate nqueens
python -m pytest -q
```

Expected result:

```text
16 passed
```

The tests verify invalid inputs, known solution counts from 1x1 through 8x8,
solution validity, event lifecycle, event limiting, and one-solution mode.

## Run the interactive simulation

From the project root, activate the Conda environment and launch the
Backtracking GUI:

```powershell
conda activate nqueens
python main.py
```

An initial board size can be selected from the command line:

```powershell
python main.py --size 8
```

The GUI supports board sizes from 1 through 20. Use **Start**, **Pause** /
**Resume**, **Step**, and **Reset** in the control panel. The `+` and `-`
buttons, or the arrow keys, change the board size. Keyboard shortcuts are:

| Key | Action |
| --- | --- |
| Enter | Start a new search |
| Space | Pause or resume |
| S | Advance one event |
| R | Reset |
| Up / Down | Increase or decrease board size |

The solver runs in a worker thread. Pygame rendering and event handling remain
on the main thread, so the window remains responsive during the search.

For a non-interactive launch smoke test, run a finite number of frames:

```powershell
$env:SDL_VIDEODRIVER = "dummy"
python main.py --size 4 --frames 2
```

The current GUI integrates only the standard recursive Backtracking solver.

## Controls

| Control | Action |
| --- | --- |
| Start | Start a new one-solution search |
| Pause / Resume | Stop or continue automatic event playback |
| Step | Advance one solver event while paused |
| Reset | Stop the search and clear the board |
| `-` / `+` | Decrease or increase the board size |

The solver event stream includes `TRY_POSITION`, `PLACE_QUEEN`,
`REJECT_POSITION`, `REMOVE_QUEEN`, `BACKTRACK`, `SOLUTION_FOUND`, and
`SEARCH_COMPLETED`. Solver code does not import or depend on Pygame.

## Known limitations

- The current GUI displays the first solution found; it does not yet browse
  all solutions.
- Board sizes above 12 may take substantially longer with standard
  Backtracking.
- The performance benchmarking and charting modules are not implemented yet.
- The GUI currently supports only the standard Backtracking algorithm.
