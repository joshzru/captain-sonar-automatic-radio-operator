# core/Heading.py
from enums.direction import direction
from .Restraints import Restraints


class Heading:

    def __init__(self, d: direction, restraints: Restraints = None):
        self.d = d
        self.restraints = Restraints() if restraints is None else restraints

    def check_restraints(self, row: int, col: int, sec: int) -> bool:
        return self.restraints.check_restraints(row, col, sec)
