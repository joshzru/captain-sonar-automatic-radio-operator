# core/Envelopes.py
from dataclasses import dataclass
from abc import ABC

from enums.command_type import command_type
from enums.direction import direction
from enums.hit_type import hit_type


@dataclass
class Command(ABC):
    command: command_type


@dataclass
class DirectionCommand(Command):
    d: direction


@dataclass
class SonarCommand(Command):
    row: int
    col: int
    sec: int


@dataclass
class DroneCommand(Command):
    sec: int
    valid: bool


@dataclass
class HitCommand(Command):
    row: int
    col: int
    hit: hit_type


@dataclass
class SurfaceCommand(Command):
    sec: int


@dataclass
class SilenceCommand(Command):
    pass
