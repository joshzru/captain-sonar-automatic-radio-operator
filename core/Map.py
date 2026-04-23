# core/Map.py
import pygame as pg

from os.path import join

import json
from path import get_maps_path, get_fonts_path
from config import AppConfig
from .Tile import Tile
from .AxisLabel import AxisLabel
from .Coordinate import Coordinate


class Map:

    _tiles: list[list[Tile]]
    _trails: dict[Coordinate, list[list[Coordinate]]]

    _row_labels: list[AxisLabel]
    _col_labels: list[AxisLabel]

    def __init__(self, config: AppConfig):
        self._config = config

        font_path: str = join(get_fonts_path(), self._config.commandline.font)
        self._font: pg.font.Font = pg.font.Font(font_path, 24)

        side_length = config.tile.side_length
        map_length = config.maps.standard_length
        map_spacing = config.maps.spacing
        x, y = config.maps.pos

        self._rect = pg.Rect(x, y, (side_length * map_length) + (map_spacing * (map_length - 1)),
                                   (side_length * map_length) + (map_spacing * (map_length - 1)))

        self._row_labels = []
        self._col_labels = []
        self.create_axis_labels()

        self._trails = dict()
        self._tiles = list()
        self.load_tiles_from_array(self.load_map_from_file("foxtrot"))

        self.assign_axis_labels()

    def load_map_from_file(self, name: str) -> list[list[int]]:
        with open(join(get_maps_path(), name + ".json"), "r") as f:
            map_array: list[list[int]] = json.load(f)
        return map_array

    def load_tiles_from_array(self, map_array: list[list[int]]) -> None:
        tile_length = self._config.tile.side_length
        map_spacing = self._config.maps.spacing

        self._tiles.clear()
        tile_row: list[Tile] = []

        x: int = self._rect.x
        y: int = self._rect.y

        row_indx: int
        row: list[int]
        for row_indx, row in enumerate(map_array):

            column_indx: int
            type: int
            for column_indx, type in enumerate(row):
                tile_row.append(Tile(x, y, row_indx, column_indx, type, self._config, self.draw_trails))
                x += tile_length + map_spacing

            x = self._rect.x
            y += tile_length + map_spacing

            self._tiles.append(tile_row)
            tile_row = []

    def draw(self, screen: pg.Surface) -> None:
        row: list[Tile]
        for row in self._tiles:
            tile: Tile
            for tile in row:
                tile.draw(screen)

        for row_label in self._row_labels:
            row_label.draw(screen)

        for col_label in self._col_labels:
            col_label.draw(screen)

    # Add arguments that allow for delegation to specific Tiles rather than all at once.
    def handle_event(self, event: pg.event.Event) -> None:
        for row_label in self._row_labels:
            row_label.handle_event(event)

        for col_label in self._col_labels:
            col_label.handle_event(event)

        if event.type == pg.MOUSEMOTION:

            row: list[Tile]
            for row in self._tiles:

                tile: Tile
                for tile in row:
                    tile.check_active(event.pos)

    def get_tile_type(self, row: int, col: int) -> int:
        if row >= 0 and row <= 14 and col >= 0 and col <= 14:
            return self._tiles[row][col].type

    def receive_heat_map(self, heat_map: list[list[int]]):
        for row in range(15):
            for col in range(15):
                tile: Tile = self._tiles[row][col]
                value: int = heat_map[row][col]

                tile.visits = value

    def receive_trails(self, trails: dict[Coordinate, list[list[Coordinate]]]) -> None:
        self._trails = trails

    def draw_trails(self, screen: pg.Surface, row: int, col: int) -> None:
        if trails := self._trails.get(Coordinate(row, col), False):
            trails: list[list[Coordinate]]
            for trail in trails:
                if len(trail) < 1:
                    continue
                for tile1, tile2 in zip(trail[:-1], trail[1:]):
                    first_tile = self._tiles[tile1.row][tile1.col]
                    second_tile = self._tiles[tile2.row][tile2.col]
                    pg.draw.line(screen, self._config.commandline.font_color, first_tile.get_center(), second_tile.get_center())
                start_row, start_col = trail[0]
                start_tile = self._tiles[start_row][start_col]
                pg.draw.circle(screen, self._config.commandline.font_color, start_tile.get_center(), 3)

    def create_axis_labels(self) -> None:
        x, y = self._config.maps.pos
        next_distance = self._config.tile.side_length + self._config.maps.spacing

        row_x = x - next_distance
        row_y = y
        for row_label in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]:
            axis_label: AxisLabel = AxisLabel(row_x, row_y, row_label, self._config)
            self._row_labels.append(axis_label)
            row_y += next_distance

        col_x = x
        col_y = y - next_distance
        for col_label in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]:
            axis_label: AxisLabel = AxisLabel(col_x, col_y, col_label, self._config)
            self._col_labels.append(axis_label)
            col_x += next_distance

    # Could change to a single map() call
    def assign_axis_labels(self) -> None:
        for row in range(15):
            for col in range(15):
                tile = self._tiles[row][col]
                row_label = self._row_labels[row]
                col_label = self._col_labels[col]

                tile.set_row_label(row_label)
                tile.set_col_label(col_label)
