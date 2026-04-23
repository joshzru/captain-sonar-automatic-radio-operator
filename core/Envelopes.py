# core/Envelopes.py
from dataclasses import dataclass
from abc import ABC

from enums.command_type import command_type
from enums.direction import direction
from enums.hit_type import hit_type


@dataclass
class Envelope(ABC):
    command: command_type


@dataclass
class DirectionCommand(Envelope):
    d: direction


@dataclass
class SonarCommand(Envelope):
    row: int
    col: int
    sec: int


@dataclass
class DroneCommand(Envelope):
    sec: int
    valid: bool


@dataclass
class HitCommand(Envelope):
    row: int
    col: int
    hit: hit_type


@dataclass
class SurfaceCommand(Envelope):
    sec: int


@dataclass
class SilenceCommand(Envelope):
    pass
