# core/Tile.py
import pygame as pg
import types
from config import AppConfig
from .AxisLabel import AxisLabel


class Tile:

    _draw_trail: types.FunctionType
    _row_label: AxisLabel = None
    _col_label: AxisLabel = None

    def __init__(self, x: int, y: int, row: int, column: int, type: int, config: AppConfig, draw_trail_delegate: types.FunctionType) -> None:
        self._config = config

        side_length = config.tile.side_length

        self._rect: pg.rect.Rect = pg.Rect(x, y, side_length, side_length)
        self.type: int = type
        self.active: bool = False
        self.row: int = row
        self.col: int = column
        self._max_vixits = 30
        self.visits = 0
        self._draw_trail = draw_trail_delegate

        self._active_color: tuple[int, int, int] = self._config.tile.active_color
        self._target_color: tuple[int, int, int] = self._config.tile.target_color

        self._border_width: int = self._config.tile.border_width
        self._border_radius: int = self._config.tile.border_radius
        self._target_radius: int = self._config.tile.target_radius

        if type:
            self._color = self._config.tile.land_color
            self._border_radius += 4
        else:
            self._color = self._config.tile.water_color

    def draw(self, screen: pg.Surface):

        highlight: bool = self.active or self._label_is_hovered()
        if self.type == 0 and highlight:
            pg.draw.rect(screen, self._active_color, self._rect.move(-2, -2), self._border_width, self._border_radius)
            if self.visits > 0 and highlight:
                if self.active:
                    self._draw_trail(screen, self.row, self.col)
                pg.draw.circle(screen, self._target_color, self._rect.move(-2, -2).center, self._border_width, self._border_radius)
        else:
            pg.draw.rect(screen, self._color, self._rect, self._border_width, self._border_radius)
            if self.visits > 0:
                pg.draw.circle(screen, self._target_color, self._rect.center, self._target_radius, self._border_width)

    def check_active(self, cursor_pos):
        x, y = cursor_pos

        self.active = self._rect.collidepoint(x, y)

    def get_center(self):
        return self._rect.center

    def set_row_label(self, row_label: AxisLabel) -> None:
        self._row_label = row_label

    def set_col_label(self, col_label: AxisLabel) -> None:
        self._col_label = col_label

    def _label_is_hovered(self):
        return (
            (self._row_label is not None and self._row_label.is_hovered())
            or (self._col_label is not None and self._col_label.is_hovered())
        )
