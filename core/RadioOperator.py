# core/RadioOperator.py
import types

from .Heading import Heading
from .Constraints import Constraints
from .Envelopes import Command, DirectionCommand, SonarCommand, DroneCommand, HitCommand, SurfaceCommand
from enums import codes, direction, command_type
from .Coordinate import Coordinate


class RadioOperator:

    _route: list[Heading]
    _positions: set[Coordinate]
    _current_position: Coordinate
    # Covers the special case of the starting position, since no heading exists for it
    _starting_constraints: Constraints

    _check_tile_type: types.FunctionType
    _send_heat_map: types.FunctionType
    _send_trails: types.FunctionType

    def __init__(self, check_tile_type_delegate: types.FunctionType, send_heat_map_delegate: types.FunctionType,
                 send_trails_delegate: types.FunctionType, starting_constraints: Constraints = None, route: list[Heading] = None):

        self._check_tile_type = check_tile_type_delegate
        self._send_heat_map = send_heat_map_delegate
        self._send_trails = send_trails_delegate

        self._route = list() if route is None else route
        self._starting_constraints = Constraints() if starting_constraints is None else starting_constraints
        self._positions = set()

        self._current_position = Coordinate(0, 0)
        self._positions.add(self._current_position)

        for heading in self._route:
            x, y = self._current_position

            match heading.d:

                case direction.NORTH:
                    self._current_position = Coordinate(x + 1, y)

                case direction.EAST:
                    self._current_position = Coordinate(x, y + 1)

                case direction.SOUTH:
                    self._current_position = Coordinate(x - 1, y)

                case direction.WEST:
                    self._current_position = Coordinate(x, y - 1)

            self._positions.add(self._current_position)

    def receive_envelope(self, envelope: Command) -> codes:
        return_code: codes
        match envelope.command:

            case command_type.DIRECTION:
                envelope: DirectionCommand = envelope
                return_code = self.append_heading(envelope.d)

            case command_type.SONAR:
                envelope: SonarCommand = envelope
                self.get_constraints().add_sonar(envelope.row, envelope.col, envelope.sec)
                return_code = codes.SONAR_ADDED

            case command_type.DRONE:
                envelope: DroneCommand = envelope
                self.get_constraints().add_drone(envelope.sec, envelope.valid)
                return_code = codes.DRONE_ADDED

            case command_type.HIT:
                envelope: HitCommand = envelope
                self.get_constraints().add_hit(envelope.row, envelope.col, envelope.hit)
                return_code = codes.HIT_ADDED

            case command_type.SURFACE:
                envelope: SurfaceCommand = envelope
                self.get_constraints().add_surface(envelope.sec)
                # Previous headings exist, but the path can now retrace them
                self._positions.clear()
                self._positions.add(self._current_position)
                return_code = codes.SURFACE_ADDED

            case command_type.SILENCE:
                self.get_constraints().set_silenced(True)
                # We only want to keep track of the positions we have visited after the silenced heading
                # If we don't do this, silence won't work since it assumes the enemy moved 0 spaces
                self._positions.clear()
                return_code = codes.HEADING_SILENCED

            case _:
                return codes.UNKNOWN

        self.calculate_heat_map()
        return return_code

    def append_heading(self, heading: direction) -> codes:
        next_position: Coordinate

        x, y = self._current_position

        match heading:

            case direction.NORTH:
                next_position = Coordinate(x + 1, y)

            case direction.EAST:
                next_position = Coordinate(x, y + 1)

            case direction.SOUTH:
                next_position = Coordinate(x - 1, y)

            case direction.WEST:
                next_position = Coordinate(x, y - 1)

            case _:
                return codes.INVALID_ARGUMENTS

        if next_position in self._positions:
            return codes.INTERSECTING_PATH

        self._route.append(Heading(heading))
        self._current_position = next_position
        self._positions.add(self._current_position)

        return codes.HEADING_ADDED

    def get_current_heading(self) -> Heading:
        if len(self._route) == 0:
            return Heading(direction.NONE, self._starting_constraints)
        else:
            return self._route[-1]

    def reset_route(self) -> None:
        self._route.clear()
        self._starting_constraints = Constraints()
        self._positions.clear()
        self._current_position = Coordinate(0, 0)

    def get_constraints(self) -> Constraints:
        if len(self._route) == 0:
            return self._starting_constraints
        else:
            return self.get_current_heading().constraints

    def get_sector_from_pos(self, row: int, col: int) -> int:
        return ((row // 5) * 3) + ((col // 5) + 1)

    def calculate_heat_map(self) -> list[list[int]]:
        heat_map: list[list[int]] = [[0 for _ in range(15)] for _ in range(15)]
        trails: dict[Coordinate, list[list[Coordinate]]] = dict()
        pos_visited: set[Coordinate] = set()

        # Handle special case of the starting space
        for row in range(15):
            for col in range(15):
                sec: int = self.get_sector_from_pos(row, col)

                # Bounds check
                if row < 0 or row > 14 or col < 0 or col > 14:
                    continue

                # Type check
                if self._check_tile_type(row, col) == 1:
                    continue

                # Constraints check
                if self._starting_constraints.check_constraints(row, col, sec):
                    if self._starting_constraints.get_silenced():
                        # TODO: Shouldn't ever happen, but implement just in case
                        pass
                    else:
                        # A tuple where the first value is the main trail
                        # and the second value is a list of all extra trails
                        current_trails: tuple[list[Coordinate], list[list[Coordinate]]] = ([Coordinate(row, col)], [])

                        coordinate: Coordinate = Coordinate(row, col)

                        pos_visited.add(coordinate)
                        self._advance_route(row, col, self._route, pos_visited, heat_map, current_trails)
                        pos_visited.remove(coordinate)
                        current_trails[1].append(current_trails[0])
                        for trail in current_trails[1]:
                            if len(trail) <= 1:
                                continue
                            if t := trails.get(trail[-1], False):
                                t.append(trail)
                            else:
                                trails[trail[-1]] = [trail]

        self._send_heat_map(heat_map)
        self._send_trails(trails)
        return heat_map

    def _advance_route(self, prev_row: int, prev_col: int, remaining_route: list[Heading], pos_visited: set[Coordinate],
                       heat_map: list[list[int]], trails: tuple[list[Coordinate], list[list[Coordinate]]]) -> bool:
        if len(remaining_route) == 0:
            heat_map[prev_row][prev_col] += 1
            return True

        current_heading: Heading = remaining_route[0]
        row, col = prev_row, prev_col

        match current_heading.d:
            case direction.NORTH: row -= 1
            case direction.SOUTH: row += 1
            case direction.EAST: col += 1
            case direction.WEST: col -= 1
            case _: raise RuntimeError("Invalid direction processed")

        coordinate: Coordinate = Coordinate(row, col)

        # Bounds check
        if row < 0 or row > 14 or col < 0 or col > 14:
            return False

        # Type check
        if self._check_tile_type(row, col) == 1:
            return False

        # Retrace check
        if coordinate in pos_visited:
            return False

        sec: int = self.get_sector_from_pos(row, col)

        if current_heading.check_constraints(row, col, sec):
            if current_heading.constraints.is_surfaced():
                pos_visited = set()

            pos_visited.add(coordinate)
            trails[0].append(coordinate)
            if current_heading.constraints.get_silenced():
                # Implement pruning to prevent repeating the same paths
                for d in [direction.NORTH, direction.EAST, direction.SOUTH, direction.WEST]:
                    path = []
                    for i in range(1, 6):
                        path.append(Heading(d))
                        new_route = path + remaining_route[1:]
                        new_trails = ([], [])
                        alt_result = self._advance_route(row, col, new_route, pos_visited, heat_map, new_trails)
                        if alt_result:
                            trails[1].append(trails[0] + new_trails[0])
                            for t in new_trails[1]:
                                trails[1].append(trails[0] + t)
            result = self._advance_route(row, col, remaining_route[1:], pos_visited, heat_map, trails)
            if not result:
                trails[0].pop()
            pos_visited.remove(coordinate)
            return result
        else:
            return False
