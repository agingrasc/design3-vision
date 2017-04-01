import cv2
import numpy as np

from domain.world.worldelement import WorldElement


class Obstacle(WorldElement):
    def __init__(self, position, radius):
        self._position = position
        self._image_position = None
        self._radius = radius
        self._shape = None
        self._orientation = ""
        self._world_position = None

    def set_shape(self, shape):
        self._shape = np.array(shape)

    def set_orientation(self, orientation):
        self._orientation = orientation

    def set_position(self, position):
        self._image_position = position

    def set_world_position(self, coordinates):
        self._world_position = coordinates

    def draw_in(self, image):
        cv2.circle(image, (self._image_position[0], self._image_position[1]), self._radius, (255, 0, 0), 2)
        cv2.circle(image, (self._image_position[0], self._image_position[1]), 1, (255, 0, 0), 2)
        cv2.drawContours(image, [self._shape], -1, (0, 255, 0), 2)

