import math

import cv2
import numpy as np

from domain.world.worldelement import WorldElement


class Robot(WorldElement):
    def __init__(self, position, orientation_vector, frame):
        self._image_position = position
        self._orientation_vector = orientation_vector
        self._angle = self._get_angle_from(self._orientation_vector)
        self._frame = frame
        self._world_position = None

    def draw_in(self, image):
        cv2.circle(image, tuple(self._image_position), 1, (255, 0, 0), 2)
        cv2.line(image, tuple(self._orientation_vector[0]), tuple(self._orientation_vector[1]), (0, 255, 0), 2)
        cv2.putText(image, str(round(self._angle, 2)), tuple(self._orientation_vector[1]),
                    fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1.2,
                    color=(0, 0, 0))

    def set_world_position(self, position):
        self._world_position = position

    def set_image_position(self, position):
        self._image_position = position

    def _get_angle_from(self, direction):
        dy = direction[1][1] - direction[0][1]
        dx = direction[1][0] - direction[0][0]

        angle = math.atan2(-dy, dx)

        return np.rad2deg(angle)
