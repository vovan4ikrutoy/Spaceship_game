import os
import random
import time

from levels import Level
from texture_manager import load_texture
import pygame
import pygame_gui


# noinspection SpellCheckingInspection


class CustomProgressBar(pygame_gui.elements.UIProgressBar):
    def status_text(self):
        return ''


def main(screen: pygame.Surface, level: Level, ship_configurations: dict):
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
            progress_bars = sorted([x for x in target.cont.elements if x.__class__ == CustomProgressBar],
                                   key=lambda el: el.relative_rect.y)
            progress_bars[0].set_current_progress(target.ship.shield / target.ship.max_shield)
            progress_bars[1].set_current_progress(target.ship.armor / target.ship.max_armor)
            progress_bars[2].set_current_progress(target.ship.hull / target.ship.max_hull)

    # Иницализация игры и интерфейса
    pygame.init()
    width, height = screen.get_width(), screen.get_height()
    manager = pygame_gui.UIManager((width, height), os.getcwd() + '/data/style.json')
    bg_img = pygame.image.load('textures/UI/bg.jpg')
    background = pygame.transform.scale(bg_img, (width, height))
    fps_counter = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 0), (20, 20)), manager=manager, text='60')
    clock = pygame.time.Clock()
    done = False
    ui_scroll = pygame_gui.elements.UIScrollingContainer(pygame.Rect(0, 0, 510, height), manager)
    ui_scroll.set_scrollable_area_dimensions((0, 0))
    money = level.money

    win_screen = pygame_gui.core.UIContainer(pygame.Rect((0, 0, width, height)), manager)
    pygame_gui.elements.UILabel(pygame.Rect(((width - 900) / 2, 250 * (height / 1080), 900, 200 * (height / 1080))),
                                manager=manager,
                                text='Ты выиграл!', container=win_screen,
                                object_id=ObjectID(object_id='#Title_text', class_id='@boba'))
    stats = pygame_gui.elements.UILabel(
        pygame.Rect(((width - 900) / 2, 350 * (height / 1080), 900, 200 * (height / 1080))),
        manager=manager,
        text='Деньги: 55%  Время: 6:33', container=win_screen,
        object_id=ObjectID(object_id='#Score', class_id='@boba'))
    score_label = pygame_gui.elements.UILabel(
        pygame.Rect(((width - 900) / 2, 420 * (height / 1080), 900, 200 * (height / 1080))),
        manager=manager,
        text='Счет: 1867(345+678+500)!', container=win_screen,
        object_id=ObjectID(object_id='#Score', class_id='@boba'))
    win_but = pygame_gui.elements.UIButton(
        pygame.Rect((560 * (width / 1920), 600 * (height / 1080), 800 * (width / 1920), 200 * (height / 1080))),
        text='Продолжить', manager=manager,
        container=win_screen,
        object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    win_screen.hide()

    lose_screen = pygame_gui.core.UIContainer(pygame.Rect((0, 0, width, height)), manager)
    pygame_gui.elements.UILabel(pygame.Rect(((width - 900) / 2, 250 * (height / 1080), 900, 200 * (height / 1080))),
                                manager=manager,
                                text='Ты проиграл!', container=lose_screen,
                                object_id=ObjectID(object_id='#Title_text', class_id='@boba'))
    text = random.choice(['Ещё раз', 'Заново', 'Черт!', 'Попытаться', 'Снова', 'С начала', 'По новой', 'Опять'])
    res_but = pygame_gui.elements.UIButton(
        pygame.Rect((560 * (width / 1920), 500 * (height / 1080), 800 * (width / 1920), 200 * (height / 1080))),
        text=text, manager=manager,
        container=lose_screen,
        object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    lost_but = pygame_gui.elements.UIButton(
        pygame.Rect((560 * (width / 1920), 725 * (height / 1080), 800 * (width / 1920), 200 * (height / 1080))),
        text='Выход', manager=manager,
        container=lose_screen,
        object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    lose_screen.hide()

    all_buttons_container = pygame_gui.core.UIContainer(relative_rect=pygame.Rect(0, 0, 400, 70), manager=manager,
                                                        container=ui_scroll)
    all_high = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 20, 85, 50)), text='High',
                                            manager=manager, container=all_buttons_container,
                                            object_id=ObjectID(class_id='@friendly_buttons', object_id='#all_button'))
    all_mid = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 20, 85, 50)), text='Mid',
                                           manager=manager, container=all_buttons_container,
                                           object_id=ObjectID(class_id='@friendly_buttons', object_id='#all_button'))
    all_low = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400, 20, 85, 50)), text='Low',
                                           manager=manager, container=all_buttons_container,
                                           object_id=ObjectID(class_id='@friendly_buttons', object_id='#all_button'))

    money_label = pygame_gui.elements.UILabel(pygame.Rect((width - 300, 50 * (height / 1080),
                                                           250, 50)), 'Деньги: ' + str(money), manager,
                                              object_id=ObjectID(class_id='@boba', object_id='#Money_but_all'))

    back_but = pygame_gui.elements.UIButton(pygame.Rect((width - 100) / 2, 0, 100,
                                                        100), '←', manager,
                                            object_id=ObjectID(class_id='@friendly_buttons', object_id='#Title_button'))

    hint_txt = pygame_gui.elements.UITextBox(f'<font pixel_size=32>{'Подсказка: ' + level.hint}</font>',
                                             pygame.Rect(60 + 300 * (width / 1920), 0,
                                                         width - (60 + 300 * (width / 1920)) - 300, 100),
                                             manager, object_id=ObjectID(class_id='@friendly_buttons',
                                                                         object_id='#Title_sub'))
    hint_txt.hide()
    hint_but = pygame_gui.elements.UIButton(pygame.Rect(width - 420, 0, 120 * (width / 1920),
                                                        120 * (height / 1080)), '', manager)
    hint_img = pygame_gui.elements.UIImage(pygame.Rect(width - 420, 0, 120 * (width / 1920),
                                                       120 * (height / 1080)),
                                           load_texture('textures/UI/help.png'), manager)
    if level.hint == '':
        hint_but.hide()
        hint_img.hide()

    ui_scroll_ships = pygame_gui.elements.UIScrollingContainer(pygame.Rect(0, 0, 60 + 300 * (width / 1920), height),
                                                               manager)
    ui_scroll_ships.set_scrollable_area_dimensions((60 + 300 * (width / 1920), height))
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
        pygame_gui.elements.UILabel(pygame.Rect((300 * (width / 1920), 150 * (height / 1080) +
                                                 counter * 200 * (height / 1080),
                                                 60, 33)), str(i.cost), manager,
                                    object_id=ObjectID(class_id='@boba', object_id='#Money_but'),
                                    container=ui_scroll_ships)
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
        img = pygame.image.load(i.img)
        cof = 160 / img.get_height()
        pygame_gui.elements.UIImage(pygame.Rect(((150 - img.get_width() * cof / 2) * (width / 1920),
                                                 (100 - img.get_height() * cof / 2 + counter * 200) * (height / 1080),
                                                 img.get_width() * cof * (width / 1920),
                                                 img.get_height() * cof * (height / 1080))), img, manager,
                                    container=ui_scroll_ships)
        counter += 1
        confs_container.hide()

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
    think_counter = 0
    start_time = time.time()
    end_time = 0
    start_money = money
    score = 0

    # Камера
    scale = 0.25 * (width / 1920)
    cam_x, cam_y = -2700, -3800
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
                return 0
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
                            if type(orbit_target) != tuple and distance < orbit_target.diagonal / 2:
                                distance = min(j.high_modules, key=lambda b: b.distance * 0.9).distance * 0.9
                            j.set_target(orbit_target, 'orbit', trigonometry.clamp(400, distance,
                                                                                   9999))
                        else:
                            j.set_target(orbit_target, 'stop')
                        is_orbiting = False
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
                            if type(distance_target) != tuple and distance < distance_target.diagonal / 2:
                                distance = min(j.high_modules, key=lambda sh: sh.distance).distance * 0.9
                            j.set_target(distance_target, 'distance', trigonometry.clamp(400, distance,
                                                                                         9999))
                        else:
                            j.set_target(distance_target, 'stop')
                        is_distance = False
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    is_selecting = True
                    selecting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                elif pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    is_targeting = True
                    targeting_start = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                elif pygame.mouse.get_pressed()[0] and selected_ship is not None and not back_button.is_focused:
                    build_space = pygame.Rect(500, 4000, 5500, 4000)
                    click_point = ((pygame.mouse.get_pos()[0] - cam_x * scale) * (1 / scale),
                                   (pygame.mouse.get_pos()[1] - cam_y * scale) * (1 / scale))
                    if build_space.collidepoint(click_point[0], click_point[1]) and money >= selected_ship.cost:
                        all_ships.append(selected_ship.to_ship(manager, ui_scroll, bullets))
                        all_ships[-1].x, all_ships[-1].y = click_point
                        money -= selected_ship.cost
                        money_label.set_text('Деньги: ' + str(money))
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
                    if len([x for x in all_ships if x.team == 'player']) > 0:
                        start_button.hide()
                        ui_scroll_ships.hide()
                        money_label.hide()
                        back_but.show()
                        hint_but.hide()
                        hint_img.hide()
                        hint_txt.hide()
                        for i in ships_buttons:
                            i.cont.hide()
                        selected_ship = None
                        started = True
                elif event.ui_element == back_button:
                    start_button.show()
                    ui_scroll_ships.show()
                    selected_ship = None
                    back_but.show()
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
                    back_but.hide()
                    ui_scroll_ships.hide()
                    selected_ship = event.ui_element.ship
                    selected_ship.apply_configuration(event.ui_element.configuration)
                    back_button.show()

                # Кнопки с менюшек
                if event.ui_element == win_but:
                    return level, score
                elif event.ui_element == lost_but:
                    return 1
                elif event.ui_element == res_but:
                    return main(screen, level, ship_configurations)
                elif event.ui_element == back_but:
                    return 1
                elif event.ui_element == hint_but:
                    hint_but.hide()
                    hint_img.hide()
                    hint_txt.show()

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
                        if i.team == 'player' and len(i.mid_modules) > 0:
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
                        if i.team == 'player' and len(i.mid_modules) > 0:
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
            cam_y += 8 * (1 / scale)
        if pressed[pygame.K_s]:
            cam_y -= 8 * (1 / scale)
        if pressed[pygame.K_a]:
            cam_x += 8 * (1 / scale)
        if pressed[pygame.K_d]:
            cam_x -= 8 * (1 / scale)
        cam_x = trigonometry.clamp(-16000 + screen.get_width() * (1 / scale), cam_x, 4000)
        cam_y = trigonometry.clamp(-16000 + screen.get_height() * (1 / scale), cam_y, 4000)

        # Логика
        del_list = []
        if think_counter > 30 and started:
            for i in all_ships:
                i.super_think(all_ships)
                redraw_targets_hp(targets)
                think_counter = 0
        else:
            think_counter += 1
        for r_ship in all_ships:
            if r_ship.hull > 0:
                r_ship.think(time_delta * game_speed)
                r_ship.physic(all_ships)
            else:
                del_list.append(r_ship)
        for i in del_list:
            if i == active_target:
                active_target = None
            all_ships.remove(i)
            if i.team == 'player':
                i.hide_ui()
            if i in selected_ships:
                for x in selected_ships:
                    x.hide_ui()
                selected_ships.remove(i)
                selected_ships.sort(key=lambda sh: sh.diagonal, reverse=True)
                counter = 0
                buttons_for_render = []
                for j in selected_ships:
                    buttons_for_render.append(j.show_ui(100 * counter + ships_ui_offset))
                    counter += 1
                if len(selected_ships) > 1:
                    all_buttons_container.show()
                else:
                    all_buttons_container.hide()
                ui_scroll.set_scrollable_area_dimensions(
                    (510, trigonometry.clamp(height, 100 * counter + ships_ui_offset,
                                             9999)))
            redraw_targets()

        for bullet in bullets:
            if bullet.dead:
                redraw_targets_hp(targets)
                bullets.remove(bullet)
            else:
                bullet.think(time_delta * game_speed, all_ships)
        if started:
            if len([x for x in all_ships if x.team == 'player']) == 0:
                started = False
                [i.set_target((0, 0), 'stop') for i in all_ships]
                lose_screen.show()
                back_but.hide()
            elif len([x for x in all_ships if x.team == 'enemy']) == 0:
                started = False
                [i.set_target((0, 0), 'stop') for i in all_ships]
                end_time = time.time()
                score = trigonometry.clamp(0, 1000 - round(time.time() - start_time) * 3, 1000) + round(
                    money / start_money * 1000) + 500
                stats.set_text(f'Время: {time.gmtime(end_time - start_time).tm_min}: '
                               f'{time.gmtime(end_time - start_time).tm_sec}  Деньги: '
                               f' {round((money / start_money) * 100)}%')
                score_label.set_text(f'Счет: {str(score)} ({1000 - round(time.time() - start_time) * 3}+'
                                     f'{round(money / start_money * 1000)}+500)')
                back_but.hide()
                win_screen.show()

        # Рендеринг
        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(cam_x * scale, cam_y * scale,
                                                          12000 * scale, 12000 * scale), 10)
        if not started:
            pygame.draw.rect(screen, (100, 100, 255),
                             pygame.Rect(500 * scale + cam_x * scale, 4000 * scale + cam_y * scale,
                                         5500 * scale, 4000 * scale), 5)
        if draw_hints:
            for i in all_ships:
                if i.team == 'player':
                    i.render_hints(screen, scale, (cam_x, cam_y))
        camera_rect = pygame.Rect(
            (-cam_x - width * 0.15, -cam_y - height * 0.15, width * 1.15 / scale, height * 1.15 / scale))
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
            for i in all_ships:
                i.hide_ui()
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
            ui_scroll.set_scrollable_area_dimensions((490, trigonometry.clamp(height, 100 * counter + ships_ui_offset,
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
            if i.hull > 0:
                pygame.draw.circle(screen, (100, 100, 255), (i.x * scale + cam_x * scale,
                                                             i.y * scale + cam_y * scale),
                                   (i.diagonal / 2) * scale, 3)
        for i in now_targeting:
            pygame.draw.circle(screen, (105, 105, 105), (i.x * scale + cam_x * scale,
                                                         i.y * scale + cam_y * scale),
                               (i.diagonal / 1.8) * scale, 3)
        for i in [getattr(x, 'ship') for x in targets]:
            pygame.draw.circle(screen, (255, 100, 100), (i.x * scale + cam_x * scale,
                                                         i.y * scale + cam_y * scale),
                               (i.diagonal / 1.9) * scale, 3)
            if active_target is not None and i == active_target.ship:
                pygame.draw.circle(screen, (230, 230, 230), (i.x * scale + cam_x * scale,
                                                             i.y * scale + cam_y * scale),
                                   (i.diagonal / 1.9) * scale, 5)
        if active_target is not None and active_target in targets:
            pygame.draw.circle(screen, (155, 155, 155), (active_target.rect.x + 50 * min((width / 1920),
                                                                                         (height / 1080)),
                                                         active_target.rect.y + 50 * min((width / 1920),
                                                                                         (height / 1080))),
                               55 * min((width / 1920), (height / 1080)), 3)
        if is_orbiting:
            distance = trigonometry.distance_between_points((pygame.mouse.get_pos()[0] /
                                                             scale - cam_x, pygame.mouse.get_pos()[1]
                                                             / scale - cam_y),
                                                            (orbit_target.x,
                                                             orbit_target.y) if type(
                                                                orbit_target) != tuple else (
                                                                orbit_target[0], orbit_target[1]))
            dist = (orbit_target.x, orbit_target.y) if type(orbit_target) == ships.Ship else (
                orbit_target[0], orbit_target[1])
            min_dist = min(min(selected_ships,
                               key=lambda s: min(s.high_modules, key=lambda m: m.distance).distance).high_modules,
                           key=lambda z: z.distance).distance
            pygame.draw.circle(screen, (100, 100, 100), (dist[0] * scale + cam_x * scale,
                                                         dist[1] * scale + cam_y * scale),
                               min_dist * 0.9 * scale, 3)
            if type(orbit_target) != tuple and distance < orbit_target.diagonal / 2:
                distance = min_dist * 0.9
            pygame.draw.circle(screen, (50, 50, 255), (dist[0] * scale + cam_x * scale,
                                                       dist[1] * scale + cam_y * scale),
                               max(distance, 400) * scale, 3)
        if is_distance:
            distance = trigonometry.distance_between_points((pygame.mouse.get_pos()[0] /
                                                             scale - cam_x, pygame.mouse.get_pos()[1]
                                                             / scale - cam_y),
                                                            (distance_target.x,
                                                             distance_target.y) if type(
                                                                distance_target) != tuple else (
                                                                distance_target[0], distance_target[1]))
            dist = (distance_target.x, distance_target.y) if type(distance_target) == ships.Ship else (
                distance_target[0], distance_target[1])
            min_dist = min(min(selected_ships,
                               key=lambda s: min(s.high_modules, key=lambda m: m.distance).distance).high_modules,
                           key=lambda z: z.distance).distance
            pygame.draw.circle(screen, (100, 100, 100), (dist[0] * scale + cam_x * scale,
                                                         dist[1] * scale + cam_y * scale),
                               min_dist * 0.9 * scale, 3)
            if type(distance_target) != tuple and distance < distance_target.diagonal / 2:
                distance = min_dist * 0.9
            pygame.draw.circle(screen, (50, 50, 255), (dist[0] * scale + cam_x * scale,
                                                       dist[1] * scale + cam_y * scale),
                               max(distance, 400) * scale, 3)
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
                                        module[3].rect.y + module[2] / 2),
                                       module[2] / 2, width=2)
        pygame.display.flip()
