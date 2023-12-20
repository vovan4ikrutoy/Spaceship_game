import pygame

import bullets


class Module:
    def __init__(self, name: str, slot_type: str, img, target_type: str, cooldown: float):
        self.name = name
        self.slot_type = slot_type
        self.img0 = img
        self.target_type = target_type
        if cooldown < 0:
            self.is_passive = True
        else:
            self.cooldown = cooldown
            self.is_passive = False

    def activate(self, target):
        print(f'hi from {self.name}!')


class Turret(Module):
    def __init__(self, name: str, img, cooldown: float, base_img, gun_img, bullets_render: list, team, base_scale=1, gun_scale=1):
        super().__init__(name, 'high', img, 'enemy', cooldown)
        self.base_img = pygame.transform.rotozoom(pygame.image.load(base_img), 0, base_scale)
        self.gun_img = pygame.transform.rotozoom(pygame.image.load(gun_img), 0, gun_scale)
        self.target = None
        self.bullets = bullets_render
        self.team = team
        self.x = 0
        self.y = 0
        self.angle = 0
        
    def activate(self, target):
        self.target = target

    def update_info(self, pos, angle):
        self.x, self.y = pos
        self.angle = angle


class StatisWebfier(Turret):
    def activate(self, target):
        super().activate(target)
        self.target.max_speed *= 0.3


class SmallRailgun(Turret):
    def activate(self, target):
        super().activate(target)
        self.bullets.append(bullets.SmallRailgunBullet((self.x, self.y), self.angle, self.team))

        
class SmallShieldBooster(Module):
    def __init__(self, name: str, img: str, cooldown: float):
        super().__init__(name, '1', img, 'self', cooldown)

    def activate(self, target):
        pass