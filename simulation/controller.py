"""Threaded bridge between a solver event generator and the GUI."""

from __future__ import annotations

from collections import deque
from threading import Condition, Lock, Thread
from time import sleep
from typing import Deque

from algorithms.backtracking import BacktrackingSolver
from algorithms.base_solver import SolverEvent


class SimulationController:
    """Run solver events off the Pygame main thread."""

    def __init__(self, size: int, speed: float = 0.04) -> None:
        self.size = size
        self.speed = speed
        self.events: Deque[SolverEvent] = deque()
        self._lock = Lock()
        self._condition = Condition(self._lock)
        self._paused = True
        self._step_requested = False
        self._stop_requested = False
        self._thread: Thread | None = None
        self.solver: BacktrackingSolver | None = None
        self.completed = False
        self.error: Exception | None = None

    @property
    def running(self) -> bool:
        """Whether the worker is currently allowed to advance."""
        with self._lock:
            return self._thread is not None and not self._paused

    @property
    def paused(self) -> bool:
        """Whether automatic event advancement is paused."""
        with self._lock:
            return self._paused

    def start(self, size: int | None = None) -> None:
        """Start a fresh one-solution search."""
        self.stop()
        if size is not None:
            self.size = size
        self.events.clear()
        self.solver = BacktrackingSolver(self.size)
        self.completed = False
        self.error = None
        with self._condition:
            self._stop_requested = False
            self._step_requested = False
            self._paused = False
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def pause(self) -> None:
        """Pause automatic advancement."""
        with self._condition:
            self._paused = True

    def resume(self) -> None:
        """Resume automatic advancement."""
        with self._condition:
            self._paused = False
            self._condition.notify_all()

    def step(self) -> None:
        """Advance exactly one event while paused."""
        with self._condition:
            if self._thread is not None and not self.completed:
                self._step_requested = True
                self._condition.notify_all()

    def set_speed(self, speed: float) -> None:
        """Set the delay between automatic events."""
        self.speed = max(0.001, speed)

    def drain_events(self) -> list[SolverEvent]:
        """Return events produced since the last GUI frame."""
        with self._lock:
            result = list(self.events)
            self.events.clear()
            return result

    def stop(self) -> None:
        """Request worker shutdown and wait briefly for it."""
        with self._condition:
            self._stop_requested = True
            self._paused = False
            self._condition.notify_all()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

    def _run(self) -> None:
        assert self.solver is not None
        try:
            for event in self.solver.solve_events(find_all=False):
                with self._lock:
                    if self._stop_requested:
                        return
                    self.events.append(event)
                with self._condition:
                    while self._paused and not self._step_requested and not self._stop_requested:
                        self._condition.wait()
                    if self._stop_requested:
                        return
                    if self._step_requested:
                        self._step_requested = False
                    else:
                        delay = self.speed
                        self._condition.release()
                        sleep(delay)
                        self._condition.acquire()
            self.completed = True
        except Exception as exc:  # surfaced to the GUI instead of silently failing
            self.error = exc
            self.completed = True

