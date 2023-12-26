import math
from typing import Optional, Dict, Iterable, Tuple

import pygame
import pygame_gui
import webbrowser
from pygame_gui.core import ObjectID, UIElement, IContainerLikeInterface
from pygame_gui.core.interfaces import IUIManagerInterface

import main
import modules
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


pygame.init()
background = pygame.image.load('textures/UI/main_bg.jpg')
(width, height) = (1920, 1080)
screen = pygame.display.set_mode((width, height))
manager = pygame_gui.UIManager((width, height), 'data/style.json')
clock = pygame.time.Clock()
pygame.display.set_caption('Tutorial 1')
screen.blit(background, (0, 0))

# Главное меню
main_container = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
title = pygame_gui.elements.UILabel(pygame.Rect((460 * math.pow(width / 1920, 2), 0, 1000, 200)), manager=manager,
                                    text='Spaceship Game', container=main_container,
                                    object_id=ObjectID(object_id='#Title_text', class_id='@boba'))
tet = pygame_gui.elements.UITextBox('<font pixel_size=42>Project by <img src="textures/UI/logo.png">'
                                    ' <a href="vova">Vladimir Yakuba<a/></font>',
                                    pygame.Rect((600 * math.pow(width / 1920, 2), 180, 1000, 200)), manager=manager,
                                    container=main_container,
                                    object_id=ObjectID(object_id='#Title_sub',
                                                       class_id='@boba'))
play = pygame_gui.elements.UIButton(
    pygame.Rect((560 * math.pow(width / 1920, 2), 330, 800, 200 * ((height - 330) / 750))), text='Играть',
    container=main_container,
    object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
settings = pygame_gui.elements.UIButton(
    pygame.Rect((560 * math.pow(width / 1920, 2), 330 + ((height - 330) / 3), 800, 200 * ((height - 330) / 750))),
    text='Настройки',
    container=main_container,
    object_id=ObjectID(object_id='#Title_button', class_id='@boba'))
exit_but = pygame_gui.elements.UIButton(
    pygame.Rect((560 * math.pow(width / 1920, 2), 330 + ((height - 330) / 1.5), 800, 200 * ((height - 330) / 750))),
    text='Выйти', container=main_container,
    object_id=ObjectID(object_id='#Title_button', class_id='@boba'))

# Экран уровней
levels = init_levels()
levels_container = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
for i in range(len(levels)):
    UIButtonWithLevel(pygame.Rect((200 + i % 4 * 400, 200 + i // 4 * 300, 300, 200)), manag=manager,
                      text=str(i + 1), object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                      container=levels_container, level=levels[i])
back_button_play = pygame_gui.elements.UIButton(pygame.Rect((50, 50, 180, 120)), manager=manager,
                                                text='←',
                                                object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                                                container=levels_container)
levels_container.hide()

# Экран настроек
settings_container = pygame_gui.core.UIContainer(pygame.Rect(0, 0, width, height), manager)
pygame_gui.elements.UILabel(pygame.Rect((460 * math.pow(width / 1920, 2), 0, 1000, 200)),
                            manager=manager, text=r'Как то тут пустовато ¯\_☹_/¯',
                            container=settings_container,
                            object_id=ObjectID(object_id='#Title_sub', class_id='@boba'))
back_button_settings = pygame_gui.elements.UIButton(pygame.Rect((50, 50, 180, 120)), manager=manager,
                                                    text='←',
                                                    object_id=ObjectID(object_id='#Title_button', class_id='@boba'),
                                                    container=settings_container)
settings_container.hide()

done = False
while done is False:
    time_delta = clock.tick(60) / 1000.0

    events = pygame.event.get()
    for event in events:
        manager.process_events(event)
        if event.type == pygame.QUIT:
            exit()
        if event.type == 32866:
            try:
                getattr(event, 'link_target')
                webbrowser.open('https://github.com/vovan4ikrutoy')
            except AttributeError:
                pass
        if event.type == 32867:
            if event.ui_element == play:
                main_container.hide()
                levels_container.show()
                screen.fill((30, 30, 30))
            elif event.ui_element == settings:
                main_container.hide()
                settings_container.show()
                screen.fill((30, 30, 30))
            elif event.ui_element == exit_but:
                exit()
            elif event.ui_element == back_button_play:
                levels_container.hide()
                main_container.show()
                screen.blit(background, (0, 0))
            elif event.ui_element == back_button_settings:
                settings_container.hide()
                main_container.show()
                screen.blit(background, (0, 0))
            elif type(event.ui_element) == UIButtonWithLevel:
                main.main(event.ui_element.level)
                done = True

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()
