import cv2
import math
import numpy as np

NUMBER_OF_MARKERS = 3
RATIO = 1.7
TARGET_MIN_DISTANCE = 12
TARGET_MIN_RADIUS = 5
TARGET_MAX_RADIUS = 30


def euc_distance(p1, p2):
    distance = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    return distance


class NoMatchingCirclesFound(Exception):
    pass


class CircleDetector:
    def __init__(self, ratio, min_distance, min_radius, max_radius):
        self.ratio = ratio
        self._min_distance = min_distance
        self._min_radius = min_radius
        self._max_radius = max_radius

    def detect_robot_markers(self, image):
        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, self.ratio, self._min_distance, param1=50, param2=30,
                                   minRadius=self._min_radius,
                                   maxRadius=self._max_radius)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            circles = np.array([position[0:2] for position in circles])
            return circles
        else:
            raise NoMatchingCirclesFound

    def detect_obstacles_markers(self, image):
        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, self.ratio, self._min_distance, param1=50, param2=60,
                                   minRadius=self._min_radius,
                                   maxRadius=self._max_radius)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            return circles
        else:
            raise NoMatchingCirclesFound
