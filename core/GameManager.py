# core/GameManager.py
import pygame as pg
import logging

from config import AppConfig
from .scenes import Scene, TitleScene, GameScene
from enums import scene_state
import logging

class GameManager:
    
    _active_scene: Scene
    _stack: list[Scene]
    _flag: bool = False
    
    def __init__(self, config: AppConfig):
        self._log = logging.getLogger(__name__)
        
        self._config = config
        self._clock: pg.time.Clock = pg.time.Clock()
        
        self._active_scene = TitleScene(self._config)
        self._stack = []
        self._log.info("Game Manager initialzied")
    
    def run(self):
        self._log.info("Game started")
        while not self._flag:
            dt: int = self._clock.tick(self._config.general.fps)
            state: scene_state = self._active_scene.tick(dt)
            
            match state:
                case scene_state.CONTINUE: continue
                case scene_state.POP_SCENE: self.pop_scene()
                case scene_state.PUSH_GAME_SCENE: self.push_scene(GameScene(self._config))
                case scene_state.PUSH_OPTIONS_SCENE: ...
                case scene_state.PUSH_START_SCENE: self.push_scene(TitleScene(self._config))
                case scene_state.QUIT: self._flag = True
                case _: self._log.warning("Scene returned unknown state in GameManager")

    def pop_scene(self):
        self._active_scene.on_exit()
        self._active_scene = self._stack.pop()
        self._active_scene.on_enter()
    
    def push_scene(self, scene: Scene):
        self._active_scene.on_exit()
        self._stack.append(self._active_scene)
        self._active_scene = scene
