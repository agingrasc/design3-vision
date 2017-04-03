import cv2
import numpy as np

from domain.detector.shape.circledetector import CircleDetector, NoMatchingCirclesFound
from domain.detector.worldelement.iworldelementdetector import IWorldElementDetector
from domain.world.obstacle import Obstacle

RATIO = 1
TARGET_MIN_DISTANCE = 20
TARGET_MIN_RADIUS = 30
TARGET_MAX_RADIUS = 42


class ShapeNotFound(Exception):
    pass


class OrientationNotFound(Exception):
    pass


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, image):
        contours_list = []

        shape = None
        orientation = ""

        cimage = cv2.Canny(image.copy(), 150, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cimage = cv2.dilate(cimage, kernel)
        (_, cnts, _) = cv2.findContours(cimage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for contour in cnts:
            approx = cv2.approxPolyDP(contour, 0.1 * cv2.arcLength(contour, True), True)
            area = cv2.contourArea(approx)

            if len(approx) == 3 and (area > 400) and (area < 800):
                shape = 'Triangle'
                orientation = self._get_orientation(approx)
                contours_list.append(approx)
                break

        if shape is None:
            for contour2 in cnts:
                approx2 = cv2.approxPolyDP(contour2, 0.01 * cv2.arcLength(contour2, True), True)
                area = cv2.contourArea(contour2)
                if (len(approx2) > 3) and (area > 500) and (area < 980):
                    shape = 'Circle'
                    contours_list.append(approx2)
                    break

        if shape is None:
            raise ShapeNotFound

        return shape, contours_list, cimage, orientation

    def _get_orientation(self, array):
        point1 = (array[0][0][0], array[0][0][1])
        point2 = (array[1][0][0], array[1][0][1])
        point3 = (array[2][0][0], array[2][0][1])
        distanceP1P2 = np.math.hypot(point2[0] - point1[0], point2[1] - point1[1])
        distanceP1P3 = np.math.hypot(point3[0] - point1[0], point3[1] - point1[1])
        distanceP2P3 = np.math.hypot(point3[0] - point2[0], point3[1] - point2[1])
        if min(distanceP1P2, distanceP1P3, distanceP2P3) == distanceP1P2:
            tip = point3
            base1 = point1
            base2 = point2
        elif min(distanceP1P2, distanceP1P3, distanceP2P3) == distanceP1P3:
            tip = point2
            base1 = point1
            base2 = point3
        else:
            tip = point1
            base1 = point2
            base2 = point3
        if (tip[1] - base1[1]) < 0 and (tip[1] - base2[1]) < 0:
            orientation = 'Left'
        elif (tip[1] - base1[1]) > 0 and (tip[1] - base2[1]) > 0:
            orientation = 'Right'
        else:
            raise OrientationNotFound
        return orientation


class NoObstaclesFound(Exception):
    pass


class ObstacleDetector(IWorldElementDetector):
    def __init__(self, shape_detector):
        self._shape_detector = shape_detector

    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        try:
            obstacles_circle = CircleDetector(RATIO, TARGET_MIN_DISTANCE, TARGET_MIN_RADIUS,
                                              TARGET_MAX_RADIUS).detect_obstacles_markers(gray)
        except NoMatchingCirclesFound:
            raise NoObstaclesFound

        obstacles = []

        for obstacle_circle in obstacles_circle[0, :]:
            region_of_interest = self._create_obstacles_coord(obstacle_circle)

            obstacle = Obstacle((obstacle_circle[0], obstacle_circle[1]), obstacle_circle[2])
            obstacle_region = self.select_region(image, region_of_interest)

            try:
                shape, contour_list, cimage, orientation = self._shape_detector.detect(obstacle_region)
                shape_contour = contour_list[0][:, 0]
                top_left = [region_of_interest[0], region_of_interest[2]]
                contour_list = [[point[0] + top_left[1], point[1] + top_left[0]] for point in shape_contour]

                obstacle.set_shape(contour_list)
                obstacle.set_orientation(orientation)
            except ShapeNotFound:
                pass

            obstacles.append(obstacle)

        if len(obstacles) == 0:
            raise NoObstaclesFound

        return obstacles

    def _create_obstacles_coord(self, obstacles):
        lst = []
        min_x = obstacles[0] - obstacles[2]
        min_y = obstacles[1] - obstacles[2]
        max_x = obstacles[0] + obstacles[2]
        max_y = obstacles[1] + obstacles[2]
        lst.append(min_y)
        lst.append(max_y)
        lst.append(min_x)
        lst.append(max_x)
        return lst

    def select_region(self, image, points):
        image = image[points[0]:points[1], points[2]:points[3]]
        return image

    def threshold_obstacles(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_white_hsv = np.array([22, 22, 22])
        higher_white_hsv = np.array([255, 255, 255])
        mask = cv2.inRange(image, lower_white_hsv, higher_white_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=1)
        return mask
