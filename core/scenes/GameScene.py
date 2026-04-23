# core/scenes/GameScene.py
import pygame as pg

from .Scene import Scene
from config import AppConfig
from ..Map import Map
from ..CommandLine import CommandLine
from ..RadioOperator import RadioOperator
from enums import scene_state


class GameScene(Scene):

    _map: Map
    _cmd: CommandLine
    _operator: RadioOperator

    def __init__(self, config: AppConfig):
        self._config = config

        self.set_window_config(config.window._780p)

        self._map = Map(config)
        self._operator = RadioOperator(
            self._map.get_tile_type,
            self._map.receive_heat_map,
            self._map.receive_trails
        )
        self._cmd = CommandLine(config, self._operator.receive_envelope)


    def tick(self, dt: int) -> scene_state:
        return_state = scene_state.CONTINUE
        
        for event in pg.event.get():
            self._map.handle_event(event)
            return_state = self.mutate_state(return_state, self._cmd.handle_event(event))
            return_state = self.mutate_state(return_state, self.handle_event(event))

        self._cmd.tick(dt)

        self._screen.fill(self._config.colors.black)

        self.draw()

        pg.display.flip()
        
        return return_state

    def draw(self) -> None:
        self._map.draw(self._screen)
        self._cmd.draw(self._screen)

    def handle_event(self, event: pg.event.Event) -> scene_state:
        if event.type == pg.QUIT:
            return scene_state.QUIT
        return scene_state.CONTINUE

    def on_exit(self) -> None: ...
    
    def on_enter(self) -> None: ...