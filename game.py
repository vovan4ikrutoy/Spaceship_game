from copy import copy
from typing import List

from levels import Level
from texture_manager import load_texture
import pygame
import pygame_gui


# noinspection SpellCheckingInspection


class CustomProgressBar(pygame_gui.elements.UIProgressBar):
    def status_text(self):
        return ''


def main(screen: pygame.Surface, level: Level, ship_configurations: dict):
    import json

    from pygame_gui.core import ObjectID

    import trigonometry
    import ships

    def redraw_targets():
        for trg in targets:
            if trg.ship not in all_ships:
                targets.remove(trg)
                trg.hide()
                trg.cont.hide()
        for trg in range(len(targets)):
            ex = width - (trg + 1) * 120 * min((width / 1920), (height / 1080))
            targets[trg].set_position((ex, 0))
            targets[trg].cont.set_position((ex, 0))

    def redraw_targets_hp(targetes):
        for target in targetes:
            progress_bars = sorted(target.cont.elements, key=lambda el: el.relative_rect.y)
            progress_bars[2].set_current_progress(target.ship.shield / target.ship.max_shield)
            progress_bars[4].set_current_progress(target.ship.armor / target.ship.max_armor)
            progress_bars[6].set_current_progress(target.ship.hull / target.ship.max_hull)

    # Иницалиазация файла стиля кнопок
    with open('data/buttons.json', 'w') as f:
        bb = dict()
        bb["@friendly_buttons"] = dict()
        bb['#button_64'] = {'colours': {"normal_border": "#333333",
                                        "normal_bg": "#444444"},
                            'misc': {"shape": "ellipse", "border_width": "4"}}
        bb['#button_32'] = {'colours': {"normal_border": "#333333",
                                        "normal_bg": "#444444"},
                            'misc': {"shape": "ellipse", "border_width": "2"}}
        bb['#button_16'] = {'colours': {"normal_border": "#333333",
                                        "normal_bg": "#444444"},
                            'misc': {"shape": "ellipse", "border_width": "1"}}
        with open('data/modules.txt', 'r') as m:
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
    width, height = screen.get_width(), screen.get_height()
    manager = pygame_gui.UIManager((width, height), 'data/style.json')
    manager.get_theme().load_theme('data/buttons.json')
    bg_img = pygame.image.load('textures/UI/bg.jpg')
    background = pygame.transform.scale(bg_img, (width, height))
    fps_counter = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 0), (20, 20)), manager=manager, text='60')
    clock = pygame.time.Clock()
    done = False
    ui_scroll = pygame_gui.elements.UIScrollingContainer(pygame.Rect(0, 0, 410, height), manager)
    ui_scroll.set_scrollable_area_dimensions((0, 0))

    all_buttons_container = pygame_gui.core.UIContainer(relative_rect=pygame.Rect(0, 0, 400, 70), manager=manager,
                                                        container=ui_scroll)
    all_high = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 20, 85, 50)), text='High',
                                            manager=manager, container=all_buttons_container,
                                            object_id=ObjectID(class_id='@friendly_buttons', object_id='#all_button'))
    all_mid = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 20, 85, 50)), text='Mid',
                                           manager=manager, container=all_buttons_container,
                                           object_id=ObjectID(class_id='@friendly_buttons', object_id='#all_button'))
    all_low = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 20, 85, 50)), text='Low',
                                           manager=manager, container=all_buttons_container,
                                           object_id=ObjectID(class_id='@friendly_buttons', object_id='#all_button'))

    ui_scroll_ships = pygame_gui.elements.UIScrollingContainer(pygame.Rect(0, 0, 300 * (width / 1920), height), manager)
    ui_scroll_ships.set_scrollable_area_dimensions((300 * (width / 1920), height))
    ui_scroll_confs = pygame_gui.elements.UIScrollingContainer(pygame.Rect(300 * (width / 1920), 0,
                                                                           500 * (width / 1920), height), manager)
    ui_scroll_confs.set_scrollable_area_dimensions((500 * (width / 1920), height))
    ships_buttons = []
    selected_ship = None

    counter = 0
    for i in ship_configurations.keys():
        confs_container = pygame_gui.core.UIContainer(pygame.Rect(0, 0, ui_scroll_confs.rect.width,
                                                                  len(ship_configurations[i]) * 150), manager,
                                                      container=ui_scroll_confs)
        ships_buttons.append(ships.UIButtonWithContainer(pygame.Rect((0, counter * 200 * (height / 1080),
                                                                      300 * (width / 1920),
                                                                      200 * (height / 1080))), '', manager,
                                                         container=ui_scroll_ships,
                                                         object_id=ObjectID(class_id='@friendly_buttons',
                                                                            object_id='#Start_but'),
                                                         cont=confs_container))
        for j in range(len(ship_configurations[i])):
            ships.UIButtonWithConfiguration(pygame.Rect((0, (j * 150) * (height / 1080),
                                                         500 * (width / 1920), 150 * (height / 1080))),
                                            ship_configurations[i][j].name, manager, confs_container,
                                            conf=ship_configurations[i][j], ship=i,
                                            object_id=ObjectID(class_id='@friendly_buttons',
                                                               object_id='#Conf_but'))
        confs_container.hide()
        img = pygame.image.load(i.img)
        cof = 160 / img.get_height()
        pygame_gui.elements.UIImage(pygame.Rect(((150 - img.get_width() * cof / 2) * (width / 1920),
                                                 (100 - img.get_height() * cof / 2 + counter * 200) * (height / 1080),
                                                 img.get_width() * cof * (width / 1920),
                                                 img.get_height() * cof * (height / 1080))), img, manager,
                                    container=ui_scroll_ships)
        counter += 1

    start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((width - 300 * (width / 1920),
                                                                           height - 180 * (height / 1080),
                                                                           300 * (width / 1920),
                                                                           180 * (height / 1080))),
                                                text='Start', manager=manager,
                                                object_id=ObjectID(class_id='@friendly_buttons',
                                                                   object_id='#Start_but'))

    back_button = pygame_gui.elements.UIButton(pygame.Rect((0, 0, 180 * (width / 1920), 160 * (height / 1080))),
                                               manager=manager, text='←',
                                               object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    back_button.hide()

    # Важно! Список пуль для обработки, он общий для всех кораблей и их модулей
    bullets = []
    # Список модулей на рендер
    buttons_for_render = []

    all_ships = []
    for i in level.enemys:
        all_ships.append(i.to_ship(manager, ui_scroll, bullets))

    # Игра
    game_speed = 1
    started = False

    # Камера
    scale = 1
    cam_x, cam_y = 0, 0
    scroll_sense = 0.05
    min_zoom, max_zoom = 0.1, 0.85
    ships_ui_offset = 70
    draw_hints = True

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

    # Орбита
    is_orbiting = False
    orbit_target = None

    # Дистанция
    is_distance = False
    distance_target = None

    while not done:
        time_delta = clock.tick(60) / 1000.0

        # Ввод
        for event in pygame.event.get():
            manager.process_events(event)
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN and started:
                if event.key == pygame.K_r:
                    if len(selected_ships) != 0:
                        x, y = pygame.mouse.get_pos()[0] - cam_x * scale, pygame.mouse.get_pos()[1] - cam_y * scale
                        for i in all_ships:
                            if trigonometry.distance_between_points((i.x, i.y),
                                                                    (x * (1 / scale),
                                                                     y * (1 / scale))) <= i.diagonal / 2:
                                orbit_target = i
                                is_orbiting = True
                                break
                        else:
                            orbit_target = (x * (1 / scale), y * (1 / scale))
                            is_orbiting = True
                elif event.key == pygame.K_f:
                    if len(selected_ships) != 0:
                        x, y = pygame.mouse.get_pos()[0] - cam_x * scale, pygame.mouse.get_pos()[1] - cam_y * scale
                        for i in all_ships:
                            if trigonometry.distance_between_points((i.x, i.y),
                                                                    (x * (1 / scale),
                                                                     y * (1 / scale))) <= i.diagonal / 2:
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
                                                                    (x * (1 / scale),
                                                                     y * (1 / scale))) <= i.diagonal / 2:
                                distance_target = i
                                is_distance = True
                                break
                        else:
                            distance_target = (x * (1 / scale), y * (1 / scale))
                            is_distance = True
                elif event.key == pygame.K_g:
                    if len(selected_ships) != 0:
                        for i in selected_ships:
                            i.set_target((0, 0), 'stop', 300)
                elif event.key == pygame.K_ESCAPE:
                    for i in selected_ships:
                        i.hide_ui()
                        buttons_for_render = []
                        ui_scroll.set_scrollable_area_dimensions((0, 0))
                    selected_ships = []
                elif event.key == pygame.K_c:
                    for i in targets:
                        i.hide()
                        i.cont.hide()
                    active_target = None
                    targets = []
                    now_targeting = dict()
                elif event.key == pygame.K_LALT:
                    draw_hints = not draw_hints
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_r and is_orbiting:
                    for j in selected_ships:
                        if orbit_target != j:
                            distance = trigonometry.distance_between_points((pygame.mouse.get_pos()[0] /
                                                                             scale - cam_x, pygame.mouse.get_pos()[1]
                                                                             / scale - cam_y),
                                                                            (orbit_target.x, orbit_target.y) if type(
                                                                                orbit_target) != tuple else (
                                                                                orbit_target[0], orbit_target[1]))
                            j.set_target(orbit_target, 'orbit', trigonometry.clamp(400, distance,
                                                                                   9999))
                        else:
                            j.set_target(orbit_target, 'stop')
                    break
                if event.key == pygame.K_e and is_distance:
                    for j in selected_ships:
                        if distance_target != j:
                            distance = trigonometry.distance_between_points((pygame.mouse.get_pos()[0] /
                                                                             scale - cam_x, pygame.mouse.get_pos()[1]
                                                                             / scale - cam_y),
                                                                            (distance_target.x,
                                                                             distance_target.y) if type(
                                                                                distance_target) != tuple else (
                                                                                distance_target[0], distance_target[1]))
                            j.set_target(distance_target, 'distance', trigonometry.clamp(400, distance,
                                                                                         9999))
                        else:
                            j.set_target(distance_target, 'stop')
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    is_selecting = True
                    selecting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                elif pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    is_targeting = True
                    targeting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                elif pygame.mouse.get_pressed()[0] and selected_ship is not None and not back_button.is_focused:
                    all_ships.append(selected_ship.to_ship(manager, ui_scroll, bullets))
                    all_ships[-1].x, all_ships[-1].y = ((pygame.mouse.get_pos()[0] - cam_x * scale) * (1 / scale),
                                                        (pygame.mouse.get_pos()[1] - cam_y * scale) * (1 / scale))
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
                if event.ui_element == start_button:
                    start_button.hide()
                    ui_scroll_ships.hide()
                    selected_ship = None
                    started = True
                elif event.ui_element == back_button:
                    start_button.show()
                    ui_scroll_ships.show()
                    selected_ship = None
                    back_button.hide()
                if type(event.ui_element) == ships.UIButtonWithModule:
                    if not event.ui_element.module.is_passive:
                        if event.ui_element.module.target_type == 'enemy':
                            if active_target is not None:
                                event.ui_element.module.activate(active_target.ship)
                        elif event.ui_element.module.target_type == 'self':
                            event.ui_element.module.activate(event.ui_element.self_ship)
                elif type(event.ui_element) == ships.UIButtonWithTarget:
                    active_target = event.ui_element
                elif type(event.ui_element) == ships.UIButtonWithContainer:
                    for i in ships_buttons:
                        i.cont.hide()
                    event.ui_element.cont.show()
                elif type(event.ui_element) == ships.UIButtonWithConfiguration:
                    for i in ships_buttons:
                        i.cont.hide()
                    start_button.hide()
                    ui_scroll_ships.hide()
                    ui_scroll.hide()
                    selected_ship = event.ui_element.ship
                    selected_ship.apply_configuration(event.ui_element.configuration)
                    back_button.show()

                # Кнопки быстрой активации всех модулей одной категории
                elif event.ui_element == all_high:
                    for i in selected_ships:
                        if i.team == 'player':
                            activness = i.high_modules[0].active
                            break
                    else:
                        activness = False
                    for modules in map(
                            lambda ship: (getattr(ship, 'high_modules'), ship) if ship.team == 'player' else None,
                            selected_ships):
                        if modules is not None:
                            for module in modules[0]:
                                if not module.is_passive and module.active == activness:
                                    if module.target_type == 'enemy':
                                        if active_target is not None:
                                            module.activate(active_target.ship)
                                    elif module.target_type == 'self':
                                        module.activate(modules[1])
                elif event.ui_element == all_mid:
                    for i in selected_ships:
                        if i.team == 'player':
                            activness = i.mid_modules[0].active
                            break
                    else:
                        activness = False
                    for modules in map(
                            lambda ship: (getattr(ship, 'mid_modules'), ship) if ship.team == 'player' else None,
                            selected_ships):
                        if modules is not None:
                            for module in modules[0]:
                                if not module.is_passive and module.active == activness:
                                    if module.target_type == 'enemy':
                                        if active_target is not None:
                                            module.activate(active_target.ship)
                                    elif module.target_type == 'self':
                                        module.activate(modules[1])
                elif event.ui_element == all_low:
                    for i in selected_ships:
                        if i.team == 'player':
                            activness = i.low_modules[0].active
                            break
                    else:
                        activness = False
                    for modules in map(
                            lambda ship: (getattr(ship, 'low_modules'), ship) if ship.team == 'player' else None,
                            selected_ships):
                        if modules is not None:
                            for module in modules[0]:
                                if not module.is_passive and module.active == activness:
                                    if module.target_type == 'enemy':
                                        if active_target is not None:
                                            module.activate(active_target.ship)
                                    elif module.target_type == 'self':
                                        module.activate(modules[1])

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
        del_list = []
        for r_ship in all_ships:
            if r_ship.hull > 0:
                r_ship.think(time_delta * game_speed)
                r_ship.physic(all_ships)
            else:
                del_list.append(r_ship)
        for i in del_list:
            all_ships.remove(i)
            redraw_targets()
            if active_target not in all_ships:
                active_target = None

        for bullet in bullets:
            if bullet.dead:
                redraw_targets_hp(targets)
                bullets.remove(bullet)
            else:
                bullet.think(time_delta * game_speed, all_ships)
        # До сюда

        # Рендеринг
        screen.blit(background, (0, 0))
        if draw_hints:
            for i in all_ships:
                i.render_hints(screen, scale, (cam_x, cam_y))
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
        if is_selecting and not is_targeting and started:
            selecting_end = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            rect = pygame.rect.Rect(min(selecting_start[0], selecting_end[0]),
                                    min(selecting_start[1], selecting_end[1]),
                                    abs(selecting_start[0] - selecting_end[0]),
                                    abs(selecting_start[1] - selecting_end[1]))
            pygame.draw.rect(screen, (100, 100, 255), rect, width=1)
            for i in all_ships:
                if i.team == 'player' and rect.collidepoint(i.x * scale + cam_x * scale, i.y * scale + cam_y * scale):
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (i.x * scale + cam_x * scale, i.y * scale + cam_y * scale),
                                       (i.diagonal / 2) * scale, 2)
        if temp_selecting is True and is_selecting is False and not is_targeting and started:
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
            selected_ships.sort(key=lambda sh: sh.diagonal, reverse=True)
            counter = 0
            buttons_for_render = []
            for i in selected_ships:
                buttons_for_render.append(i.show_ui(100 * counter + ships_ui_offset))
                counter += 1
            if len(selected_ships) > 1:
                all_buttons_container.show()
            else:
                all_buttons_container.hide()
            ui_scroll.set_scrollable_area_dimensions((390, trigonometry.clamp(height, 100 * counter + ships_ui_offset,
                                                                              9999)))

        # Обработка выбора целей через shift
        if is_targeting and not is_selecting and started:
            targeting_end = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            rect = pygame.rect.Rect(min(targeting_start[0], targeting_end[0]),
                                    min(targeting_start[1], targeting_end[1]),
                                    abs(targeting_start[0] - targeting_end[0]),
                                    abs(targeting_start[1] - targeting_end[1]))
            pygame.draw.rect(screen, (255, 100, 100), rect, width=1)
            for i in all_ships:
                if i.team == 'enemy' and rect.collidepoint(i.x * scale + cam_x * scale, i.y * scale + cam_y * scale):
                    pygame.draw.circle(screen, (255, 255, 255),
                                       (i.x * scale + cam_x * scale, i.y * scale + cam_y * scale),
                                       (i.diagonal / 2) * scale, 2)
        if temp_targeting is True and is_targeting is False and not is_selecting and started:
            rect = pygame.rect.Rect(min(targeting_start[0], targeting_end[0]),
                                    min(targeting_start[1], targeting_end[1]),
                                    abs(targeting_start[0] - targeting_end[0]),
                                    abs(targeting_start[1] - targeting_end[1]))
            ans = []
            for i in all_ships:
                if i.team == 'enemy' and rect.collidepoint(i.x * scale + cam_x * scale, i.y * scale + cam_y * scale):
                    ans.append(i)
            for i in ans:
                if (now_targeting.get(i) is None and i not in list(map(lambda sh: sh.ship, targets))
                        and len(now_targeting) + len(targets) < 7):
                    now_targeting[i] = 5

        for i in selected_ships:
            pygame.draw.circle(screen, (100, 100, 255), (i.x * scale + cam_x * scale,
                                                         i.y * scale + cam_y * scale),
                               (i.diagonal / 2) * scale, 5)
        for i in now_targeting:
            pygame.draw.circle(screen, (105, 105, 105), (i.x * scale + cam_x * scale,
                                                         i.y * scale + cam_y * scale),
                               (i.diagonal / 1.8) * scale, 5)
        for i in [getattr(x, 'ship') for x in targets]:
            pygame.draw.circle(screen, (255, 100, 100), (i.x * scale + cam_x * scale,
                                                         i.y * scale + cam_y * scale),
                               (i.diagonal / 1.9) * scale, 5)
        if active_target is not None:
            pygame.draw.circle(screen, (155, 155, 155), (active_target.rect.x + 50 * min((width / 1920),
                                                                                         (height / 1080)),
                                                         active_target.rect.y + 50 * min((width / 1920),
                                                                                         (height / 1080))),
                               55 * min((width / 1920), (height / 1080)), 3)
        temp_selecting = is_selecting
        temp_targeting = is_targeting

        ans = []
        for i in now_targeting.keys():
            now_targeting[i] -= time_delta
            if now_targeting[i] < 0:
                temp_target = ships.UIButtonWithTarget(
                    relative_rect=pygame.Rect(width - (len(targets) + 1) * 120 * min((width / 1920), (height / 1080)),
                                              0,
                                              100 * min((width / 1920), (height / 1080)),
                                              100 * min((width / 1920), (height / 1080))),
                    text='', manager=manager, ship=i)
                targets.append(temp_target)
                temp_target.cont = pygame_gui.core.UIContainer(pygame.Rect(temp_target.relative_rect.x,
                                                                           temp_target.relative_rect.y,
                                                                           temp_target.rect.width,
                                                                           temp_target.rect.height * 2), manager)
                pygame_gui.elements.UIImage(pygame.Rect(0, 0, temp_target.rect.width, temp_target.rect.height), i.img0,
                                            manager, container=temp_target.cont)
                CustomProgressBar(pygame.Rect(25 * (width / 1920), 106 * (height / 1080),
                                              75 * (width / 1920), 27 * (height / 1080)),
                                  manager, container=temp_target.cont,
                                  object_id=ObjectID(class_id='@boba',
                                                     object_id='#Shield_bar')).maximum_progress = i.max_shield
                CustomProgressBar(pygame.Rect(25 * (width / 1920), 139 * (height / 1080),
                                              75 * (width / 1920), 27 * (height / 1080)),
                                  manager, container=temp_target.cont,
                                  object_id=ObjectID(class_id='@boba',
                                                     object_id='#Armor_bar')).maximum_progress = i.max_armor
                CustomProgressBar(pygame.Rect(25 * (width / 1920), 173 * (height / 1080),
                                              75 * (width / 1920), 27 * (height / 1080)),
                                  manager, container=temp_target.cont,
                                  object_id=ObjectID(class_id='@boba',
                                                     object_id='#Hull_bar')).maximum_progress = i.max_hull
                pygame_gui.elements.UIImage(
                    pygame.Rect(0, 105 * (height / 1080), 20 * (width / 1920), 28 * (height / 1080)),
                    load_texture('textures/UI/shd.png'), manager, container=temp_target.cont)
                pygame_gui.elements.UIImage(
                    pygame.Rect(0, 138 * (height / 1080), 20 * (width / 1920), 28 * (height / 1080)),
                    load_texture('textures/UI/arm.png'), manager, container=temp_target.cont)
                pygame_gui.elements.UIImage(
                    pygame.Rect(0, 172 * (height / 1080), 20 * (width / 1920), 28 * (height / 1080)),
                    load_texture('textures/UI/hll.png'), manager, container=temp_target.cont)
                redraw_targets_hp(targets)
                ans.append(i)
        for i in ans:
            del now_targeting[i]

        # Рендеринг интерфейса
        fps_counter.set_text(str(trigonometry.clamp(0, int(clock.get_fps()), 60)))
        manager.update(time_delta)
        manager.draw_ui(screen)
        for i in buttons_for_render:
            for module in i:
                if not module[0].is_passive and module[0].passed <= module[0].cooldown:
                    progress = module[0].passed / module[0].cooldown
                    if module[0].active:
                        color = (0, 255 * progress, 0)
                    else:
                        color = (255 * progress, 0, 0)

                    pygame.draw.circle(screen, color,
                                       (module[1][0] + 20 + module[2] / 2,
                                        module[1][1] + module[2] / 2 - (ui_scroll.vert_scroll_bar.scroll_position * 1.36
                                                                        if ui_scroll.vert_scroll_bar else 0)),
                                       module[2] / 2, width=2)
        pygame.display.flip()
