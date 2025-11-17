import pygame
import math


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, event_scheduler, pos: pygame.Vector2 = None, speed: float = 150.0, width: int = 20, height: int = 20):
        super().__init__()
        self.width = width
        self.height = height
        self.color = (0, 0, 255)  # blue
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            center=(pos.x, pos.y) if pos else (640, 360))
        self.pos = pos or pygame.Vector2(640, 360)
        self.speed = speed
        self.is_melee = True
        self.melee_damage = 1
        self.melee_attack_speed = 1.0  # attacks per second
        self.melee_last_attack_time = 0.0

        self.event_scheduler = event_scheduler

        # Health system
        self.max_health = 30
        self.health = self.max_health

        self.target_current = None

        self.state = "idle"

        # Direction control
        # current walking direction (normalized)
        self.direction = pygame.Vector2(1, 0)
        self.direction_to_player = pygame.Vector2(
            0, 0)  # target direction toward player
        self.rotation_speed = 1.5  # radians per second for turning

        self.game = game

    def spawn(self, world) -> None:
        """Spawn enemy at random position within world boundaries"""
        world_rect = world.get_boundaries()

        import random
        x = random.randint(world_rect.left + self.width // 2,
                           world_rect.right - self.width // 2)
        y = random.randint(world_rect.top + self.height // 2,
                           world_rect.bottom - self.height // 2)

        self.pos = pygame.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        print(f"Enemy spawned at ({x}, {y})")

    def find_closest_player(self, players) -> pygame.Vector2:
        """Find the closest player and return its position"""
        closest_player = None
        closest_distance = float('inf')

        for player in players:
            distance = self.pos.distance_to(player.pos)
            if distance < closest_distance:
                closest_distance = distance
                closest_player = player
                self.target_current = closest_player

    def update(self, world, dt: float, players) -> None:
        if self.state == "dead":
            return  # Do not update if dead
        # Step 1: Get current direction to player
        self.find_closest_player(players)
        target_pos = self.target_current.pos if self.target_current else None
        if target_pos:
            self.direction_to_player = (target_pos - self.pos).normalize()
        else:
            self.direction_to_player = pygame.Vector2(0, 0)

        # Step 2-5: Smoothly rotate current direction toward player direction
        self.update_direction(dt)

        # Step 6: Diced action decision based on collision
        self.decide_action(dt, players, world)

    def update_direction(self, dt: float) -> None:
        """Smoothly rotate current direction toward player direction"""
        if self.direction_to_player.length() == 0:
            return  # No target, keep current direction

        # Check if angle between current direction and player direction > 90°
        dot_product = self.direction.dot(self.direction_to_player)

        if dot_product < 0:  # angle > 90°, player is "behind" enemy
            # Immediately snap to closest cardinal direction toward player
            self.direction = self.get_cardinal_direction_to_player()
        else:
            # Normal smooth rotation (angle <= 90°)
            current_angle = math.atan2(self.direction.y, self.direction.x)
            target_angle = math.atan2(
                self.direction_to_player.y, self.direction_to_player.x)

            # Calculate angle difference (shortest path)
            angle_diff = target_angle - current_angle

            # Normalize angle difference to [-π, π]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            # Apply rotation speed limit
            max_rotation = self.rotation_speed * dt
            if abs(angle_diff) <= max_rotation:
                # Close enough, snap to target
                new_angle = target_angle
            else:
                # Rotate by maximum amount toward target
                new_angle = current_angle + \
                    math.copysign(max_rotation, angle_diff)

            # Update direction vector
            self.direction = pygame.Vector2(
                math.cos(new_angle), math.sin(new_angle))

    def get_cardinal_direction_to_player(self) -> pygame.Vector2:
        """Get the best cardinal direction (up/down/left/right) toward player"""
        dx = self.direction_to_player.x
        dy = self.direction_to_player.y

        # Choose direction based on which component is larger
        if abs(dx) > abs(dy):
            # Horizontal movement is dominant
            if dx > 0:
                return pygame.Vector2(1, 0)   # Right
            else:
                return pygame.Vector2(-1, 0)  # Left
        else:
            # Vertical movement is dominant
            if dy > 0:
                return pygame.Vector2(0, 1)   # Down (positive Y in pygame)
            else:
                return pygame.Vector2(0, -1)  # Up (negative Y in pygame)

    def decide_action(self, dt: float, players, world) -> None:
        # Calculate new position
        new_pos = self.pos + self.direction * self.speed * dt

        # Check if this movement would cause collision with any player
        would_collide = self.check_collision_at_position(new_pos, players)

        if would_collide and self.is_melee:
            self.attack_melee()
        else:
            self.move(world, dt, players, new_pos)

    def move(self, world, dt: float, players, new_pos) -> None:
        self.state = "move"

        # Move towards the closest player
        self.pos = new_pos

        # Get world boundaries
        world_rect = world.get_boundaries()

        # Clamp position to world boundaries (keeping enemy fully inside)
        half_width = self.width / 2
        half_height = self.height / 2

        self.pos.x = max(world_rect.left + half_width,
                         min(world_rect.right - half_width, self.pos.x))
        self.pos.y = max(world_rect.top + half_height,
                         min(world_rect.bottom - half_height, self.pos.y))

        # Sync position back to rect (important for sprite drawing)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def check_collision_at_position(self, new_pos: pygame.Vector2, players) -> bool:
        """Check if moving to new_pos would cause collision with any player"""
        # Create a temporary rect at the new position
        temp_rect = pygame.Rect(0, 0, self.width, self.height)
        temp_rect.center = (int(new_pos.x), int(new_pos.y))

        # Check collision with each player
        for player in players:
            if temp_rect.colliderect(player.rect):
                return True

        return False

    def attack_melee(self) -> None:
        """Perform melee attack when touching a player"""
        # check cooldown for melee attack
        current_time = pygame.time.get_ticks() / 1000.0  # convert to seconds
        if current_time - self.melee_last_attack_time < 1.0 / self.melee_attack_speed:
            self.state = "idle"
            return  # still in cooldown
        # Execute attack
        if self.target_current:
            self.state = "attack_melee"
            self.target_current.take_damage(self.melee_damage)
            self.melee_last_attack_time = current_time

    def take_damage(self, damage, source=None):
        """Handle taking damage from projectiles or other sources"""
        self.health -= damage
        self.color = (255, 165, 0)  # flash orange on hit
        self.image.fill(self.color)

        # Handle death
        if self.health <= 0:
            self.on_death(source)

    def on_death(self, source=None):
        """Handle enemy death"""
        print(f"Enemy died! Source: {source}")
        # Visual effect when dying
        self.color = (255, 0, 0)  # Turn red briefly
        self.game.kill_counter += 1
        self.image.fill(self.color)
        self.state = "dead"
        self.event_scheduler.schedule_event(
            pygame.time.get_ticks() / 1000.0 + 1, self.kill)  # kill after 1s
        # Remove from all sprite groups
        # self.kill()
