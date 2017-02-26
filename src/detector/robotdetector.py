import cv2
import glob

import math

import numpy as np


def euc_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class NoRobotMarkersFound(Exception):
    pass


class RobotDetector:
    def detect_position(self, image):
        image = self._preprocess(image)
        threshold = self._threshold_robot_makers(image)
        robot_markers = self._find_robot_markers(threshold)

        contours = np.array([position[0:2] for position in robot_markers])
        center, radius = self._get_enclosing_circle(contours)

        if self._has_all_robot_markers(robot_markers):
            contours = self._detect_with_center_of_mass(threshold, center, contours)

            if self._has_all_robot_markers(contours):
                raise NoRobotMarkersFound

            center, radius = self._get_enclosing_circle(contours)
        return {
            "center": center,
            "radius": radius
        }

    def _preprocess(self, image):
        image = cv2.medianBlur(image, ksize=5)
        return image

    def _threshold_robot_makers(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_fuchia_hsv = np.array([120, 90, 90])
        higher_fuchia_hsv = np.array([205, 255, 255])
        mask = cv2.inRange(image, lower_fuchia_hsv, higher_fuchia_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel)
        return mask

    def _find_robot_markers(self, image):
        robot_markers = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 2.0, 12, param1=50, param2=30, minRadius=5,
                                         maxRadius=30)
        if robot_markers is not None:
            return np.round(robot_markers[0, :]).astype("int")
        else:
            raise NoRobotMarkersFound

    def _detect_with_center_of_mass(self, threshold, approx_center, contours):
        center_of_masses = []
        cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts[1]:
            try:
                center = self._find_center_of_mass(contour)
                center_of_masses.append(center)
            except ZeroDivisionError:
                continue
        c = closest_from(approx_center, center_of_masses)

        contours = contours.tolist()
        contours.append(c[0])
        contours.append(c[1])
        contours.append(c[2])
        return np.array(contours)

    def _find_center_of_mass(self, contour):
        contour_moments = cv2.moments(contour)
        center_x = int(contour_moments["m10"] / contour_moments["m00"])
        center_y = int(contour_moments["m01"] / contour_moments["m00"])
        return [center_x, center_y]

    def _has_all_robot_markers(self, markers):
        return len(markers) < 3

    def _get_enclosing_circle(self, contours):
        (r_x, r_y), r_r = cv2.minEnclosingCircle(contours)
        return (int(r_x), int(r_y)), int(r_r)


def closest_from(point, points):
    return sorted(points, key=lambda p: euc_distance(point, p))


if __name__ == '__main__':
    robot_detector = RobotDetector()
    images = glob.glob('data/images/robot_images/*.jpg')

    for filename in images:
        image = cv2.imread(filename)

        robot_position = robot_detector.detect_position(image)
