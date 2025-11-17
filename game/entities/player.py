import pygame

from game.systems.input import InputState
from game.systems.weapons import WeaponManager


class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos: pygame.Vector2 = None, speed: float = 300.0, player_width: int = 40, player_height: int = 40, enemies=None):
        self.game = game
        # Character frames crop settings (adjust these values to match your sprite)
        self.char_width = 14
        self.char_height = 25
        self.char_frame_aspect_ratio = self.char_width / self.char_height
        self.char_frame_scale_factor = 3

        self.width = self.char_width * self.char_frame_scale_factor
        self.height = self.width / self.char_frame_aspect_ratio

        pygame.sprite.Sprite.__init__(self)

        # Load and setup sprite sheet
        self.sprite_sheet = pygame.image.load(
            "game/assets/char1/walk.png").convert_alpha()
        self.frame_width = self.sprite_sheet.get_width() // 6  # 6 frames per row
        self.frame_height = self.sprite_sheet.get_height() // 4  # 4 rows

        # Animation state
        self.current_frame = 0
        self.animation_speed = 10  # frames per second
        self.animation_timer = 0
        self.direction = 'down'  # default direction
        self.is_moving = False

        # Extract all frames from sprite sheet
        self.frames = {}
        directions = ['down', 'left', 'right', 'up']

        # Calculate center offset to crop the character from each frame
        crop_x = (self.frame_width - self.char_width) // 2
        crop_y = (self.frame_height - self.char_height) // 2

        for row, direction in enumerate(directions):
            self.frames[direction] = []
            for col in range(6):
                # Extract the full frame first
                full_frame = pygame.Surface(
                    (self.frame_width, self.frame_height), pygame.SRCALPHA)
                full_frame.blit(self.sprite_sheet, (0, 0),
                                (col * self.frame_width, row * self.frame_height,
                                self.frame_width, self.frame_height))

                # Crop just the character part
                cropped_char = pygame.Surface(
                    (self.char_width, self.char_height), pygame.SRCALPHA)
                cropped_char.blit(full_frame, (0, 0),
                                  (crop_x, crop_y, self.char_width, self.char_height))

                # Scale up the cropped character to fill the sprite size
                scaled_char = pygame.transform.scale(
                    cropped_char, (self.width, self.height))

                self.frames[direction].append(scaled_char)

        # Set initial image
        self.image = self.frames['down'][0]
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

        # Create collision mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, world, dt: float, input_state: InputState):
        # Get world boundaries
        world_rect = world.get_boundaries()

        # Apply movement with boundary checking
        new_pos = pygame.Vector2(self.pos)
        self.is_moving = False

        # Check movement and set direction
        if input_state.up:
            new_pos.y -= self.speed * dt
            self.direction = 'up'
            self.is_moving = True
        if input_state.down:
            new_pos.y += self.speed * dt
            self.direction = 'down'
            self.is_moving = True
        if input_state.left:
            new_pos.x -= self.speed * dt
            self.direction = 'left'
            self.is_moving = True
        if input_state.right:
            new_pos.x += self.speed * dt
            self.direction = 'right'
            self.is_moving = True

        # Clamp position to world boundaries (keeping player fully inside)
        half_width = self.width / 2
        half_height = self.height / 2

        new_pos.x = max(world_rect.left + half_width,
                        min(world_rect.right - half_width, new_pos.x))
        new_pos.y = max(world_rect.top + half_height,
                        min(world_rect.bottom - half_height, new_pos.y))

        self.pos = new_pos

        # Update animation
        self.update_animation(dt)

        # Sync position back to rect (important for sprite drawing)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.enemies = self.game.enemies
        self.weapons.update(dt)

    def draw(self, world):
        # Get world offset for proper positioning
        world_offset = world.get_draw_offset()

        # Draw the player sprite with offset
        # Center the sprite image on the player's position
        sprite_rect = self.image.get_rect()
        sprite_rect.center = (
            int(self.rect.centerx + world_offset[0]),
            int(self.rect.centery + world_offset[1])
        )
        world.surface.blit(self.image, sprite_rect)

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

    def update_animation(self, dt):
        """Update sprite animation based on movement"""
        if self.is_moving:
            # Update animation timer
            self.animation_timer += dt

            # Change frame when timer exceeds frame duration
            if self.animation_timer >= 1.0 / self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % 6
        else:
            # Reset to first frame when not moving
            self.current_frame = 0
            self.animation_timer = 0

        # Update the image based on direction and frame
        self.image = self.frames[self.direction][self.current_frame]

        # Update collision mask when image changes
        self.mask = pygame.mask.from_surface(self.image)

    def pixel_perfect_collision(self, other_sprite):
        """Check for pixel-perfect collision with another sprite that has a mask"""
        if not hasattr(other_sprite, 'mask'):
            # Fallback to rect collision if other sprite doesn't have mask
            return self.rect.colliderect(other_sprite.rect)

        # Calculate offset between sprites
        offset_x = other_sprite.rect.x - self.rect.x
        offset_y = other_sprite.rect.y - self.rect.y

        # Check if masks overlap
        return self.mask.overlap(other_sprite.mask, (offset_x, offset_y)) is not None

    def get_collision_rect(self):
        """Get a tighter bounding rect based on the actual sprite content"""
        # Get the bounding rect of non-transparent pixels
        mask_rect = self.mask.get_bounding_rects()
        if mask_rect:
            # Use the first (and usually only) bounding rect
            tight_rect = mask_rect[0]
            # Adjust position relative to sprite's world position
            tight_rect.x += self.rect.x
            tight_rect.y += self.rect.y
            return tight_rect
        else:
            # Fallback to regular rect if no mask bounds found
            return self.rect
