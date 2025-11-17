import pygame

from game.systems.projectile import Projectile


class Attack:
    def __init__(self, weapon):
        self.weapon = weapon
        self.attack_counter = 0
        self.timer = 0.0
        self.attack_duration = weapon.attack_duration

        self.projectiles = pygame.sprite.Group()

    def execute(self):
        # Placeholder for attack logic
        self.attack_counter += 1
        if self.weapon.type == "melee":
            self.weapon.visible = False
        if self.weapon.targets:
            for target_tuple in self.weapon.targets:
                # Extract enemy from (distance, enemy) tuple
                enemy = target_tuple[1]
                self.fire_projectile(enemy)

    def fire_projectile(self, target):
        projectile = Projectile(self, self.weapon, target, self.weapon.damage)
        self.projectiles.add(projectile)
        projectile.launch()
