"""Small Pygame UI helpers."""

from __future__ import annotations

import pygame


class Button:
    """A clickable labeled button."""

    def __init__(self, rect: pygame.Rect, label: str) -> None:
        self.rect = rect
        self.label = label

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        enabled: bool = True,
    ) -> None:
        """Draw the button with an enabled/disabled appearance."""
        fill = (61, 105, 145) if enabled else (75, 78, 84)
        pygame.draw.rect(surface, fill, self.rect, border_radius=5)
        text = font.render(self.label, True, (245, 247, 250))
        surface.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, position: tuple[int, int]) -> bool:
        """Return whether a mouse position is inside the button."""
        return self.rect.collidepoint(position)

