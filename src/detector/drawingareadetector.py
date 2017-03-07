import cv2
import numpy as np


class NoDrawingAreaFound(Exception):
    pass


class DrawingAreaDetector:
    def __init__(self):
        pass

    def detect_area(self, image):
        image = self._preprocess(image)
        mask = self._threshold_green(image)
        drawing_area = self._find_drawing_area(mask)
        return drawing_area

    def _preprocess(self, image):
        image = cv2.medianBlur(image, ksize=3)
        return image

    def _threshold_green(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green_hsv = np.array([50, 100, 100])
        upper_green_hsv = np.array([80, 255, 255])
        mask = cv2.inRange(image, lower_green_hsv, upper_green_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=(5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=3)
        return mask

    def _find_drawing_area(self, image):
        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        biggest_contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]
        epsilon = 0.02 * cv2.arcLength(biggest_contour, True)
        square_approximation = cv2.approxPolyDP(biggest_contour, epsilon, True)
        if len(square_approximation) == 4:
            square_approximation = np.array([corner[0] for corner in square_approximation])
            return square_approximation.tolist()
        else:
            raise NoDrawingAreaFound
