import math
import random
from typing import Tuple, Optional, Dict, Iterable

import pygame
import pygame_gui
from pygame_gui.core import ObjectID, IContainerLikeInterface, UIElement
from pygame_gui.core.interfaces import IUIManagerInterface

import trigonometry
import modules


# noinspection SpellCheckingInspection


class Ship:
    def __init__(self, name: str, weight: float, max_speed: float, max_shield: float, max_armor: float, max_hull: float,
                 img: str, pos: tuple, manager: pygame_gui.UIManager, cont: pygame_gui.elements.ui_vertical_scroll_bar,
                 team='player', scale=float(1), high_modules=None, mid_modules=None, low_modules=None,
                 high_module_slots=None):

        if high_module_slots is None:
            high_module_slots = []
        if high_modules is None:
            high_modules = []
        if mid_modules is None:
            mid_modules = []
        if low_modules is None:
            low_modules = []

        # Характеристики
        self.name = name
        self.weight = weight
        self.max_speed = max_speed

        self.max_shield = max_shield
        self.max_armor = max_armor
        self.max_hull = max_hull

        self.shield = max_shield
        self.armor = max_armor
        self.hull = max_hull

        self.team = team

        # Визуальные данные
        self.scale = scale
        self.img0 = pygame.image.load(img)
        self.img0 = pygame.transform.rotozoom(self.img0, 0, self.scale)
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
        self.dist_type = 'stop'
        self.dist_const = 0

        # Модули
        self.high_modules = high_modules
        self.high_module_slots = high_module_slots
        self.mid_modules = mid_modules
        self.low_modules = low_modules

        self.tags = []
        self.ui_container = None
        self.init_ui(manager, cont)

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
                if trigonometry.distance_between_points((self.x, self.y), (i.x, i.y)) < (
                        self.diagonal / 2 + i.diagonal / 2) and i != self:
                    strenght = (((self.diagonal / 2 + i.diagonal / 2) / trigonometry.distance_between_points(
                        (self.x, self.y), (i.x, i.y))) - 1) * 5
                    ang = trigonometry.angle_from_to_point((self.x, self.y), (i.x, i.y))
                    i.x -= trigonometry.clamp(-i.diagonal, 0.2 * self.weight * math.pow(strenght, 1.3) * -math.cos(
                        ang / 180 * math.pi), i.diagonal)
                    i.y -= trigonometry.clamp(-i.diagonal,
                                              0.2 * self.weight * math.pow(strenght,
                                                                           1.3) * math.sin(ang / 180 * math.pi),
                                              i.diagonal)
            except ZeroDivisionError:
                ang = random.uniform(0, 360)
                i.x -= trigonometry.clamp(0, 0.2 * self.weight * 27 * -math.cos(ang / 180 * math.pi),
                                          i.diagonal)
                i.y -= trigonometry.clamp(0, 0.2 * self.weight * 27 * math.sin(ang / 180 * math.pi),
                                          i.diagonal)
                i.speed *= 0.2

    def think(self, delta_time):
        # for i in self.mid_modules:
        #     if i.is_passive is False:
        #         i.passed_time +=

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
        spd_cof = 0.0166 / delta_time

        if self.dist_type == 'point' or self.dist_type == 'orbit':
            if (abs(self.angle - self.dist_dir) > 1
                    and trigonometry.distance_between_points((self.x, self.y), self.dist) >= self.max_speed * 8):
                if abs(self.angle - self.dist_dir) > 180:
                    t_angle = self.angle - 180 if self.angle > 180 else 360 - (180 - self.angle)
                    t_between = self.dist_dir - 180 if self.dist_dir > 180 else 360 - (180 - self.dist_dir)
                    self.angle = (((t_angle * self.weight * spd_cof + t_between)
                                   / (self.weight * spd_cof + 1)) + 180) % 360
                else:
                    self.angle = ((self.angle * self.weight * spd_cof + self.dist_dir)
                                  / (self.weight * spd_cof + 1)) % 360

        elif self.dist_type == 'distance':
            ang = trigonometry.angle_from_to_point(self.dist, (self.x, self.y))
            point = (self.dist[0] - self.dist_const * -math.cos(ang / 180 * math.pi), self.dist[1] - self.dist_const *
                     math.sin(ang / 180 * math.pi))
            if (abs(self.angle - self.dist_dir) > 1
                    and trigonometry.distance_between_points((self.x, self.y), point) >= self.max_speed * 5):
                if abs(self.angle - self.dist_dir) > 180:
                    t_angle = self.angle - 180 if self.angle > 180 else 360 - (180 - self.angle)
                    t_between = self.dist_dir - 180 if self.dist_dir > 180 else 360 - (180 - self.dist_dir)
                    self.angle = ((((t_angle * self.weight * spd_cof + t_between) / (self.weight * spd_cof + 1)) + 180)
                                  % 360)
                else:
                    self.angle = (((self.angle * self.weight * spd_cof + self.dist_dir) / (self.weight * spd_cof + 1))
                                  % 360)

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
        self.x += self.speed * math.cos(self.speed_dir / 180 * math.pi) * 60 * delta_time
        self.y += self.speed * -math.sin(self.speed_dir / 180 * math.pi) * 60 * delta_time

    def render(self, screen, scale, cam_pos):
        # Рендер подсказок
        pygame.draw.rect(screen, (0, 0, 255, 100),
                         ((self.dist[0] - 6) * scale + cam_pos[0] * scale,
                          (self.dist[1] - 6) * scale + cam_pos[1] * scale, 12, 12))

        # Рендер корабля
        img = pygame.transform.rotozoom(self.img0, self.angle, scale)
        rect = img.get_rect()
        rect.center = math.floor(self.x) * scale + cam_pos[0] * scale, math.floor(self.y) * scale + cam_pos[1] * scale
        screen.blit(img, rect)

        # Рендер пушек
        for i in range(len(self.high_modules)):
            if hasattr(self.high_modules[i], 'base_img'):
                center = trigonometry.rotate((0, 0),
                                             (self.high_module_slots[i][0], self.high_module_slots[i][1]),
                                             -math.radians(self.angle))

                img = pygame.transform.rotozoom(self.high_modules[i].base_img, self.angle, scale * 1.5)
                rect = img.get_rect()
                rect.center = ((math.floor(self.x) + cam_pos[0] + center[0]) * scale,
                               (math.floor(self.y) + cam_pos[1] + center[1]) * scale)
                screen.blit(img, rect)

                if self.high_modules[i].target is not None:
                    angle = trigonometry.angle_from_to_point((math.floor(self.x) + center[0],
                                                              math.floor(self.y) + center[1]),
                                                             (self.high_modules[i].target.x,
                                                              self.high_modules[i].target.y))
                else:
                    angle = self.angle
                img = pygame.transform.rotozoom(self.high_modules[i].gun_img, angle, scale * 1.5)
                rect = img.get_rect()
                rect.center = ((math.floor(self.x) + cam_pos[0] + center[0]) * scale,
                               (math.floor(self.y) + cam_pos[1] + center[1]) * scale)
                screen.blit(img, rect)

    def init_ui(self, manager, cont):
        if self.team == 'player':
            self.ui_container = pygame_gui.core.UIContainer(relative_rect=pygame.Rect((0, 0), (500, 70)),
                                                            manager=manager,
                                                            container=cont)
            res = trigonometry.calculate_res(len(self.high_modules))
            res_str = '_64' if res == 1 else '_32' if res == 2 else '_16'
            for rect, i in trigonometry.calculate_rects(len(self.high_modules), 70, 80):
                module = self.high_modules[i]
                UIButtonWithModule(
                    relative_rect=rect,
                    manager=manager,
                    text='21312312312',
                    container=self.ui_container,
                    object_id=ObjectID(class_id='@friendly_buttons', object_id='#' + module.img0 + res_str),
                    module=module,
                    self_ship=self)

            res = trigonometry.calculate_res(len(self.mid_modules))
            res_str = '_64' if res == 1 else '_32' if res == 2 else '_16'
            for rect, i in trigonometry.calculate_rects(len(self.mid_modules), 70, 160):
                module = self.mid_modules[i]
                UIButtonWithModule(
                    relative_rect=rect, manager=manager,
                    text='2312312312',
                    container=self.ui_container,
                    object_id=ObjectID(class_id='@friendly_buttons', object_id='#' + module.img0 + res_str),
                    module=module,
                    self_ship=self)

            res = trigonometry.calculate_res(len(self.low_modules))
            res_str = '_64' if res == 1 else '_32' if res == 2 else '_16'
            for rect, i in trigonometry.calculate_rects(len(self.low_modules), 70, 240):
                module = self.low_modules[i]
                UIButtonWithModule(
                    relative_rect=rect, manager=manager,
                    text=module.name,
                    container=self.ui_container,
                    object_id=ObjectID(class_id='@friendly_buttons', object_id='#' + module.img0 + res_str),
                    module=module,
                    self_ship=self)

            pygame_gui.elements.UIImage(relative_rect=pygame.Rect((0, 0), (70, 70)), manager=manager,
                                        image_surface=self.img0,
                                        container=self.ui_container)
            self.ui_container.hide()

    def show_ui(self, pos):
        self.ui_container.show()
        self.ui_container.set_relative_position((20, pos))

    def hide_ui(self):
        self.ui_container.hide()


class UIButtonWithModule(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect: pygame.Rect | Tuple[float, float] | pygame.Vector2,
                 text: str,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 tool_tip_text: str | None = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: ObjectID | str | None = None,
                 anchors: str | UIElement = None,
                 allow_double_clicks: bool = False,
                 generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
                 visible: int = 1,
                 *,
                 tool_tip_object_id: Optional[ObjectID] = None,
                 text_kwargs: Optional[Dict[str, str]] = None,
                 tool_tip_text_kwargs: Optional[Dict[str, str]] = None, module: modules.Module = None, self_ship):
        super().__init__(relative_rect, text, manager, container, tool_tip_text, starting_height, parent_element,
                         object_id, anchors, allow_double_clicks, generate_click_events_from, visible,
                         tool_tip_object_id=tool_tip_object_id, text_kwargs=text_kwargs,
                         tool_tip_text_kwargs=tool_tip_text_kwargs)
        self.module = module
        self.self_ship = self_ship


class UIButtonWithShip(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect: pygame.Rect | Tuple[float, float] | pygame.Vector2,
                 text: str,
                 manager: Optional[IUIManagerInterface] = None,
                 container: Optional[IContainerLikeInterface] = None,
                 tool_tip_text: str | None = None,
                 starting_height: int = 1,
                 parent_element: UIElement = None,
                 object_id: ObjectID | str | None = None,
                 anchors: str | UIElement = None,
                 allow_double_clicks: bool = False,
                 generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
                 visible: int = 1,
                 *,
                 tool_tip_object_id: Optional[ObjectID] = None,
                 text_kwargs: Optional[Dict[str, str]] = None,
                 tool_tip_text_kwargs: Optional[Dict[str, str]] = None, ship: Ship = None):
        super().__init__(relative_rect, text, manager, container, tool_tip_text, starting_height, parent_element,
                         object_id, anchors, allow_double_clicks, generate_click_events_from, visible,
                         tool_tip_object_id=tool_tip_object_id, text_kwargs=text_kwargs,
                         tool_tip_text_kwargs=tool_tip_text_kwargs)
        self.ship = ship
