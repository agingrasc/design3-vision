import cv2
import glob
import math
import numpy as np

NUMBER_OF_MARKERS = 3


def euc_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class NoRobotMarkersFound(Exception):
    pass


class RobotPositionDetector:
    def detect_position(self, image):
        image = self._preprocess(image)
        threshold = self._threshold_robot_makers(image)

        robot_markers = self._detect_markers_from_circles(threshold)
        robot_position = self._get_robot_position(robot_markers)

        if self._missing_markers(robot_markers):
            markers = self._detect_markers_from_center_of_mass(threshold, robot_position, robot_markers)

            if self._missing_markers(markers):
                raise NoRobotMarkersFound

            robot_position = self._get_robot_position(markers)

        return robot_position

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

    def _detect_markers_from_circles(self, threshold_image):
        robot_markers = cv2.HoughCircles(threshold_image, cv2.HOUGH_GRADIENT, 2.0, 12, param1=50, param2=30,
                                         minRadius=5,
                                         maxRadius=30)
        if robot_markers is not None:
            robot_markers = np.round(robot_markers[0, :]).astype("int")
            robot_markers = np.array([position[0:2] for position in robot_markers])
            return robot_markers
        else:
            raise NoRobotMarkersFound

    def _detect_markers_from_center_of_mass(self, threshold, approx_center, contours):
        center_of_masses = []
        cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts[1]:
            try:
                center_of_masses.append(self._find_center_of_mass(contour))
            except ZeroDivisionError:
                continue
        neighbours = closest_from(approx_center, center_of_masses)

        contours = contours.tolist()
        contours.append(neighbours[0])
        contours.append(neighbours[1])
        contours.append(neighbours[2])
        return np.array(contours)

    def _find_center_of_mass(self, contour):
        contour_moments = cv2.moments(contour)
        center_x = int(contour_moments["m10"] / contour_moments["m00"])
        center_y = int(contour_moments["m01"] / contour_moments["m00"])
        return [center_x, center_y]

    def _get_robot_position(self, contours):
        (r_x, r_y), r_r = cv2.minEnclosingCircle(contours)
        return (int(r_x), int(r_y))

    def _missing_markers(self, markers):
        return len(markers) < NUMBER_OF_MARKERS


def closest_from(point, points):
    return sorted(points, key=lambda p: euc_distance(point, p))


if __name__ == '__main__':
    robot_detector = RobotPositionDetector()
    images = glob.glob('../../data/images/robot_images/*.jpg')

    for filename in images:
        image = cv2.imread(filename)

        robot_position = robot_detector.detect_position(image)

        cv2.circle(image, robot_position, 1, (0, 0, 0), 2)
        cv2.imshow("Position", image)
        cv2.waitKey(3000)
