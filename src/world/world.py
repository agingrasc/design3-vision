from geometry.coordinate import Coordinate


class World:
    def __init__(self, width, length, origin_x, origin_y, target_to_world):
        self._width = width
        self._length = length
        self._unit = "mm"
        self._image_origin = Coordinate(origin_x, origin_y)
        self._target_to_world = target_to_world
