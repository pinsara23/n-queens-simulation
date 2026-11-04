"""Chessboard rendering and event-driven board state."""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from algorithms.base_solver import SolverEvent, SolverEventType


class BoardView:
    """Render a resizable chessboard and the current search state."""

    def __init__(self, size: int) -> None:
        self.size = size
        self.queens = [-1] * size
        self.highlight: tuple[int, int, tuple[int, int, int]] | None = None
        self.solution: tuple[int, ...] | None = None

    def reset(self, size: int | None = None) -> None:
        """Clear the board, optionally changing its size."""
        if size is not None:
            self.size = size
        self.queens = [-1] * self.size
        self.highlight = None
        self.solution = None

    def apply_event(self, event: SolverEvent) -> None:
        """Update visual state from one solver event."""
        if event.event_type is SolverEventType.PLACE_QUEEN:
            if event.column is not None and event.row < self.size:
                self.queens[event.row] = event.column
                self.highlight = (event.row, event.column, (64, 190, 130))
        elif event.event_type is SolverEventType.REJECT_POSITION:
            if event.column is not None:
                self.highlight = (event.row, event.column, (220, 86, 86))
        elif event.event_type is SolverEventType.REMOVE_QUEEN:
            if self.solution is None and event.row < self.size:
                self.queens[event.row] = -1
                self.highlight = (event.row, event.column or 0, (230, 180, 70))
        elif event.event_type is SolverEventType.SOLUTION_FOUND:
            self.solution = event.solution
            if event.solution is not None:
                self.queens = list(event.solution)
        elif event.event_type is SolverEventType.SEARCH_COMPLETED:
            self.highlight = None

    def draw(
        self,
        surface: pygame.Surface,
        area: pygame.Rect,
        font: pygame.font.Font,
    ) -> None:
        """Draw the board within the supplied area."""
        cell = max(1, min(area.width, area.height) // self.size)
        board_width = cell * self.size
        board_rect = pygame.Rect(
            area.x + (area.width - board_width) // 2,
            area.y + (area.height - board_width) // 2,
            board_width,
            board_width,
        )
        light = (238, 232, 213)
        dark = (109, 142, 113)
        for row in range(self.size):
            for column in range(self.size):
                rect = pygame.Rect(
                    board_rect.x + column * cell,
                    board_rect.y + row * cell,
                    cell,
                    cell,
                )
                color = light if (row + column) % 2 == 0 else dark
                pygame.draw.rect(surface, color, rect)
                if self.highlight and self.highlight[:2] == (row, column):
                    pygame.draw.rect(surface, self.highlight[2], rect, max(2, cell // 12))

                if row < len(self.queens) and self.queens[row] == column:
                    label = font.render("Q", True, (38, 42, 48))
                    surface.blit(label, label.get_rect(center=rect.center))
        pygame.draw.rect(surface, (28, 32, 38), board_rect, 2)
