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
        self.img1 = load_texture('textures/modules/' + img)
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

    def affect(self, ship):
        pass

    def use(self, target):
        pass

    def think(self, delta_time):
        if self.target is not None and self.target.hull == 0:
            self.active = False
            self.target = None
        if not self.is_passive:
            self.passed += delta_time
            if self.active:
                if self.passed >= self.cooldown:
                    self.use(self.target)
                    self.passed = 0


class Turret(Module):
    def __init__(self, name: str, cooldown: float, gun_img, bullets_render=None, team='player',
                 gun_scale=float(1), distance=None):
        super().__init__(name, 'high', 'turret.png', 'enemy', cooldown)
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
        if abs(self.angle - self.cached_angle_g) > 5:
            self.cached_image_g = pygame.transform.rotate(self.cached_scaled_g, self.angle)
            self.cached_angle_g = self.angle
        return self.cached_image_g


class StatisWebfier(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 1, 'textures/turrets/gun.png')

    def use(self, target):
        self.target.max_speed *= 0.3


class SmallRailgun(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 1, 'textures/turrets/small_railgun.png',
                         bullets_render, team, 2, 1500)

    def use(self, target):
        self.bullets.append(bullets.SmallRailgunBullet((self.x, self.y),
                                                       self.angle + random.uniform(-15, 15), self.team))


class MediumRailgun(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 3.5, 'textures/turrets/medium_railgun.png',
                         bullets_render, team, 1.5 * 1.75, 2800)

    def use(self, target):
        self.bullets.append(bullets.MediumRailgunBullet((self.x, self.y),
                                                        self.angle + random.uniform(-5, 5), self.team))


class LargeRailgun(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small railgun', 2, 'textures/turrets/gun.png',
                         bullets_render, team, 1.5 * 1.75 * 1.75, 1500)

    def use(self, target):
        self.bullets.append(bullets.SmallRailgunBullet((self.x, self.y), self.angle, self.team))


class SmallRocketLauncher(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small rck launc', 4, 'textures/turrets/small_rocket_l.png',
                         bullets_render, team, 2, 3000)

    def use(self, target):
        self.bullets.append(bullets.SmallRocket((self.x, self.y), self.angle, self.team, target))


class Flamethrower(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('flamethrower', 0.1, 'textures/turrets/flame_throw.png',
                         bullets_render, team, 2, 1450)

    def use(self, target):
        self.bullets.append(bullets.Flame((self.x, self.y), self.angle + random.uniform(-9, 9), self.team))


class MediumRocketLauncher(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('small rck launc', 6, 'textures/turrets/medium_rocket_l.png',
                         bullets_render, team, 2.5, 4000)

    def use(self, target):
        self.bullets.append(bullets.MediumRocket((self.x, self.y), self.angle, self.team, target))


class IonGun(Turret):
    def __init__(self, bullets_render: list, team: str):
        super().__init__('ion gun', 1.5, 'textures/turrets/ion_gun.png',
                         bullets_render, team, 2, 2000)

    def use(self, target):
        self.bullets.append(bullets.IonBullet((self.x, self.y), self.angle, self.team))

        
class ShieldBooster(Module):
    def __init__(self, heal=50):
        super().__init__('heal', 'mid', 'small_shield_booster.png',
                         'self', 3.5)
        self.heal = heal

    def use(self, target):
        target.shield = trigonometry.clamp(0, target.shield + target.max_shield * 0.15, target.max_shield)


class ShieldReinforcement(Module):
    def __init__(self):
        super().__init__('shd rein', 'low', 'small_shield_reinforcment.png',
                         'self', -1)

    def affect(self, ship):
        ship.max_shield *= 1.2
        ship.shield = ship.max_shield


class ArmorRein(Module):
    def __init__(self):
        super().__init__('arm rein', 'low', 'arm_rein.png',
                         'self', -1)

    def affect(self, ship):
        ship.max_armor *= 1.15
        ship.armor = ship.max_armor


class ArmorRepair(Module):
    def __init__(self):
        super().__init__('arm rein', 'mid', 'armor_rep.png',
                         'self', 5)

    def use(self, target):
        target.armor = trigonometry.clamp(0, target.armor + target.max_armor * 0.15, target.max_armor)


class Acceleration(Module):
    def __init__(self):
        super().__init__('accel', 'low', 'ab.png',
                         'self', -1)

    def affect(self, ship):
        ship.max_speed *= 1.3
