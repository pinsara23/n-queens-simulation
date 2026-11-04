"""Launch the interactive N-Queens Backtracking visualization."""

from __future__ import annotations

import argparse
import sys

import pygame

from algorithms.base_solver import SolverEventType, SolverStatistics
from simulation.controller import SimulationController
from visualization.board import BoardView
from visualization.ui_components import Button


class NQueensApp:
    """Pygame application for interactive Backtracking visualization."""

    def __init__(self, size: int = 8) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((1100, 720), pygame.RESIZABLE)
        pygame.display.set_caption("N-Queens - Backtracking Simulation")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 34)
        self.body_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.size = size
        self.board = BoardView(size)
        self.controller = SimulationController(size)
        self.status = "Ready"
        self.stats = SolverStatistics()
        self.running = True
        self.buttons: list[Button] = []

    def run(self, max_frames: int | None = None) -> None:
        """Run the event loop until the window closes."""
        frames = 0
        try:
            while self.running and (max_frames is None or frames < max_frames):
                self._handle_events()
                self._update()
                self._draw()
                pygame.display.flip()
                self.clock.tick(60)
                frames += 1
        finally:
            self.controller.stop()
            pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_SPACE:
            self._toggle_pause()
        elif key == pygame.K_RETURN:
            self._start()
        elif key == pygame.K_s:
            self.controller.step()
        elif key == pygame.K_r:
            self._reset()
        elif key in (pygame.K_MINUS, pygame.K_DOWN):
            self._change_size(-1)
        elif key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_UP):
            self._change_size(1)

    def _handle_click(self, position: tuple[int, int]) -> None:
        for button in self.buttons:
            if not button.clicked(position):
                continue
            if button.label == "Start":
                self._start()
            elif button.label in ("Pause", "Resume"):
                self._toggle_pause()
            elif button.label == "Step":
                self.controller.step()
            elif button.label == "Reset":
                self._reset()
            elif button.label == "-" or button.label == "+":
                self._change_size(-1 if button.label == "-" else 1)

    def _start(self) -> None:
        self.board.reset(self.size)
        self.controller.start(self.size)
        self.status = "Running"

    def _reset(self) -> None:
        self.controller.stop()
        self.board.reset(self.size)
        self.stats = SolverStatistics()
        self.status = "Ready"

    def _toggle_pause(self) -> None:
        if self.controller.paused:
            self.controller.resume()
            self.status = "Running"
        else:
            self.controller.pause()
            self.status = "Paused"

    def _change_size(self, delta: int) -> None:
        new_size = max(1, min(20, self.size + delta))
        if new_size != self.size:
            self.size = new_size
            self._reset()

    def _update(self) -> None:
        for event in self.controller.drain_events():
            self.board.apply_event(event)
            if event.event_type is SolverEventType.SOLUTION_FOUND:
                self.status = "Solution found"
            elif event.event_type is SolverEventType.SEARCH_COMPLETED:
                self.status = "Completed"
        if self.controller.solver is not None:
            self.stats = self.controller.solver.get_statistics()
        if self.controller.error is not None:
            self.status = f"Error: {self.controller.error}"

    def _draw(self) -> None:
        self.screen.fill((24, 28, 34))
        width, height = self.screen.get_size()
        panel_width = min(320, max(260, width // 3))
        board_area = pygame.Rect(20, 70, width - panel_width - 40, height - 90)
        self.board.draw(self.screen, board_area, self.title_font)
        title = self.title_font.render("N-Queens: Backtracking", True, (242, 244, 247))
        self.screen.blit(title, (20, 20))
        self._draw_panel(pygame.Rect(width - panel_width, 0, panel_width, height))

    def _draw_panel(self, panel: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, (36, 41, 49), panel)
        x = panel.x + 18
        self.screen.blit(self.body_font.render(f"Board size: {self.size} x {self.size}", True, (240, 240, 240)), (x, 25))
        self.screen.blit(self.small_font.render("Use +/- or arrow keys to change", True, (180, 186, 194)), (x, 53))
        self.screen.blit(self.body_font.render(f"Status: {self.status}", True, (240, 240, 240)), (x, 90))

        y = 130
        self.buttons = [
            Button(pygame.Rect(x, y, 82, 34), "Start"),
            Button(pygame.Rect(x + 90, y, 92, 34), "Pause" if not self.controller.paused else "Resume"),
            Button(pygame.Rect(x + 190, y, 70, 34), "Step"),
            Button(pygame.Rect(x, y + 44, 82, 34), "Reset"),
            Button(pygame.Rect(x + 90, y + 44, 40, 34), "-"),
            Button(pygame.Rect(x + 140, y + 44, 40, 34), "+"),
        ]
        for button in self.buttons:
            button.draw(self.screen, self.small_font)

        y += 102
        self.screen.blit(self.body_font.render("Statistics", True, (240, 240, 240)), (x, y))
        labels = (
            ("Recursive calls", self.stats.recursive_calls),
            ("Attempts", self.stats.attempted_placements),
            ("Valid placements", self.stats.valid_placements),
            ("Backtracks", self.stats.backtracking_operations),
            ("Search nodes", self.stats.search_nodes),
            ("Solutions", self.stats.solutions_found),
            ("Max depth", self.stats.maximum_recursion_depth),
            ("Elapsed", f"{self.stats.elapsed_time:.4f}s"),
        )
        for label, value in labels:
            y += 28
            self.screen.blit(self.small_font.render(f"{label}: {value}", True, (202, 208, 216)), (x, y))
        help_text = ("Enter: start   Space: pause/resume", "S: step   R: reset")
        for line in help_text:
            y += 35
            self.screen.blit(self.small_font.render(line, True, (165, 172, 182)), (x, y))


def main(argv: list[str] | None = None) -> int:
    """Parse options and launch the application."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=8, help="initial board size")
    parser.add_argument(
        "--frames",
        type=int,
        default=None,
        help="exit after this many frames (useful for smoke tests)",
    )
    args = parser.parse_args(argv)
    if not 1 <= args.size <= 20:
        parser.error("--size must be between 1 and 20")
    if args.frames is not None and args.frames < 1:
        parser.error("--frames must be positive")
    NQueensApp(args.size).run(max_frames=args.frames)
    return 0


if __name__ == "__main__":
    sys.exit(main())
