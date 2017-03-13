import math


class Coordinate:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def distance_from(self, other):
        return math.sqrt(((self._x - other._x) ** 2) + ((self._y - other._y) ** 2))

    def __str__(self):
        return "({0}, {1})".format(self._x, self._y)
