# enums/command_type.py
from enum import Enum


class command_type(Enum):
    DIRECTION = 0
    SONAR = 1
    DRONE = 2
    HIT = 3
    SURFACE = 4
    SILENCE = 5
