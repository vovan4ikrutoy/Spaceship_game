import pygame.transform
import math

import trigonometry
from texture_manager import load_texture


class Bullet:
    def __init__(self, pos, angle: float, radius: float, speed: float, damage: float, lifetime: float, img: str,
                 team: str):
        self.x = pos[0]
        self.y = pos[1]
        self.angle = angle
        self.radius = radius
        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime
        self.passed = 0
        self.img0 = load_texture(img)
        self.team = team
        self.dead = False

        self.cached_image = None
        self.cached_scale = 0

    def think(self, delta_time, all_ships):
        self.x += math.cos(math.radians(self.angle)) * self.speed * (delta_time / 0.01666)
        self.y -= math.sin(math.radians(self.angle)) * self.speed * (delta_time / 0.01666)
        self.passed += delta_time
        if self.passed >= self.lifetime:
            self.dead = True
        for ship in all_ships:
            if (ship.team != self.team
                    and (trigonometry.distance_between_points((self.x, self.y), (ship.x, ship.y))
                         <= ship.diagonal / 2 + self.radius)):
                self.impact(ship, all_ships)

    def render(self, screen, scale, cam_pos):
        if abs(self.cached_scale - scale) > 0.04:
            self.cached_image = pygame.transform.rotozoom(self.img0, self.angle, scale)
        img = self.cached_image
        rect = img.get_rect()
        rect.center = math.floor(self.x) * scale + cam_pos[0] * scale, math.floor(self.y) * scale + cam_pos[1] * scale
        screen.blit(img, rect)

    def impact(self, ship, all_ships):
        ship.take_damage(self.damage)
        self.dead = True


class SmallRailgunBullet(Bullet):
    def __init__(self, pos, angle, team):
        super().__init__(pos, angle, 20, 20, 25, 1.1, 'textures/bullets/bullet.png', team)
