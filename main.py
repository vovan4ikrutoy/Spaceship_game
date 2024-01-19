import os
from pathlib import Path
from typing import Optional, Dict, Iterable, Tuple

import pygame
import pygame_gui
import webbrowser
from pygame_gui.core import ObjectID, UIElement, IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

import game
import modules
import ships
from levels import init_levels


class UIButtonWithLevel(pygame_gui.elements.UIButton):
    def __init__(self, relative_rect: pygame.Rect | Tuple[float, float] | pygame.Vector2,
                 text: str,
                 manag: Optional[IUIManagerInterface] = None,
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
                 tool_tip_text_kwargs: Optional[Dict[str, str]] = None, level):
        super().__init__(relative_rect, text, manag, container, tool_tip_text, starting_height, parent_element,
                         object_id, anchors, allow_double_clicks, generate_click_events_from, visible,
                         tool_tip_object_id=tool_tip_object_id, text_kwargs=text_kwargs,
                         tool_tip_text_kwargs=tool_tip_text_kwargs)
        self.level = level


class SaveReadError(Exception):
    pass


os.environ['SDL_VIDEO_CENTERED'] = '1'
levels_list = init_levels()
save = Path('saves/save.txt')
if save.exists():
    with open('saves/' + save.name, 'r') as file:
        data = list(map(str.rstrip, file.readlines()))
        try:
            if len(data) != 2:
                err = 1 / 0
            resolution = (0, 0) if data[0] == 'fullscreen' else tuple(map(int, data[0].split('x')))
            scores = list(map(int, data[1].split()))
        except BaseException:
            raise SaveReadError("Ошибка чтения сохранения")
        file.close()
else:
    resolution = (0, 0)
    with open('saves/' + save.name, 'w') as file:
        file.write('fullscreen\n')
        file.write('0 ' * len(levels_list))
        scores = [0 for _ in range(len(levels_list))]
        file.close()
pygame.init()
screen = pygame.display.set_mode(resolution, pygame.NOFRAME)
width, height = screen.get_size()
background = pygame.transform.scale(pygame.image.load('textures/UI/main_bg.jpg'), (width, height))
manager = pygame_gui.UIManager((width, height), os.getcwd() + '/data/style.json')
clock = pygame.time.Clock()
pygame.display.set_caption('Звездные Корабли')
screen.blit(background, (0, 0))
temp_focus = False

# Сборки кораблей
ship_configurations = dict()
Scout = ships.ScoutShip((0, 0))
ship_configurations[Scout] = [ships.Configuration('Боевая модификация', Scout, [modules.SmallRailgun],
                                                  mid_modules=[modules.ShieldBooster],
                                                  low_modules=[modules.ShieldReinforcement]),
                              ships.Configuration('Корабль поддержки', Scout, [modules.IonGun],
                                                  low_modules=[modules.Acceleration]),
                              ships.Configuration('Ракетная установка', Scout, [modules.SmallRocketLauncher])]
Destroyer = ships.DestroyerShip((0, 0))
ship_configurations[Destroyer] = [
    ships.Configuration('Уничтожитель', Destroyer, [modules.SmallRailgun, modules.SmallRailgun, modules.SmallRailgun],
                        [modules.ShieldBooster], [modules.ShieldReinforcement, modules.ShieldReinforcement]),
    ships.Configuration('Ракетная площадка', Destroyer,
                        [modules.SmallRocketLauncher, modules.SmallRocketLauncher, modules.SmallRocketLauncher]),
    ships.Configuration('Гибрид', Destroyer, [modules.SmallRailgun, modules.SmallRailgun, modules.SmallRocketLauncher],
                        [modules.ShieldBooster], [modules.ShieldReinforcement])]
Miner = ships.MinerShip((0, 0))
ship_configurations[Miner] = [ships.Configuration('Снайпер', Miner, [modules.MediumRailgun, modules.MediumRailgun],
                                                  low_modules=[modules.Acceleration]),
                              ships.Configuration('Противоастероидное покрытие', Miner,
                                                  [modules.MediumRocketLauncher, modules.MediumRocketLauncher],
                                                  [modules.ArmorRepair], [modules.ArmorRein])]
Carrier = ships.CarrierShip((0, 0))
ship_configurations[Carrier] = [
    ships.Configuration('Щит императора', Carrier, [modules.MediumRailgun, modules.MediumRailgun, modules.MediumRailgun],
                        [modules.ShieldBooster, modules.ShieldBooster],
                        [modules.ShieldReinforcement, modules.ShieldReinforcement, modules.ShieldReinforcement, modules.ArmorRein]),
    ships.Configuration('Контроль дистанции', Carrier,
                        [modules.Flamethrower, modules.MediumRocketLauncher, modules.MediumRocketLauncher],
                        [modules.ArmorRepair, modules.ArmorRepair],
                        [modules.ArmorRein, modules.ArmorRein]),
    ships.Configuration('Берсерк', Carrier,
                        [modules.Flamethrower, modules.Flamethrower, modules.Flamethrower],
                        [],
                        [modules.ArmorRein, modules.ArmorRein, modules.ArmorRein, modules.ArmorRein,
                         modules.Acceleration, modules.Acceleration])
]
Dominator = ships.DominatorShip((0, 0))
ship_configurations[Dominator] = [ships.Configuration('bebras', Dominator, [modules.LargeRailgun])]


def init_ui():
    # Главное меню
    main_cont = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
    pygame_gui.elements.UILabel(pygame.Rect(((width - 900) / 2, 0, 900, 200 * (height / 1080))),
                                manager=manager,
                                text='Spaceship Game', container=main_cont,
                                object_id=ObjectID(object_id='#Title_text', class_id='@boba'))
    pygame_gui.elements.UITextBox(f'<font pixel_size={round(42 * (width / 1920))}>Project by <img '
                                  'src="textures/UI/logo.png">'
                                  ' <a href="vova">Vladimir Yakuba<a/></font>',
                                  pygame.Rect((560 * (width / 1920), 180 * (height / 1080),
                                               700 * (width / 1920) + 100, 200 * (height / 1080))),
                                  manager=manager,
                                  container=main_cont,
                                  object_id=ObjectID(object_id='#Title_sub',
                                                     class_id='@boba'))
    play = pygame_gui.elements.UIButton(
        pygame.Rect((560 * (width / 1920), 330 * (height / 1080), 800 * (width / 1920), 200 * (height / 1080))),
        text='Играть',
        container=main_cont,
        object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    settings = pygame_gui.elements.UIButton(
        pygame.Rect((560 * (width / 1920), 570 * (height / 1080), 800 * (width / 1920), 200 * (height / 1080))),
        text='Настройки',
        container=main_cont,
        object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    exit_but = pygame_gui.elements.UIButton(
        pygame.Rect((560 * (width / 1920), 820 * (height / 1080), 800 * (width / 1920), 200 * (height / 1080))),
        text='Выйти', container=main_cont,
        object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    main_cont.hide()

    # Экран уровней
    levels_cont = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
    for i in range(len(levels_list)):
        UIButtonWithLevel(pygame.Rect(((200 + i % 4 * 400) * (width / 1920),
                                       (200 + i // 4 * 300) * (height / 1080),
                                       300 * (width / 1920),
                                       200 * (height / 1080))),
                          manag=manager, text=str(i + 1),
                          object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                          container=levels_cont, level=levels_list[i])
        if scores[i] != 0:
            pygame_gui.elements.UILabel(pygame.Rect(((200 + i % 4 * 400) * (width / 1920),
                                                     (350 + i // 4 * 300) * (height / 1080),
                                                     300 * (width / 1920),
                                                     50 * (height / 1080))), str(scores[i]), manager, levels_cont,
                                        object_id=ObjectID(object_id='#Level_score', class_id='@boba'))
    back_button_pl = pygame_gui.elements.UIButton(pygame.Rect((50, 50, 180 * (width / 1920),
                                                               120 * (height / 1080))), manager=manager,
                                                  text='←',
                                                  object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                                                  container=levels_cont)
    final_but = pygame_gui.elements.UIButton(pygame.Rect((200 * (width / 1920), 1500 * (height / 1920),
                                                          1500 * (width / 1920), 200 * (height / 1080))),
                                             'Результаты!', manager, container=levels_cont,
                                             object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    if scores[-1] == 0:
        final_but.set_position((-1000, -1000))
    levels_cont.hide()

    # Экран настроек
    settings_cont = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
    res_drop = pygame_gui.elements.UIDropDownMenu(list({'Полный экран', '1920x1080',
                                                        '1280x720', '960x540',
                                                        f'{screen.get_width()}x{screen.get_height()}'}),
                                                  f'{screen.get_width()}x{screen.get_height()}',
                                                  pygame.Rect((460 * (width / 1920), 150 * (height / 1080),
                                                               300 * (width / 1920), 40)),
                                                  manager, settings_cont)
    pygame_gui.elements.UILabel(pygame.Rect((770 * (width / 1920), 150 * (height / 1080), 400, 40)),
                                manager=manager, text=r'Разрешение экрана',
                                container=settings_cont,
                                object_id=ObjectID(object_id='#Settings', class_id='@boba'))
    reset_butt = pygame_gui.elements.UIButton(pygame.Rect(((width - 900) / 2, (height - (300 * (height / 1080))),
                                                           900, 100)),
                                              'Сбросить настройки', manager, settings_cont,
                                              object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
    back_button_set = pygame_gui.elements.UIButton(pygame.Rect((50, 50, 180, 120)), manager=manager,
                                                   text='←',
                                                   object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                                                   container=settings_cont)
    settings_cont.hide()
    return (main_cont, levels_cont, settings_cont, play, settings, exit_but, back_button_set, back_button_pl, res_drop,
            reset_butt, final_but)


(main_container, levels_container, settings_container, play_but,
 settings_but, exit_butt, back_button_settings, back_button_play, resolution_dropdown, reset_but, final_bu) = init_ui()
main_container.show()


def write_settings():
    with open('saves/' + save.name, 'w') as f:
        f.write('fullscreen\n' if resolution == (0, 0) else f'{width}x{height}\n')
        f.write(' '.join(list(map(str, scores))))
        f.close()


done = False
while done is False:
    time_delta = clock.tick(60) / 1000.0
    events = pygame.event.get()
    for event in events:
        manager.process_events(event)
        if event.type == pygame.QUIT:
            write_settings()
            exit()
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            try:
                getattr(event, 'link_target')
                webbrowser.open('https://github.com/vovan4ikrutoy')
            except AttributeError:
                pass
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == play_but:
                main_container.hide()
                levels_container.show()
                screen.fill((30, 30, 30))
            elif event.ui_element == settings_but:
                main_container.hide()
                settings_container.show()
                screen.fill((30, 30, 30))
            elif event.ui_element == exit_butt:
                write_settings()
                exit()
            elif event.ui_element == back_button_play:
                levels_container.hide()
                screen.blit(background, (0, 0))
                main_container.show()
            elif event.ui_element == back_button_settings:
                settings_container.hide()
                main_container.show()
                screen.blit(background, (0, 0))
            elif event.ui_element == reset_but:
                [x.set_text('') if type(x) == pygame_gui.elements.UILabel and len(x.text) > 3 else None
                 for x in levels_container.elements]
                scores = [0 for _ in range(len(levels_list))]
                write_settings()
            elif event.ui_element == final_bu:
                levels_container.hide()
                screen.blit(background, (0, 0))
                pygame_gui.elements.UILabel(pygame.Rect((0, 0, width, height / 3)), 'Поздравляем!', manager,
                                            object_id=ObjectID(object_id='#Title_text', class_id='@boba'))
                pygame_gui.elements.UILabel(pygame.Rect((0, height / 3.6, width, height / 3)),
                                            f'Ваш счет: {sum(scores)}',
                                            manager,
                                            object_id=ObjectID(object_id='#Title_text', class_id='@boba'))
                pygame_gui.elements.UIButton(pygame.Rect((width / 6, height / 1.5, width / 1.5, height / 4)),
                                             'Выход', manager,
                                             object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
            elif event.ui_element.text == 'Выход':
                write_settings()
                exit()
            elif type(event.ui_element) == UIButtonWithLevel and \
                    (event.ui_element.level.number == 0 or scores[event.ui_element.level.number - 1] != 0):
                result = game.main(screen, event.ui_element.level, ship_configurations)
                screen.fill((30, 30, 30))
                if type(result) == int:
                    # Вышел из игры
                    if result == 0:
                        write_settings()
                        exit()
                    # Проиграл
                    elif result == 1:
                        pass
                else:
                    # Победил
                    [x.hide() if type(x) == pygame_gui.elements.UILabel and len(x.text) > 3 else None
                     for x in levels_container.elements]
                    if result[1] > scores[result[0].number]:
                        scores[result[0].number] = result[1]
                    for i in range(len(levels_list)):
                        if scores[i] != 0:
                            pygame_gui.elements.UILabel(pygame.Rect(((200 + i % 4 * 400) * (width / 1920),
                                                                     (350 + i // 4 * 300) * (height / 1080),
                                                                     300 * (width / 1920),
                                                                     50 * (height / 1080))), str(scores[i]), manager,
                                                        levels_container,
                                                        object_id=ObjectID(object_id='#Level_score', class_id='@boba'))

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == resolution_dropdown:
                if event.text != 'Полный экран':
                    pygame.display.set_mode((int(event.text.split('x')[0]), int(event.text.split('x')[1])))
                    resolution = screen.get_size()
                else:
                    pygame.display.set_mode((0, 0), pygame.NOFRAME)
                    resolution = (0, 0)
                width, height = screen.get_size()
                background = pygame.transform.scale(pygame.image.load('textures/UI/main_bg.jpg'), (width, height))
                manager.clear_and_reset()
                manager.set_window_resolution((width, height))
                temp_res = event.text
                (main_container, levels_container, settings_container, play_but,
                 settings_but, exit_butt, back_button_settings, back_button_play, resolution_dropdown,
                 reset_but, final_bu) = init_ui()
                screen.fill((30, 30, 30))
                settings_container.show()

    if resolution_dropdown.is_focused != temp_focus:
        screen.fill((30, 30, 30))
        temp_focus = resolution_dropdown.is_focused
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()
