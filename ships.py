import math
import random
import pygame
import pygame_gui

import trigonometry
import modules
# noinspection SpellCheckingInspection


class Ship:
    def __init__(self, weight: int, max_speed: int, img: str, pos: (int, int), manager, high_modules: [modules.module]=[], mid_modules: [modules.module]=[], low_modules: [modules.module]=[]):
        # Характеристики
        self.weight = weight
        self.max_speed = max_speed

        # Визуальные данные
        self.img0 = pygame.image.load(img)
        self.img0.convert()
        self.to_render = []

        # Физические данные
        self.angle = 0
        self.x, self.y = pos
        self.rect0 = self.img0.get_rect()
        self.rect0.x, self.rect0.y = pos
        self.size = max(self.rect0.w, self.rect0.h) / 2
        self.acceleration = (max_speed / (weight / 10))
        self.speed = 0
        self.speed_dir = 0
        self.diagonal = math.sqrt(math.pow(self.rect0.width, 2) + math.pow(self.rect0.height, 2))

        # Логические данные
        self.target = None
        self.dist = pos
        self.dist_dir = self.angle
        self.dist_type = 'point'
        self.dist_const = 0

        # Модули
        self.high_modules = high_modules
        self.high_module_slots = []
        self.high_modules_ui = []
        self.mid_modiles = mid_modules
        self.low_modules = low_modules

        self.ui_container = None
        self.init_ui(manager)

    def set_target(self, target, dist_type: str, dist_const=0):
        if type(target) == tuple:
            self.dist = target
            self.target = None
        elif type(target) == Ship:
            self.dist = (target.x, target.y)
            self.target = target
        self.dist_type = dist_type
        self.dist_const = dist_const

    def physic(self, all_ships):
        for i in all_ships:
            try:
                if trigonometry.distance_between_points((self.x, self.y), (i.x, i.y)) < (self.diagonal / 2 + i.diagonal / 2) and i != self:
                    strenght = (((self.diagonal / 2 + i.diagonal / 2) / trigonometry.distance_between_points((self.x, self.y), (i.x, i.y))) - 1) * 5
                    ang = trigonometry.angle_from_to_point((self.x, self.y), (i.x, i.y))
                    i.x -= trigonometry.clamp(-i.diagonal, 0.2 * self.weight * math.pow(strenght, 3) * -math.cos(ang / 180 * math.pi), i.diagonal)
                    i.y -= trigonometry.clamp(-i.diagonal, 0.2 * self.weight * math.pow(strenght, 3) * math.sin(ang / 180 * math.pi), i.diagonal)
            except ZeroDivisionError:
                ang = random.uniform(0, 360)
                i.x -= trigonometry.clamp(0, 0.2 * self.weight * 27 * -math.cos(ang / 180 * math.pi),
                                          i.diagonal)
                i.y -= trigonometry.clamp(0, 0.2 * self.weight * 27 * math.sin(ang / 180 * math.pi),
                                          i.diagonal)
                i.speed *= 0.2

    def think(self, ships_around):
        if self.target is not None:
            self.dist = (self.target.x, self.target.y)

        # Вычисляем направление
        if self.dist_type == 'point':
            self.dist_dir = (trigonometry.angle_from_to_point((self.x, self.y), self.dist))

        elif self.dist_type == 'orbit':
            horizont = (trigonometry.angle_from_to_point((self.x, self.y), self.dist) + 90) % 360
            ang = trigonometry.angle_from_to_point(self.dist, (self.x, self.y))
            point = (self.dist[0] - self.dist_const * -math.cos(ang / 180 * math.pi), self.dist[1] - self.dist_const *
                     math.sin(ang / 180 * math.pi))
            vertical = trigonometry.angle_from_to_point((self.x, self.y), point)
            cof = math.pow(1 / (trigonometry.distance_between_points((self.x, self.y), point) / 200), 2)
            if abs(horizont - vertical) > 180:
                t_angle = horizont - 180 if horizont > 180 else 360 - (180 - horizont)
                t_between = vertical - 180 if vertical > 180 else 360 - (180 - vertical)
                self.dist_dir = (((t_angle * cof + t_between) / (1 + cof)) + 180) % 360
            else:
                self.dist_dir = ((horizont * cof + vertical) / (1 + cof)) % 360

        elif self.dist_type == 'distance':
            ang = trigonometry.angle_from_to_point(self.dist, (self.x, self.y))
            point = (self.dist[0] - self.dist_const * -math.cos(ang / 180 * math.pi), self.dist[1] - self.dist_const *
                     math.sin(ang / 180 * math.pi))
            self.dist_dir = trigonometry.angle_from_to_point((self.x, self.y), point)

        elif self.dist_type == 'stop':
            pass

        # Поворот корабля к точке назначения
        if self.dist_type == 'point' or self.dist_type == 'orbit':
            if abs(self.angle - self.dist_dir) > 1 and trigonometry.distance_between_points((self.x, self.y), self.dist) >= self.max_speed * 8:
                if abs(self.angle - self.dist_dir) > 180:
                    t_angle = self.angle - 180 if self.angle > 180 else 360 - (180 - self.angle)
                    t_between = self.dist_dir - 180 if self.dist_dir > 180 else 360 - (180 - self.dist_dir)
                    self.angle = (((t_angle * self.weight + t_between) / (self.weight + 1)) + 180) % 360
                else:
                    self.angle = ((self.angle * self.weight + self.dist_dir) / (self.weight + 1)) % 360

        elif self.dist_type == 'distance':
            ang = trigonometry.angle_from_to_point(self.dist, (self.x, self.y))
            point = (self.dist[0] - self.dist_const * -math.cos(ang / 180 * math.pi), self.dist[1] - self.dist_const *
                     math.sin(ang / 180 * math.pi))
            if abs(self.angle - self.dist_dir) > 1 and trigonometry.distance_between_points((self.x, self.y), point) >= self.max_speed * 5:
                if abs(self.angle - self.dist_dir) > 180:
                    t_angle = self.angle - 180 if self.angle > 180 else 360 - (180 - self.angle)
                    t_between = self.dist_dir - 180 if self.dist_dir > 180 else 360 - (180 - self.dist_dir)
                    self.angle = (((t_angle * self.weight + t_between) / (self.weight + 1)) + 180) % 360
                else:
                    self.angle = ((self.angle * self.weight + self.dist_dir) / (self.weight + 1)) % 360

        elif self.dist_type == 'stop':
            pass

        # Движение корабля
        if self.dist_type == 'point':
            if trigonometry.distance_between_points((self.x, self.y), self.dist) >= self.max_speed * 15:
                self.speed_dir = self.angle
                self.speed = trigonometry.clamp(0, self.speed + self.acceleration, self.max_speed)
            else:
                if trigonometry.distance_between_points((self.x, self.y), self.dist) >= self.max_speed * 8:
                    self.speed_dir = self.angle
                self.speed *= 0.95

        elif self.dist_type == 'orbit':
            self.speed_dir = self.angle
            self.speed = trigonometry.clamp(0, self.speed + self.acceleration, self.max_speed)

        elif self.dist_type == 'distance':
            ang = trigonometry.angle_from_to_point(self.dist, (self.x, self.y))
            point = (self.dist[0] - self.dist_const * -math.cos(ang / 180 * math.pi), self.dist[1] - self.dist_const *
                     math.sin(ang / 180 * math.pi))
            if trigonometry.distance_between_points((self.x, self.y), point) >= self.max_speed * 10:
                self.speed_dir = self.angle
                self.speed = trigonometry.clamp(0, self.speed + self.acceleration, self.max_speed)
            else:
                if trigonometry.distance_between_points((self.x, self.y), point) >= self.max_speed * 5:
                    self.speed_dir = self.angle
                self.speed *= 0.95

        elif self.dist_type == 'stop':
            self.speed *= 0.95
        self.x += self.speed * math.cos(self.speed_dir / 180 * math.pi)
        self.y += self.speed * -math.sin(self.speed_dir / 180 * math.pi)

    def render(self, screen, scale, cam_pos):
        # Рендеринг корабля
        img = pygame.transform.rotozoom(self.img0, self.angle, scale)
        rect = img.get_rect()
        rect.center = math.floor(self.x) * scale + cam_pos[0], math.floor(self.y) * scale + cam_pos[1]
        pygame.draw.rect(screen, (0, 0, 255, 100), ((self.dist[0] - 6) * scale + cam_pos[0], (self.dist[1] - 6) * scale + cam_pos[1], 12, 12))
        screen.blit(img, rect)
        # До сюда

    def init_ui(self, manager):
        self.ui_container = pygame_gui.core.UIContainer(relative_rect=pygame.Rect((-70, 0), (500, 70)), manager=manager,
                                                        anchors={'right': 'right', 'top': 'top'},
                                                        container=manager.root_container)
        temp_list = self.high_modules
        for rect in trigonometry.calculate_rects(len(self.high_modules), 70, 100):
            module = temp_list.pop()
            pygame_gui.elements.UIButton(
                relative_rect=rect,
                manager=manager,
                text=module.name,
                container=self.ui_container)

        temp_list = self.mid_modiles
        for rect in trigonometry.calculate_rects(len(self.mid_modiles), 70, 200):
            module = temp_list.pop()
            pygame_gui.elements.UIButton(relative_rect=rect, manager=manager,
                                         text=module.name,
                                         container=self.ui_container)

        temp_list = self.low_modules
        for rect in trigonometry.calculate_rects(len(self.low_modules), 70, 300):
            module = temp_list.pop()
            pygame_gui.elements.UIButton(relative_rect=rect, manager=manager,
                                         text=module.name,
                                         container=self.ui_container)
        pygame_gui.elements.UIImage(relative_rect=pygame.Rect((0, 0), (70, 70)), manager=manager,
                                    image_surface=self.img0,
                                    container=self.ui_container)
        self.ui_container.hide()

    def show_ui(self, manager, pos):
        self.ui_container.show()
        self.ui_container.set_relative_position((-400, pos))

    def hide_ui(self):
        self.ui_container.hide()
