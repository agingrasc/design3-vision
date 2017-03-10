import cv2
import glob

from infrastructure.camera import JSONCameraModelRepository
from detector.robotpositiondetector import CircleDetector
from detector.robotpositiondetector import NoMatchingCirclesFound


RATIO = 1
TARGET_MIN_DISTANCE = 20
TARGET_MIN_RADIUS = 30
TARGET_MAX_RADIUS = 42


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

    def create_list_of_rect(self, obstacles):
        lst = []
        min_x = obstacles[0] - obstacles[2]
        min_y = obstacles[1] - obstacles[2]
        max_x = obstacles[0] + obstacles[2]
        max_y = obstacles[1] + obstacles[2]
        lst.append(min_x)
        lst.append(min_y)
        lst.append(max_x)
        lst.append(max_y)
        return lst

    def list_manager(self, obstacles):
        if obstacles.shape[1] == 0:
            return
        if obstacles.shape[1] == 1:
            lst1 = self.create_list_of_rect(obstacles[0][0])
            return lst1
        if obstacles.shape[1] == 2:
            lst1 = self.create_list_of_rect(obstacles[0][0])
            lst2 = self.create_list_of_rect(obstacles[0][1])
            return lst1, lst2
        return

    def _median_blur(self, img):
        img = cv2.medianBlur(img, 5)
        return img
    def _convert_color_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return img

if __name__ == '__main__':
    obstacle_detector = ObstacleDetector()
    camera_repository = JSONCameraModelRepository('../../data/camera_models/camera_models.json')
    camera_model = camera_repository.get_camera_model_by_id(0)

    images = glob.glob('../../data/images/full_scene/*.jpg')

    for filename in images:
        image = cv2.imread(filename, 0)

        image = camera_model.undistort_image(image)

        try:
            cimg = obstacle_detector.detect_obstacle(image)[0]
            ob = obstacle_detector.detect_obstacle(image)[1]
            ab = obstacle_detector.list_manager(ob)
            print(ab, ': ', filename)
        except NoMatchingCirclesFound:
            pass

        cv2.imshow('detected circles', cimg)
        cv2.waitKey(2000)
