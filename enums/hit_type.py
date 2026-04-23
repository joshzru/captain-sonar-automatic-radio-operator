# enums/hit_type.py
from enum import Enum


class hit_type(Enum):

    MISS = 0
    INDIRECT = 1
    DIRECT = 2
    UNKNOWN = 3
