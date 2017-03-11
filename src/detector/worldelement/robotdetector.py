import cv2
import glob
import math
import numpy as np

from detector.shape.circledetector import NoMatchingCirclesFound, CircleDetector
from infrastructure.camera import JSONCameraModelRepository
from world.robot import Robot

NUMBER_OF_MARKERS = 3
TARGET_MIN_DISTANCE = 12
TARGET_MIN_RADIUS = 5
TARGET_MAX_RADIUS = 30


def euc_distance(p1, p2):
    distance = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    return distance


class RobotDetector:
    def detect(self, image):
        image = self._preprocess(image)
        threshold = self._threshold_robot_makers(image)

        robot_markers = CircleDetector(TARGET_MIN_DISTANCE, TARGET_MIN_RADIUS, TARGET_MAX_RADIUS).detect(threshold)
        robot_position = self._get_robot_position(robot_markers)

        if self._missing_markers(robot_markers):
            robot_markers = self._detect_markers_from_center_of_mass(threshold, robot_position, robot_markers)

            if self._missing_markers(robot_markers):
                raise NoMatchingCirclesFound

            robot_position = self._get_robot_position(robot_markers)

        leading_marker = self._get_leading_marker(robot_markers)
        direction_vector = [robot_position, leading_marker]

        return Robot(robot_position, direction_vector)

    def _preprocess(self, image):
        image = cv2.medianBlur(image, ksize=5)
        return image

    def _threshold_robot_makers(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_fuchia_hsv = np.array([120, 100, 100])
        higher_fuchia_hsv = np.array([176, 255, 255])
        mask = cv2.inRange(image, lower_fuchia_hsv, higher_fuchia_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=1)
        return mask

    def _detect_markers_from_center_of_mass(self, threshold, approx_center, contours):
        center_of_masses = []
        cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts[1]:
            try:
                center_of_masses.append(self._find_center_of_mass(contour))
            except ZeroDivisionError:
                continue

        new_points = order_by_neighbours(approx_center, center_of_masses)

        contours = contours.tolist()

        to_add = []
        for new in new_points:
            duplicate = False
            for contour in contours:
                if euc_distance(new, contour) < 10 or euc_distance(new, contour) > 125:
                    duplicate = True
            if duplicate is False:
                to_add.append(new)

        for add in to_add:
            contours.append(add)

        return np.array(contours)

    def _get_leading_marker(self, markers):
        tip = markers[0]
        max_mean = 0
        for marker in markers:
            mean = find_mean_distance(marker, markers)
            if mean > max_mean:
                max_mean = mean
                tip = marker
        return tip

    def _get_robot_position(self, contours):
        (r_x, r_y), r_r = cv2.minEnclosingCircle(contours)
        return (int(r_x), int(r_y))

    def _find_center_of_mass(self, contour):
        contour_moments = cv2.moments(contour)
        center_x = int(contour_moments["m10"] / contour_moments["m00"])
        center_y = int(contour_moments["m01"] / contour_moments["m00"])
        return [center_x, center_y]

    def _missing_markers(self, markers):
        return len(markers) < NUMBER_OF_MARKERS


def order_by_neighbours(point, points):
    return sorted(points, key=lambda p: euc_distance(point, p))


def find_mean_distance(point, points):
    sum = 0
    for p in points:
        if point[0] != p[0] and point[1] != p[1]:
            sum += euc_distance(point, p)
    mean_distance = sum / len(points) - 1
    return mean_distance


if __name__ == '__main__':
    robot_detector = RobotDetector()
    camera_repository = JSONCameraModelRepository('../../../data/camera_models/camera_models.json')
    camera_model = camera_repository.get_camera_model_by_id(0)

    images = glob.glob('../../../data/images/robot_images/*.jpg')

    for filename in images:
        image = cv2.imread(filename)

        image = camera_model.undistort_image(image)

        try:
            robot = robot_detector.detect(image)

            robot.draw_in(image)
        except NoMatchingCirclesFound:
            pass

        cv2.imshow("Position", image)
        cv2.waitKey(3000)
