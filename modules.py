import pygame
import random

import bullets


class Module:
    def __init__(self, name: str, slot_type: str, img, target_type: str, cooldown: float):
        self.name = name
        self.slot_type = slot_type
        self.img0 = img
        self.img1 = pygame.image.load('textures/modules/' + img + '.png')
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
                self.passed = 0
                self.target = target

    def use(self, target):
        pass

    def think(self, delta_time):
        if not self.is_passive:
            self.passed += delta_time * random.uniform(0.95, 1.05)
            if self.active:
                if self.passed >= self.cooldown:
                    self.use(self.target)
                    self.passed = 0


class Turret(Module):
    def __init__(self, name: str, img, cooldown: float, base_img, gun_img, bullets_render=None, team='player', base_scale=1, gun_scale=1):
        super().__init__(name, 'high', img, 'enemy', cooldown)
        self.base_img = pygame.transform.rotozoom(pygame.image.load(base_img), 0, base_scale)
        self.gun_img = pygame.transform.rotozoom(pygame.image.load(gun_img), 0, gun_scale)
        self.target = None
        self.bullets = bullets_render
        self.team = team
        self.x = 0
        self.y = 0
        self.angle = 0

    def update_info(self, pos, angle):
        self.x, self.y = pos
        self.angle = angle


class StatisWebfier(Turret):
    def __init__(self):
        super().__init__('small railgun', 'small_railgun', 1,
                         'textures/turrets/basic_base.png', 'textures/turrets/gun.png')

    def use(self, target):
        self.target.max_speed *= 0.3


class SmallRailgun(Turret):
    def __init__(self, bullets_render: list, team: str, cooldown=1.0):
        super().__init__('small railgun', 'small_railgun', cooldown,
                         'textures/turrets/basic_base.png', 'textures/turrets/gun.png',
                         bullets_render, team)

    def use(self, target):
        self.bullets.append(bullets.SmallRailgunBullet((self.x, self.y), self.angle, self.team))

        
class SmallShieldBooster(Module):
    def __init__(self, cooldown=1.0):
        super().__init__('heal', 'mid', 'small_shield_booster', 'self', cooldown)

    def use(self, target):
        target.shield += 200


class SmallShieldReinforcement(Module):
    def __init__(self):
        super().__init__('shd rein', 'low', 'small_shield_reinforcment', 'self', -1)
