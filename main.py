import math
import random

import pygame
import trigonometry
from ships import Ship

# noinspection SpellCheckingInspection

pygame.init()
screen = pygame.display.set_mode((1920, 900))
clock = pygame.time.Clock()
done = False
center = (910, 450)
all_ships = [Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(70, 2, 'textures/ships/test_ship_big.png', (random.uniform(-500, 500), random.uniform(-500, 500))),
             Ship(10, 10, 'textures/ships/test_ship.png', (random.uniform(-500, 500), random.uniform(-500, 500)))]
scale = 0.6
cam_x, cam_y = 500, 500
scroll_sense = 0.05

selected_ships = []
is_selecting = False
selecting_start = 0, 0
selecting_end = 0, 0
temp_selecting = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x, pygame.mouse.get_pos()[1] - cam_y
                    for i in selected_ships:
                        i.set_target((x * (1 / scale), y * (1 / scale)), 'orbit', 300)
            if event.key == pygame.K_f:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x, pygame.mouse.get_pos()[1] - cam_y
                    temp = 0
                    biggest = max(selected_ships, key=lambda x: x.diagonal).diagonal
                    for i in selected_ships:
                        i.set_target((x * (1 / scale) + biggest * 1.3 * (temp % 5),
                                      y * (1 / scale) + biggest * 1.3 * (temp // 5)), 'point')
                        temp += 1
            if event.key == pygame.K_e:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x, pygame.mouse.get_pos()[1] - cam_y
                    for i in selected_ships:
                        i.set_target((x * (1 / scale), y * (1 / scale)), 'distance', 300)
            if event.key == pygame.K_g:
                if len(selected_ships) != 0:
                    for i in selected_ships:
                        i.set_target((0, 0), 'stop', 300)
            if event.key == pygame.K_ESCAPE:
                selected_ships = []
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                is_selecting = True
                selecting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        if event.type == pygame.MOUSEBUTTONUP:
            if not pygame.mouse.get_pressed()[0]:
                is_selecting = False
        if event.type == pygame.MOUSEWHEEL:
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
    # Ввод
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]: cam_y += 8
    if pressed[pygame.K_s]: cam_y -= 8
    if pressed[pygame.K_a]: cam_x += 8
    if pressed[pygame.K_d]: cam_x -= 8
    # До сюда

    # Логика
    for r_ship in all_ships:
        r_ship.think(all_ships)
    for r_ship in all_ships:
        r_ship.physic(all_ships)
    # До сюда

    screen.fill((30, 30, 30))

    # Рендеринг
    for r_ship in all_ships:
        r_ship.render(screen, scale, (cam_x, cam_y))
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
    for i in selected_ships:
        pygame.draw.circle(screen, (100, 100, 255), (i.x * scale + cam_x, i.y * scale + cam_y),
                           (i.diagonal / 2) * scale, 5)
    temp_selecting = is_selecting
    # До сюда

    clock.tick(60)
    pygame.display.update()
