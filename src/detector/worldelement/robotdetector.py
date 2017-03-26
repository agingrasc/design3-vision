import cv2
import math

from detector.shape.circledetector import NoMatchingCirclesFound
from detector.shape.squaredetector import SquareDetector
from detector.worldelement.iworldelementdetector import IWorldElementDetector
from config import *

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

        contours = self._detect_robot_markers_contours(threshold)

        robot_markers = np.array([self._find_center_of_mass(contour) for contour in contours])

        if self._ensure_has_all_markers(robot_markers):
            raise NoMatchingCirclesFound

        robot_position = self._get_robot_position(robot_markers)
        orientation_vector = self._get_orientation_vector(robot_position, robot_markers)

        return Robot(robot_position, orientation_vector, None)

    def _threshold_robot_makers(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image, LOWER_FUCHSIA_HSV, HIGHER_FUCHSIA_HSV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel, iterations=3)
        return mask

    def _detect_robot_markers_contours(self, threshold):
        contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        contours = [contour for contour in contours if cv2.contourArea(contour) > 200]
        return np.array(contours)

    def _get_robot_position(self, targets_center):
        (r_x, r_y), r_r = cv2.minEnclosingCircle(targets_center)
        return (int(r_x), int(r_y))

    def _get_orientation_vector(self, robot_position, robot_markers):
        leading_marker = self._get_leading_marker(robot_markers)
        direction_vector = [robot_position, leading_marker]
        return direction_vector

    def _get_leading_marker(self, markers):
        distance_1 = euc_distance(markers[0], markers[1])

        distance_2 = euc_distance(markers[0], markers[2])

        distance_3 = euc_distance(markers[1], markers[2])

        if distance_1 > distance_2 and distance_3 > distance_2:
            return markers[1]
        if distance_1 > distance_3 and distance_2 > distance_3:
            return markers[0]
        else:
            return markers[2]

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
