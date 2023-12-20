import time

import pygame
import json

import modules
import trigonometry
import ships
import pygame_gui

# noinspection SpellCheckingInspection


# Иницалиазация файла стиля кнопок
with open('buttons.json', 'w') as f:
    bb = dict()
    bb["@friendly_buttons"] = dict()
    bb['#button_64'] = {'colours': {"normal_border": "#333333",
                                    "hovered_border": "#333333",
                                    "disabled_border": "#333333",
                                    "selected_border": "#333333",
                                    "active_border": "#333333"},
                        'misc': {"shape": "ellipse", "border_width": "4"}}
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
    with open('modules.txt', 'r') as m:
        for i in map(str.rstrip, m.readlines()):
            bb[f'#{i}_64'] = {'prototype': '#button_64',
                              'images': {
                                  "normal_image": {'path': f'textures/modules/{i}.png',
                                                   "sub_surface_rect": "0,0,64,64"}}}
            bb[f'#{i}_32'] = {'prototype': '#button_32',
                              'images': {
                                  "normal_image": {'path': f'textures/modules/{i}.png',
                                                   "sub_surface_rect": "64,0,32,32"}}}
            bb[f'#{i}_16'] = {'prototype': '#button_16',
                              'images': {
                                  "normal_image": {'path': f'textures/modules/{i}.png',
                                                   "sub_surface_rect": "64,32,16,16"}}}

    json.dump(bb, f, ensure_ascii=False, indent=4)

# Иницализация игры и интерфейса
pygame.init()
screen = pygame.display.set_mode((1920, 900))
manager = pygame_gui.UIManager((1920, 900), 'style.json')
manager.get_theme().load_theme('buttons.json')
background = pygame.image.load('textures/UI/bg.jpg')
fps_counter = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 0), (20, 20)), manager=manager, text='60')
clock = pygame.time.Clock()
done = False
center = (910, 450)
ui_scroll = pygame_gui.elements.UIScrollingContainer(pygame.Rect(0, 0, 500, 900), manager)
ui_scroll.set_scrollable_area_dimensions((0, 0))

# Важно! Список пуль для обработки, он общий для всех кораблей и их модулей
bullets = []

all_ships = \
    [ships.Ship(name='player ship', weight=5, max_speed=5, max_shield=700, max_armor=300, max_hull=200,
                img='textures/ships/test_ship.png', pos=(0, 0), manager=manager, cont=ui_scroll, team='player',
                scale=2,
                high_modules=[modules.StatisWebfier('statis web', 'statis_webfire',
                                                    1, 'textures/turrets/basic_base.png',
                                                    'textures/turrets/gun.png', bullets, 'player'),
                              modules.SmallRailgun('railgun', 'small_railgun',
                                                   1, 'textures/turrets/basic_base.png',
                                                   'textures/turrets/gun.png', bullets, 'player')],
                mid_modules=[modules.SmallShieldBooster('heal', 'small_shield_booster', 1)
                             for _ in range(4)], high_module_slots=[(-25, -42), (-25, 42)])
     for _ in range(5)]
for _ in range(1):
    all_ships.append(ships.Ship(name='enemy ship', weight=20, max_speed=2, max_shield=1500, max_armor=800, max_hull=350,
                                img='textures/ships/test_enemy.png', pos=(300, 0), manager=manager, cont=ui_scroll,
                                team='enemy', scale=3,
                                high_modules=[modules.StatisWebfier('statis web', 'statis_webfire', 1,
                                                                    'textures/turrets/basic_base.png',
                                                                    'textures/turrets/gun.png', bullets, 'player')],
                                mid_modules=[modules.SmallShieldBooster('heal', 'small_shield_booster', 1) for _ in
                                             range(4)], high_module_slots=[(0, 0)]))
game_speed = 1

# Камера
scale = 0.6
cam_x, cam_y = 0, 0
scroll_sense = 0.05
min_zoom, max_zoom = 0.1, 1

# Выбор кораблей
selected_ships = []
is_selecting = False
selecting_start = 0, 0
selecting_end = 0, 0
temp_selecting = False

# Захват цели
targets = []
now_targeting = dict()
is_targeting = False
targeting_start = 0, 0
targeting_end = 0, 0
temp_targeting = False
active_target = None

while not done:
    time_delta = clock.tick(60) / 1000.0

    # Ввод
    for event in pygame.event.get():
        manager.process_events(event)
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x * scale, pygame.mouse.get_pos()[1] - cam_y * scale
                    for i in all_ships:
                        if trigonometry.distance_between_points((i.x, i.y),
                                                                (x * (1 / scale), y * (1 / scale))) <= i.diagonal / 2:
                            for j in selected_ships:
                                if i != j:
                                    j.set_target(i, 'orbit', 400)
                                else:
                                    j.set_target(i, 'stop')
                            break
                    else:
                        for i in selected_ships:
                            i.set_target((x * (1 / scale), y * (1 / scale)), 'orbit', 400)
            elif event.key == pygame.K_f:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x * scale, pygame.mouse.get_pos()[1] - cam_y * scale
                    for i in all_ships:
                        if trigonometry.distance_between_points((i.x, i.y),
                                                                (x * (1 / scale), y * (1 / scale))) <= i.diagonal / 2:
                            for j in selected_ships:
                                if j != i:
                                    j.set_target(i, 'point')
                                else:
                                    j.set_target(i, 'stop')
                            break
                    else:
                        temp = 0
                        biggest = max(selected_ships, key=lambda ship: ship.diagonal).diagonal
                        for i in selected_ships:
                            i.set_target((x * (1 / scale) + biggest * 1.2 * (temp % 5),
                                          y * (1 / scale) + biggest * 1.2 * (temp // 5)), 'point')
                            temp += 1
            elif event.key == pygame.K_e:
                if len(selected_ships) != 0:
                    x, y = pygame.mouse.get_pos()[0] - cam_x * scale, pygame.mouse.get_pos()[1] - cam_y * scale
                    for i in all_ships:
                        if trigonometry.distance_between_points((i.x, i.y),
                                                                (x * (1 / scale), y * (1 / scale))) <= i.diagonal / 2:
                            for j in selected_ships:
                                if i != j:
                                    j.set_target(i, 'distance', 600)
                                else:
                                    j.set_target(i, 'stop')
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
                    ui_scroll.set_scrollable_area_dimensions((0, 0))
                selected_ships = []
            elif event.key == pygame.K_c:
                targets = []
                now_targeting = dict()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                is_selecting = True
                selecting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            elif pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LSHIFT]:
                is_targeting = True
                targeting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            if not pygame.mouse.get_pressed()[0] and is_selecting:
                is_selecting = False
            if not pygame.mouse.get_pressed()[0] and is_targeting:
                is_targeting = False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                if scale <= max_zoom - scroll_sense:
                    cam_x -= (1920 * (1 / scale) - 1920 * (1 / (scale + scroll_sense))) / 3
                    cam_y -= (900 * (1 / scale) - 900 * (1 / (scale + scroll_sense))) / 3
                    scale += scroll_sense
                    scale = trigonometry.clamp(min_zoom, scale, max_zoom)
            else:
                if scale >= min_zoom + scroll_sense:
                    cam_x += (1920 * (1 / (scale - scroll_sense)) - 1920 * (1 / scale)) / 3
                    cam_y += (900 * (1 / (scale - scroll_sense)) - 900 * (1 / scale)) / 3
                    scale -= scroll_sense
                    scale = trigonometry.clamp(min_zoom, scale, max_zoom)
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if type(event.ui_element) == ships.UIButtonWithModule:
                if event.ui_element.module.target_type == 'enemy':
                    if active_target is not None:
                        event.ui_element.module.activate(active_target.ship)
                elif event.ui_element.module.target_type == 'self':
                    event.ui_element.module.activate(event.ui_element.self_ship)
            elif type(event.ui_element) == ships.UIButtonWithShip:
                active_target = event.ui_element

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]:
        cam_y += 8
    if pressed[pygame.K_s]:
        cam_y -= 8
    if pressed[pygame.K_a]:
        cam_x += 8
    if pressed[pygame.K_d]:
        cam_x -= 8

    # Логика
    for r_ship in all_ships:
        r_ship.think(time_delta * game_speed)
        r_ship.physic(all_ships)
    for bullet in bullets:
        if bullet.dead:
            bullets.remove(bullet)
        else:
            bullet.think(time_delta * game_speed, all_ships)
    # До сюда

    # Рендеринг кораблей
    start = time.time()
    screen.blit(background, (0, 0))
    # threads = [Thread(target=r_ship.render, args=(screen, scale, (cam_x, cam_y),)) for r_ship in all_ships]
    # for t in threads:
    #     t.start()
    # for t in threads:
    #     t.join()
    camera_rect = pygame.Rect((-cam_x - 200, -cam_y - 200, 2520 / scale, 1300 / scale))
    things_for_render = []
    for i in all_ships:
        if camera_rect.collidepoint(i.x, i.y):
            things_for_render.append(i)
    for i in bullets:
        if camera_rect.collidepoint(i.x, i.y):
            things_for_render.append(i)
    for r_ship in things_for_render:
        r_ship.render(screen, scale, (cam_x, cam_y))

    # Обработка выбора кораблей через ctrl
    if is_selecting and not is_targeting:
        selecting_end = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        rect = pygame.rect.Rect(min(selecting_start[0], selecting_end[0]),
                                min(selecting_start[1], selecting_end[1]),
                                abs(selecting_start[0] - selecting_end[0]),
                                abs(selecting_start[1] - selecting_end[1]))
        pygame.draw.rect(screen, (100, 100, 255), rect, width=1)
        for i in all_ships:
            if i.team == 'player' and rect.collidepoint(i.x * scale + cam_x * scale, i.y * scale + cam_y * scale):
                pygame.draw.circle(screen, (255, 255, 255), (i.x * scale + cam_x * scale, i.y * scale + cam_y * scale),
                                   (i.diagonal / 2) * scale, 2)
    if temp_selecting is True and is_selecting is False and not is_targeting:
        for i in selected_ships:
            i.hide_ui()
        rect = pygame.rect.Rect(min(selecting_start[0], selecting_end[0]),
                                min(selecting_start[1], selecting_end[1]),
                                abs(selecting_start[0] - selecting_end[0]),
                                abs(selecting_start[1] - selecting_end[1]))
        ans = []
        for i in all_ships:
            if i.team == 'player' and rect.collidepoint(i.x * scale + cam_x * scale, i.y * scale + cam_y * scale):
                ans.append(i)
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            selected_ships = set(selected_ships)
            selected_ships.update(ans)
            selected_ships = list(selected_ships)
        else:
            selected_ships = ans
        counter = 0
        for i in selected_ships:
            i.show_ui(70 * counter + 20)
            counter += 1
        ui_scroll.set_scrollable_area_dimensions((450, trigonometry.clamp(900, 70 * counter + 20, 9999)))

    # Обработка выбора целей через shift
    if is_targeting and not is_selecting:
        targeting_end = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
        rect = pygame.rect.Rect(min(targeting_start[0], targeting_end[0]),
                                min(targeting_start[1], targeting_end[1]),
                                abs(targeting_start[0] - targeting_end[0]),
                                abs(targeting_start[1] - targeting_end[1]))
        pygame.draw.rect(screen, (255, 100, 100), rect, width=1)
        for i in all_ships:
            if i.team == 'enemy' and rect.collidepoint(i.x * scale + cam_x * scale, i.y * scale + cam_y * scale):
                pygame.draw.circle(screen, (255, 255, 255), (i.x * scale + cam_x * scale, i.y * scale + cam_y * scale),
                                   (i.diagonal / 2) * scale, 2)
    if temp_targeting is True and is_targeting is False and not is_selecting:
        rect = pygame.rect.Rect(min(targeting_start[0], targeting_end[0]),
                                min(targeting_start[1], targeting_end[1]),
                                abs(targeting_start[0] - targeting_end[0]),
                                abs(targeting_start[1] - targeting_end[1]))
        ans = []
        for i in all_ships:
            if i.team == 'enemy' and rect.collidepoint(i.x * scale + cam_x * scale, i.y * scale + cam_y * scale):
                ans.append(i)
        for i in ans:
            if now_targeting.get(i) is None and i not in targets and len(now_targeting) + len(targets) < 5:
                now_targeting[i] = 5

    for i in selected_ships:
        pygame.draw.circle(screen, (100, 100, 255), (i.x * scale + cam_x * scale, i.y * scale + cam_y * scale),
                           (i.diagonal / 2) * scale, 5)
    for i in now_targeting:
        pygame.draw.circle(screen, (105, 105, 105), (i.x * scale + cam_x * scale, i.y * scale + cam_y * scale),
                           (i.diagonal / 1.8) * scale, 5)
    for i in targets:
        pygame.draw.circle(screen, (155, 155, 155), (i.x * scale + cam_x * scale, i.y * scale + cam_y * scale),
                           (i.diagonal / 1.9) * scale, 5)
    if active_target is not None:
        pygame.draw.circle(screen, (155, 155, 155), (active_target.rect.x + 50, active_target.rect.y + 50),
                           55, 3)
    temp_selecting = is_selecting
    temp_targeting = is_targeting
    ans = []
    for i in now_targeting.keys():
        now_targeting[i] -= time_delta
        if now_targeting[i] < 0:
            ships.UIButtonWithShip(relative_rect=pygame.Rect(1300 - len(targets) * 120, 0, 100, 100), text=i.name,
                                   manager=manager, ship=i)
            targets.append(i)
            ans.append(i)
    for i in ans:
        del now_targeting[i]

    # Рендеринг интерфейса
    fps_counter.set_text(str(trigonometry.clamp(0, int(clock.get_fps()), 60)))
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.update()
