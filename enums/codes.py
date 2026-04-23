# enums/codes.py
from enum import Enum


class codes(Enum):

    UNKNOWN = 0
    INVALID_ARGUMENTS = 2
    INTERSECTING_PATH = 3
    HEADING_ADDED = 4
    SONAR_ADDED = 5
    DRONE_ADDED = 6
    HIT_ADDED = 7
    SURFACE_ADDED = 8
    HEADING_SILENCED = 9
    EXIT = 10
