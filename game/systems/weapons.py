import pygame

from game.systems.attack import Attack


class Weapon(pygame.sprite.Sprite):
    def __init__(self, name, damage, range, player=None, slot=0):
        super().__init__()
        self.name = name
        self.player = player
        self.damage = damage
        self.range = range
        self.type = "melee"
        self.max_targets = 1
        self.targets = None
        self.targeted_enemy = None

        self.pos = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0, 0)

        # Load weapon sprite based on weapon name
        if name == "dagger":
            try:
                # Load dagger sprite
                dagger_sprite = pygame.image.load("game/assets/dagger.png").convert_alpha()
                # Scale to desired weapon size (20x10 was the original rectangle size)
                self.image_orig = pygame.transform.scale(dagger_sprite, (20, 10))
            except Exception:
                # Fallback to green rectangle if sprite can't be loaded
                self.image_orig = pygame.Surface((20, 10))
                self.image_orig.set_colorkey((0, 0, 0))
                self.image_orig.fill((0, 255, 0))
        else:
            # Default weapon appearance for other weapons
            self.image_orig = pygame.Surface((20, 10))
            self.image_orig.set_colorkey((0, 0, 0))
            self.image_orig.fill((0, 255, 0))
        
        # create working copy
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.visible = True

        # states that a attack circle will give the weapon
        # idle, cooling down, fired, returning
        self.state = "idle"

        self.attack_duration = 0.2  # seconds
        self.attack = Attack(self)
        self.attack_timer = 0.0  # separate attack timer for weapon

        self.cooldown_duration = 1  # seconds
        self.cooldown_timer = 0.0

        self.piercing_count = 0  # number of targets the projectile can pierce through

    def update(self, dt: float):
        self.update_position()
        self.rotate_weapon_in_direction()
        should_attack = self.check_attack_condition()
        if should_attack:
            self.attack.execute()
            self.state = "attacking"
            self.attack_timer = 0.0  # Reset weapon's attack timer
        if self.state == "attacking":
            # After attack duration, return to idle
            self.attack_timer += dt
            if self.attack_timer >= self.attack_duration:
                self.attack_timer = 0.0
                self.visible = True  # Make weapon visible again
                self.start_cooldown()
        if self.state == "cooldown":
            self.cooldown_timer += dt
            if self.cooldown_timer >= self.cooldown_duration:
                self.state = "idle"
                self.cooldown_timer = 0.0

    def start_cooldown(self):
        self.state = "cooldown"

    def check_attack_condition(self):
        # Must be idle to attack
        if self.state != "idle":
            return False

        # Must have a target
        if not self.targeted_enemy:
            return False

        # If weapon has infinite range (None), can always attack
        if self.range is None:
            return True

        # Check if target is within range
        distance_to_enemy = self.pos.distance_to(self.targeted_enemy.pos)
        return distance_to_enemy <= self.range

    def rotate_weapon_in_direction(self):
        # calc direction from weapons position to targeted enemy
        if self.targeted_enemy:
            direction_to_target = self.targeted_enemy.pos - self.pos
            if direction_to_target.length() > 0:  # avoid division by zero
                self.direction = direction_to_target.normalize()
            else:
                self.direction = pygame.Vector2(1, 0)  # default right
        else:
            # default right when no targets
            self.direction = pygame.Vector2(1, 0)
        # Calculate angle from direction vector
        angle = self.direction.angle_to(pygame.Vector2(1, 0))

        # Store the old center position
        old_center = self.rect.center

        # Rotate the original image (always from original to avoid cumulative distortion)
        self.image = pygame.transform.rotate(self.image_orig, angle)

        # Get new rect from rotated image
        self.rect = self.image.get_rect()

        # Restore the center position
        self.rect.center = old_center

    def update_position(self):
        # Target is now assigned by WeaponManager, just use it
        # get direction from player to assigned target
        if self.targeted_enemy and self.player:
            direction_to_target = self.targeted_enemy.pos - self.player.pos
            if direction_to_target.length() > 0:  # avoid division by zero
                self.direction = direction_to_target.normalize()
            else:
                self.direction = pygame.Vector2(1, 0)  # default right
        else:
            # default right when no targets
            self.direction = pygame.Vector2(1, 0)

        # update weapon position based on player position and direction to target with offset in that direction
        if self.player:
            self.pos = pygame.Vector2(
                self.player.pos.x + self.direction.x * 30,
                self.player.pos.y + self.direction.y * 30
            )
            self.rect.center = (int(self.pos.x), int(self.pos.y))


class WeaponManager:
    def __init__(self, player=None, starting_weapon: str = "dagger"):
        self.player = player
        self.weapon_count = 0
        self.weapons = pygame.sprite.Group()

        self.create_starting_weapons(starting_weapon, 2)

    def create_starting_weapons(self, weapon_name: str, count: int):
        for i in range(count):
            weapon = Weapon(weapon_name, damage=20,
                            range=300, player=self.player)
            self.weapons.add(weapon)
            self.weapon_count += 1

    def update(self, dt: float):
        # First, distribute targets among all weapons
        self.distribute_targets()

        for weapon in self.weapons:
            weapon.update(dt)
            # Update projectiles for each weapon
            weapon.attack.projectiles.update(dt)

    def distribute_targets(self):
        """Distribute targets among weapons to avoid duplicates"""
        if not self.player or not self.player.enemies:
            # No enemies available, clear all targets
            for weapon in self.weapons:
                weapon.targets = None
                weapon.targeted_enemy = None
            return

        # Get all available enemies sorted by distance
        all_enemies = self.player.get_closest_enemies(len(self.player.enemies))

        if not all_enemies:
            # No enemies found
            for weapon in self.weapons:
                weapon.targets = None
                weapon.targeted_enemy = None
            return

        # Assign targets to weapons
        weapon_list = list(self.weapons)
        for i, weapon in enumerate(weapon_list):
            if len(all_enemies) > 0:
                # Cycle through enemies if more weapons than enemies
                enemy_index = i % len(all_enemies)
                target_enemy = all_enemies[enemy_index]
                weapon.targets = [target_enemy]
                # Extract enemy from (distance, enemy) tuple
                weapon.targeted_enemy = target_enemy[1]
            else:
                weapon.targets = None
                weapon.targeted_enemy = None

    def draw(self, surface, world_offset=(0, 0)):
        # Draw each weapon with the world offset
        for weapon in self.weapons:
            # Draw weapon only if visible
            if weapon.visible:
                offset_pos = (
                    int(weapon.rect.centerx + world_offset[0]),
                    int(weapon.rect.centery + world_offset[1])
                )
                draw_rect = weapon.rect.copy()
                draw_rect.center = offset_pos
                surface.blit(weapon.image, draw_rect)

            # Always draw projectiles regardless of weapon visibility

            for projectile in weapon.attack.projectiles:
                proj_offset_pos = (
                    int(projectile.rect.centerx + world_offset[0]),
                    int(projectile.rect.centery + world_offset[1])
                )
                proj_draw_rect = projectile.rect.copy()
                proj_draw_rect.center = proj_offset_pos
                surface.blit(projectile.image, proj_draw_rect)
