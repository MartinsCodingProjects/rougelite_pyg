import pygame
from typing import Tuple


class World():
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        self.margin_percent = 0.01  # 1% of world width as margin

        # Visual world surface (includes margin)
        self.world_width = (self.screen_size[0] * 0.9)
        self.world_height = (self.screen_size[1] * 0.9)
        self.margin = int(
            min(self.world_width, self.world_height) * self.margin_percent)

        self.world_position = (
            (self.screen_size[0] - self.world_width) / 2, (self.screen_size[1] - self.world_height) / 2)
        self.surface = pygame.Surface((self.world_width, self.world_height))
        self.surface.fill((125, 125, 125))  # gray background

        # Logical playable area (world minus margin)
        self.playable_width = self.world_width - (self.margin * 2)
        self.playable_height = self.world_height - (self.margin * 2)

    def update_world_size(self, new_size: Tuple[int, int]) -> None:
        self.screen_size = new_size

        # Visual world surface (includes margin)
        self.world_width = (self.screen_size[0] * 0.9)
        self.world_height = (self.screen_size[1] * 0.9)
        self.world_position = (
            (self.screen_size[0] - self.world_width) / 2, (self.screen_size[1] - self.world_height) / 2)
        self.surface = pygame.Surface((self.world_width, self.world_height))
        self.surface.fill((125, 125, 125))  # grey background

        # Recalculate responsive margin
        self.margin = int(
            min(self.world_width, self.world_height) * self.margin_percent)

        # Update logical playable area
        self.playable_width = self.world_width - (self.margin * 2)
        self.playable_height = self.world_height - (self.margin * 2)

    def get_boundaries(self) -> pygame.Rect:
        """Returns the playable boundaries (excluding margin) for collision detection"""
        return pygame.Rect(0, 0, self.playable_width, self.playable_height)

    def get_draw_offset(self) -> Tuple[int, int]:
        """Returns offset for drawing entities with margin"""
        return (self.margin, self.margin)
