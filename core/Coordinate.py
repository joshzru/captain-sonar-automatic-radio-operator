# core/Coordinate.py

class Coordinate:

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __iter__(self):
        yield self.row
        yield self.col
