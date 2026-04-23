# core/AxisLabel.py
import pygame as pg

from os.path import join

from path import get_fonts_path
from config import AppConfig


class AxisLabel:

    _is_hovered: bool = False
    _label_rect: pg.Rect

    def __init__(self, x: int, y: int, label: str, config: AppConfig):
        self._config = config
        self._rect = pg.Rect(x, y, self._config.tile.side_length, self._config.tile.side_length)

        font_path = join(get_fonts_path(), self._config.commandline.font)
        self._font = pg.font.Font(font_path, self._config.tile.side_length)

        self._label = label
        self._label_surface = self._font.render(self._label, True, self._config.commandline.font_color)

        self._label_rect = self._label_surface.get_rect(center=self._rect.center)

    def draw(self, screen: pg.Surface):
        screen.blit(self._label_surface, self._label_rect)

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.MOUSEMOTION:
            self._is_hovered = self._rect.collidepoint(event.pos)

    def is_hovered(self) -> bool:
        return self._is_hovered
