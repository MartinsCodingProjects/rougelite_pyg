import pygame


class Projectile(pygame.sprite.Sprite):
    def __init__(self, attack, weapon, target, damage):
        super().__init__()
        self.weapon = weapon
        self.target = target
        self.damage = damage
        # Create a bright, visible projectile image
        # Create a copy of the weapon's image so it stays visible when weapon is hidden
        self.image = self.weapon.image.copy()
        # self.image.fill((255, 0, 255))  # Bright magenta - very visible
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2(self.weapon.pos)
        self.attack = attack
        self.direction = self.weapon.direction
        # reach target in attack duration
        self.speed = self.weapon.range / self.weapon.attack_duration
        # Give projectile its own timer
        self.timer = 0.0

        self.state = None

    def launch(self):
        if self.weapon.type == "melee":
            self.state = "melee_fired"

    def update(self, dt: float):
        self.timer += dt

        if self.state == "melee_fired":
            # Check if attack duration is over
            if self.timer >= self.weapon.attack_duration:
                self.kill()  # remove projectile
            else:
                # Keep moving in original direction
                movement = self.direction * self.speed * dt
                self.pos += movement
                self.rect.center = (int(self.pos.x), int(self.pos.y))

                # Check for collision with enemies
                self.check_collision()

    def check_collision(self):
        """Check collision with enemies and handle damage"""
        if not self.weapon.player or not self.weapon.player.enemies:
            return

        for enemy in self.weapon.player.enemies:
            if self.rect.colliderect(enemy.rect):
                self.on_hit(enemy)
                break  # Hit first enemy, stop checking

    def on_hit(self, enemy):
        """Handle projectile behavior when hitting an enemy"""

        # Deal damage to enemy
        enemy.take_damage(self.damage, self)

        if self.weapon.piercing_count == 0:
            self.kill()  # remove projectile
        else:
            self.weapon.piercing_count -= 1

        # Handle projectile behavior after hit
        if self.weapon.type == "melee":
            # Melee projectiles continue through (for now)
            # Could add different behaviors here like:
            # - self.kill() for weapons that stop on hit
            # - Bounce behavior
            # - Piercing behavior
            pass
