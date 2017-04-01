import cv2
import numpy as np


class NoMatchingCirclesFound(Exception):
    pass


class CircleDetector:
    def __init__(self, min_distance, min_radius, max_radius):
        self._min_distance = min_distance
        self._min_radius = min_radius
        self._max_radius = max_radius

    def detect(self, image):
        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1.7, self._min_distance, param1=50, param2=30,
                                   minRadius=self._min_radius,
                                   maxRadius=self._max_radius)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            circles = np.array([position[0:2] for position in circles])
            return circles
        else:
            raise NoMatchingCirclesFound
