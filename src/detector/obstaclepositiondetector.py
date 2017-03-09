import cv2
import glob

from infrastructure.camera import JSONCameraModelRepository
from detector.robotpositiondetector import CircleDetector
from detector.robotpositiondetector import NoMatchingCirclesFound


RATIO = 1
TARGET_MIN_DISTANCE = 20
TARGET_MIN_RADIUS = 20
TARGET_MAX_RADIUS = 40


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
        return cimg

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
            cimg = obstacle_detector.detect_obstacle(image)
        except NoMatchingCirclesFound:
            pass

        cv2.imshow('detected circles', cimg)
        cv2.waitKey(2000)
