import random

import pygame.transform
import math

import trigonometry
from texture_manager import load_texture


class Bullet:
    def __init__(self, pos, angle: float, radius: float, speed: float, damage: float, lifetime: float, img: str,
                 team: str, size=float(1)):
        self.x = pos[0]
        self.y = pos[1]
        self.angle = angle
        self.radius = radius
        self.speed = speed * random.uniform(0.9, 1.1)
        self.damage = damage
        self.lifetime = lifetime
        self.passed = 0
        self.img0 = pygame.transform.rotozoom(load_texture(img), 0, size)
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


class Rocket(Bullet):
    def __init__(self, pos, angle: float, radius: float, speed: float, damage: float, lifetime: float, img: str,
                 team: str, target, explosion_radius, size=float(1)):
        self.target = target
        self.cached_scaled = pygame.transform.rotozoom(load_texture(img), 0, 1)
        self.cached_angle = angle
        self.size = size
        self.explosion_radius = explosion_radius
        super().__init__(pos, angle, radius, speed, damage, lifetime, img, team)
        self.cached_scale = 0

    def think(self, delta_time, all_ships):
        if self.target.hull > 0:
            self.angle = trigonometry.angle_from_to_point((self.x, self.y), (self.target.x, self.target.y))
        super().think(delta_time, all_ships)

    def render(self, screen, scale, cam_pos):
        if abs(self.cached_scale - scale) > 0.04:
            self.cached_scaled = pygame.transform.rotozoom(self.img0, 0, scale * self.size)
            self.cached_scale = scale
            self.cached_angle = 0
            self.cached_image = self.cached_scaled
        if abs(self.angle - self.cached_angle) > 5:
            self.cached_image = pygame.transform.rotate(self.cached_scaled, self.angle)
            self.cached_angle = self.angle
        img = self.cached_image
        rect = img.get_rect()
        rect.center = math.floor(self.x) * scale + cam_pos[0] * scale, math.floor(self.y) * scale + cam_pos[1] * scale
        screen.blit(img, rect)

    def impact(self, ship, all_ships):
        for i in all_ships:
            dist = trigonometry.distance_between_points((self.x, self.y), (i.x, i.y))
            if dist < self.explosion_radius:
                i.take_damage((1 - (dist / self.explosion_radius)) * self.damage)
        self.dead = True


class SmallRocket(Rocket):
    def __init__(self, pos, angle, team, target):
        super().__init__(pos, angle, 25, 12.5, 60, 20,
                         'textures/bullets/small_rocket.png', team, target, 300, 2)


class MediumRocket(Rocket):
    def __init__(self, pos, angle, team, target):
        super().__init__(pos, angle, 70, 7.5, 350, 20,
                         'textures/bullets/medium_rocket.png', team, target, 500, 2.5)


class SmallRailgunBullet(Bullet):
    def __init__(self, pos, angle, team):
        super().__init__(pos, angle, 20, 30, 25, 1.1,
                         'textures/bullets/small_railgun_b.png', team)


class Flame(Bullet):
    def __init__(self, pos, angle, team):
        super().__init__(pos, angle, 110, 60 * random.uniform(0.8, 1), 2.5, 0.55,
                         'textures/bullets/flame.png', team, 2.5)

    def think(self, delta_time, all_ships):
        self.speed *= 0.98
        super().think(delta_time, all_ships)

    def impact(self, ship, all_ships):
        ship.take_damage(self.damage)


class IonBullet(Bullet):
    def __init__(self, pos, angle, team):
        super().__init__(pos, angle, 50, 15, 5, 10,
                         'textures/bullets/ion_b.png', team)

    def impact(self, ship, all_ships):
        ship.max_speed *= 0.94
        ship.take_damage(self.damage)
        self.dead = True


class MediumRailgunBullet(Bullet):
    def __init__(self, pos, angle, team):
        super().__init__(pos, angle, 30, 75, 100, 1.1, 'textures/bullets/medium_railgun_b.png', team)
