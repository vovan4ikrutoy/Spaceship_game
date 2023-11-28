import pygame


class Module:
    def __init__(self, name: str, slot_type: str, img='', cooldown: float = -1):
        self.name = name
        self.slot_type = slot_type
        self.img0 = img
        if cooldown < 0:
            self.is_passive = True
        else:
            self.cooldown = cooldown
            self.is_passive = False

    def activate(self, target):
        print(f'hi from {self.name}!')


class StatisWebfier(Module):
    def activate(self, target):
        target.ship.max_speed *= 0.3