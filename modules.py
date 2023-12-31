import pygame
import random

import bullets
import trigonometry
from texture_manager import load_texture


class Module:
    def __init__(self, name: str, slot_type: str, img, target_type: str, cooldown: float):
        self.name = name
        self.slot_type = slot_type
        self.img0 = img
        self.img1 = load_texture('textures/modules/' + img + '.png')
        self.target_type = target_type
        self.target = None
        if cooldown < 0:
            self.is_passive = True
        else:
            self.cooldown = cooldown
            self.passed = cooldown
            self.active = False
            self.is_passive = False

    def activate(self, target):
        if self.active:
            self.target = None
            self.active = False
        else:
            if self.passed >= self.cooldown:
                self.active = True
                self.passed = self.cooldown * random.uniform(0, 0.15)
                self.target = target

    def use(self, target):
        pass

    def think(self, delta_time):
        if self.target is not None and self.target.hull == 0:
            self.active = False
        if not self.is_passive:
            self.passed += delta_time
            if self.active:
                if self.passed >= self.cooldown:
                    self.use(self.target)
                    self.passed = 0


class Turret(Module):
    def __init__(self, name: str, img, cooldown: float, gun_img, bullets_render=None, team='player',
                 gun_scale=float(1), distance=None):
        super().__init__(name, 'high', img, 'enemy', cooldown)
        self.gun_img = pygame.transform.rotozoom(load_texture(gun_img), 0, gun_scale)
        self.target = None
        self.bullets = bullets_render
        self.team = team
        self.x = 0
        self.y = 0
        self.angle = 0
        self.distance = distance

        self.cached_image_b = None
        self.cached_scaled_b = None
        self.cached_angle_b = 1999
        self.cached_scale_b = 0
        self.cached_image_g = None
        self.cached_scaled_g = None
        self.cached_angle_g = 1999
        self.cached_scale_g = 0

    def update_info(self, pos, angle):
        self.x, self.y = pos
        self.angle = angle
        if self.distance is not None and self.target is not None and self.active is True\
            and trigonometry.distance_between_points((self.x, self.y),
                                                     (self.target.x, self.target.y)) > self.distance:
            self.active = False

    def render(self, scale: float):
        if abs(scale - self.cached_scale_g) > 0.04:
            self.cached_scaled_g = pygame.transform.rotozoom(self.gun_img, 0, scale)
            self.cached_image_g = pygame.transform.rotate(self.cached_scaled_g, self.angle)
            self.cached_scale_g = scale
        if abs(self.angle - self.cached_angle_g) > 20:
            self.cached_image_g = pygame.transform.rotate(self.cached_scaled_g, self.angle)
            self.cached_angle_g = self.angle
        return self.cached_image_g


class StatisWebfier(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 'small_railgun', 1, 'textures/turrets/gun.png')

    def use(self, target):
        self.target.max_speed *= 0.3


class SmallRailgun(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 'small_railgun', 2, 'textures/turrets/gun.png',
                         bullets_render, team, 1.5, 2000)

    def use(self, target):
        self.bullets.append(bullets.SmallRailgunBullet((self.x, self.y), self.angle, self.team))


class MediumRailgun(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 'small_railgun', 2, 'textures/turrets/gun.png',
                         bullets_render, team, 1.5 * 1.75, 3500)

    def use(self, target):
        self.bullets.append(bullets.SmallRailgunBullet((self.x, self.y), self.angle, self.team))


class LargeRailgun(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 'small_railgun', 2, 'textures/turrets/gun.png',
                         bullets_render, team, 1.5 * 1.75 * 1.75, 7000)

    def use(self, target):
        self.bullets.append(bullets.SmallRailgunBullet((self.x, self.y), self.angle, self.team))

        
class SmallShieldBooster(Module):
    def __init__(self):
        super().__init__('heal', 'mid', 'small_shield_booster', 'self', 1)

    def use(self, target):
        target.shield += 200


class SmallShieldReinforcement(Module):
    def __init__(self):
        super().__init__('shd rein', 'low', 'small_shield_reinforcment', 'self', -1)
