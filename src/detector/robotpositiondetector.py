import cv2
import glob
import math
import numpy as np

NUMBER_OF_MARKERS = 3
TARGET_MIN_DISTANCE = 12
TARGET_MIN_RADIUS = 5
TARGET_MAX_RADIUS = 30


def euc_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


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


class RobotPositionDetector:
    def detect_position(self, image):
        image = self._preprocess(image)
        threshold = self._threshold_robot_makers(image)

        robot_markers = CircleDetector(TARGET_MIN_DISTANCE, TARGET_MIN_RADIUS, TARGET_MAX_RADIUS).detect(threshold)
        robot_position = self._get_robot_position(robot_markers)

        if self._missing_markers(robot_markers):
            robot_markers = self._detect_markers_from_center_of_mass(threshold, robot_position, robot_markers)

            if self._missing_markers(robot_markers):
                raise NoMatchingCirclesFound

            robot_position = self._get_robot_position(robot_markers)

        direction = self._get_direction_vector(robot_markers, robot_position)

        return {
            "robot_center": robot_position,
            "direction": direction
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

    def _detect_markers_from_center_of_mass(self, threshold, approx_center, contours):
        center_of_masses = []
        cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts[1]:
            try:
                center_of_masses.append(self._find_center_of_mass(contour))
            except ZeroDivisionError:
                continue

        neighbours = order_by_neighbours(approx_center, center_of_masses)

        contours = contours.tolist()
        contours.append(neighbours[0])
        contours.append(neighbours[1])
        contours.append(neighbours[2])
        return np.array(contours)

    def _get_direction_vector(self, markers, robot_position):
        tip = markers[0]
        max_mean = 0
        for marker in markers:
            mean = find_mean_distance(marker, markers)
            if mean > max_mean:
                max_mean = mean
                tip = marker
        return [robot_position, tip]

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


def order_by_neighbours(point, points):
    return sorted(points, key=lambda p: euc_distance(point, p))


def find_mean_distance(point, points):
    sum = 0
    for p in points:
        if point[0] != p[0] and point[1] != p[1]:
            sum += euc_distance(point, p)
    return sum / len(points) - 1


def get_robot_angle(robot_position):
    u = [1, 0]
    v = robot_position['direction'][1] - robot_position['direction'][0]

    angle = math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))

    return np.rad2deg(angle)

if __name__ == '__main__':
    robot_detector = RobotPositionDetector()
    images = glob.glob('../../data/images/robot_images/*.jpg')

    for filename in images:
        image = cv2.imread(filename)

        robot_position = robot_detector.detect_position(image)

        degrees = get_robot_angle(robot_position)

        cv2.circle(image, robot_position['robot_center'], 1, (0, 0, 0), 2)
        cv2.line(image, tuple(robot_position['direction'][0]), tuple(robot_position['direction'][1]), (0, 255, 0), 2)
        cv2.arrowedLine(image, (0, 0), (50, 0), (0, 255, 0), 3)
        cv2.putText(image, str(degrees), tuple(robot_position['direction'][1]), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.0, color=(255, 255, 255))
        cv2.imshow("Position", image)
        cv2.waitKey(3000)
