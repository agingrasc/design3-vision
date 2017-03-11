import cv2
import math

import numpy as np


class Robot:
    def __init__(self, position, direction):
        self._position = position
        self._direction = direction
        self._angle = self._get_angle_from(self._direction)

    def draw_in(self, image):
        cv2.circle(image, self._position, 1, (0, 0, 0), 2)
        cv2.line(image, tuple(self._direction[0]), tuple(self._direction[1]), (0, 255, 0), 2)
        cv2.arrowedLine(image, (0, 0), (50, 0), (0, 255, 0), 3)
        cv2.putText(image, str(round(self._angle, 2)), tuple(self._direction[1]),
                    fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1.2,
                    color=(0, 0, 0))

    def _get_angle_from(self, direction):
        u = [1, 0]
        v = direction[1] - direction[0]

        angle = math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

        return np.rad2deg(angle)
