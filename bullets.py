from pygame import image, transform
import math

import trigonometry


class Bullet:
    def __init__(self, pos, angle, radius, speed, damage, img, team):
        self.x = pos[0]
        self.y = pos[1]
        self.angle = angle
        self.radius = radius
        self.speed = speed
        self.damage = damage
        self.img0 = image.load(img)
        self.team = team
        self.dead = False

    def think(self, delta_time, all_ships):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed
        for ship in all_ships:
            if (ship.team != self.team
                    and (trigonometry.distance_between_points((self.x, self.y), (ship.x, ship.y))
                         <= ship.diagonal / 2 + self.radius)):
                self.dead = True

    def render(self, screen, scale, cam_pos):
        img = transform.rotozoom(self.img0, self.angle, scale)
        rect = img.get_rect()
        rect.center = math.floor(self.x) * scale + cam_pos[0] * scale, math.floor(self.y) * scale + cam_pos[1] * scale
        screen.blit(img, rect)


class SmallRailgunBullet(Bullet):
    def __init__(self, pos, angle, team):
        super().__init__(pos, angle, 10, 3, 25, 'textures/bullets/bullet.png', team)
