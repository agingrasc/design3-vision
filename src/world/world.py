from geometry.coordinate import Coordinate


class World:
    def __init__(self, width, length, origin_x, origin_y):
        self._width = width
        self._length = length
        self._unit = "cm"
        self._image_origin = Coordinate(origin_x, origin_y)
