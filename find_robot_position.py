import cv2
import glob

import math

import numpy as np


class RobotDetector:
    def detect_robot_position(self, image):
        image = self._preprocess(image)
        threshold = self._threshold_robot_makers(image)
        circles = cv2.HoughCircles(threshold, cv2.HOUGH_GRADIENT, 2.0, 12, param1=50, param2=30, minRadius=5,
                                   maxRadius=30)

        position = {}

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            contours = np.array([x[0:2] for x in circles])
            (x, y), radius = cv2.minEnclosingCircle(contours)

            center_of_robot = [x, y]

            center = (int(x), int(y))
            radius = int(radius)

            if len(circles) < 3:
                center_of_masses = []
                cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in cnts[1]:
                    M = cv2.moments(contour)
                    try:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        center = [cX, cY]
                        center_of_masses.append(center)
                    except ZeroDivisionError:
                        continue

                c = closest(center_of_masses, center_of_robot)

                contours = contours.tolist()
                contours.append(c[0])
                contours.append(c[1])
                contours.append(c[2])
                contours = np.array(contours)

                (r_x, r_y), r_r = cv2.minEnclosingCircle(contours)

                center = (int(r_x), int(r_y))
                radius = int(r_r)

            position = {"center": center, "radius": radius}

        return position

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


def closest(points, point):
    return sorted(points, key=lambda p: math.sqrt((p[0] - point[0]) ** 2 + (p[1] - point[1]) ** 2))


if __name__ == '__main__':
    robot_detector = RobotDetector()
    images = glob.glob('data/images/robot_targets/*.jpg')

    for filename in images:
        image = cv2.imread(filename)

        robot_position = robot_detector.detect_robot_position(image)
