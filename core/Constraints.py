# core/constraints.py
from dataclasses import dataclass

from enums.hit_type import hit_type


@dataclass
class Sonar:
    row: int
    col: int
    sec: int


@dataclass
class Drone:
    sec: int
    valid: bool


@dataclass
class Hit:
    row: int
    col: int
    hit: hit_type


@dataclass
class Surface:
    sec: int


class Constraints:

    _sonar: list[Sonar]
    _drone: list[Drone]
    _hit: list[Hit]
    _surface: list[Surface]
    _silenced: bool

    def __init__(self, sonar: list[Sonar] = None, drone: list[Drone] = None, hit: list[Hit] = None, surface: list[Surface] = None,
                 silenced: bool = False):

        self._sonar = list() if sonar is None else list(sonar)
        self._drone = list() if drone is None else list(drone)
        self._hit = list() if hit is None else list(hit)
        self._surface = list() if surface is None else list(surface)
        self._silenced = silenced


    def add_sonar(self, row: int, col: int, sec: int) -> None:
        if [row, col, sec].count(-1) != 1:
            raise ValueError("Exactly one of (row, col, sec) must be -1")

        self._sonar.append(Sonar(
            row=row,
            col=col,
            sec=sec
        ))


    def check_sonar(self, row: int, col: int, sec: int) -> bool:
        """validates a set of sonar constraints against the given values.

        Each constraint must have exactly one field set to -1. This function checks that,
        for each constraint, the two specified (non -1) values do not both match the
        corresponding arguments

        Returns True if all constraints pass the check; otherwise, returns False.

        Args:
            row (int): The given row
            col (int): The given column
            sec (int): The given sector

        Returns:
            bool: Whether the constraint holds true (false if violated).
        """
        for constraint in self._sonar:
            r, c, s = constraint.row, constraint.col, constraint.sec

            if r == -1 and not ((col == c) ^ (sec == s)):
                return False
            elif c == -1 and not ((row == r) ^ (sec == s)):
                return False
            elif s == -1 and not ((row == r) ^ (col == c)):
                return False

        return True


    def add_drone(self, sec: int, valid: bool) -> None:
        if sec < 1 or sec > 9:
            raise ValueError("sec must be between 1 and 9")

        self._drone.append(Drone(
            valid=valid,
            sec=sec
        ))


    def check_drone(self, sec: int) -> bool:
        for constraint in self._drone:
            if constraint.valid == (constraint.sec != sec):
                return False

        return True


    def add_hit(self, row: int, col: int, hit: hit_type) -> None:
        if row < 0 or row > 14:
            raise ValueError("row must be between 0 and 14")
        elif col < 0 or col > 14:
            raise ValueError("col must be between 0 and 14")

        self._hit.append(Hit(
            row=row,
            col=col,
            hit=hit
        ))


    def check_hit(self, row: int, col: int) -> bool:
        for constraint in self._hit:
            match constraint.hit:
                case hit_type.MISS:
                    # Must not be within 1 Tile of the hit
                    if abs(row - constraint.row) <= 1 and abs(col - constraint.col) <= 1:
                        return False
                case hit_type.INDIRECT:
                    # Must be within 1 tile of the hit, but not exactly where the hit is
                    if (row, col) == (constraint.row, constraint.col):
                        return False
                    elif abs(row - constraint.row) > 1 or abs(col - constraint.col) > 1:
                        return False
                case hit_type.DIRECT:
                    # Must be exactly where the hit is
                    if row != constraint.row or col != constraint.col:
                        return False
                case _:
                    raise ValueError("Invalid hit type")
        return True


    def add_surface(self, sec: int) -> None:
        if sec < 1 or sec > 9:
            raise ValueError("sec must be between 1 and 9")
        self._surface.append(Surface(
            sec=sec
        ))


    def check_surface(self, sec: int) -> bool:
        return all(sec == constraint.sec for constraint in self._surface)


    def check_constraints(self, row: int, col: int, sec: int) -> bool:
        return (
            self.check_sonar(row, col, sec)
            and self.check_drone(sec)
            and self.check_hit(row, col)
            and self.check_surface(sec)
        )


    # It should be impossible for silence to be applied more than once to a single heading,
    # however, just in case, it would be a good idea to implement that functionality
    def set_silenced(self, silenced: bool) -> None:
        self._silenced = silenced


    def get_silenced(self) -> bool:
        return self._silenced


    def is_surfaced(self) -> bool:
        return True if len(self._surface) > 0 else False
