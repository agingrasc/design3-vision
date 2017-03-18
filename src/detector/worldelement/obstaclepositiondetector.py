import glob

import cv2
import numpy as np

from infrastructure.camera import JSONCameraModelRepository
from detector.robotpositiondetector import CircleDetector


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

    def detect_shape(self, image):
        contours_list = []
        shape = 'Undefined'
        orientation = 'Undefined'
        cimage = self._preProcess(image)
        (_, cnts, _) = cv2.findContours(cimage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts:
            approx = cv2.approxPolyDP(contour, 0.1 * cv2.arcLength(contour, True), True)
            area = cv2.contourArea(approx)

            if (len(approx) == 3 and (area > 600) and (area < 800)):
                shape = 'Triangle'
                orientation = self._get_orientation(approx)
                contours_list.append(approx)
                break
        if(shape == 'Undefined'):
            for contour2 in cnts:
                approx2 = cv2.approxPolyDP(contour2, 0.01 * cv2.arcLength(contour2, True), True)
                area = cv2.contourArea(contour2)
                if ((len(approx2) > 8) and (area > 880) and (area < 980)):
                    shape = 'Circle'
                    contours_list.append(approx2)
                    break
        if(shape == 'Undefined'):
            raise ShapeNotFound
        return shape, contours_list, cimage, orientation

    def _preProcess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 180, 180)
        return edged

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
        if(tip[1] - base1[1]) < 0 and (tip[1] - base2[1]) < 0:
            orientation = 'Left'
        elif (tip[1] - base1[1]) > 0 and (tip[1] - base2[1]) > 0:
            orientation = 'Right'
        else:
            raise OrientationNotFound
        return orientation

class Image:
    def __init__(self):
        pass
    def select_region(self, image, points):
        image = image[points[0]:points[1], points[2]:points[3]]
        return image

class ObstacleDetector:
    def __init__(self):
        pass

    def detect_obstacle(self, img):
        img = self._median_blur(img)
        cimg = self._convert_color_image(img)
        obstacles = CircleDetector(RATIO, TARGET_MIN_DISTANCE, TARGET_MIN_RADIUS,
                TARGET_MAX_RADIUS).detect_obstacles_markers(img)
        for i in obstacles[0, :]:
            # draw the outer circle
            cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
        self.square_bounding(obstacles, cimg)
        return cimg, obstacles

    def square_bounding(self, obstacles, cimg):
        i = 0
        while i < obstacles.shape[1]:
            min_x = obstacles[0][i][0] - obstacles[0][i][2]
            min_y = obstacles[0][i][1] - obstacles[0][i][2]
            height = obstacles[0][i][2]
            width = obstacles[0][i][2]
            cv2.rectangle(cimg, (min_x, min_y), (min_x + 2*width, min_y + 2*height), (0, 255, 0), 2)
            i += 1

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

    def list_generator(self, obstacles):
        if obstacles.shape[1] == 0:
            return
        elif obstacles.shape[1] == 1:
            lst1 = self._create_obstacles_coord(obstacles[0][0])
            return lst1
        elif obstacles.shape[1] == 2:
            lst1 = self._create_obstacles_coord(obstacles[0][0])
            lst2 = self._create_obstacles_coord(obstacles[0][1])
            return lst1, lst2
        elif obstacles.shape[1] == 3:
            lst1 = self._create_obstacles_coord(obstacles[0][0])
            lst2 = self._create_obstacles_coord(obstacles[0][1])
            lst3 = self._create_obstacles_coord(obstacles[0][2])
            return lst1, lst2, lst3
        return

    def threshold_obstacles(self, image):
        image = self._median_blur(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_white_hsv = np.array([22, 22, 22])
        higher_white_hsv = np.array([255, 255, 255])
        mask = cv2.inRange(image, lower_white_hsv, higher_white_hsv)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=1)
        return mask


    def _median_blur(self, img):
        img = cv2.medianBlur(img, 5)
        return img
    def _convert_color_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return img

if __name__ == '__main__':
    obstacle_detector = ObstacleDetector()
    sd = ShapeDetector()
    traitement = Image()
    camera_repository = JSONCameraModelRepository('../../../data/camera_models/camera_models.json')
    camera_model = camera_repository.get_camera_model_by_id(0)

    images = glob.glob('../../../data/images/full_scene/*.jpg')


    for filename in images:
        image = cv2.imread(filename, 0)
        imageColor = cv2.imread(filename)

        image = camera_model.undistort_image(image)
        imageColor = camera_model.undistort_image(imageColor)

        try:
            cimg = obstacle_detector.detect_obstacle(image)[0]
            obstacle_coord = obstacle_detector.detect_obstacle(image)[1]
            region_of_interest = obstacle_detector.list_generator(obstacle_coord)
            for points in region_of_interest:
                imageCut = traitement.select_region(imageColor, points)
                shape, contour_list, cimage, orientation = sd.detect_shape(imageCut)
                print(region_of_interest, ' : ', filename, ' : ', shape, orientation)
                cv2.drawContours(imageCut, contour_list, 0, (0, 255, 0), 2)
                cv2.imshow('detected circles', imageCut)
                cv2.waitKey(0)
        except ShapeNotFound:
            pass



