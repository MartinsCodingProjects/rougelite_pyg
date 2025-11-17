import pygame
from typing import Tuple


class GUI:
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size

        # Font for text rendering
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)  # Default font, size 36
        # Smaller font for less important info
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.text_color = (255, 255, 255)  # White text
        # Semi-transparent black background
        self.background_color = (0, 0, 0, 128)

        # GUI positioning
        self.margin = 10
        self.line_height = 40

        # Game Over screen elements
        self.button_width = 200
        self.button_height = 60
        self.button_color = (64, 64, 64)  # Dark gray
        self.button_hover_color = (96, 96, 96)  # Lighter gray
        self.button_text_color = (255, 255, 255)  # White text

    def update_screen_size(self, new_size: Tuple[int, int]) -> None:
        """Update GUI when screen is resized"""
        self.screen_size = new_size

    def render_text_with_background(self, text: str, font: pygame.font.Font,
                                    text_color: Tuple[int, int, int],
                                    bg_color: Tuple[int, int, int, int]) -> pygame.Surface:
        """Render text with a semi-transparent background"""
        # Render the text
        text_surface = font.render(text, True, text_color)

        # Create background surface with alpha
        bg_surface = pygame.Surface((text_surface.get_width() + 20,
                                     text_surface.get_height() + 10), pygame.SRCALPHA)
        bg_surface.fill(bg_color)

        # Blit text onto background
        bg_surface.blit(text_surface, (10, 5))

        return bg_surface

    def draw(self, screen: pygame.Surface, players, game_time: float, game_over: bool = False, kill_counter: int = 0) -> None:
        """Draw all GUI elements"""
        if game_over:
            self.draw_game_over(screen)
        else:
            self.draw_player_info(screen, players)
            self.draw_game_info(screen, game_time, kill_counter)

    def draw_player_info(self, screen: pygame.Surface, players) -> None:
        """Draw player health and other player-specific information"""
        y_offset = self.margin

        for i, player in enumerate(players):
            # Player health
            health_text = f"Player {i + 1} Health: {int(player.health)}"
            health_surface = self.render_text_with_background(
                health_text, self.font, self.text_color, self.background_color
            )
            screen.blit(health_surface, (self.margin, y_offset))
            y_offset += self.line_height

    def draw_game_info(self, screen: pygame.Surface, game_time: float, kill_counter: int = 0) -> None:
        """Draw game-wide information like time, score, etc."""
        # Game time in top-right corner
        time_text = f"Time: {int(game_time)}s"
        time_surface = self.render_text_with_background(
            time_text, self.font, self.text_color, self.background_color
        )

        # Position in top-right corner
        time_x = self.screen_size[0] - time_surface.get_width() - self.margin
        time_y = self.margin

        screen.blit(time_surface, (time_x, time_y))

        # Kill counter below the time
        kill_text = f"Kills: {kill_counter}"
        kill_surface = self.render_text_with_background(
            kill_text, self.font, self.text_color, self.background_color
        )

        # Position below the time
        kill_x = self.screen_size[0] - kill_surface.get_width() - self.margin
        kill_y = self.margin + time_surface.get_height() + 5

        screen.blit(kill_surface, (kill_x, kill_y))

    def draw_debug_info(self, screen: pygame.Surface, fps: float, enemy_count: int) -> None:
        """Draw debug information (optional, can be toggled)"""
        debug_y = self.screen_size[1] - 60  # Bottom of screen

        # FPS counter
        fps_text = f"FPS: {int(fps)}"
        fps_surface = self.render_text_with_background(
            fps_text, self.small_font, self.text_color, self.background_color
        )
        screen.blit(fps_surface, (self.margin, debug_y))

        # Enemy count
        enemy_text = f"Enemies: {enemy_count}"
        enemy_surface = self.render_text_with_background(
            enemy_text, self.small_font, self.text_color, self.background_color
        )
        screen.blit(enemy_surface, (self.margin, debug_y + 25))

    def draw_game_over(self, screen: pygame.Surface) -> None:
        """Draw the game over screen with restart and quit buttons"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay
        screen.blit(overlay, (0, 0))

        # Draw "GAME OVER" text
        game_over_font = pygame.font.Font(None, 72)
        game_over_text = game_over_font.render(
            "GAME OVER", True, (255, 0, 0))  # Red text
        game_over_rect = game_over_text.get_rect(
            center=(self.screen_size[0] // 2, self.screen_size[1] // 2 - 100))
        screen.blit(game_over_text, game_over_rect)

        # Calculate button positions
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        # Draw restart button
        restart_rect = self.draw_button(
            screen, "RESTART", center_x - self.button_width // 2, center_y - 10)

        # Draw quit button
        quit_rect = self.draw_button(
            screen, "QUIT", center_x - self.button_width // 2, center_y + 70)

    def draw_button(self, screen: pygame.Surface, text: str, x: int, y: int) -> pygame.Rect:
        """Draw a button and return its rectangle for click detection"""
        button_rect = pygame.Rect(x, y, self.button_width, self.button_height)

        # Draw button background
        pygame.draw.rect(screen, self.button_color, button_rect)
        pygame.draw.rect(screen, self.button_text_color,
                         button_rect, 2)  # White border

        # Draw button text
        button_font = pygame.font.Font(None, 36)
        button_text = button_font.render(text, True, self.button_text_color)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)

        return button_rect

    def get_game_over_button_rects(self) -> Tuple[pygame.Rect, pygame.Rect]:
        """Get the rectangles for restart and quit buttons for click detection"""
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        restart_rect = pygame.Rect(
            center_x - self.button_width // 2, center_y - 10, self.button_width, self.button_height)
        quit_rect = pygame.Rect(center_x - self.button_width //
                                2, center_y + 70, self.button_width, self.button_height)

        return restart_rect, quit_rect
