import math
import random
import pygame
import json

import modules
import trigonometry
from ships import Ship
import pygame_gui

# noinspection SpellCheckingInspection


with open('buttons.json', 'w') as f:
    bb = dict()
    bb["@friendly_buttons"] = {"text_vert_alignment": "top"}
    bb['#button_64'] = {'colours': {"normal_border": "#333333",
                                 "hovered_border": "#333333",
                                 "disabled_border": "#333333",
                                 "selected_border": "#333333",
                                 "active_border": "#333333"},
                     'misc': {"shape": "ellipse", "border_width": "5"}}
    bb['#button_32'] = {'colours': {"normal_border": "#333333",
                                    "hovered_border": "#333333",
                                    "disabled_border": "#333333",
                                    "selected_border": "#333333",
                                    "active_border": "#333333"},
                        'misc': {"shape": "ellipse", "border_width": "2"}}
    bb['#button_16'] = {'colours': {"normal_border": "#333333",
                                    "hovered_border": "#333333",
                                    "disabled_border": "#333333",
                                    "selected_border": "#333333",
                                    "active_border": "#333333"},
                        'misc': {"shape": "ellipse", "border_width": "1"}}
    with open('modules', 'r') as m:
        for i in map(str.rstrip, m.readlines()):
            bb[f'#{i}_64'] = {'prototype': '#button_64',
                              'images': {
                                  "normal_image": {'path': f'textures/modules/{i}.png', "sub_surface_rect": "0,0,64,64"}}}
            bb[f'#{i}_32'] = {'prototype': '#button_32',
                              'images': {
                                  "normal_image": {'path': f'textures/modules/{i}.png', "sub_surface_rect": "64,0,32,32"}}}
            bb[f'#{i}_16'] = {'prototype': '#button_16',
                              'images': {
                                  "normal_image": {'path': f'textures/modules/{i}.png', "sub_surface_rect": "64,32,16,16"}}}

    json.dump(bb, f, ensure_ascii=False, indent=4)

pygame.init()
screen = pygame.display.set_mode((1920, 900))
manager = pygame_gui.UIManager((1920, 900), 'style.json')
manager.get_theme().load_theme('buttons.json')
background = pygame.Surface((1920, 1080))
background.fill(pygame.Color('#000000'))

clock = pygame.time.Clock()
done = False
center = (910, 450)
all_ships = [Ship(10, 10, 'textures/ships/test_ship.png', (0, 0), manager,
                  mid_modules=[modules.module('piska', img='small_shield_booster'), modules.module('piska', img='small_shield_booster'), modules.module('piska', img='small_shield_booster'),
                               modules.module('piska', img='small_shield_reinforcment')], high_modules=[modules.module('statis webfier', img='statis_webfire')]),
             Ship(70, 2, 'textures/ships/test_ship_big.png', (random.uniform(-500, 500), random.uniform(-500, 500)),
                  manager)]
for i in range(9):
    all_ships.append(
        Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500)), manager))
scale = 0.6
cam_x, cam_y = 0, 0
scroll_sense = 0.05
hello_button = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 0), (20, 20)), manager=manager, text='60')
selected_ships = []
is_selecting = False
selecting_start = 0, 0
selecting_end = 0, 0
temp_selecting = False
while not done:
    time_delta = clock.tick(60) / 1000.0

    # Ввод
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x, pygame.mouse.get_pos()[1] - cam_y
                    x, y = pygame.mouse.get_pos()[0] - cam_x, pygame.mouse.get_pos()[1] - cam_y
                    for i in all_ships:
                        if trigonometry.distance_between_points((i.x, i.y),
                                                                (x * (1 / scale), y * (1 / scale))) <= i.diagonal / 2:
                            for j in selected_ships:
                                j.set_target(i, 'orbit', 400)
                            break
                    else:
                        for i in selected_ships:
                            i.set_target((x * (1 / scale), y * (1 / scale)), 'orbit', 400)
            elif event.key == pygame.K_f:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x, pygame.mouse.get_pos()[1] - cam_y
                    for i in all_ships:
                        if trigonometry.distance_between_points((i.x, i.y),
                                                                (x * (1 / scale), y * (1 / scale))) <= i.diagonal / 2:
                            for j in selected_ships:
                                j.set_target(i, 'point')
                            break
                    else:
                        temp = 0
                        biggest = max(selected_ships, key=lambda x: x.diagonal).diagonal
                        for i in selected_ships:
                            i.set_target((x * (1 / scale) + biggest * 1.2 * (temp % 5),
                                          y * (1 / scale) + biggest * 1.2 * (temp // 5)), 'point')
                            temp += 1
            elif event.key == pygame.K_e:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x, pygame.mouse.get_pos()[1] - cam_y
                    for i in all_ships:
                        if trigonometry.distance_between_points((i.x, i.y),
                                                                (x * (1 / scale), y * (1 / scale))) <= i.diagonal / 2:
                            for j in selected_ships:
                                j.set_target(i, 'distance', 600)
                            break
                    else:
                        for i in selected_ships:
                            i.set_target((x * (1 / scale), y * (1 / scale)), 'distance', 300)
            elif event.key == pygame.K_g:
                if len(selected_ships) != 0:
                    for i in selected_ships:
                        i.set_target((0, 0), 'stop', 300)
            elif event.key == pygame.K_ESCAPE:
                for i in selected_ships:
                    i.hide_ui()
                selected_ships = []
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                is_selecting = True
                selecting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if not pygame.mouse.get_pressed()[0]:
                is_selecting = False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                if scale >= 0.5 + scroll_sense:
                    cam_x -= (1920 * (1 / scale) - 1920 * (1 / (scale + scroll_sense))) / 3
                    cam_y -= (900 * (1 / scale) - 900 * (1 / (scale + scroll_sense))) / 3
                scale += scroll_sense
                scale = trigonometry.clamp(0.5, scale, 2)
            else:
                if scale >= 0.5 + scroll_sense:
                    cam_x += (1920 * (1 / (scale - scroll_sense)) - 1920 * (1 / scale)) / 3
                    cam_y += (900 * (1 / (scale - scroll_sense)) - 900 * (1 / scale)) / 3
                scale -= scroll_sense
                scale = trigonometry.clamp(0.5, scale, 2)

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]: cam_y += 8
    if pressed[pygame.K_s]: cam_y -= 8
    if pressed[pygame.K_a]: cam_x += 8
    if pressed[pygame.K_d]: cam_x -= 8

    # Логика
    for r_ship in all_ships:
        r_ship.think(all_ships)
    for r_ship in all_ships:
        r_ship.physic(all_ships)
    # До сюда

    # Рендеринг кораблей
    screen.blit(background, (0, 0))
    for r_ship in all_ships:
        r_ship.render(screen, scale, (cam_x, cam_y))

    # Обработка выбора через ctrl
    if is_selecting:
        selecting_end = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        rect = pygame.rect.Rect(min(selecting_start[0], selecting_end[0]),
                                min(selecting_start[1], selecting_end[1]),
                                abs(selecting_start[0] - selecting_end[0]),
                                abs(selecting_start[1] - selecting_end[1]))
        pygame.draw.rect(screen, (100, 100, 255), rect, width=1)
        for i in all_ships:
            if rect.collidepoint(i.x * scale + cam_x, i.y * scale + cam_y):
                pygame.draw.circle(screen, (255, 255, 255), (i.x * scale + cam_x, i.y * scale + cam_y),
                                   (i.diagonal / 2) * scale, 2)
    if temp_selecting is True and is_selecting is False:
        for i in selected_ships:
            i.hide_ui()
        rect = pygame.rect.Rect(min(selecting_start[0], selecting_end[0]),
                                min(selecting_start[1], selecting_end[1]),
                                abs(selecting_start[0] - selecting_end[0]),
                                abs(selecting_start[1] - selecting_end[1]))
        ans = []
        for i in all_ships:
            if rect.collidepoint(i.x * scale + cam_x, i.y * scale + cam_y):
                ans.append(i)
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            selected_ships = set(selected_ships)
            selected_ships.update(ans)
            selected_ships = list(selected_ships)
        else:
            selected_ships = ans
        counter = 0
        for i in selected_ships:
            i.show_ui(manager, 70 * counter + 30)
            counter += 1

    for i in selected_ships:
        pygame.draw.circle(screen, (100, 100, 255), (i.x * scale + cam_x, i.y * scale + cam_y),
                           (i.diagonal / 2) * scale, 5)
    temp_selecting = is_selecting
    # Рендеринг интерфейса
    hello_button.set_text(str(trigonometry.clamp(0, int(clock.get_fps()), 60)))
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.update()
