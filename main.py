import os
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


os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
width, height = screen.get_size()
background = pygame.transform.scale(pygame.image.load('textures/UI/main_bg.jpg'), (width, height))
manager = pygame_gui.UIManager((width, height), 'data/style.json')
clock = pygame.time.Clock()
pygame.display.set_caption('Tutorial 1')
screen.blit(background, (0, 0))
temp_focus = False

# Сборки кораблей
ship_configurations = dict()
Scout = ships.ScoutShip((0, 0))
ship_configurations[Scout] = [ships.Configuration('Test Configuration', Scout),
                              ships.Configuration('Test Configuration2', Scout)]
Destroyer = ships.DestroyerShip((0, 0))
ship_configurations[Destroyer] = [ships.Configuration('Test Configuration', Destroyer),
                                  ships.Configuration('Test Configuration2', Destroyer)]


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
    levels = init_levels()
    levels_cont = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
    for i in range(len(levels)):
        UIButtonWithLevel(pygame.Rect(((200 + i % 4 * 400) * (width / 1920),
                                       (200 + i // 4 * 300) * (height / 1080),
                                       300 * (width / 1920),
                                       200 * (height / 1080))),
                          manag=manager, text=str(i + 1),
                          object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                          container=levels_cont, level=levels[i])
    back_button_pl = pygame_gui.elements.UIButton(pygame.Rect((50, 50, 180 * (width / 1920),
                                                               120 * (height / 1080))), manager=manager,
                                                  text='←',
                                                  object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                                                  container=levels_cont)
    levels_cont.hide()

    # Экран настроек
    settings_cont = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
    res_drop = pygame_gui.elements.UIDropDownMenu(list({'Полный экран', '1920x1080',
                                                   '1280x720', '800x600',
                                                   f'{screen.get_width()}x{screen.get_height()}'}),
                                                  f'{screen.get_width()}x{screen.get_height()}',
                                                  pygame.Rect((460 * (width / 1920), 150 * (height / 1080),
                                                               300 * (width / 1920), 30)),
                                                  manager, settings_cont)
    pygame_gui.elements.UILabel(pygame.Rect((460 * (width / 1920), height - 200, 1000 * (width / 1920), 200)),
                                manager=manager, text=r'Как то тут пустовато ¯\_☹_/¯',
                                container=settings_cont,
                                object_id=ObjectID(object_id='#Settings', class_id='@boba'))
    back_button_set = pygame_gui.elements.UIButton(pygame.Rect((50, 50, 180, 120)), manager=manager,
                                                   text='←',
                                                   object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                                                   container=settings_cont)
    settings_cont.hide()
    return main_cont, levels_cont, settings_cont, play, settings, exit_but, back_button_set, back_button_pl, res_drop


(main_container, levels_container, settings_container, play_but,
 settings_but, exit_butt, back_button_settings, back_button_play, resolution_dropdown) = init_ui()
main_container.show()

done = False
while done is False:
    time_delta = clock.tick(60) / 1000.0
    events = pygame.event.get()
    for event in events:
        manager.process_events(event)
        if event.type == pygame.QUIT:
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
                exit()
            elif event.ui_element == back_button_play:
                levels_container.hide()
                screen.blit(background, (0, 0))
                main_container.show()
            elif event.ui_element == back_button_settings:
                settings_container.hide()
                main_container.show()
                screen.blit(background, (0, 0))
            elif type(event.ui_element) == UIButtonWithLevel:
                game.main(screen, event.ui_element.level, ship_configurations)
                done = True
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == resolution_dropdown:
                if event.text != 'Полный экран':
                    pygame.display.set_mode((int(event.text.split('x')[0]), int(event.text.split('x')[1])))
                else:
                    pygame.display.set_mode((0, 0), pygame.NOFRAME)
                width, height = screen.get_size()
                temp_res = event.text
                manager.clear_and_reset()
                (main_container, levels_container, settings_container, play_but,
                 settings_but, exit_butt, back_button_settings, back_button_play, resolution_dropdown) = init_ui()
                screen.fill((30, 30, 30))
                settings_container.show()

    if resolution_dropdown.is_focused != temp_focus:
        screen.fill((30, 30, 30))
        temp_focus = resolution_dropdown.is_focused
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()
