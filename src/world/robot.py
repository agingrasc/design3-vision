import cv2
import math

import numpy as np


class Robot:
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

        if self._frame is not None:
            self._frame.draw_in(image)

    def set_world_position(self, position):
        self._world_position = position

    def set_image_position(self, position):
        self._image_position = position

    def _get_angle_from(self, direction):
        u = [1, 0]
        v = direction[1] - direction[0]

        angle = math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

        return np.rad2deg(angle)
