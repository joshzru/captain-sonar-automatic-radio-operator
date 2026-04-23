# /core/scenes/Scene.py
import pygame as pg

import os
from os.path import join
from abc import ABC, abstractmethod

from config import AppConfig
from path import get_media_path
from enums import scene_state


class Scene(ABC):

    _screen: pg.surface.Surface

    _config: AppConfig
    
    _state_priority: dict[scene_state, int] = {
            scene_state.QUIT: 100,
            scene_state.POP_SCENE: 80,
            scene_state.PUSH_GAME_SCENE: 60,
            scene_state.PUSH_OPTIONS_SCENE: 50,
            scene_state.PUSH_START_SCENE: 40,
            scene_state.CONTINUE: 0
        }

    @abstractmethod
    def on_enter(self) -> None: ...

    @abstractmethod
    def on_exit(self) -> None: ...
    
    @abstractmethod
    def draw(self) -> None: ...

    @abstractmethod
    def handle_event(self, event: pg.event.Event) -> scene_state: ...

    @abstractmethod
    def tick(self, delta_time: int) -> scene_state: ...

    def set_window_config(self, resolution: tuple[int, int]) -> None:

        monitor_width, monitor_height = pg.display.list_modes()[0]
        window_width, window_height = resolution
        icon_path: str = join(get_media_path(), self._config.window.icon_name)
        window_icon = pg.image.load(icon_path)

        pg.display.quit()

        # Center window on monitor
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{monitor_width / 2 - window_width / 2},{monitor_height / 2 - window_height / 2}"
        self._screen = pg.display.set_mode((window_width, window_height))

        pg.display.set_caption(self._config.window.caption)
        pg.display.set_icon(window_icon)
    
    def mutate_state(self, cur: scene_state, new: scene_state) -> scene_state:
        if self._state_priority[new] > self._state_priority[cur]:
            return new
        else:
            return cur
