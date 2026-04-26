# core/Heading.py
from enums.direction import direction
from .Constraints import Constraints


class Heading:

    def __init__(self, d: direction, constraints: Constraints = None):
        self.d = d
        self.constraints = Constraints() if constraints is None else constraints

    def check_constraints(self, row: int, col: int, sec: int) -> bool:
        return self.constraints.check_constraints(row, col, sec)
