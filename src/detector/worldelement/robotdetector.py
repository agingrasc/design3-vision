import cv2
import math

from detector.shape.circledetector import NoMatchingCirclesFound
from detector.shape.squaredetector import SquareDetector
from src.detector.worldelement.iworldelementdetector import IWorldElementDetector
from src.config import *

from world.robot import Robot


def euc_distance(p1, p2):
    distance = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    return distance


class RobotDetector(IWorldElementDetector):
    def __init__(self, shape_factory):
        self._shape_factory = shape_factory

    def detect(self, image):
        threshold = self._threshold_robot_makers(image)

        ##### Commented out for performance reason for now ####
        # robot_frame = self._detect_robot_frame(image)

        robot_markers = self._detect_robot_markers(threshold)

        if self._ensure_has_all_markers(robot_markers):
            raise NoMatchingCirclesFound

        robot_position = self._get_robot_position(robot_markers)
        orientation_vector = self._get_direction_vector(robot_position, robot_markers)

        return Robot(robot_position, orientation_vector, None)

    def _threshold_robot_makers(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image, LOWER_FUCHSIA_HSV, HIGHER_FUCHSIA_HSV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel, iterations=3)
        return mask

    def _detect_robot_markers(self, threshold):
        contours = np.array(cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1])
        robot_markers = np.array([self._find_center_of_mass(contour) for contour in contours])
        return np.array(robot_markers)

    def _get_robot_position(self, targets_center):
        (r_x, r_y), r_r = cv2.minEnclosingCircle(targets_center)
        return (int(r_x), int(r_y))

    def _get_direction_vector(self, robot_position, robot_markers):
        leading_marker = self._get_leading_marker(robot_markers)
        direction_vector = [robot_position, leading_marker]
        return direction_vector

    def _get_leading_marker(self, markers):
        tip = markers[0]
        max_mean = 0
        for marker in markers:
            mean = self._find_mean_distance(marker, markers)
            if mean > max_mean:
                max_mean = mean
                tip = marker
        return tip

    def _find_center_of_mass(self, contour):
        contour_moments = cv2.moments(contour)
        center_x = int(contour_moments["m10"] / contour_moments["m00"])
        center_y = int(contour_moments["m01"] / contour_moments["m00"])
        return [center_x, center_y]

    def _ensure_has_all_markers(self, markers):
        return len(markers) < NUMBER_OF_MARKERS

    def _detect_robot_frame(self, image):
        squares = SquareDetector(self._shape_factory).detect(image)
        squares = [square for square in squares if 14000 <= square.area() <= 18000]
        if len(squares) > 0:
            return squares[0]
        else:
            return None

    def _find_mean_distance(self, point, points):
        sum = 0
        for p in points:
            if point[0] != p[0] and point[1] != p[1]:
                sum += euc_distance(point, p)
        mean_distance = sum / len(points) - 1
        return mean_distance
