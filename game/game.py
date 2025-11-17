import pygame
from typing import Tuple
import asyncio

from game.entities.player import Player
from game.entities.enemy import Enemy
from game.systems.input import InputManager, InputState
from game.entities.world import World
from game.systems.event_scheduler import EventScheduler
from game.systems.gui import GUI


class Game:
    def __init__(self, size: Tuple[int, int] = (1280, 720), fps: int = 60) -> None:
        self.screen_size = size
        self.fps = fps

        # Pygame objects (initialized in init_pygame)
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.world = None

        # game state
        self.is_running = False
        self.game_time = 0.0  # seconds
        self.game_over = False

        self.event_scheduler = EventScheduler()

        self.input_manager = InputManager()

        self.gui = None

        # players
        self.player1 = None
        self.players = None

        self.enemies = None

        self.kill_counter = 0

        self.wave_counter = 0

    def init_pygame(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            self.screen_size, pygame.RESIZABLE)

        # Init enemies first
        self.enemies = pygame.sprite.Group()

        # Init players with enemies reference
        self.player1 = Player(self, enemies=self.enemies)
        self.players = pygame.sprite.Group()
        # lets think of this as multiplayer ready
        self.players.add(self.player1)
        self.event_scheduler.schedule_event(
            self.game_time + 1, self.spawn_enemy_wave)

        self.world = World(self.screen_size)

        # Initialize GUI
        self.gui = GUI(self.screen_size)

        pygame.display.set_caption("Rougelite")
        self.clock = pygame.time.Clock()
        self.is_running = True

    def handle_input_events(self, events) -> None:
        # Handle global events (quit, resize, etc.)
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.screen_size = event.size
                self.screen = pygame.display.set_mode(
                    self.screen_size, pygame.RESIZABLE)
                self.world.update_world_size(self.screen_size)
                self.gui.update_screen_size(self.screen_size)
            elif event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                self.handle_game_over_clicks(event.pos)

    def update(self, per_player_states, dt: float) -> None:
        if self.game_over:
            return
        # update players
        players_alive = False
        for pid, player in enumerate(self.players):
            input_state = per_player_states.get(pid, InputState())
            player.update(self.world, dt, input_state)
            if player.health > 0:
                players_alive = True
        if not players_alive:
            self.set_game_over()

        # update enemies
        for enemy in self.enemies:
            enemy.update(self.world, dt, self.players)

    def draw(self) -> None:
        assert self.screen is not None
        self.screen.fill((128, 0, 128))

        # draw world background first
        if self.world:
            # draw world surface
            self.draw_world()

            # Draw players with offset

            self.draw_players()

            # Draw enemies with offset
            self.draw_enemies()

            # Blit world surface to screen
            self.screen.blit(self.world.surface, self.world.world_position)

        # Draw GUI on top of everything
        self.gui.draw(self.screen, self.players,
                      self.game_time, self.game_over, self.kill_counter)

    async def run(self) -> None:
        self.init_pygame()
        assert self.clock is not None

        while self.is_running:
            # handle timing of internal game time
            dt = self.clock.tick(self.fps) / 1000.0
            dt = min(dt, 0.05)  # Cap at 50 ms (20 FPS worst case)
            self.game_time += dt

            # Get input states and events
            per_player_states, events = self.input_manager.poll()

            # Handle global events (quit, resize, keys etc.)
            self.handle_input_events(events)

            # Run scheduled events
            self.event_scheduler.run_pending(self.game_time)

            # update all entities
            self.update(per_player_states, dt)

            # draw everything
            self.draw()

            pygame.display.flip()
            await asyncio.sleep(0)  # yield control to browser
        pygame.quit()

    def spawn_enemy_wave(self) -> None:
        # Spawn a wave of enemies
        enemy_number = self.wave_counter * 2 + 3  # increase number each wave
        self.wave_counter += 1
        for _ in range(enemy_number):  # spawn 5 enemies
            enemy = Enemy(game=self, event_scheduler=self.event_scheduler)
            enemy.spawn(self.world)
            self.enemies.add(enemy)

        # Schedule next wave in 10 seconds
        self.event_scheduler.schedule_event(
            self.game_time + 4, self.spawn_enemy_wave)

    def draw_players(self) -> None:
        for player in self.players:
            player.draw(self.world)

    def draw_enemies(self) -> None:
        world_offset = self.world.get_draw_offset()
        for enemy in self.enemies:
            offset_pos = (
                int(enemy.rect.centerx + world_offset[0]),
                int(enemy.rect.centery + world_offset[1])
            )
            draw_rect = enemy.rect.copy()
            draw_rect.center = offset_pos
            self.world.surface.blit(enemy.image, draw_rect)

    def draw_world(self) -> None:
        # Clear world surface and draw background
        self.world.surface.fill((100, 100, 100))  # margin color
        playable_rect = pygame.Rect(self.world.margin, self.world.margin,
                                    self.world.playable_width, self.world.playable_height)
        pygame.draw.rect(self.world.surface,
                         (125, 125, 125), playable_rect)

    def set_game_over(self) -> None:
        print("Game Over! All players have been defeated.")
        self.game_over = True
        # clear scheduled events
        self.event_scheduler.clear()

    def handle_game_over_clicks(self, mouse_pos: tuple) -> None:
        """Handle mouse clicks on game over screen buttons"""
        restart_rect, quit_rect = self.gui.get_game_over_button_rects()

        if restart_rect.collidepoint(mouse_pos):
            self.restart_game()
        elif quit_rect.collidepoint(mouse_pos):
            self.is_running = False

    def restart_game(self) -> None:
        """Restart the game to initial state"""
        print("Restarting game...")

        # Reset game state
        self.game_over = False
        self.game_time = 0.0

        # Reset player health and position
        for player in self.players:
            player.health = 100
            player.pos = pygame.Vector2(640, 360)
            player.rect.center = (int(player.pos.x), int(player.pos.y))

        # Clear all enemies
        self.enemies.empty()

        # Clear event scheduler and schedule first wave
        self.event_scheduler = EventScheduler()
        self.event_scheduler.schedule_event(
            self.game_time + 2, self.spawn_enemy_wave)
