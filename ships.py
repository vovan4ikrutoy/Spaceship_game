import math
import random
from copy import copy
from typing import Tuple, Optional, Dict, Iterable

import pygame
import pygame_gui
from pygame_gui.core import ObjectID, IContainerLikeInterface, UIElement
from pygame_gui.core.interfaces import IUIManagerInterface

import trigonometry
import modules
from texture_manager import load_texture


# noinspection SpellCheckingInspection


class CustomProgressBar(pygame_gui.elements.UIProgressBar):
    def status_text(self):
        return ''


class Ship:
    def __init__(self, name: str, weight: float, max_speed: float, max_shield: float, max_armor: float, max_hull: float,
                 img: str, pos: tuple, manager: pygame_gui.UIManager, cont: pygame_gui.elements.ui_vertical_scroll_bar,
                 bullets_render_list, team='player', scale=float(1), high_modules=None, mid_modules=None,
                 low_modules=None, high_module_slots=None, ai_type='normal'):

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
        self.img0 = load_texture(img)
        self.img0 = pygame.transform.rotozoom(self.img0, 0, self.scale)
        self.img0.convert()

        self.cached_image = None
        self.cached_scaled = None
        self.cached_scale = 500
        self.cached_angle = 999

        # Физические данные
        if team == 'player':
            self.angle = 0
        else:
            self.angle = 180
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
        self.targeting_ship = None
        self.orbit_dir = False
        self.AI_type = ai_type

        # Модули
        self.high_modules = high_modules
        self.high_module_slots = high_module_slots
        self.mid_modules = mid_modules
        self.low_modules = low_modules

        self.tags = []
        self.ui_container = None
        self.init_modules(bullets_render_list)
        self.init_ui(manager, cont)

    def take_damage(self, damage):
        temp_damage = damage
        if temp_damage > self.shield:
            temp_damage -= self.shield
            self.shield = 0
            if temp_damage > self.armor:
                temp_damage -= self.armor
                self.armor = 0
                if temp_damage >= self.hull:
                    self.hull = 0
                    if self.team == 'player':
                        self.ui_container.elements[0].set_image(load_texture('textures/UI/dead.png'))
                else:
                    self.hull -= temp_damage
            else:
                self.armor -= temp_damage
        else:
            self.shield -= temp_damage

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
                i.x -= trigonometry.clamp(0, 0.2 * self.weight * 2 * -math.cos(ang / 180 * math.pi),
                                          i.diagonal)
                i.y -= trigonometry.clamp(0, 0.2 * self.weight * 2 * math.sin(ang / 180 * math.pi),
                                          i.diagonal)
                i.speed *= 0.2
        self.x = trigonometry.clamp(0, self.x, 12000)
        self.y = trigonometry.clamp(0, self.y, 12000)

    def super_think(self, all_ships):
        self.update_ui()

        if self.team == 'enemy':
            if self.targeting_ship is None or random.randint(1, 10) == 1 or self.targeting_ship.hull == 0:
                player_ships = [x for x in copy(all_ships) if x.team == 'player']
                if len(player_ships) > 0:
                    self.targeting_ship = min(player_ships,
                                              key=lambda x: trigonometry.distance_between_points((self.x, self.y),
                                                                                                 (x.x, x.y)))
                    self.set_target(self.targeting_ship, 'orbit',
                                    min(self.high_modules, key=lambda x: x.distance).distance
                                    * (0.5 if self.AI_type == 'normal' else 0.9 if self.AI_type == 'sniper' else 0.25))
            elif random.randint(1, 150) == 1:
                player_ships = [x for x in copy(all_ships) if x.team == 'player']
                self.targeting_ship = random.choice(player_ships)
                self.set_target(self.targeting_ship, 'orbit', min(self.high_modules,
                                                                  key=lambda x: x.distance if x.__class__.__bases__[
                                                                                                  0] == modules.Turret
                                                                  else 999999).distance * 0.9)
            if self.targeting_ship is not None:
                for i in self.high_modules:
                    if i.__class__.__bases__[0] == modules.Turret:
                        if i.active is False:
                            i.activate(self.targeting_ship)
                        elif i.target != self.targeting_ship:
                            i.target = self.targeting_ship
            for i in self.mid_modules:
                if i.active is False:
                    i.activate(self)

    def think(self, delta_time):
        self.shield = trigonometry.clamp(0, self.shield + delta_time / 1 * self.max_shield / 60, self.max_shield)

        for i in range(len(self.high_module_slots)):
            if i < len(self.high_modules):
                self.high_modules[i].think(delta_time)
                center = trigonometry.rotate((0, 0),
                                             (self.high_module_slots[i][0], self.high_module_slots[i][1]),
                                             -math.radians(self.angle))
                if self.high_modules[i].target is not None:
                    angle = trigonometry.angle_from_to_point((math.floor(self.x) + center[0],
                                                              math.floor(self.y) + center[1]),
                                                             (self.high_modules[i].target.x,
                                                              self.high_modules[i].target.y))
                else:
                    angle = self.angle
                self.high_modules[i].update_info((math.floor(self.x) + center[0], math.floor(self.y) + center[1]),
                                                 angle)
        for i in self.mid_modules:
            i.think(delta_time)
        for i in self.low_modules:
            i.think(delta_time)

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
            if trigonometry.distance_between_points((self.x, self.y), self.dist) >= 0.4 * self.diagonal:
                self.speed_dir = self.angle
                self.speed = trigonometry.clamp(0, self.speed + self.acceleration, self.max_speed)
            else:
                if trigonometry.distance_between_points((self.x, self.y), self.dist) >= 0.2 * self.diagonal:
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

    def render_hints(self, screen, scale, cam_pos):
        # Рендер подсказок
        if self.dist_type == 'point':
            pygame.draw.rect(screen, (50, 50, 255),
                             ((self.dist[0] - 6) * scale + cam_pos[0] * scale,
                              (self.dist[1] - 6) * scale + cam_pos[1] * scale, 12, 12))
        elif self.dist_type == 'orbit' or self.dist_type == 'distance':
            pygame.draw.circle(screen, (50, 50, 255), (self.dist[0] * scale + cam_pos[0] * scale,
                                                       self.dist[1] * scale + cam_pos[1] * scale),
                               self.dist_const * scale,
                               3)

            ang = trigonometry.angle_from_to_point(self.dist, (self.x, self.y))
            point = (self.dist[0] - self.dist_const * -math.cos(ang / 180 * math.pi), self.dist[1] - self.dist_const *
                     math.sin(ang / 180 * math.pi))
            pygame.draw.circle(screen, (50, 50, 255), (point[0] * scale + cam_pos[0] * scale,
                                                       point[1] * scale + cam_pos[1] * scale),
                               10)
            pygame.draw.circle(screen, (50, 50, 255), (self.dist[0] * scale + cam_pos[0] * scale,
                                                       self.dist[1] * scale + cam_pos[1] * scale), 10)

    def render(self, screen, scale, cam_pos):
        # Рендер корабля
        self.update_ui()
        if abs(scale - self.cached_scale) > 0.04:
            self.cached_scaled = pygame.transform.rotozoom(self.img0, 0, scale)
            self.cached_image = pygame.transform.rotate(self.cached_scaled, self.angle)
            self.cached_scale = scale
        if abs(self.angle - self.cached_angle) > 200 / self.diagonal * 5:
            self.cached_image = pygame.transform.rotate(self.cached_scaled, self.angle)
            self.cached_angle = self.angle
        rect = self.cached_image.get_rect()
        rect.center = math.floor(self.x) * scale + cam_pos[0] * scale, math.floor(self.y) * scale + cam_pos[1] * scale
        screen.blit(self.cached_image, rect)

        # Рендер пушек
        for i in range(len(self.high_modules)):
            if type(self.high_modules[i]).__bases__[0] == modules.Turret:
                gun_img = self.high_modules[i].render(scale)
                center = trigonometry.rotate((0, 0),
                                             (self.high_module_slots[i][0], self.high_module_slots[i][1]),
                                             -math.radians(self.angle))

                if self.high_modules[i].target is not None:
                    angle = trigonometry.angle_from_to_point((math.floor(self.x) + center[0],
                                                              math.floor(self.y) + center[1]),
                                                             (self.high_modules[i].target.x,
                                                              self.high_modules[i].target.y))
                else:
                    angle = self.angle
                self.high_modules[i].update_info((math.floor(self.x) + center[0], math.floor(self.y) + center[1]),
                                                 angle)
                rect = gun_img.get_rect()
                rect.center = ((math.floor(self.x) + cam_pos[0] + center[0]) * scale,
                               (math.floor(self.y) + cam_pos[1] + center[1]) * scale)
                screen.blit(gun_img, rect)

    def init_modules(self, bullets_render_list):
        for i in range(len(self.high_modules)):
            if self.high_modules[i].__bases__[0] == modules.Turret:
                self.high_modules[i] = self.high_modules[i](bullets_render_list, self.team)
                self.high_modules[i].affect(self)
            else:
                self.high_modules[i] = self.high_modules[i]()
                self.high_modules[i].affect(self)
        for i in range(len(self.mid_modules)):
            self.mid_modules[i] = self.mid_modules[i]()
            self.mid_modules[i].affect(self)
        for i in range(len(self.low_modules)):
            self.low_modules[i] = self.low_modules[i]()
            self.low_modules[i].affect(self)

    def init_ui(self, manager, cont):
        if self.team == 'player':
            self.ui_container = pygame_gui.core.UIContainer(relative_rect=pygame.Rect((0, 0), (510, 100)),
                                                            manager=manager,
                                                            container=cont)

            pygame_gui.elements.UIImage(relative_rect=pygame.Rect((0, 0), (70, 70)), manager=manager,
                                        image_surface=self.img0,
                                        container=self.ui_container)

            CustomProgressBar(pygame.Rect(105, 0,
                                          70, 20),
                              manager, container=self.ui_container,
                              object_id=ObjectID(class_id='@boba',
                                                 object_id='#Shield_bar')).maximum_progress = self.max_shield
            CustomProgressBar(pygame.Rect(105, 30,
                                          70, 20),
                              manager, container=self.ui_container,
                              object_id=ObjectID(class_id='@boba',
                                                 object_id='#Armor_bar')).maximum_progress = self.max_armor
            CustomProgressBar(pygame.Rect(105, 60,
                                          70, 20),
                              manager, container=self.ui_container,
                              object_id=ObjectID(class_id='@boba',
                                                 object_id='#Hull_bar')).maximum_progress = self.max_hull
            pygame_gui.elements.UIImage(
                pygame.Rect(80, 0, 20, 20),
                load_texture('textures/UI/shd.png'), manager, container=self.ui_container)
            pygame_gui.elements.UIImage(
                pygame.Rect(80, 30, 20, 20),
                load_texture('textures/UI/arm.png'), manager, container=self.ui_container)
            pygame_gui.elements.UIImage(
                pygame.Rect(80, 60, 20, 20),
                load_texture('textures/UI/hll.png'), manager, container=self.ui_container)

            res = trigonometry.calculate_res(len(self.high_modules))
            res_str = '_64' if res == 1 else '_32' if res == 2 else '_16'
            for rect, i in trigonometry.calculate_rects(len(self.high_modules), 80, 180):
                module = self.high_modules[i]
                img = module.gun_img if module.__class__.__bases__[0] == modules.Turret else load_texture(module.img0)
                rect1 = pygame.Rect((rect.x + (1 - trigonometry.clamp(0.1, img.get_rect().width /
                                                                      img.get_rect().height, 1)) * rect.width * 0.5,
                                     rect.y + (1 - trigonometry.clamp(0.1, img.get_rect().height /
                                                                      img.get_rect().width, 1)) * rect.height * 0.5,
                                     rect.width * trigonometry.clamp(0, img.get_rect().width /
                                                                     img.get_rect().height, 1),
                                     rect.height * trigonometry.clamp(0, img.get_rect().height /
                                                                      img.get_rect().width, 1)))
                UIButtonWithModule(
                    relative_rect=rect,
                    manager=manager,
                    text='',
                    container=self.ui_container,
                    object_id=ObjectID(class_id='@friendly_buttons', object_id='#fixed' + res_str),
                    module=module,
                    self_ship=self)
                pygame_gui.elements.UIImage(rect1, img, manager, container=self.ui_container)

            res = trigonometry.calculate_res(len(self.mid_modules))
            res_str = '_64' if res == 1 else '_32' if res == 2 else '_16'
            for rect, i in trigonometry.calculate_rects(len(self.mid_modules), 80, 280):
                module = self.mid_modules[i]
                UIButtonWithModule(
                    relative_rect=rect, manager=manager,
                    text='',
                    container=self.ui_container,
                    object_id=ObjectID(class_id='@friendly_buttons', object_id='#fixed' + res_str),
                    module=module,
                    self_ship=self)
                pygame_gui.elements.UIImage(rect, module.img1, manager, container=self.ui_container)

            res = trigonometry.calculate_res(len(self.low_modules))
            res_str = '_64' if res == 1 else '_32' if res == 2 else '_16'
            for rect, i in trigonometry.calculate_rects(len(self.low_modules), 80, 380):
                module = self.low_modules[i]
                UIButtonWithModule(
                    relative_rect=rect, manager=manager,
                    text=module.name,
                    container=self.ui_container,
                    object_id=ObjectID(class_id='@friendly_buttons', object_id='#fixed' + res_str),
                    module=module,
                    self_ship=self)
                pygame_gui.elements.UIImage(rect, module.img1, manager, container=self.ui_container)
            self.ui_container.hide()

    def update_ui(self):
        if self.ui_container:
            progress_bars = sorted([x for x in self.ui_container.elements if x.__class__ == CustomProgressBar],
                                   key=lambda el: el.relative_rect.y)
            progress_bars[0].set_current_progress(self.shield / self.max_shield)
            progress_bars[1].set_current_progress(self.armor / self.max_armor)
            progress_bars[2].set_current_progress(self.hull / self.max_hull)

    def show_ui(self, pos):
        self.ui_container.show()
        self.ui_container.set_relative_position((20, pos))
        elements = []
        for i in self.ui_container.elements[1:]:
            if type(i) == UIButtonWithModule:
                elements.append(i)
        return [(button.module, (button.relative_rect.x, pos + button.relative_rect.y), button.relative_rect.width,
                 button)
                for button in elements]

    def hide_ui(self):
        if self.ui_container:
            self.ui_container.hide()


class Configuration:
    def __init__(self, name, for_ship, high_modules=None, mid_modules=None, low_modules=None):
        self.name = name
        self.for_ship = for_ship
        self.high_modules = high_modules
        self.mid_modules = mid_modules
        self.low_modules = low_modules
        if high_modules is None:
            high_modules = []
        if mid_modules is None:
            mid_modules = []
        if low_modules is None:
            low_modules = []


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


class UIButtonWithTarget(pygame_gui.elements.UIButton):
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
                 tool_tip_text_kwargs: Optional[Dict[str, str]] = None, ship: Ship = None,
                 img: pygame_gui.elements.UIImage = None):
        super().__init__(relative_rect, text, manager, container, tool_tip_text, starting_height, parent_element,
                         object_id, anchors, allow_double_clicks, generate_click_events_from, visible,
                         tool_tip_object_id=tool_tip_object_id, text_kwargs=text_kwargs,
                         tool_tip_text_kwargs=tool_tip_text_kwargs)
        self.ship = ship
        self.cont = img


class UIButtonWithContainer(pygame_gui.elements.UIButton):
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
                 tool_tip_text_kwargs: Optional[Dict[str, str]] = None, cont: pygame_gui.core.ui_container = None):
        super().__init__(relative_rect, text, manager, container, tool_tip_text, starting_height, parent_element,
                         object_id, anchors, allow_double_clicks, generate_click_events_from, visible,
                         tool_tip_object_id=tool_tip_object_id, text_kwargs=text_kwargs,
                         tool_tip_text_kwargs=tool_tip_text_kwargs)
        self.cont = cont


class UIButtonWithConfiguration(pygame_gui.elements.UIButton):
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
                 tool_tip_text_kwargs: Optional[Dict[str, str]] = None, conf: Configuration = None, ship: Ship = None):
        super().__init__(relative_rect, text, manager, container, tool_tip_text, starting_height, parent_element,
                         object_id, anchors, allow_double_clicks, generate_click_events_from, visible,
                         tool_tip_object_id=tool_tip_object_id, text_kwargs=text_kwargs,
                         tool_tip_text_kwargs=tool_tip_text_kwargs)
        self.configuration = conf
        self.ship = ship


class ShipLevelHolder:
    def __init__(self, name: str, weight: float, max_speed: float, max_shield: float, max_armor: float, max_hull: float,
                 img: str, pos: tuple, cost: int, team='player', high_modules=None, mid_modules=None,
                 low_modules=None, high_module_slots=None, scale=float(2), ai_type='normal'):
        self.name = name
        self.weight = weight
        self.max_speed = max_speed
        self.max_shield = max_shield
        self.max_armor = max_armor
        self.max_hull = max_hull
        self.img = img
        self.pos = pos
        self.cost = cost
        self.team = team
        self.scale = scale
        self.high_modules = high_modules
        self.mid_modules = mid_modules
        self.low_modules = low_modules
        self.high_module_slots = high_module_slots
        self.ai_type = ai_type

    def apply_configuration(self, configuration):
        self.high_modules = configuration.high_modules
        self.mid_modules = configuration.mid_modules
        self.low_modules = configuration.low_modules

    def to_ship(self, manager: pygame_gui.UIManager, cont: pygame_gui.elements.ui_vertical_scroll_bar,
                bullet_render_list):
        return Ship(self.name, self.weight, self.max_speed, self.max_shield, self.max_armor, self.max_hull, self.img,
                    self.pos, manager, cont, bullet_render_list, team=self.team, scale=self.scale,
                    high_modules=copy(self.high_modules), mid_modules=copy(self.mid_modules),
                    low_modules=copy(self.low_modules), high_module_slots=self.high_module_slots, ai_type=self.ai_type)


# Пресеты различный кораблей
class ScoutShip(ShipLevelHolder):
    def __init__(self, pos: tuple, team='player', high_modules=None, mid_modules=None, low_modules=None,
                 ai_type='normal'):
        if team == 'player':
            img = 'textures/ships/Scout_player.png'
        else:
            img = 'textures/ships/Scout_enemy.png'
        super().__init__('Разведчик', 5, 6.5, 50, 200, 100,
                         img, pos, 150, team, high_modules, mid_modules,
                         low_modules, [(-40, 0)], ai_type=ai_type)


class DestroyerShip(ShipLevelHolder):
    def __init__(self, pos: tuple, team='player', high_modules=None, mid_modules=None, low_modules=None,
                 ai_type='normal'):
        if team == 'player':
            img = 'textures/ships/Destroyer_player.png'
        else:
            img = 'textures/ships/Destroyer_enemy.png'
        super().__init__('Фрегат', 12, 4, 250, 700, 200,
                         img, pos, 500, team, high_modules, mid_modules,
                         low_modules, [(40, 0), (-10, 0), (-60, -0)], ai_type=ai_type)


class MinerShip(ShipLevelHolder):
    def __init__(self, pos: tuple, team='player', high_modules=None, mid_modules=None, low_modules=None,
                 ai_type='normal'):
        if team == 'player':
            img = 'textures/ships/Miner_player.png'
        else:
            img = 'textures/ships/Miner_enemy.png'
        super().__init__('Буровик', 30, 3.5, 350, 1400, 300,
                         img, pos, 1200, team, high_modules, mid_modules,
                         low_modules, [(0, 65), (-60, -60)], ai_type=ai_type)


class CarrierShip(ShipLevelHolder):
    def __init__(self, pos: tuple, team='player', high_modules=None, mid_modules=None, low_modules=None,
                 ai_type='normal'):
        if team == 'player':
            img = 'textures/ships/carrier_player.png'
        else:
            img = 'textures/ships/carrier_enemy.png'
        super().__init__('Эсминец', 70, 2.5, 1500, 3500, 500,
                         img, pos, 3500, team, high_modules, mid_modules,
                         low_modules, [(150, 0), (-25, 0), (-115, 0)], 1.5, ai_type=ai_type)


class DominatorShip(ShipLevelHolder):
    def __init__(self, pos: tuple, team='player', high_modules=None, mid_modules=None, low_modules=None,
                 ai_type='normal'):
        if team == 'player':
            img = 'textures/ships/Dominator_player.png'
        else:
            img = 'textures/ships/Dominator_enemy.png'
        super().__init__('Доминатор', 150, 1.5, 3000, 10000, 2000,
                         img, pos, 10000, team, high_modules, mid_modules,
                         low_modules, [(0, 0)], 3, ai_type=ai_type)
