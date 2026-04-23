# enums/scene_state.py
from enum import Enum


class scene_state(Enum):
    CONTINUE = 0
    POP_SCENE = 1
    PUSH_GAME_SCENE = 2
    PUSH_OPTIONS_SCENE = 3
    PUSH_START_SCENE = 4
    QUIT = 5