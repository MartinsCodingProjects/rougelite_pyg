import pygame

from game.systems.input import InputState
from game.systems.weapons import WeaponManager


class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos: pygame.Vector2 = None, speed: float = 300.0, player_width: int = 40, player_height: int = 40, enemies=None):
        self.game = game
        self.width = player_width
        self.height = player_height

        pygame.sprite.Sprite.__init__(self)
        self.color = (255, 0, 0)  # red
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)

        # Draw black dot in center of the red square for debugging
        pygame.draw.circle(self.image, (0, 0, 0), (20, 20), 3)

        self.rect = self.image.get_rect()
        self.rect.center = (pos.x if pos else 640, pos.y if pos else 360)

        self.pos = pos or pygame.Vector2(640, 360)  # default center position
        self.speed = speed

        self.health = 100
        self.starting_weapon = "dagger"

        # Store enemies reference for targeting and combat
        self.enemies = enemies

        self.weapons = WeaponManager(
            player=self, starting_weapon=self.starting_weapon)

    def update(self, world, dt: float, input_state: InputState):
        # Get world boundaries
        world_rect = world.get_boundaries()

        # Apply movement with boundary checking
        new_pos = pygame.Vector2(self.pos)

        if input_state.up:
            new_pos.y -= self.speed * dt
        if input_state.down:
            new_pos.y += self.speed * dt
        if input_state.left:
            new_pos.x -= self.speed * dt
        if input_state.right:
            new_pos.x += self.speed * dt

        # Clamp position to world boundaries (keeping player fully inside)
        half_width = self.width / 2
        half_height = self.height / 2

        new_pos.x = max(world_rect.left + half_width,
                        min(world_rect.right - half_width, new_pos.x))
        new_pos.y = max(world_rect.top + half_height,
                        min(world_rect.bottom - half_height, new_pos.y))

        self.pos = new_pos

        # Sync position back to rect (important for sprite drawing)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.enemies = self.game.enemies
        self.weapons.update(dt)

    def draw(self, world):
        # Get world offset for proper positioning
        world_offset = world.get_draw_offset()

        # Draw the player sprite with offset
        offset_pos = (
            int(self.rect.centerx + world_offset[0]),
            int(self.rect.centery + world_offset[1])
        )
        draw_rect = self.rect.copy()
        draw_rect.center = offset_pos
        world.surface.blit(self.image, draw_rect)

        # Draw the player's weapons (they need offset too)
        self.weapons.draw(world.surface, world_offset)

    def take_damage(self, damage, source=None):
        """Handle taking damage from enemies or other sources"""
        self.health -= damage

        # Handle death
        if self.health <= 0:
            print("Player died!")
            # Could trigger game over here

    def get_closest_enemies(self, n=1):
        """Return a list of the n closest enemies to the player"""
        if self.enemies == None:
            return []
        # calculate distance to each enemy
        enemies_with_distance = []
        for enemy in self.enemies:
            if enemy.state == "dead":
                continue  # skip dead enemies
            distance = self.pos.distance_to(enemy.pos)
            enemies_with_distance.append((distance, enemy))

        # sort by distance and return the n closest
        enemies_with_distance.sort(key=lambda x: x[0])
        return enemies_with_distance[:n]
